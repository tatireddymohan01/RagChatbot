"""
Unit tests for Health endpoint
Tests GET /health endpoint
"""
import pytest
from unittest.mock import patch


class TestHealthEndpoint:
    """Test cases for health check endpoint"""
    
    def test_health_check_success(self, client):
        """
        Test successful health check response
        Should return 200 with service info
        """
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "status" in data
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
        assert "timestamp" in data
        assert "model" in data
        assert "capabilities" in data
    
    def test_health_check_contains_timestamp(self, client):
        """
        Test that health check includes valid timestamp
        """
        response = client.get("/health")
        data = response.json()
        
        # Verify timestamp is ISO format
        assert "timestamp" in data
        assert "T" in data["timestamp"]
        assert ":" in data["timestamp"]
    
    def test_health_check_contains_model_info(self, client):
        """
        Test that health check includes model information
        """
        response = client.get("/health")
        data = response.json()
        
        assert "model" in data
        # Model should be a non-empty string
        assert isinstance(data["model"], str)
        assert len(data["model"]) > 0
    
    def test_health_check_capabilities_structure(self, client):
        """
        Test that health check includes capabilities
        """
        response = client.get("/health")
        data = response.json()
        
        assert "capabilities" in data
        assert isinstance(data["capabilities"], dict)
        assert "full_site_scraping" in data["capabilities"]
        assert isinstance(data["capabilities"]["full_site_scraping"], bool)
    
    @patch('shutil.which')
    def test_health_check_chromedriver_available(self, mock_which, client):
        """
        Test health check when ChromeDriver is available
        """
        mock_which.return_value = "/usr/bin/chromedriver"
        
        response = client.get("/health")
        data = response.json()
        
        # Should detect ChromeDriver as available
        assert data["capabilities"]["full_site_scraping"] is True
    
    @patch('shutil.which')
    def test_health_check_chromedriver_unavailable(self, mock_which, client):
        """
        Test health check when ChromeDriver is not available
        """
        mock_which.return_value = None
        
        response = client.get("/health")
        data = response.json()
        
        # Should detect ChromeDriver as unavailable
        assert data["capabilities"]["full_site_scraping"] is False
    
    def test_health_check_response_type(self, client):
        """
        Test that health check returns JSON
        """
        response = client.get("/health")
        
        assert response.headers["content-type"].startswith("application/json")
    
    def test_health_check_no_authentication_required(self, client):
        """
        Test that health check doesn't require authentication
        """
        response = client.get("/health")
        
        # Should not require any auth headers
        assert response.status_code == 200
    
    def test_health_check_contains_app_name(self, client):
        """
        Test that health check includes application name
        """
        response = client.get("/health")
        data = response.json()
        
        assert "service" in data
        assert data["service"] != ""
        assert isinstance(data["service"], str)
    
    def test_health_check_consistent_responses(self, client):
        """
        Test that multiple health checks return consistent structure
        """
        response1 = client.get("/health")
        response2 = client.get("/health")
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Same keys in both responses
        assert set(data1.keys()) == set(data2.keys())
        
        # Status should always be healthy
        assert data1["status"] == "healthy"
        assert data2["status"] == "healthy"
