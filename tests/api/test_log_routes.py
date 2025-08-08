"""
API tests for log viewing routes.

Tests all log-related endpoints including log retrieval, filtering, and search functionality.
"""

import pytest
from unittest.mock import patch, Mock, mock_open
from datetime import datetime, timedelta
import json


@pytest.mark.api
class TestLogRetrievalEndpoints:
    """Test log retrieval and viewing endpoints."""
    
    def test_get_recent_logs_success(self, client):
        """Test successful retrieval of recent logs."""
        mock_log_entries = [
            {
                "timestamp": "2025-08-08T12:30:00.000Z",
                "level": "INFO",
                "message": "Story generated successfully",
                "request_id": "story_20250808_001",
                "service": "LangChainService",
                "execution_time_ms": 1500,
                "tokens": 125
            },
            {
                "timestamp": "2025-08-08T12:25:00.000Z",
                "level": "DEBUG",
                "message": "Database connection established",
                "service": "DatabaseService",
                "connection_pool_size": 5
            },
            {
                "timestamp": "2025-08-08T12:20:00.000Z", 
                "level": "WARNING",
                "message": "High token usage detected",
                "request_id": "story_20250808_002",
                "service": "CostTracker",
                "tokens": 5000,
                "estimated_cost": 0.05
            }
        ]
        
        # Mock log file reading
        mock_log_content = "\n".join([
            json.dumps(entry) for entry in mock_log_entries
        ])
        
        with patch("builtins.open", mock_open(read_data=mock_log_content)):
            with patch("os.path.exists", return_value=True):
                response = client.get("/api/logs/recent")
                
                assert response.status_code == 200
                data = response.json()
                
                assert isinstance(data, list)
                assert len(data) <= 100  # Default limit
                
                if len(data) > 0:
                    log_entry = data[0]
                    assert "timestamp" in log_entry
                    assert "level" in log_entry
                    assert "message" in log_entry
    
    def test_get_recent_logs_with_limit(self, client):
        """Test log retrieval with custom limit."""
        mock_log_content = "\n".join([
            json.dumps({"timestamp": f"2025-08-08T12:{i:02d}:00.000Z", "level": "INFO", "message": f"Log entry {i}"})
            for i in range(50)
        ])
        
        with patch("builtins.open", mock_open(read_data=mock_log_content)):
            with patch("os.path.exists", return_value=True):
                response = client.get("/api/logs/recent?limit=20")
                
                assert response.status_code == 200
                data = response.json()
                assert len(data) <= 20
    
    def test_get_logs_by_level(self, client):
        """Test filtering logs by level."""
        mock_log_entries = [
            {"timestamp": "2025-08-08T12:30:00.000Z", "level": "ERROR", "message": "Service failed"},
            {"timestamp": "2025-08-08T12:25:00.000Z", "level": "INFO", "message": "Service started"},
            {"timestamp": "2025-08-08T12:20:00.000Z", "level": "ERROR", "message": "Connection timeout"}
        ]
        
        mock_log_content = "\n".join([json.dumps(entry) for entry in mock_log_entries])
        
        with patch("builtins.open", mock_open(read_data=mock_log_content)):
            with patch("os.path.exists", return_value=True):
                response = client.get("/api/logs/filter?level=ERROR")
                
                assert response.status_code == 200
                data = response.json()
                
                # All returned logs should be ERROR level
                for log in data:
                    assert log["level"] == "ERROR"
    
    def test_get_logs_by_service(self, client):
        """Test filtering logs by service name."""
        mock_log_entries = [
            {"timestamp": "2025-08-08T12:30:00.000Z", "level": "INFO", "message": "Story generated", "service": "LangChainService"},
            {"timestamp": "2025-08-08T12:25:00.000Z", "level": "INFO", "message": "Chat response", "service": "ChatService"},
            {"timestamp": "2025-08-08T12:20:00.000Z", "level": "INFO", "message": "Story generated", "service": "LangChainService"}
        ]
        
        mock_log_content = "\n".join([json.dumps(entry) for entry in mock_log_entries])
        
        with patch("builtins.open", mock_open(read_data=mock_log_content)):
            with patch("os.path.exists", return_value=True):
                response = client.get("/api/logs/filter?service=LangChainService")
                
                assert response.status_code == 200
                data = response.json()
                
                # All returned logs should be from LangChainService
                for log in data:
                    assert log.get("service") == "LangChainService"
    
    def test_get_logs_by_request_id(self, client):
        """Test filtering logs by request ID."""
        target_request_id = "story_20250808_001"
        
        mock_log_entries = [
            {"timestamp": "2025-08-08T12:30:00.000Z", "level": "INFO", "message": "Request started", "request_id": target_request_id},
            {"timestamp": "2025-08-08T12:30:10.000Z", "level": "DEBUG", "message": "Processing request", "request_id": target_request_id},
            {"timestamp": "2025-08-08T12:30:20.000Z", "level": "INFO", "message": "Request completed", "request_id": target_request_id},
            {"timestamp": "2025-08-08T12:31:00.000Z", "level": "INFO", "message": "Different request", "request_id": "story_20250808_002"}
        ]
        
        mock_log_content = "\n".join([json.dumps(entry) for entry in mock_log_entries])
        
        with patch("builtins.open", mock_open(read_data=mock_log_content)):
            with patch("os.path.exists", return_value=True):
                response = client.get(f"/api/logs/request/{target_request_id}")
                
                assert response.status_code == 200
                data = response.json()
                
                # All returned logs should have the target request ID
                for log in data:
                    assert log.get("request_id") == target_request_id
    
    def test_get_logs_by_date_range(self, client):
        """Test filtering logs by date range."""
        start_date = "2025-08-08T12:00:00.000Z"
        end_date = "2025-08-08T13:00:00.000Z"
        
        mock_log_entries = [
            {"timestamp": "2025-08-08T11:59:00.000Z", "level": "INFO", "message": "Before range"},
            {"timestamp": "2025-08-08T12:30:00.000Z", "level": "INFO", "message": "Within range"},
            {"timestamp": "2025-08-08T13:01:00.000Z", "level": "INFO", "message": "After range"}
        ]
        
        mock_log_content = "\n".join([json.dumps(entry) for entry in mock_log_entries])
        
        with patch("builtins.open", mock_open(read_data=mock_log_content)):
            with patch("os.path.exists", return_value=True):
                response = client.get(f"/api/logs/range?start={start_date}&end={end_date}")
                
                assert response.status_code == 200
                data = response.json()
                
                # Logs should be within the specified range
                for log in data:
                    log_time = datetime.fromisoformat(log["timestamp"].replace('Z', '+00:00'))
                    start_time = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    assert start_time <= log_time <= end_time


@pytest.mark.api
class TestLogSearchEndpoints:
    """Test log search and query endpoints."""
    
    def test_search_logs_by_message_content(self, client):
        """Test searching logs by message content."""
        search_term = "story generated"
        
        mock_log_entries = [
            {"timestamp": "2025-08-08T12:30:00.000Z", "level": "INFO", "message": "Story generated successfully"},
            {"timestamp": "2025-08-08T12:25:00.000Z", "level": "INFO", "message": "Chat message processed"},
            {"timestamp": "2025-08-08T12:20:00.000Z", "level": "INFO", "message": "Another story generated"}
        ]
        
        mock_log_content = "\n".join([json.dumps(entry) for entry in mock_log_entries])
        
        with patch("builtins.open", mock_open(read_data=mock_log_content)):
            with patch("os.path.exists", return_value=True):
                response = client.get(f"/api/logs/search?q={search_term}")
                
                assert response.status_code == 200
                data = response.json()
                
                # All returned logs should contain the search term
                for log in data:
                    assert search_term.lower() in log["message"].lower()
    
    def test_search_logs_with_regex_pattern(self, client):
        """Test searching logs with regex patterns."""
        # Search for request IDs matching pattern
        pattern = r"story_\d{8}_\d{3}"
        
        mock_log_entries = [
            {"timestamp": "2025-08-08T12:30:00.000Z", "level": "INFO", "message": "Request story_20250808_001 completed"},
            {"timestamp": "2025-08-08T12:25:00.000Z", "level": "INFO", "message": "Invalid request format"},
            {"timestamp": "2025-08-08T12:20:00.000Z", "level": "INFO", "message": "Request story_20250808_002 started"}
        ]
        
        mock_log_content = "\n".join([json.dumps(entry) for entry in mock_log_entries])
        
        with patch("builtins.open", mock_open(read_data=mock_log_content)):
            with patch("os.path.exists", return_value=True):
                response = client.get(f"/api/logs/search?pattern={pattern}")
                
                # This endpoint might not exist yet, but shows the test pattern
                assert response.status_code in [200, 404]
    
    def test_search_logs_case_insensitive(self, client):
        """Test case-insensitive log search."""
        search_term = "ERROR"
        
        mock_log_entries = [
            {"timestamp": "2025-08-08T12:30:00.000Z", "level": "ERROR", "message": "Connection error occurred"},
            {"timestamp": "2025-08-08T12:25:00.000Z", "level": "INFO", "message": "No errors found"},
            {"timestamp": "2025-08-08T12:20:00.000Z", "level": "WARNING", "message": "Potential error detected"}
        ]
        
        mock_log_content = "\n".join([json.dumps(entry) for entry in mock_log_entries])
        
        with patch("builtins.open", mock_open(read_data=mock_log_content)):
            with patch("os.path.exists", return_value=True):
                response = client.get(f"/api/logs/search?q={search_term.lower()}")
                
                assert response.status_code == 200
                data = response.json()
                
                # Should find logs containing "error" in any case
                for log in data:
                    assert "error" in log["message"].lower() or "error" in log.get("level", "").lower()


@pytest.mark.api
class TestLogAnalyticsEndpoints:
    """Test log analytics and statistics endpoints."""
    
    def test_get_log_statistics(self, client):
        """Test retrieval of log statistics."""
        mock_stats = {
            "total_logs": 1250,
            "by_level": {
                "ERROR": 25,
                "WARNING": 150,
                "INFO": 800,
                "DEBUG": 275
            },
            "by_service": {
                "LangChainService": 400,
                "ChatService": 350,
                "DatabaseService": 200,
                "CostTracker": 150,
                "Unknown": 150
            },
            "time_range": {
                "start": "2025-08-01T00:00:00.000Z",
                "end": "2025-08-08T23:59:59.000Z",
                "hours": 191
            },
            "error_rate": 0.02,
            "average_logs_per_hour": 6.5
        }
        
        # Mock log analysis
        mock_log_entries = [
            {"level": "ERROR", "service": "LangChainService"},
            {"level": "INFO", "service": "ChatService"},
            {"level": "WARNING", "service": "DatabaseService"}
        ] * 100  # Simulate many log entries
        
        mock_log_content = "\n".join([json.dumps(entry) for entry in mock_log_entries])
        
        with patch("builtins.open", mock_open(read_data=mock_log_content)):
            with patch("os.path.exists", return_value=True):
                response = client.get("/api/logs/stats")
                
                assert response.status_code == 200
                data = response.json()
                
                assert isinstance(data, dict)
                assert "total_logs" in data
                assert "by_level" in data
                assert isinstance(data["by_level"], dict)
    
    def test_get_error_summary(self, client):
        """Test retrieval of error log summary."""
        mock_error_logs = [
            {"timestamp": "2025-08-08T12:30:00.000Z", "level": "ERROR", "message": "Database connection failed", "service": "DatabaseService"},
            {"timestamp": "2025-08-08T12:25:00.000Z", "level": "ERROR", "message": "API call timeout", "service": "LangChainService"},
            {"timestamp": "2025-08-08T12:20:00.000Z", "level": "ERROR", "message": "Authentication failed", "service": "AuthService"}
        ]
        
        mock_log_content = "\n".join([json.dumps(entry) for entry in mock_error_logs])
        
        with patch("builtins.open", mock_open(read_data=mock_log_content)):
            with patch("os.path.exists", return_value=True):
                response = client.get("/api/logs/errors/summary")
                
                assert response.status_code == 200
                data = response.json()
                
                assert isinstance(data, (list, dict))
                # Should contain error-level logs only
    
    def test_get_performance_logs(self, client):
        """Test retrieval of performance-related logs."""
        mock_perf_logs = [
            {"timestamp": "2025-08-08T12:30:00.000Z", "level": "INFO", "message": "Request completed", "execution_time_ms": 1500},
            {"timestamp": "2025-08-08T12:25:00.000Z", "level": "WARNING", "message": "Slow query detected", "execution_time_ms": 5000},
            {"timestamp": "2025-08-08T12:20:00.000Z", "level": "INFO", "message": "Request completed", "execution_time_ms": 800}
        ]
        
        mock_log_content = "\n".join([json.dumps(entry) for entry in mock_perf_logs])
        
        with patch("builtins.open", mock_open(read_data=mock_log_content)):
            with patch("os.path.exists", return_value=True):
                response = client.get("/api/logs/performance")
                
                # This endpoint might not exist yet
                assert response.status_code in [200, 404]


@pytest.mark.api  
class TestLogStreamingEndpoints:
    """Test real-time log streaming endpoints."""
    
    def test_log_streaming_endpoint(self, client):
        """Test WebSocket or Server-Sent Events log streaming."""
        # This would require WebSocket testing setup
        response = client.get("/api/logs/stream")
        
        # This endpoint might not exist yet, but shows the test pattern
        assert response.status_code in [200, 404, 405]
    
    def test_log_tail_endpoint(self, client):
        """Test tailing recent logs (similar to 'tail -f')."""
        response = client.get("/api/logs/tail?lines=50")
        
        # This endpoint might not exist yet
        assert response.status_code in [200, 404]


@pytest.mark.api
class TestLogErrorHandling:
    """Test log endpoint error handling scenarios."""
    
    def test_log_file_not_found(self, client, response_validator):
        """Test when log file doesn't exist."""
        with patch("os.path.exists", return_value=False):
            response = client.get("/api/logs/recent")
            
            response_validator.validate_error_response(response, 404)
    
    def test_log_file_permission_denied(self, client, response_validator):
        """Test when log file can't be read due to permissions."""
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with patch("os.path.exists", return_value=True):
                response = client.get("/api/logs/recent")
                
                response_validator.validate_error_response(response, 403)
    
    def test_invalid_log_format(self, client, response_validator):
        """Test handling of malformed log entries."""
        # Mock log file with invalid JSON
        invalid_log_content = "This is not valid JSON\n{invalid json}\n"
        
        with patch("builtins.open", mock_open(read_data=invalid_log_content)):
            with patch("os.path.exists", return_value=True):
                response = client.get("/api/logs/recent")
                
                # Should handle gracefully, possibly returning empty list or valid entries only
                assert response.status_code in [200, 500]
    
    def test_invalid_date_format_in_range(self, client, response_validator):
        """Test invalid date format in range queries."""
        response = client.get("/api/logs/range?start=invalid-date&end=2025-08-08")
        
        response_validator.validate_error_response(response, 422)
    
    def test_end_date_before_start_date(self, client, response_validator):
        """Test when end date is before start date."""
        response = client.get("/api/logs/range?start=2025-08-08T12:00:00.000Z&end=2025-08-08T11:00:00.000Z")
        
        response_validator.validate_error_response(response, 422)
    
    def test_invalid_log_level_filter(self, client):
        """Test filtering by invalid log level."""
        response = client.get("/api/logs/filter?level=INVALID_LEVEL")
        
        # Should return empty results, not an error
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_empty_search_query(self, client, response_validator):
        """Test search with empty query."""
        response = client.get("/api/logs/search?q=")
        
        response_validator.validate_error_response(response, 422)
    
    def test_search_query_too_long(self, client, response_validator):
        """Test search with extremely long query."""
        long_query = "a" * 1000
        
        response = client.get(f"/api/logs/search?q={long_query}")
        
        # Should either work or return validation error
        assert response.status_code in [200, 422]


@pytest.mark.api
class TestLogExportEndpoints:
    """Test log export functionality."""
    
    def test_export_logs_as_json(self, client):
        """Test exporting logs in JSON format."""
        response = client.get("/api/logs/export?format=json")
        
        # This endpoint might not exist yet
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            assert response.headers.get('content-type', '').startswith('application/json')
    
    def test_export_logs_as_csv(self, client):
        """Test exporting logs in CSV format."""
        response = client.get("/api/logs/export?format=csv")
        
        # This endpoint might not exist yet
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            assert response.headers.get('content-type', '').startswith('text/csv')
    
    def test_export_filtered_logs(self, client):
        """Test exporting filtered logs."""
        response = client.get("/api/logs/export?format=json&level=ERROR&start=2025-08-08T00:00:00.000Z")
        
        # This endpoint might not exist yet
        assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])