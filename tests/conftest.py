"""
Pytest configuration and shared fixtures for all tests
"""
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """
    FastAPI test client
    """
    return TestClient(app)


@pytest.fixture
def mock_rag_chain():
    """
    Mock RAG chain for testing chat endpoint
    """
    mock_chain = Mock()
    mock_chain.query_with_memory = Mock(
        return_value=(
            "This is a test answer.",
            [
                {"content": "Test document content", "source": "test.pdf", "page": 1},
                {"content": "Another test content", "source": "test.txt"}
            ]
        )
    )
    mock_chain.query = Mock(
        return_value=(
            "This is a test answer with history.",
            [
                {"content": "Test content", "source": "test.pdf"}
            ]
        )
    )
    return mock_chain


@pytest.fixture
def mock_document_loader():
    """
    Mock document loader for file processing
    """
    mock_loader = Mock()
    mock_loader.process_uploaded_file = Mock(
        return_value=[
            Mock(page_content="Chunk 1 content", metadata={"source": "test.pdf"}),
            Mock(page_content="Chunk 2 content", metadata={"source": "test.pdf"})
        ]
    )
    mock_loader.chunk_documents = Mock(
        return_value=[
            Mock(page_content="Chunk 1", metadata={"source": "url"}),
            Mock(page_content="Chunk 2", metadata={"source": "url"})
        ]
    )
    return mock_loader


@pytest.fixture
def mock_vectorstore_manager():
    """
    Mock vectorstore manager
    """
    mock_manager = Mock()
    mock_manager.add_documents = Mock(return_value=5)
    mock_manager.delete_by_source = Mock(
        return_value={"deleted": 3, "matched": 5}
    )
    return mock_manager


@pytest.fixture
def mock_web_scraper():
    """
    Mock web scraper for URL ingestion
    """
    mock_scraper = Mock()
    mock_scraper.scrape_website = Mock(
        return_value=[
            Mock(page_content="Website content", metadata={"source": "https://example.com"})
        ]
    )
    mock_scraper.scrape_multiple_urls_simple = Mock(
        return_value=[
            Mock(page_content="URL content", metadata={"source": "https://example.com/page"})
        ]
    )
    return mock_scraper


@pytest.fixture
def mock_sitemap_crawler():
    """
    Mock sitemap crawler for sitemap ingestion
    """
    mock_crawler = Mock()
    mock_crawler.parse_sitemap = Mock(
        return_value=[
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3"
        ]
    )
    return mock_crawler


@pytest.fixture
def mock_document_monitor():
    """
    Mock document monitor for folder processing
    """
    mock_monitor = Mock()
    mock_monitor.process_new_documents = Mock(
        return_value={
            "status": "success",
            "message": "Processed new documents",
            "documents_processed": 2,
            "chunks_created": 10,
            "files": ["doc1.pdf", "doc2.txt"]
        }
    )
    mock_monitor.reset_tracking = Mock()
    return mock_monitor


@pytest.fixture
def setup_mocks(
    mock_rag_chain,
    mock_document_loader,
    mock_vectorstore_manager,
    mock_web_scraper,
    mock_sitemap_crawler,
    mock_document_monitor
):
    """
    Setup all mocks for integration
    Patches the get_* functions in their respective modules
    """
    patches = [
        patch('app.api.chat.get_rag_chain', return_value=mock_rag_chain),
        patch('app.api.ingest.get_document_loader', return_value=mock_document_loader),
        patch('app.api.ingest.get_vectorstore_manager', return_value=mock_vectorstore_manager),
        patch('app.api.ingest.get_web_scraper', return_value=mock_web_scraper),
        patch('app.api.ingest.get_sitemap_crawler', return_value=mock_sitemap_crawler),
        patch('app.api.ingest.get_document_monitor', return_value=mock_document_monitor),
        patch('app.services.rag_chain.get_rag_chain', return_value=mock_rag_chain),
        patch('app.services.document_loader.get_document_loader', return_value=mock_document_loader),
        patch('app.core.vectorstore.get_vectorstore_manager', return_value=mock_vectorstore_manager),
        patch('app.services.web_scraper.get_web_scraper', return_value=mock_web_scraper),
        patch('app.services.sitemap_crawler.get_sitemap_crawler', return_value=mock_sitemap_crawler),
        patch('app.services.document_monitor.get_document_monitor', return_value=mock_document_monitor),
    ]
    
    # Start all patches
    patch_objs = [p.start() for p in patches]
    
    try:
        yield {
            'rag_chain': mock_rag_chain,
            'document_loader': mock_document_loader,
            'vectorstore_manager': mock_vectorstore_manager,
            'web_scraper': mock_web_scraper,
            'sitemap_crawler': mock_sitemap_crawler,
            'document_monitor': mock_document_monitor
        }
    finally:
        # Stop all patches
        for p in patches:
            p.stop()
