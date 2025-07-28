from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/context", tags=["context"])

@router.get("/test")
async def test_context():
    """Test endpoint for context routes"""
    return {"message": "Context routes are working!"}

@router.post("/upload")
async def upload_file_simple():
    """Simplified upload endpoint for testing"""
    return {"message": "Upload endpoint working, but not implemented yet"}

@router.post("/execute") 
async def execute_simple():
    """Simplified execute endpoint for testing"""
    return {"message": "Execute endpoint working, but not implemented yet"}