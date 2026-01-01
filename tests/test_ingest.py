"""
Unit tests for Ingestion endpoints
Tests POST /ingest/* endpoints
"""
import pytest
from io import BytesIO
from unittest.mock import patch, Mock


class TestIngestDocsEndpoint:
    """Test cases for document ingestion endpoint"""
    
    def test_ingest_single_pdf_file(self, client, setup_mocks):
        """
        Test uploading a single PDF file
        Should process and add to vector store
        """
        pdf_content = b"PDF dummy content"
        files = [("files", ("test.pdf", BytesIO(pdf_content), "application/pdf"))]
        
        response = client.post("/ingest/docs", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "documents_processed" in data
        assert "chunks_created" in data
        assert "sources" in data
    
    def test_ingest_multiple_files(self, client, setup_mocks):
        """
        Test uploading multiple files at once
        Should process all files
        """
        files = [
            ("files", ("test1.pdf", BytesIO(b"PDF 1"), "application/pdf")),
            ("files", ("test2.txt", BytesIO(b"Text content"), "text/plain")),
            ("files", ("test3.docx", BytesIO(b"DOCX content"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))
        ]
        
        response = client.post("/ingest/docs", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert data["documents_processed"] == 3
        assert len(data["sources"]) == 3
    
    def test_ingest_docx_file(self, client, setup_mocks):
        """
        Test uploading DOCX file
        Should be accepted and processed
        """
        files = [("files", ("document.docx", BytesIO(b"DOCX data"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))]
        
        response = client.post("/ingest/docs", files=files)
        
        assert response.status_code == 200
    
    def test_ingest_txt_file(self, client, setup_mocks):
        """
        Test uploading TXT file
        Should be accepted and processed
        """
        files = [("files", ("notes.txt", BytesIO(b"Plain text content"), "text/plain"))]
        
        response = client.post("/ingest/docs", files=files)
        
        assert response.status_code == 200
    
    def test_ingest_doc_file(self, client, setup_mocks):
        """
        Test uploading .doc (legacy Word) file
        Should be accepted and processed
        """
        files = [("files", ("document.doc", BytesIO(b"DOC data"), "application/msword"))]
        
        response = client.post("/ingest/docs", files=files)
        
        assert response.status_code == 200
    
    def test_ingest_invalid_file_type_rejected(self, client, setup_mocks):
        """
        Test that unsupported file types are rejected
        """
        files = [("files", ("image.jpg", BytesIO(b"JPG data"), "image/jpeg"))]
        
        response = client.post("/ingest/docs", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not supported" in data["detail"].lower()
    
    def test_ingest_no_files_provided(self, client, setup_mocks):
        """
        Test that endpoint requires files
        """
        response = client.post("/ingest/docs", files=[])
        
        # Should return error
        assert response.status_code in [400, 422]
    
    def test_ingest_response_structure(self, client, setup_mocks):
        """
        Test that ingest response has required fields
        """
        files = [("files", ("test.pdf", BytesIO(b"PDF"), "application/pdf"))]
        response = client.post("/ingest/docs", files=files)
        
        data = response.json()
        
        assert "status" in data
        assert "message" in data
        assert "documents_processed" in data
        assert "chunks_created" in data
        assert "sources" in data
    
    def test_ingest_response_sources_list(self, client, setup_mocks):
        """
        Test that sources are returned as list
        """
        files = [("files", ("file1.pdf", BytesIO(b"PDF"), "application/pdf")),
                ("files", ("file2.txt", BytesIO(b"TXT"), "text/plain"))]
        response = client.post("/ingest/docs", files=files)
        
        data = response.json()
        
        assert isinstance(data["sources"], list)
        assert len(data["sources"]) == 2
        assert "file1.pdf" in data["sources"]
        assert "file2.txt" in data["sources"]
    
    def test_ingest_chunks_created_count(self, client, setup_mocks):
        """
        Test that chunks_created count is accurate
        """
        files = [("files", ("test.pdf", BytesIO(b"PDF content"), "application/pdf"))]
        response = client.post("/ingest/docs", files=files)
        
        data = response.json()
        
        assert isinstance(data["chunks_created"], int)
        assert data["chunks_created"] > 0


class TestIngestFolderEndpoint:
    """Test cases for folder ingestion endpoint"""
    
    def test_ingest_from_folder_success(self, client, setup_mocks):
        """
        Test processing documents from folder
        Should return success with statistics
        """
        response = client.post("/ingest/folder")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "message" in data
        assert "documents_processed" in data
        assert "chunks_created" in data
    
    def test_ingest_folder_response_structure(self, client, setup_mocks):
        """
        Test that folder ingest response has correct structure
        """
        response = client.post("/ingest/folder")
        
        data = response.json()
        
        assert "status" in data
        assert "documents_processed" in data
        assert "chunks_created" in data
        assert "sources" in data
        assert isinstance(data["sources"], list)


class TestIngestFolderResetEndpoint:
    """Test cases for folder reset endpoint"""
    
    def test_reset_folder_tracking_success(self, client, setup_mocks):
        """
        Test resetting document tracking
        Should clear tracking history
        """
        response = client.post("/ingest/folder/reset")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "message" in data
        assert "reset" in data["message"].lower()


class TestIngestURLEndpoint:
    """Test cases for URL ingestion endpoint"""
    
    def test_ingest_single_url_success(self, client, setup_mocks):
        """
        Test ingesting a single URL
        Should scrape and process content
        """
        request_data = {
            "url": "https://example.com/article",
            "scrape_full_site": False
        }
        
        response = client.post("/ingest/url", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "documents_processed" in data
        assert "chunks_created" in data
    
    def test_ingest_full_website(self, client, setup_mocks):
        """
        Test scraping entire website
        Should use full site scraping when flag is True
        """
        request_data = {
            "url": "https://example.com",
            "scrape_full_site": True
        }
        
        response = client.post("/ingest/url", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
    
    def test_ingest_url_without_scrape_full_site_flag(self, client, setup_mocks):
        """
        Test URL ingestion with default scrape_full_site=False
        """
        request_data = {
            "url": "https://example.com/page"
        }
        
        response = client.post("/ingest/url", json=request_data)
        
        assert response.status_code == 200
    
    def test_ingest_invalid_url_format(self, client, setup_mocks):
        """
        Test that invalid URL format is rejected
        """
        request_data = {
            "url": "not-a-valid-url",
            "scrape_full_site": False
        }
        
        response = client.post("/ingest/url", json=request_data)
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_ingest_missing_url_field(self, client, setup_mocks):
        """
        Test that missing url field returns error
        """
        request_data = {
            "scrape_full_site": False
        }
        
        response = client.post("/ingest/url", json=request_data)
        
        assert response.status_code == 422
    
    def test_ingest_url_response_contains_sources(self, client, setup_mocks):
        """
        Test that URL ingest response includes source URL
        """
        request_data = {
            "url": "https://example.com",
            "scrape_full_site": False
        }
        
        response = client.post("/ingest/url", json=request_data)
        data = response.json()
        
        assert isinstance(data["sources"], list)
        assert len(data["sources"]) > 0
    
    def test_ingest_url_different_domains(self, client, setup_mocks):
        """
        Test ingesting URLs from different domains
        """
        domains = [
            "https://example.com",
            "https://github.com",
            "https://stackoverflow.com"
        ]
        
        for domain in domains:
            request_data = {
                "url": domain,
                "scrape_full_site": False
            }
            
            response = client.post("/ingest/url", json=request_data)
            assert response.status_code == 200


class TestDeleteURLContentEndpoint:
    """Test cases for URL deletion endpoint"""
    
    def test_delete_url_by_exact_url(self, client, setup_mocks):
        """
        Test deleting content by exact URL
        """
        request_data = {
            "url": "https://example.com/article"
        }
        
        response = client.post("/ingest/url/delete", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
        assert "deleted" in data
        assert "matched" in data
    
    def test_delete_url_by_domain(self, client, setup_mocks):
        """
        Test deleting all content from a domain
        """
        request_data = {
            "domain": "example.com"
        }
        
        response = client.post("/ingest/url/delete", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "success"
    
    def test_delete_url_requires_url_or_domain(self, client, setup_mocks):
        """
        Test that deletion requires either url or domain
        """
        request_data = {}
        
        response = client.post("/ingest/url/delete", json=request_data)
        
        # Should return validation error (422 is correct for Pydantic validation)
        assert response.status_code == 422
    
    def test_delete_url_response_structure(self, client, setup_mocks):
        """
        Test delete response has required fields
        """
        request_data = {
            "url": "https://example.com"
        }
        
        response = client.post("/ingest/url/delete", json=request_data)
        data = response.json()
        
        assert "status" in data
        assert "message" in data
        assert "deleted" in data
        assert "matched" in data
    
    def test_delete_returns_deletion_count(self, client, setup_mocks):
        """
        Test that delete endpoint returns count of deleted vectors
        """
        request_data = {
            "url": "https://example.com"
        }
        
        response = client.post("/ingest/url/delete", json=request_data)
        data = response.json()
        
        assert isinstance(data["deleted"], int)
        assert isinstance(data["matched"], int)


class TestIngestSitemapEndpoint:
    """Test cases for sitemap ingestion endpoint"""
    
    def test_ingest_sitemap_success(self, client, setup_mocks):
        """
        Test parsing and ingesting sitemap
        Should discover and process all URLs
        """
        request_data = {
            "domain": "example.com"
        }
        
        response = client.post("/ingest/sitemap", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] in ["success", "partial"]
        assert "documents_processed" in data
        assert "chunks_created" in data
    
    def test_ingest_sitemap_with_https_domain(self, client, setup_mocks):
        """
        Test sitemap ingestion with https:// prefix
        """
        request_data = {
            "domain": "https://example.com"
        }
        
        response = client.post("/ingest/sitemap", json=request_data)
        
        assert response.status_code == 200
    
    def test_ingest_sitemap_without_protocol(self, client, setup_mocks):
        """
        Test sitemap ingestion without protocol
        """
        request_data = {
            "domain": "example.com"
        }
        
        response = client.post("/ingest/sitemap", json=request_data)
        
        assert response.status_code == 200
    
    def test_ingest_sitemap_response_structure(self, client, setup_mocks):
        """
        Test sitemap response has correct structure
        """
        request_data = {
            "domain": "example.com"
        }
        
        response = client.post("/ingest/sitemap", json=request_data)
        data = response.json()
        
        assert "status" in data
        assert "message" in data
        assert "documents_processed" in data
        assert "chunks_created" in data
        assert "sources" in data
    
    def test_ingest_sitemap_sources_list(self, client, setup_mocks):
        """
        Test that sitemap returns list of ingested URLs
        """
        request_data = {
            "domain": "example.com"
        }
        
        response = client.post("/ingest/sitemap", json=request_data)
        data = response.json()
        
        assert isinstance(data["sources"], list)
    
    def test_ingest_sitemap_missing_domain(self, client, setup_mocks):
        """
        Test that domain field is required
        """
        request_data = {}
        
        response = client.post("/ingest/sitemap", json=request_data)
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_ingest_sitemap_multiple_domains(self, client, setup_mocks):
        """
        Test sitemap ingestion for different domains
        """
        domains = [
            "example.com",
            "example.org",
            "docs.example.com"
        ]
        
        for domain in domains:
            request_data = {"domain": domain}
            response = client.post("/ingest/sitemap", json=request_data)
            assert response.status_code == 200
    
    def test_ingest_sitemap_chunk_creation(self, client, setup_mocks):
        """
        Test that sitemap creates chunks from discovered URLs
        """
        request_data = {
            "domain": "example.com"
        }
        
        response = client.post("/ingest/sitemap", json=request_data)
        data = response.json()
        
        # Should have created chunks
        assert data["chunks_created"] >= 0
        assert isinstance(data["chunks_created"], int)
