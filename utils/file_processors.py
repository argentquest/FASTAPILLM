import json
import csv
import io
import time
from typing import Tuple, Optional
from pathlib import Path

# Import PDF processing libraries
PDF_AVAILABLE = False
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    try:
        import pdfplumber
        PDF_AVAILABLE = True
    except ImportError:
        pass  # PDF processing will be disabled

from logging_config import get_logger

logger = get_logger(__name__)


class FileProcessingError(Exception):
    """Custom exception for file processing errors"""
    pass


class FileProcessor:
    """Handles processing of different file types into text content"""
    
    @staticmethod
    def process_file(file_path: str, original_filename: str) -> Tuple[str, float]:
        """
        Process a file and return its content as text with processing time.
        
        Args:
            file_path: Path to the uploaded file
            original_filename: Original filename with extension
            
        Returns:
            Tuple of (processed_content, processing_time_ms)
            
        Raises:
            FileProcessingError: If file processing fails
        """
        start_time = time.time()
        
        try:
            # Determine file type from extension
            file_ext = Path(original_filename).suffix.lower()
            
            logger.info("Processing file", 
                       filename=original_filename,
                       file_type=file_ext,
                       file_path=file_path)
            
            if file_ext == '.txt':
                content = FileProcessor._process_txt(file_path)
            elif file_ext == '.json':
                content = FileProcessor._process_json(file_path)
            elif file_ext == '.csv':
                content = FileProcessor._process_csv(file_path)
            elif file_ext == '.pdf':
                content = FileProcessor._process_pdf(file_path)
            else:
                raise FileProcessingError(f"Unsupported file type: {file_ext}")
            
            # Add header with filename
            header = f"=== FILE: {original_filename} ===\n\n"
            processed_content = header + content
            
            processing_time = (time.time() - start_time) * 1000
            
            logger.info("File processing completed",
                       filename=original_filename,
                       content_length=len(processed_content),
                       processing_time_ms=round(processing_time, 2))
            
            return processed_content, processing_time
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error("File processing failed",
                        filename=original_filename,
                        error=str(e),
                        error_type=type(e).__name__,
                        processing_time_ms=round(processing_time, 2))
            raise FileProcessingError(f"Failed to process {original_filename}: {str(e)}")
    
    @staticmethod
    def _process_txt(file_path: str) -> str:
        """Process a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if not content.strip():
                raise FileProcessingError("Text file is empty")
                
            return content.strip()
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    content = file.read()
                return content.strip()
            except Exception as e:
                raise FileProcessingError(f"Could not decode text file: {str(e)}")
        except Exception as e:
            raise FileProcessingError(f"Could not read text file: {str(e)}")
    
    @staticmethod
    def _process_json(file_path: str) -> str:
        """Process a JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Pretty print the JSON with proper formatting
            formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
            
            # Add a brief description
            description = f"JSON Data Structure:\n{'-' * 20}\n"
            return description + formatted_json
            
        except json.JSONDecodeError as e:
            raise FileProcessingError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise FileProcessingError(f"Could not read JSON file: {str(e)}")
    
    @staticmethod
    def _process_csv(file_path: str) -> str:
        """Process a CSV file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(file, delimiter=delimiter)
                rows = list(reader)
            
            if not rows:
                raise FileProcessingError("CSV file is empty")
            
            # Format as a readable table
            result = "CSV Data:\n" + "=" * 40 + "\n\n"
            
            # Add header row if present
            if rows:
                headers = rows[0]
                result += "Headers: " + " | ".join(headers) + "\n"
                result += "-" * (len(" | ".join(headers)) + 10) + "\n\n"
                
                # Add data rows (limit to first 50 rows to avoid huge content)
                data_rows = rows[1:51]  # Skip header, take up to 50 rows
                
                for i, row in enumerate(data_rows, 1):
                    result += f"Row {i}: " + " | ".join(str(cell) for cell in row) + "\n"
                
                if len(rows) > 51:  # Header + 50 data rows
                    result += f"\n... and {len(rows) - 51} more rows\n"
                
                result += f"\nTotal rows: {len(rows) - 1} (excluding header)\n"
                result += f"Total columns: {len(headers)}\n"
            
            return result
            
        except Exception as e:
            raise FileProcessingError(f"Could not process CSV file: {str(e)}")
    
    @staticmethod
    def _process_pdf(file_path: str) -> str:
        """Process a PDF file"""
        if not PDF_AVAILABLE:
            raise FileProcessingError("PDF processing not available. Please install PyPDF2 or pdfplumber.")
        
        try:
            # Try with PyPDF2 first
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    if len(pdf_reader.pages) == 0:
                        raise FileProcessingError("PDF file has no pages")
                    
                    text = ""
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        page_text = page.extract_text()
                        if page_text.strip():
                            text += f"\n--- Page {page_num} ---\n"
                            text += page_text.strip() + "\n"
                    
                    if not text.strip():
                        raise FileProcessingError("Could not extract text from PDF (may be image-based)")
                    
                    return text.strip()
                    
            except Exception as e:
                # If PyPDF2 fails, try pdfplumber
                try:
                    import pdfplumber
                    with pdfplumber.open(file_path) as pdf:
                        if len(pdf.pages) == 0:
                            raise FileProcessingError("PDF file has no pages")
                        
                        text = ""
                        for page_num, page in enumerate(pdf.pages, 1):
                            page_text = page.extract_text()
                            if page_text and page_text.strip():
                                text += f"\n--- Page {page_num} ---\n"
                                text += page_text.strip() + "\n"
                        
                        if not text.strip():
                            raise FileProcessingError("Could not extract text from PDF (may be image-based)")
                        
                        return text.strip()
                        
                except ImportError:
                    raise FileProcessingError(f"PDF processing failed with PyPDF2: {str(e)}")
                    
        except Exception as e:
            raise FileProcessingError(f"Could not process PDF file: {str(e)}")


def get_supported_extensions() -> list:
    """Get list of supported file extensions"""
    extensions = ['.txt', '.json', '.csv']
    if PDF_AVAILABLE:
        extensions.append('.pdf')
    return extensions


def is_supported_file(filename: str) -> bool:
    """Check if a file type is supported"""
    ext = Path(filename).suffix.lower()
    return ext in get_supported_extensions()


def validate_file_size(file_size: int, max_size_mb: int = 10) -> bool:
    """Validate file size against maximum allowed size"""
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes