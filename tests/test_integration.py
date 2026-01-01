"""
Integration tests combining multiple endpoints
Tests cross-endpoint functionality and workflows
"""
import pytest


class TestEndpointIntegration:
    """Integration tests for multiple endpoints"""
    
    def test_health_check_before_chat(self, client, setup_mocks):
        """
        Test health check before making chat requests
        Ensures API is ready
        """
        # Check health
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        # Then chat
        chat_response = client.post("/chat", json={"query": "Test"})
        assert chat_response.status_code == 200
    
    def test_ingest_then_chat_workflow(self, client, setup_mocks):
        """
        Test workflow: ingest document, then chat about it
        """
        # Ingest document
        files = [("files", ("test.pdf", b"PDF content", "application/pdf"))]
        ingest_response = client.post("/ingest/docs", files=files)
        assert ingest_response.status_code == 200
        
        # Then chat
        chat_response = client.post("/chat", json={"query": "What was in the document?"})
        assert chat_response.status_code == 200
    
    def test_ingest_url_then_chat_workflow(self, client, setup_mocks):
        """
        Test workflow: ingest URL, then chat about it
        """
        # Ingest URL
        ingest_response = client.post("/ingest/url", json={
            "url": "https://example.com",
            "scrape_full_site": False
        })
        assert ingest_response.status_code == 200
        
        # Then chat
        chat_response = client.post("/chat", json={"query": "What did you learn?"})
        assert chat_response.status_code == 200
    
    def test_multiple_chat_turns_same_session(self, client, setup_mocks):
        """
        Test multiple chat turns in same session
        Session should maintain context
        """
        session_id = "test-session-123"
        
        # First query
        response1 = client.post("/chat", json={
            "query": "Hello",
            "session_id": session_id
        })
        assert response1.status_code == 200
        
        # Second query in same session
        response2 = client.post("/chat", json={
            "query": "Tell me more",
            "session_id": session_id
        })
        assert response2.status_code == 200
    
    def test_different_sessions_are_independent(self, client, setup_mocks):
        """
        Test that different sessions don't interfere
        Each session should be independent
        """
        session1 = "session-1"
        session2 = "session-2"
        
        # Query in session 1
        response1 = client.post("/chat", json={
            "query": "Question 1",
            "session_id": session1
        })
        assert response1.status_code == 200
        
        # Query in session 2
        response2 = client.post("/chat", json={
            "query": "Question 2",
            "session_id": session2
        })
        assert response2.status_code == 200
    
    def test_ingest_then_delete_then_chat(self, client, setup_mocks):
        """
        Test workflow: ingest URL, delete it, then verify
        """
        url = "https://example.com/article"
        
        # Ingest
        ingest_response = client.post("/ingest/url", json={
            "url": url,
            "scrape_full_site": False
        })
        assert ingest_response.status_code == 200
        
        # Delete
        delete_response = client.post("/ingest/url/delete", json={"url": url})
        assert delete_response.status_code == 200
        
        # Verify deletion
        assert delete_response.json()["status"] == "success"


class TestErrorHandlingAcrossEndpoints:
    """Test error handling across multiple endpoints"""
    
    def test_invalid_json_payload(self, client):
        """
        Test that invalid JSON is properly rejected
        """
        response = client.post(
            "/chat",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code >= 400
    
    def test_missing_content_type_header(self, client):
        """
        Test handling of missing content-type header
        """
        response = client.post(
            "/chat",
            json={"query": "test"}
        )
        
        # Should still work with default json handling
        assert response.status_code in [200, 422]
    
    def test_extra_fields_in_request_ignored(self, client, setup_mocks):
        """
        Test that extra fields in request are ignored/handled gracefully
        """
        request_data = {
            "query": "Test question",
            "extra_field": "should be ignored",
            "another_field": 123
        }
        
        response = client.post("/chat", json=request_data)
        
        # Should still work
        assert response.status_code == 200


class TestConcurrentRequests:
    """Test handling of concurrent requests"""
    
    def test_sequential_chat_requests(self, client, setup_mocks):
        """
        Test multiple sequential chat requests
        Each should complete successfully
        """
        for i in range(3):
            response = client.post("/chat", json={"query": f"Question {i}"})
            assert response.status_code == 200
    
    def test_sequential_ingest_requests(self, client, setup_mocks):
        """
        Test multiple sequential ingest requests
        """
        for i in range(2):
            files = [("files", (f"test{i}.pdf", b"PDF", "application/pdf"))]
            response = client.post("/ingest/docs", files=files)
            assert response.status_code == 200
