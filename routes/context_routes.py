from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import time
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from schemas.context import (
    FileUploadResponse, ContextPromptRequest, ContextPromptResponse, 
    ContextExecutionList
)
from database import get_db, ContextPromptExecution, get_model_info
from utils.file_processors import FileProcessor, FileProcessingError, is_supported_file, validate_file_size
from services.context_services import (
    LangChainContextService, 
    SemanticKernelContextService, 
    LangGraphContextService
)
from logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/context", tags=["context"])

# In-memory storage for temporary files (in production, use Redis or database)
temp_files = {}

# Context service instances (lazy loaded)
_context_services = {
    "semantic-kernel": None,
    "langchain": None,
    "langgraph": None
}

def get_context_service(service_name: str):
    """Lazy load context service instances"""
    if _context_services[service_name] is None:
        logger.info(f"Initializing {service_name} context service for prompt execution")
        if service_name == "semantic-kernel":
            _context_services[service_name] = SemanticKernelContextService()
        elif service_name == "langchain":
            _context_services[service_name] = LangChainContextService()
        elif service_name == "langgraph":
            _context_services[service_name] = LangGraphContextService()
    return _context_services[service_name]


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(..., description="File to upload (PDF, CSV, TXT, JSON)")
):
    """
    Upload and process a file for use as context in prompts.
    
    Supports PDF, CSV, TXT, and JSON files up to 10MB.
    Files are processed immediately and stored temporarily.
    
    Args:
        file: The uploaded file
        
    Returns:
        FileUploadResponse with file ID and processing details
        
    Raises:
        HTTPException: If file is invalid, too large, or processing fails
    """
    request_id = getattr(request.state, 'request_id', None)
    start_time = time.time()
    
    logger.info("File upload started",
               filename=file.filename,
               content_type=file.content_type,
               request_id=request_id)
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        if not is_supported_file(file.filename):
            supported = ['.pdf', '.csv', '.txt', '.json']
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Supported formats: {', '.join(supported)}"
            )
        
        # Read file content to check size
        file_content = await file.read()
        file_size = len(file_content)
        
        if not validate_file_size(file_size):
            raise HTTPException(
                status_code=413, 
                detail="File too large. Maximum size is 10MB"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Process file content
            processed_content, processing_time = FileProcessor.process_file(
                temp_file_path, 
                file.filename
            )
            
            # Store in temporary storage
            temp_files[file_id] = {
                'file_path': temp_file_path,
                'original_filename': file.filename,
                'file_type': Path(file.filename).suffix.lower()[1:],  # Remove dot
                'file_size_bytes': file_size,
                'processed_content': processed_content,
                'processed_content_length': len(processed_content),
                'processing_time_ms': processing_time,
                'created_at': datetime.utcnow(),
                'request_id': request_id
            }
            
            total_time = (time.time() - start_time) * 1000
            
            logger.info("File upload completed successfully",
                       file_id=file_id,
                       filename=file.filename,
                       file_size_bytes=file_size,
                       processed_content_length=len(processed_content),
                       processing_time_ms=round(processing_time, 2),
                       total_time_ms=round(total_time, 2),
                       request_id=request_id)
            
            return FileUploadResponse(
                file_id=file_id,
                original_filename=file.filename,
                file_type=Path(file.filename).suffix.lower()[1:],
                file_size_bytes=file_size,
                processed_content_length=len(processed_content),
                processing_time_ms=round(processing_time, 2),
                status="success",
                error_message=None
            )
            
        except FileProcessingError as e:
            # Clean up temp file
            os.unlink(temp_file_path)
            
            total_time = (time.time() - start_time) * 1000
            logger.error("File processing failed",
                        filename=file.filename,
                        error=str(e),
                        total_time_ms=round(total_time, 2),
                        request_id=request_id)
            
            raise HTTPException(status_code=422, detail=str(e))
            
    except HTTPException:
        raise
    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        logger.error("File upload failed",
                    filename=file.filename if file else "unknown",
                    error=str(e),
                    error_type=type(e).__name__,
                    total_time_ms=round(total_time, 2),
                    request_id=request_id)
        
        raise HTTPException(
            status_code=500, 
            detail=f"File upload failed: {str(e)}"
        )


@router.post("/execute", response_model=ContextPromptResponse)
async def execute_context_prompt(
    request_data: ContextPromptRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Execute a prompt using uploaded file content as context.
    
    Replaces [context] placeholder in system prompt with processed file content,
    executes the prompt using the specified AI method, and tracks costs.
    
    Args:
        request_data: The prompt execution request
        request: FastAPI request object
        db: Database session
        
    Returns:
        ContextPromptResponse with execution results and metrics
        
    Raises:
        HTTPException: If file not found, validation fails, or execution fails
    """
    request_id = getattr(request.state, 'request_id', None)
    start_time = time.time()
    user_ip = request.client.host if request.client else None
    
    logger.info("Context prompt execution started",
               file_ids=request_data.file_ids,
               file_count=len(request_data.file_ids),
               method=request_data.method,
               system_prompt_length=len(request_data.system_prompt),
               user_prompt_length=len(request_data.user_prompt),
               request_id=request_id)
    
    # Create database record for tracking
    execution_record = ContextPromptExecution(
        original_filename="",  # Will be updated
        file_type="",  # Will be updated
        file_size_bytes=0,  # Will be updated
        system_prompt=request_data.system_prompt,
        user_prompt=request_data.user_prompt,
        method=request_data.method,
        request_id=request_id,
        user_ip=user_ip,
        status="processing"
    )
    
    try:
        # Validate all files exist
        missing_files = [fid for fid in request_data.file_ids if fid not in temp_files]
        if missing_files:
            raise HTTPException(
                status_code=404, 
                detail=f"Files not found: {', '.join(missing_files)}. Please upload files first."
            )
        
        # Collect all file data and combine content
        combined_content = []
        filenames = []
        file_types = []
        total_size = 0
        total_processing_time = 0
        
        for file_id in request_data.file_ids:
            file_data = temp_files[file_id]
            combined_content.append(f"\n\n--- File: {file_data['original_filename']} ---\n{file_data['processed_content']}")
            filenames.append(file_data['original_filename'])
            file_types.append(file_data['file_type'])
            total_size += file_data['file_size_bytes']
            total_processing_time += file_data['processing_time_ms']
        
        combined_content_str = ''.join(combined_content)
        combined_file_type = 'multiple' if len(file_types) > 1 else file_types[0]
        
        # Update execution record with combined file info
        execution_record.original_filename = ', '.join(filenames)
        execution_record.file_type = combined_file_type
        execution_record.file_size_bytes = total_size
        execution_record.processed_content_length = len(combined_content_str)
        execution_record.file_processing_time_ms = total_processing_time
        
        # Validate system prompt contains [context] placeholder
        if '[context]' not in request_data.system_prompt:
            execution_record.status = "failed"
            execution_record.error_message = "System prompt must contain [context] placeholder"
            db.add(execution_record)
            db.commit()
            
            raise HTTPException(
                status_code=400,
                detail="System prompt must contain [context] placeholder"
            )
        
        # Replace [context] with combined file content
        final_system_prompt = request_data.system_prompt.replace(
            '[context]', 
            combined_content_str
        )
        
        execution_record.final_prompt_length = len(final_system_prompt)
        
        logger.debug("Executing context prompt",
                    file_ids=request_data.file_ids,
                    filenames=filenames,
                    final_prompt_length=len(final_system_prompt),
                    method=request_data.method)
        
        # Get model info
        model_info = get_model_info()
        execution_record.provider = model_info["provider"]
        execution_record.model = model_info["model"]
        
        # Execute with LLM using context service
        llm_start_time = time.time()
        context_service = get_context_service(request_data.method)
        
        # Use the execute_prompt method for direct prompt execution (not story generation)
        llm_response, usage_info = await context_service.execute_prompt(
            final_system_prompt,
            request_data.user_prompt
        )
        
        llm_execution_time = (time.time() - llm_start_time) * 1000
        total_execution_time = (time.time() - start_time) * 1000
        
        # Update execution record with results
        execution_record.llm_response = llm_response
        execution_record.llm_execution_time_ms = llm_execution_time
        execution_record.total_execution_time_ms = total_execution_time
        execution_record.input_tokens = usage_info["input_tokens"]
        execution_record.output_tokens = usage_info["output_tokens"]
        execution_record.total_tokens = usage_info["total_tokens"]
        execution_record.estimated_cost_usd = usage_info["estimated_cost_usd"]
        execution_record.input_cost_per_1k_tokens = usage_info["input_cost_per_1k_tokens"]
        execution_record.output_cost_per_1k_tokens = usage_info["output_cost_per_1k_tokens"]
        execution_record.status = "completed"
        execution_record.completed_at = datetime.utcnow()
        
        # Save to database
        db.add(execution_record)
        db.commit()
        db.refresh(execution_record)
        
        # Clean up temporary files
        for file_id in request_data.file_ids:
            try:
                file_data = temp_files[file_id]
                os.unlink(file_data['file_path'])
                del temp_files[file_id]
            except Exception as cleanup_error:
                logger.warning("Failed to clean up temporary file",
                              file_id=file_id,
                              error=str(cleanup_error))
        
        logger.info("Context prompt execution completed successfully",
                   execution_id=execution_record.id,
                   file_ids=request_data.file_ids,
                   filenames=filenames,
                   method=request_data.method,
                   response_length=len(llm_response),
                   llm_execution_time_ms=round(llm_execution_time, 2),
                   total_execution_time_ms=round(total_execution_time, 2),
                   input_tokens=usage_info["input_tokens"],
                   output_tokens=usage_info["output_tokens"],
                   estimated_cost_usd=usage_info["estimated_cost_usd"],
                   request_id=request_id)
        
        return ContextPromptResponse(
            id=execution_record.id,
            llm_response=llm_response,
            original_filename=', '.join(filenames),
            file_type=combined_file_type,
            processed_content_length=len(combined_content_str),
            final_prompt_length=len(final_system_prompt),
            file_processing_time_ms=total_processing_time,
            llm_execution_time_ms=round(llm_execution_time, 2),
            total_execution_time_ms=round(total_execution_time, 2),
            input_tokens=usage_info["input_tokens"],
            output_tokens=usage_info["output_tokens"],
            total_tokens=usage_info["total_tokens"],
            estimated_cost_usd=usage_info["estimated_cost_usd"],
            input_cost_per_1k_tokens=usage_info["input_cost_per_1k_tokens"],
            output_cost_per_1k_tokens=usage_info["output_cost_per_1k_tokens"],
            method=request_data.method,
            model=model_info["model"],
            request_id=request_id,
            created_at=execution_record.created_at
        )
        
    except HTTPException:
        execution_record.status = "failed"
        execution_record.total_execution_time_ms = (time.time() - start_time) * 1000
        db.add(execution_record)
        db.commit()
        raise
    except Exception as e:
        execution_record.status = "failed"
        execution_record.error_message = str(e)
        execution_record.total_execution_time_ms = (time.time() - start_time) * 1000
        db.add(execution_record)
        db.commit()
        
        logger.error("Context prompt execution failed",
                    file_ids=request_data.file_ids,
                    method=request_data.method,
                    error=str(e),
                    error_type=type(e).__name__,
                    total_time_ms=round((time.time() - start_time) * 1000, 2),
                    request_id=request_id)
        
        raise HTTPException(
            status_code=500,
            detail=f"Execution failed: {str(e)}"
        )


@router.get("/files")
async def get_uploaded_files(request: Request):
    """Get list of uploaded files.
    
    Returns a list of currently uploaded files with their metadata.
    """
    request_id = getattr(request.state, 'request_id', None)
    logger.info("Fetching uploaded files list", request_id=request_id)
    
    files_list = []
    for file_id, file_info in temp_files.items():
        files_list.append({
            "id": file_id,
            "name": file_info['original_filename'],
            "size": file_info['file_size_bytes'],
            "upload_date": file_info['created_at'].isoformat()
        })
    
    logger.info("Files list retrieved", 
                file_count=len(files_list), 
                request_id=request_id)
    
    return files_list


@router.delete("/files/{file_id}")
async def delete_uploaded_file(
    file_id: str,
    request: Request
):
    """Delete an uploaded file."""
    request_id = getattr(request.state, 'request_id', None)
    
    if file_id not in temp_files:
        logger.warning("File not found for deletion", 
                      file_id=file_id, 
                      request_id=request_id)
        raise HTTPException(status_code=404, detail="File not found")
    
    file_info = temp_files[file_id]
    filename = file_info['original_filename']
    
    # Clean up temp file
    try:
        if os.path.exists(file_info['file_path']):
            os.unlink(file_info['file_path'])
    except Exception as e:
        logger.warning("Error deleting temp file", 
                      file_path=file_info['file_path'],
                      error=str(e),
                      request_id=request_id)
    
    # Remove from memory
    del temp_files[file_id]
    
    logger.info("File deleted successfully", 
                file_id=file_id,
                filename=filename,
                request_id=request_id)
    
    return {"message": "File deleted successfully"}


@router.get("/executions", response_model=List[ContextExecutionList])
async def get_context_executions(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get list of context prompt executions.
    
    Returns a paginated list of previous context prompt executions
    ordered by creation date (newest first).
    
    Args:
        skip: Number of executions to skip
        limit: Maximum number of executions to return
        db: Database session
        
    Returns:
        List of ContextExecutionList objects
    """
    executions = db.query(ContextPromptExecution).order_by(
        ContextPromptExecution.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [
        ContextExecutionList(
            id=execution.id,
            original_filename=execution.original_filename,
            file_type=execution.file_type,
            method=execution.method,
            model=execution.model,
            estimated_cost_usd=float(execution.estimated_cost_usd) if execution.estimated_cost_usd else None,
            total_tokens=execution.total_tokens,
            total_execution_time_ms=execution.total_execution_time_ms,
            created_at=execution.created_at.isoformat(),
            status=execution.status
        )
        for execution in executions
    ]


@router.get("/executions/{execution_id}", response_model=ContextPromptResponse)
async def get_context_execution(
    execution_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific context prompt execution by ID.
    
    Args:
        execution_id: The execution ID
        db: Database session
        
    Returns:
        Complete ContextPromptResponse with execution details
        
    Raises:
        HTTPException: 404 if execution not found
    """
    execution = db.query(ContextPromptExecution).filter(
        ContextPromptExecution.id == execution_id
    ).first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return ContextPromptResponse.from_orm(execution)