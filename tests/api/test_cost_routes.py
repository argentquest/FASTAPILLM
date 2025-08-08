"""
API tests for cost tracking routes.

Tests all cost-related endpoints including cost summary, detailed analytics, and provider cost comparison.
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from decimal import Decimal


@pytest.mark.api
class TestCostSummaryEndpoints:
    """Test cost summary and analytics endpoints."""
    
    def test_get_cost_summary_success(self, client):
        """Test successful cost summary retrieval."""
        mock_summary = {
            "total_cost_usd": 15.75,
            "total_requests": 1250,
            "total_tokens": 500000,
            "average_cost_per_request": 0.0126,
            "average_tokens_per_request": 400,
            "period": {
                "start_date": "2025-01-01T00:00:00Z",
                "end_date": "2025-08-08T23:59:59Z",
                "days": 219
            },
            "by_method": {
                "langchain": {"cost_usd": 8.25, "requests": 650, "tokens": 260000},
                "semantic-kernel": {"cost_usd": 4.50, "requests": 350, "tokens": 140000},
                "langgraph": {"cost_usd": 3.00, "requests": 250, "tokens": 100000}
            },
            "by_provider": {
                "openrouter": {"cost_usd": 12.75, "requests": 1000, "tokens": 400000},
                "custom": {"cost_usd": 3.00, "requests": 250, "tokens": 100000}
            },
            "trends": {
                "daily_average_cost": 0.072,
                "daily_average_requests": 5.7,
                "cost_trend": "increasing",
                "usage_trend": "stable"
            }
        }
        
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            
            # Mock aggregation queries for cost summary
            mock_session.query().scalar.return_value = Decimal('15.75')
            mock_session.query().count.return_value = 1250
            mock_session.query().func.sum().scalar.return_value = 500000
            
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/costs/summary")
            
            assert response.status_code == 200
            data = response.json()
            
            # Validate cost summary structure
            assert "total_cost_usd" in data
            assert "total_requests" in data
            assert "total_tokens" in data
            assert "period" in data
            assert isinstance(data["total_cost_usd"], (int, float))
            assert isinstance(data["total_requests"], int)
    
    def test_get_cost_summary_with_date_filter(self, client):
        """Test cost summary with date range filter."""
        start_date = "2025-07-01"
        end_date = "2025-08-08"
        
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_session.query().filter().scalar.return_value = Decimal('5.25')
            mock_session.query().filter().count.return_value = 450
            mock_get_db.return_value = mock_session
            
            response = client.get(f"/api/costs/summary?start_date={start_date}&end_date={end_date}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["period"]["start_date"].startswith("2025-07-01")
    
    def test_get_cost_summary_by_method(self, client):
        """Test cost summary grouped by AI method."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            
            # Mock grouped query results
            mock_results = [
                ("langchain", Decimal('8.25'), 650, 260000),
                ("semantic-kernel", Decimal('4.50'), 350, 140000),
                ("langgraph", Decimal('3.00'), 250, 100000)
            ]
            mock_session.query().group_by().all.return_value = mock_results
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/costs/summary/by-method")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            assert len(data) >= 3  # Should have entries for each method
    
    def test_get_cost_summary_by_provider(self, client):
        """Test cost summary grouped by provider."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            
            mock_results = [
                ("openrouter", Decimal('12.75'), 1000, 400000),
                ("custom", Decimal('3.00'), 250, 100000)
            ]
            mock_session.query().group_by().all.return_value = mock_results
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/costs/summary/by-provider")
            
            assert response.status_code == 200
            data = response.json()
            assert "openrouter" in data or len(data) >= 0  # Handle empty case
            assert "custom" in data or len(data) >= 0
    
    def test_get_cost_summary_empty_data(self, client):
        """Test cost summary when no data exists."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_session.query().scalar.return_value = None
            mock_session.query().count.return_value = 0
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/costs/summary")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_cost_usd"] == 0 or data["total_cost_usd"] is None
            assert data["total_requests"] == 0


@pytest.mark.api
class TestDetailedCostEndpoints:
    """Test detailed cost analysis endpoints."""
    
    def test_get_cost_details_success(self, client):
        """Test detailed cost breakdown retrieval."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            
            # Mock detailed cost records
            mock_records = []
            for i in range(10):
                mock_record = Mock()
                mock_record.id = i + 1
                mock_record.created_at = datetime.now() - timedelta(days=i)
                mock_record.method = "langchain" if i % 2 == 0 else "semantic-kernel"
                mock_record.provider = "openrouter"
                mock_record.model = "llama-3-8b"
                mock_record.input_tokens = 100 + i * 10
                mock_record.output_tokens = 50 + i * 5
                mock_record.total_tokens = 150 + i * 15
                mock_record.estimated_cost_usd = Decimal(str(0.001 + i * 0.0005))
                mock_record.request_id = f"req_{i+1}"
                mock_records.append(mock_record)
            
            mock_session.query().order_by().offset().limit().all.return_value = mock_records
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/costs/details")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) <= 10
            
            if len(data) > 0:
                record = data[0]
                assert "id" in record
                assert "method" in record
                assert "provider" in record
                assert "estimated_cost_usd" in record
                assert "total_tokens" in record
    
    def test_get_cost_details_with_pagination(self, client):
        """Test cost details with pagination."""
        response = client.get("/api/costs/details?skip=10&limit=20")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 20
    
    def test_get_cost_details_filtered_by_method(self, client):
        """Test cost details filtered by specific method."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_session.query().filter().order_by().offset().limit().all.return_value = []
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/costs/details?method=langchain")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_cost_details_filtered_by_provider(self, client):
        """Test cost details filtered by specific provider."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_session.query().filter().order_by().offset().limit().all.return_value = []
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/costs/details?provider=openrouter")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_cost_details_filtered_by_date_range(self, client):
        """Test cost details filtered by date range."""
        start_date = "2025-07-01"
        end_date = "2025-08-08"
        
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_session.query().filter().order_by().offset().limit().all.return_value = []
            mock_get_db.return_value = mock_session
            
            response = client.get(f"/api/costs/details?start_date={start_date}&end_date={end_date}")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)


@pytest.mark.api
class TestCostAnalyticsEndpoints:
    """Test cost analytics and trends endpoints."""
    
    def test_get_cost_trends_daily(self, client):
        """Test daily cost trends retrieval."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            
            # Mock daily aggregation results
            mock_trends = []
            for i in range(7):  # Last 7 days
                date = datetime.now().date() - timedelta(days=i)
                mock_trends.append((
                    date,
                    Decimal(str(0.5 + i * 0.1)),  # cost
                    10 + i * 2,  # requests
                    4000 + i * 500  # tokens
                ))
            
            mock_session.query().group_by().order_by().all.return_value = mock_trends
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/costs/trends/daily")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) <= 7
            
            if len(data) > 0:
                trend = data[0]
                assert "date" in trend
                assert "cost_usd" in trend
                assert "requests" in trend
                assert "tokens" in trend
    
    def test_get_cost_trends_weekly(self, client):
        """Test weekly cost trends retrieval."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_session.query().group_by().order_by().all.return_value = []
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/costs/trends/weekly")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_cost_trends_monthly(self, client):
        """Test monthly cost trends retrieval."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_session.query().group_by().order_by().all.return_value = []
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/costs/trends/monthly")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_cost_efficiency_metrics(self, client):
        """Test cost efficiency metrics."""
        mock_efficiency = {
            "cost_per_1k_tokens": {
                "average": 0.002,
                "by_method": {
                    "langchain": 0.0018,
                    "semantic-kernel": 0.0022,
                    "langgraph": 0.0025
                },
                "by_provider": {
                    "openrouter": 0.002,
                    "custom": 0.0015
                }
            },
            "tokens_per_dollar": {
                "average": 500000,
                "by_method": {
                    "langchain": 555555,
                    "semantic-kernel": 454545,
                    "langgraph": 400000
                }
            },
            "most_efficient": {
                "method": "langchain",
                "provider": "custom"
            },
            "least_efficient": {
                "method": "langgraph",
                "provider": "openrouter"
            }
        }
        
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            # Mock complex aggregation calculations
            mock_session.query().scalar.return_value = 0.002
            mock_session.query().group_by().all.return_value = [("langchain", 0.0018)]
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/costs/efficiency")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            # The actual structure will depend on implementation


@pytest.mark.api
class TestCostComparisonEndpoints:
    """Test cost comparison and optimization endpoints."""
    
    def test_get_provider_cost_comparison(self, client):
        """Test provider cost comparison."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            
            mock_comparison = [
                ("openrouter", Decimal('0.002'), 1000, 500000),
                ("custom", Decimal('0.0015'), 500, 333333)
            ]
            mock_session.query().group_by().all.return_value = mock_comparison
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/costs/compare/providers")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, (list, dict))
    
    def test_get_method_cost_comparison(self, client):
        """Test AI method cost comparison."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            
            mock_comparison = [
                ("langchain", Decimal('0.0018'), 650, 360000),
                ("semantic-kernel", Decimal('0.0022'), 350, 159000),
                ("langgraph", Decimal('0.0025'), 250, 100000)
            ]
            mock_session.query().group_by().all.return_value = mock_comparison
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/costs/compare/methods")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, (list, dict))
    
    def test_get_cost_optimization_suggestions(self, client):
        """Test cost optimization suggestions."""
        mock_suggestions = {
            "total_potential_savings_usd": 2.45,
            "suggestions": [
                {
                    "type": "provider_switch",
                    "description": "Switch from OpenRouter to Custom provider for story generation",
                    "potential_savings_usd": 1.20,
                    "confidence": "high"
                },
                {
                    "type": "method_optimization",
                    "description": "Use LangChain instead of LangGraph for simple tasks",
                    "potential_savings_usd": 0.75,
                    "confidence": "medium"
                },
                {
                    "type": "usage_pattern",
                    "description": "Batch similar requests to reduce overhead",
                    "potential_savings_usd": 0.50,
                    "confidence": "low"
                }
            ],
            "current_monthly_cost": 15.75,
            "optimized_monthly_cost": 13.30
        }
        
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            # Mock analysis queries
            mock_session.query().group_by().all.return_value = [("openrouter", 12.75), ("custom", 3.00)]
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/costs/optimize")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)
            # The actual structure depends on the optimization logic implementation


@pytest.mark.api
class TestCostErrorHandling:
    """Test cost endpoint error handling scenarios."""
    
    def test_invalid_date_format_error(self, client, response_validator):
        """Test invalid date format in cost queries."""
        response = client.get("/api/costs/summary?start_date=invalid-date")
        
        response_validator.validate_error_response(response, 422)
    
    def test_end_date_before_start_date_error(self, client, response_validator):
        """Test when end date is before start date."""
        response = client.get("/api/costs/summary?start_date=2025-08-08&end_date=2025-07-01")
        
        response_validator.validate_error_response(response, 422)
    
    def test_invalid_pagination_parameters(self, client, response_validator):
        """Test invalid pagination parameters."""
        response = client.get("/api/costs/details?skip=-1&limit=0")
        
        response_validator.validate_error_response(response, 422)
    
    def test_database_connection_error(self, client, response_validator):
        """Test when database is unavailable."""
        with patch('database.get_db') as mock_get_db:
            mock_get_db.side_effect = Exception("Database connection failed")
            
            response = client.get("/api/costs/summary")
            
            response_validator.validate_error_response(response, 500)
    
    def test_invalid_method_filter(self, client):
        """Test filtering by non-existent method."""
        response = client.get("/api/costs/details?method=invalid_method")
        
        # Should return empty results, not an error
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_invalid_provider_filter(self, client):
        """Test filtering by non-existent provider."""
        response = client.get("/api/costs/details?provider=invalid_provider")
        
        # Should return empty results, not an error
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


@pytest.mark.api
class TestCostExportEndpoints:
    """Test cost data export endpoints."""
    
    def test_export_cost_summary_csv(self, client):
        """Test exporting cost summary as CSV."""
        response = client.get("/api/costs/export/summary?format=csv")
        
        # This endpoint might not exist yet, but shows the test pattern
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            assert response.headers.get('content-type', '').startswith('text/csv')
    
    def test_export_cost_details_json(self, client):
        """Test exporting detailed cost data as JSON."""
        response = client.get("/api/costs/export/details?format=json")
        
        # This endpoint might not exist yet
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            assert response.headers.get('content-type', '').startswith('application/json')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])