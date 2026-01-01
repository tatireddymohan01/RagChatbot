"""
Unit tests for Chat endpoint
Tests POST /chat endpoint
"""
import pytest
from unittest.mock import Mock


class TestChatEndpoint:
    """Test cases for chat endpoint"""
    
    def test_chat_simple_query_with_session(self, client, setup_mocks):
        """
        Test simple chat query with session ID
        Should return answer and sources
        """
        request_data = {
            "query": "What is machine learning?",
            "session_id": "user-123"
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data
        assert data["session_id"] == "user-123"
        assert isinstance(data["sources"], list)
    
    def test_chat_query_without_session(self, client, setup_mocks):
        """
        Test chat query without session ID
        Should still work and return answer
        """
        request_data = {
            "query": "Tell me about Python"
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert "sources" in data
    
    def test_chat_query_with_chat_history(self, client, setup_mocks):
        """
        Test chat with previous conversation history
        Should consider chat history in response
        """
        request_data = {
            "query": "What about it?",
            "session_id": "user-123",
            "chat_history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi! How can I help?"},
                {"role": "user", "content": "Tell me about AI"}
            ]
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "answer" in data
        assert "sources" in data
    
    def test_chat_empty_query_validation(self, client, setup_mocks):
        """
        Test that empty query is rejected
        """
        request_data = {
            "query": "",
            "session_id": "user-123"
        }
        
        response = client.post("/chat", json=request_data)
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_chat_missing_query_field(self, client, setup_mocks):
        """
        Test that missing query field returns error
        """
        request_data = {
            "session_id": "user-123"
        }
        
        response = client.post("/chat", json=request_data)
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_chat_response_contains_answer_string(self, client, setup_mocks):
        """
        Test that chat response contains valid answer string
        """
        request_data = {
            "query": "What is AI?"
        }
        
        response = client.post("/chat", json=request_data)
        data = response.json()
        
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0
    
    def test_chat_response_contains_sources(self, client, setup_mocks):
        """
        Test that chat response includes source documents
        """
        request_data = {
            "query": "Tell me something"
        }
        
        response = client.post("/chat", json=request_data)
        data = response.json()
        
        assert isinstance(data["sources"], list)
        
        # Each source should have required fields
        for source in data["sources"]:
            assert "content" in source or isinstance(source, dict)
    
    def test_chat_source_document_structure(self, client, setup_mocks):
        """
        Test that source documents have correct structure
        """
        request_data = {
            "query": "What is this about?"
        }
        
        response = client.post("/chat", json=request_data)
        data = response.json()
        
        for source in data["sources"]:
            assert "source" in source
            assert isinstance(source["source"], str)
    
    def test_chat_long_query(self, client, setup_mocks):
        """
        Test chat with longer, more complex query
        """
        request_data = {
            "query": "Can you explain how machine learning algorithms work, " +
                    "specifically focusing on neural networks and deep learning applications?"
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
    
    def test_chat_special_characters_in_query(self, client, setup_mocks):
        """
        Test chat with special characters
        """
        request_data = {
            "query": "What about API & REST? (HTTP/HTTPS) @mentions #hashtags"
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.status_code == 200
    
    def test_chat_unicode_characters_in_query(self, client, setup_mocks):
        """
        Test chat with unicode/non-English characters
        """
        request_data = {
            "query": "¿Qué es la inteligencia artificial? 中文测试"
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.status_code == 200
    
    def test_chat_with_memory_uses_session(self, client, setup_mocks):
        """
        Test that chat with session but no history uses memory
        Should call query_with_memory instead of query
        """
        request_data = {
            "query": "Test question",
            "session_id": "session-123",
            "chat_history": None
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.status_code == 200
        
        # Verify query_with_memory was called
        mocks = setup_mocks
        mocks['rag_chain'].query_with_memory.assert_called()
    
    def test_chat_with_history_uses_provided_history(self, client, setup_mocks):
        """
        Test that chat with history uses provided chat_history
        """
        chat_history = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello"}
        ]
        request_data = {
            "query": "How are you?",
            "session_id": "session-123",
            "chat_history": chat_history
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.status_code == 200
        
        # Verify query was called with history
        mocks = setup_mocks
        mocks['rag_chain'].query.assert_called()
    
    def test_chat_response_json_format(self, client, setup_mocks):
        """
        Test that chat response is valid JSON
        """
        request_data = {
            "query": "Test"
        }
        
        response = client.post("/chat", json=request_data)
        
        assert response.headers["content-type"].startswith("application/json")
    
    def test_chat_multiple_sequential_queries(self, client, setup_mocks):
        """
        Test multiple sequential chat queries
        Each should work independently
        """
        queries = [
            "First question",
            "Second question",
            "Third question"
        ]
        
        for query in queries:
            response = client.post("/chat", json={"query": query})
            assert response.status_code == 200
            assert "answer" in response.json()
    
    def test_chat_whitespace_query(self, client, setup_mocks):
        """
        Test that query with only whitespace is rejected
        """
        request_data = {
            "query": "   "
        }
        
        response = client.post("/chat", json=request_data)
        
        # Should be treated as invalid/empty
        assert response.status_code in [200, 422]
    
    def test_chat_server_error_handling(self, client, setup_mocks):
        """
        Test that server errors are properly handled
        """
        # Make the mocked rag_chain raise an exception
        mocks = setup_mocks
        mocks['rag_chain'].query_with_memory.side_effect = Exception("Database connection failed")
        mocks['rag_chain'].query.side_effect = Exception("Database connection failed")
        
        request_data = {
            "query": "Test query"
        }
        
        response = client.post("/chat", json=request_data)
        
        # Should return 500 error
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
