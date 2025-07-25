from fastapi import APIRouter, Query, HTTPException, Request
from fastapi.responses import HTMLResponse
from typing import List, Optional, Dict, Any
import json
import os
from datetime import datetime, timedelta
import re
from pathlib import Path

from config import settings
from logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/logs", tags=["logs"])

def parse_log_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse a structured log line into a dictionary.
    
    Handles both JSON and plain text log formats. For plain text, parses the format:
    [timestamp] [LEVEL] [logger] message | key=value key=value
    
    Args:
        line: A single log line to parse.
        
    Returns:
        A dictionary containing parsed log data with fields like timestamp,
        level, event, logger, and any extracted key-value pairs. Returns
        None if the line cannot be parsed.
        
    Examples:
        >>> parse_log_line('{"timestamp": "2024-01-01T10:00:00", "level": "info"}')
        {'timestamp': '2024-01-01T10:00:00', 'level': 'info'}
        >>> parse_log_line('[2024-01-01T10:00:00Z] [INFO] [main] Starting server | version=1.0.0')
        {'timestamp': '2024-01-01T10:00:00Z', 'level': 'INFO', 'logger': 'main', 'event': 'Starting server', 'version': '1.0.0'}
    """
    try:
        line = line.strip()
        if not line:
            return None
            
        # Try to parse as JSON first
        if line.startswith('{') and line.endswith('}'):
            return json.loads(line)
        
        # Parse plain text format: [timestamp] [LEVEL] [logger] message | key=value key=value
        log_data = {}
        
        # Extract components using step-by-step parsing
        remaining = line
        
        # Extract timestamp: [2025-07-24T23:08:33.297639Z]
        timestamp_match = re.search(r'^\[([^\]]+)\]', remaining)
        if timestamp_match:
            log_data['timestamp'] = timestamp_match.group(1)
            remaining = remaining[timestamp_match.end():].strip()
        
        # Extract level: [INFO]
        level_match = re.search(r'^\[([^\]]+)\]', remaining)
        if level_match:
            log_data['level'] = level_match.group(1).lower()
            remaining = remaining[level_match.end():].strip()
        
        # Extract logger: [main]
        logger_match = re.search(r'^\[([^\]]+)\]', remaining)
        if logger_match:
            log_data['logger'] = logger_match.group(1)
            remaining = remaining[logger_match.end():].strip()
        
        # Split remaining on | if present
        if '|' in remaining:
            message_part, additional_part = remaining.split('|', 1)
            log_data['event'] = message_part.strip()
            
            # Parse key=value pairs from additional part
            additional_part = additional_part.strip()
            if additional_part:
                # Split by space and parse key=value pairs
                parts = additional_part.split()
                for part in parts:
                    if '=' in part:
                        key, value = part.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Try to convert numeric values
                        try:
                            if '.' in value and value.replace('.', '').replace('-', '').isdigit():
                                log_data[key] = float(value)
                            elif value.replace('-', '').isdigit():
                                log_data[key] = int(value)
                            else:
                                log_data[key] = value
                        except ValueError:
                            log_data[key] = value
        else:
            # No additional data, just the message
            log_data['event'] = remaining.strip()
        
        # Return data if we found the basic components
        if 'timestamp' in log_data and 'level' in log_data:
            return log_data
        
        # Fallback: try to extract any bracketed components we can find
        else:
            # Extract timestamp if present
            timestamp_match = re.search(r'\[([^\]]+Z)\]', line)
            if timestamp_match:
                log_data['timestamp'] = timestamp_match.group(1)
            
            # Extract level if present
            level_match = re.search(r'\[(DEBUG|INFO|WARNING|ERROR|CRITICAL)\]', line, re.IGNORECASE)
            if level_match:
                log_data['level'] = level_match.group(1).lower()
            
            # If we found some components, use the rest as the event
            if log_data:
                # Remove the parsed parts and use the rest as event
                remaining = line
                for match in [timestamp_match, level_match]:
                    if match:
                        remaining = remaining.replace(match.group(0), '', 1)
                log_data['event'] = remaining.strip()
                return log_data
        
        return None
        
    except Exception as e:
        logger.debug("Failed to parse log line", error=str(e), line_preview=line[:100])
        return None

def get_log_files() -> List[str]:
    """Get list of available log files.
    
    Scans the configured log directory for all log files, including
    rotated logs. Files are sorted by modification time (newest first).
    
    Returns:
        A list of absolute file paths to log files, sorted by modification
        time in descending order. Returns empty list if log directory
        doesn't exist.
        
    Examples:
        >>> get_log_files()
        ['/app/logs/app.log', '/app/logs/app.log.2024-01-01_10', ...]
    """
    log_dir = Path(settings.log_file_path).parent if settings.log_file_path else Path("logs")
    
    if not log_dir.exists():
        return []
    
    log_files = []
    for file_path in log_dir.glob("*.log*"):
        if file_path.is_file():
            log_files.append(str(file_path))
    
    return sorted(log_files, key=lambda x: os.path.getmtime(x), reverse=True)

def read_log_file(file_path: str, page: int = 1, per_page: int = 50, 
                  level_filter: Optional[str] = None, 
                  search_term: Optional[str] = None) -> Dict[str, Any]:
    """Read and paginate log file entries.
    
    Reads a log file, parses each line, applies filters, and returns
    paginated results. Entries are returned in reverse chronological
    order (newest first).
    
    Args:
        file_path: Path to the log file to read.
        page: Page number (1-indexed). Defaults to 1.
        per_page: Number of entries per page. Defaults to 50.
        level_filter: Optional log level filter (debug, info, warning, error).
        search_term: Optional search term to filter entries.
        
    Returns:
        A dictionary containing:
        - entries: List of parsed log entries for the current page
        - pagination: Pagination metadata (current_page, total_pages, etc.)
        - filters: Applied filters (level_filter, search_term)
        
    Raises:
        HTTPException: 404 if file not found, 500 for read errors.
        
    Examples:
        >>> read_log_file('/logs/app.log', page=1, per_page=25, level_filter='error')
        {
            'entries': [...],
            'pagination': {'current_page': 1, 'total_pages': 5, ...},
            'filters': {'level_filter': 'error', 'search_term': None}
        }
    """
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Log file not found")
    
    all_entries = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                parsed = parse_log_line(line)
                if parsed:
                    parsed['line_number'] = line_num
                    parsed['raw_line'] = line.strip()
                    
                    # Apply level filter
                    if level_filter and parsed.get('level', '').lower() != level_filter.lower():
                        continue
                    
                    # Apply search filter
                    if search_term:
                        search_text = json.dumps(parsed).lower()
                        if search_term.lower() not in search_text:
                            continue
                    
                    all_entries.append(parsed)
    
    except Exception as e:
        logger.error(f"Error reading log file: {e}")
        raise HTTPException(status_code=500, detail="Error reading log file")
    
    # Reverse to show newest first
    all_entries.reverse()
    
    # Calculate pagination
    total_entries = len(all_entries)
    total_pages = (total_entries + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    entries = all_entries[start_idx:end_idx]
    
    return {
        'entries': entries,
        'pagination': {
            'current_page': page,
            'per_page': per_page,
            'total_entries': total_entries,
            'total_pages': total_pages,
            'has_previous': page > 1,
            'has_next': page < total_pages,
            'previous_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page < total_pages else None
        },
        'filters': {
            'level_filter': level_filter,
            'search_term': search_term
        }
    }

@router.get("/", response_class=HTMLResponse)
async def log_viewer_page():
    """Serve the log viewer HTML page.
    
    Returns a complete HTML page with JavaScript for interactive log viewing.
    The page includes:
    - Real-time log viewing with auto-refresh
    - Filtering by log level and search terms
    - Pagination controls
    - Statistics dashboard
    - Responsive design with Bootstrap
    
    Returns:
        HTMLResponse containing the complete log viewer interface.
        
    Examples:
        >>> GET /logs/
        Returns interactive log viewer HTML page
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Story Generator - Log Viewer</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.2/font/bootstrap-icons.css">
        <link rel="stylesheet" href="/static/logs.css">
        <style>
            .log-entry {
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 0.85rem;
                border-left: 4px solid #ddd;
                margin-bottom: 1rem;
            }
            .log-entry.level-debug { border-left-color: #6c757d; }
            .log-entry.level-info { border-left-color: #0d6efd; }
            .log-entry.level-warning { border-left-color: #fd7e14; }
            .log-entry.level-error { border-left-color: #dc3545; }
            .log-entry.level-critical { border-left-color: #6f42c1; }
            
            .log-timestamp { color: #6c757d; font-weight: 500; }
            .log-level { font-weight: bold; text-transform: uppercase; }
            .log-level.debug { color: #6c757d; }
            .log-level.info { color: #0d6efd; }
            .log-level.warning { color: #fd7e14; }
            .log-level.error { color: #dc3545; }
            .log-level.critical { color: #6f42c1; }
            
            .log-message { font-weight: 500; margin: 0.25rem 0; }
            .log-details { font-size: 0.8rem; color: #495057; }
            .log-details .badge { font-size: 0.75rem; margin-right: 0.25rem; }
            
            .log-search { background: #f8f9fa; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; }
            .stats-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .refresh-btn { position: fixed; bottom: 2rem; right: 2rem; z-index: 1000; }
            
            .json-viewer {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 0.375rem;
                padding: 0.75rem;
                margin-top: 0.5rem;
                max-height: 200px;
                overflow-y: auto;
            }
            
            .collapsible-content {
                max-height: 100px;
                overflow: hidden;
                transition: max-height 0.3s ease;
            }
            .collapsible-content.expanded {
                max-height: none;
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/">
                    <i class="bi bi-file-text me-2"></i>AI Story Generator - Log Viewer
                </a>
                <div class="d-flex">
                    <a href="/" class="btn btn-outline-light btn-sm me-2">
                        <i class="bi bi-house"></i> Home
                    </a>
                    <button id="refreshBtn" class="btn btn-outline-light btn-sm">
                        <i class="bi bi-arrow-clockwise"></i> Refresh
                    </button>
                </div>
            </div>
        </nav>

        <div class="container-fluid my-4">
            <!-- Search and Filters -->
            <div class="log-search">
                <div class="row">
                    <div class="col-md-6">
                        <label for="searchInput" class="form-label">Search Logs</label>
                        <input type="text" class="form-control" id="searchInput" placeholder="Search in messages, errors, request IDs...">
                    </div>
                    <div class="col-md-3">
                        <label for="levelFilter" class="form-label">Log Level</label>
                        <select class="form-select" id="levelFilter">
                            <option value="">All Levels</option>
                            <option value="debug">Debug</option>
                            <option value="info">Info</option>
                            <option value="warning">Warning</option>
                            <option value="error">Error</option>
                            <option value="critical">Critical</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <label for="logFile" class="form-label">Log File</label>
                        <select class="form-select" id="logFile">
                            <option value="">Loading...</option>
                        </select>
                    </div>
                </div>
                <div class="row mt-3">
                    <div class="col">
                        <button class="btn btn-primary" onclick="searchLogs()">
                            <i class="bi bi-search"></i> Search
                        </button>
                        <button class="btn btn-secondary ms-2" onclick="clearFilters()">
                            <i class="bi bi-x-circle"></i> Clear
                        </button>
                        <div class="float-end">
                            <label for="perPageSelect" class="form-label me-2">Entries per page:</label>
                            <select class="form-select d-inline-block w-auto" id="perPageSelect">
                                <option value="25">25</option>
                                <option value="50" selected>50</option>
                                <option value="100">100</option>
                                <option value="200">200</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Stats Row -->
            <div class="row mb-4">
                <div class="col-md-12">
                    <div class="card stats-card">
                        <div class="card-body">
                            <div class="row text-center">
                                <div class="col">
                                    <h5 class="mb-0" id="totalEntries">-</h5>
                                    <small>Total Entries</small>
                                </div>
                                <div class="col">
                                    <h5 class="mb-0" id="currentPage">-</h5>
                                    <small>Current Page</small>
                                </div>
                                <div class="col">
                                    <h5 class="mb-0" id="errorCount">-</h5>
                                    <small>Errors</small>
                                </div>
                                <div class="col">
                                    <h5 class="mb-0" id="warningCount">-</h5>
                                    <small>Warnings</small>
                                </div>
                                <div class="col">
                                    <h5 class="mb-0" id="lastUpdated">-</h5>
                                    <small>Last Updated</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Log Entries -->
            <div id="logEntries">
                <div class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Loading log entries...</p>
                </div>
            </div>

            <!-- Pagination -->
            <nav aria-label="Log pagination" id="paginationNav" style="display: none;">
                <ul class="pagination justify-content-center" id="pagination">
                </ul>
            </nav>
        </div>

        <!-- Floating Refresh Button -->
        <button class="btn btn-primary refresh-btn rounded-circle" onclick="refreshLogs()" title="Auto-refresh">
            <i class="bi bi-arrow-clockwise"></i>
        </button>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            let currentData = null;
            let currentPage = 1;
            let autoRefreshInterval = null;

            // Initialize
            document.addEventListener('DOMContentLoaded', function() {
                loadLogFiles();
                loadLogs();
                
                // Set up auto-refresh
                autoRefreshInterval = setInterval(refreshLogs, 30000); // 30 seconds
                
                // Search on Enter
                document.getElementById('searchInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        searchLogs();
                    }
                });
                
                // Auto-search on select changes
                document.getElementById('levelFilter').addEventListener('change', searchLogs);
                document.getElementById('logFile').addEventListener('change', searchLogs);
                document.getElementById('perPageSelect').addEventListener('change', searchLogs);
            });

            async function loadLogFiles() {
                try {
                    const response = await fetch('/logs/files');
                    const files = await response.json();
                    
                    const select = document.getElementById('logFile');
                    select.innerHTML = '<option value="">Select log file...</option>';
                    
                    files.forEach(file => {
                        const option = document.createElement('option');
                        option.value = file;
                        option.textContent = file.split('/').pop();
                        if (file.includes('app.log') && !file.includes('.')) {
                            option.selected = true;
                        }
                        select.appendChild(option);
                    });
                } catch (error) {
                    console.error('Error loading log files:', error);
                }
            }

            async function loadLogs(page = 1) {
                const logFile = document.getElementById('logFile').value;
                const level = document.getElementById('levelFilter').value;
                const search = document.getElementById('searchInput').value;
                const perPage = document.getElementById('perPageSelect').value;
                
                if (!logFile) {
                    return;
                }
                
                try {
                    const params = new URLSearchParams({
                        page: page,
                        per_page: perPage
                    });
                    
                    if (level) params.append('level', level);
                    if (search) params.append('search', search);
                    
                    const response = await fetch(`/logs/entries/${encodeURIComponent(logFile)}?${params}`);
                    const data = await response.json();
                    
                    currentData = data;
                    currentPage = page;
                    
                    renderLogEntries(data.entries);
                    renderPagination(data.pagination);
                    updateStats(data);
                    
                } catch (error) {
                    console.error('Error loading logs:', error);
                    document.getElementById('logEntries').innerHTML = 
                        '<div class="alert alert-danger">Error loading logs: ' + error.message + '</div>';
                }
            }

            function renderLogEntries(entries) {
                const container = document.getElementById('logEntries');
                
                if (entries.length === 0) {
                    container.innerHTML = '<div class="alert alert-info">No log entries found matching your criteria.</div>';
                    return;
                }
                
                const html = entries.map(entry => {
                    const level = (entry.level || 'info').toLowerCase();
                    const timestamp = entry.timestamp ? new Date(entry.timestamp).toLocaleString() : 'Unknown';
                    const message = entry.event || entry.message || 'No message';
                    
                    // Extract key details
                    const details = Object.entries(entry)
                        .filter(([key, value]) => !['timestamp', 'level', 'event', 'message', 'logger', 'line_number', 'raw_line'].includes(key))
                        .map(([key, value]) => `<span class="badge bg-secondary">${key}: ${value}</span>`)
                        .join(' ');
                    
                    return `
                        <div class="card log-entry level-${level}">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-start">
                                    <div class="flex-grow-1">
                                        <div class="d-flex align-items-center mb-2">
                                            <span class="log-timestamp">${timestamp}</span>
                                            <span class="log-level ${level} ms-2">[${level.toUpperCase()}]</span>
                                            ${entry.logger ? `<span class="badge bg-primary ms-2">${entry.logger}</span>` : ''}
                                        </div>
                                        <div class="log-message">${message}</div>
                                        ${details ? `<div class="log-details mt-2">${details}</div>` : ''}
                                    </div>
                                    <div class="ms-3">
                                        <button class="btn btn-sm btn-outline-secondary" onclick="toggleDetails(this, ${entry.line_number})">
                                            <i class="bi bi-eye"></i>
                                        </button>
                                    </div>
                                </div>
                                <div id="details-${entry.line_number}" class="json-viewer" style="display: none;">
                                    <pre><code>${JSON.stringify(entry, null, 2)}</code></pre>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');
                
                container.innerHTML = html;
            }

            function renderPagination(pagination) {
                const nav = document.getElementById('paginationNav');
                const container = document.getElementById('pagination');
                
                if (pagination.total_pages <= 1) {
                    nav.style.display = 'none';
                    return;
                }
                
                nav.style.display = 'block';
                
                let html = '';
                
                // Previous button
                html += `<li class="page-item ${!pagination.has_previous ? 'disabled' : ''}">
                    <a class="page-link" href="#" onclick="loadLogs(${pagination.previous_page || 1})">Previous</a>
                </li>`;
                
                // Page numbers
                const startPage = Math.max(1, pagination.current_page - 2);
                const endPage = Math.min(pagination.total_pages, pagination.current_page + 2);
                
                if (startPage > 1) {
                    html += `<li class="page-item"><a class="page-link" href="#" onclick="loadLogs(1)">1</a></li>`;
                    if (startPage > 2) {
                        html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
                    }
                }
                
                for (let i = startPage; i <= endPage; i++) {
                    html += `<li class="page-item ${i === pagination.current_page ? 'active' : ''}">
                        <a class="page-link" href="#" onclick="loadLogs(${i})">${i}</a>
                    </li>`;
                }
                
                if (endPage < pagination.total_pages) {
                    if (endPage < pagination.total_pages - 1) {
                        html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
                    }
                    html += `<li class="page-item"><a class="page-link" href="#" onclick="loadLogs(${pagination.total_pages})">${pagination.total_pages}</a></li>`;
                }
                
                // Next button
                html += `<li class="page-item ${!pagination.has_next ? 'disabled' : ''}">
                    <a class="page-link" href="#" onclick="loadLogs(${pagination.next_page || pagination.total_pages})">Next</a>
                </li>`;
                
                container.innerHTML = html;
            }

            function updateStats(data) {
                document.getElementById('totalEntries').textContent = data.pagination.total_entries.toLocaleString();
                document.getElementById('currentPage').textContent = `${data.pagination.current_page} / ${data.pagination.total_pages}`;
                
                // Count errors and warnings
                const errorCount = data.entries.filter(e => e.level === 'error').length;
                const warningCount = data.entries.filter(e => e.level === 'warning').length;
                
                document.getElementById('errorCount').textContent = errorCount;
                document.getElementById('warningCount').textContent = warningCount;
                document.getElementById('lastUpdated').textContent = new Date().toLocaleTimeString();
            }

            function toggleDetails(button, lineNumber) {
                const details = document.getElementById(`details-${lineNumber}`);
                const icon = button.querySelector('i');
                
                if (details.style.display === 'none') {
                    details.style.display = 'block';
                    icon.className = 'bi bi-eye-slash';
                } else {
                    details.style.display = 'none';
                    icon.className = 'bi bi-eye';
                }
            }

            function searchLogs() {
                loadLogs(1);
            }

            function clearFilters() {
                document.getElementById('searchInput').value = '';
                document.getElementById('levelFilter').value = '';
                loadLogs(1);
            }

            function refreshLogs() {
                loadLogs(currentPage);
            }

            // Cleanup interval on page unload
            window.addEventListener('beforeunload', function() {
                if (autoRefreshInterval) {
                    clearInterval(autoRefreshInterval);
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get("/files")
async def get_log_files_endpoint():
    """Get list of available log files.
    
    API endpoint that returns all available log files in the configured
    log directory. Used by the log viewer interface to populate the
    file selection dropdown.
    
    Returns:
        List of log file paths.
        
    Raises:
        HTTPException: 500 if unable to retrieve log files.
        
    Examples:
        >>> GET /logs/files
        ["/app/logs/app.log", "/app/logs/app.log.2024-01-01_10"]
    """
    logger.info("Log files requested")
    try:
        files = get_log_files()
        logger.info("Log files retrieved", file_count=len(files))
        return files
    except Exception as e:
        logger.error("Failed to get log files", error=str(e), error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to retrieve log files")

@router.get("/entries/{file_path:path}")
async def get_log_entries(
    file_path: str,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=500, description="Entries per page"),
    level: Optional[str] = Query(None, description="Filter by log level"),
    search: Optional[str] = Query(None, description="Search term")
):
    """Get paginated log entries from a specific file.
    
    Retrieves parsed and filtered log entries from the specified log file.
    Includes security checks to ensure only files within the log directory
    can be accessed.
    
    Args:
        file_path: Path to the log file (relative or absolute).
        page: Page number for pagination (1-indexed).
        per_page: Number of entries per page (1-500).
        level: Optional filter by log level (debug, info, warning, error).
        search: Optional search term to filter entries.
        
    Returns:
        Dictionary containing paginated log entries and metadata.
        
    Raises:
        HTTPException:
            - 403 if attempting to access files outside log directory
            - 404 if log file not found
            - 500 for other errors
            
    Examples:
        >>> GET /logs/entries/app.log?page=1&per_page=50&level=error
        {
            "entries": [...],
            "pagination": {...},
            "filters": {"level_filter": "error", "search_term": null}
        }
    """
    logger.info("Log entries requested", 
               file_path=file_path, 
               page=page, 
               per_page=per_page,
               level_filter=level,
               search_term=search)
    
    try:
        # Security check - ensure file is in logs directory
        abs_file_path = os.path.abspath(file_path)
        log_dir = os.path.abspath(Path(settings.log_file_path).parent if settings.log_file_path else "logs")
        
        if not abs_file_path.startswith(log_dir):
            logger.warning("Unauthorized log file access attempt", 
                          requested_path=file_path,
                          abs_path=abs_file_path)
            raise HTTPException(status_code=403, detail="Access denied")
        
        result = read_log_file(file_path, page, per_page, level, search)
        
        logger.info("Log entries retrieved", 
                   file_path=file_path,
                   total_entries=result['pagination']['total_entries'],
                   returned_entries=len(result['entries']))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve log entries", 
                    file_path=file_path, 
                    error=str(e),
                    error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Failed to retrieve log entries")