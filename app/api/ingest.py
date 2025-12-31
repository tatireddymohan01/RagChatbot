"""
Document and URL Ingestion Endpoints
Handles uploading documents and scraping web content
"""
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.ingest_schema import URLIngestRequest, URLDeleteRequest, SitemapIngestRequest, IngestResponse
from app.services.document_loader import get_document_loader
from app.services.web_scraper import get_web_scraper
from app.services.sitemap_crawler import get_sitemap_crawler
from app.services.document_monitor import get_document_monitor
from app.core.vectorstore import get_vectorstore_manager
from app.core.config import get_settings
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/ingest/docs", response_model=IngestResponse)
async def ingest_documents(files: List[UploadFile] = File(...)):
    """
    Ingest documents (PDF, DOCX, TXT) into the vector store
    
    Args:
        files: List of uploaded files
        
    Returns:
        IngestResponse with processing status and statistics
    """
    try:
        logger.info(f"Received {len(files)} files for ingestion")
        
        # Validate file types
        allowed_extensions = {".pdf", ".docx", ".doc", ".txt"}
        
        for file in files:
            file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type not supported: {file.filename}. Allowed: PDF, DOCX, TXT"
                )
        
        # Process files
        document_loader = get_document_loader()
        vectorstore_manager = get_vectorstore_manager()
        
        all_chunks = []
        source_names = []
        
        for file in files:
            try:
                logger.info(f"Processing file: {file.filename}")
                
                # Read file content
                content = await file.read()
                
                # Process and chunk the document
                chunks = document_loader.process_uploaded_file(content, file.filename)
                all_chunks.extend(chunks)
                source_names.append(file.filename)
                
                logger.info(f"Created {len(chunks)} chunks from {file.filename}")
                
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {e}")
                # Continue with other files
        
        if not all_chunks:
            raise HTTPException(
                status_code=400,
                detail="No valid documents could be processed"
            )
        
        # Add to vector store
        num_added = vectorstore_manager.add_documents(all_chunks)
        
        response = IngestResponse(
            status="success",
            message=f"Successfully ingested {len(files)} document(s)",
            documents_processed=len(files),
            chunks_created=num_added,
            sources=source_names
        )
        
        logger.info(f"Ingestion complete: {num_added} chunks added to vector store")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during document ingestion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing documents: {str(e)}"
        )


@router.post("/ingest/folder", response_model=IngestResponse)
async def ingest_from_folder():
    """
    Process only new or modified documents from the configured documents folder
    (Automatically tracks which files have been processed)
    
    Returns:
        IngestResponse with processing status and statistics
    """
    try:
        settings = get_settings()
        logger.info(f"Checking for new/modified documents in: {settings.documents_folder}")
        
        # Use document monitor for intelligent processing
        monitor = get_document_monitor()
        result = monitor.process_new_documents()
        
        response = IngestResponse(
            status=result['status'],
            message=result['message'],
            documents_processed=result['documents_processed'],
            chunks_created=result['chunks_created'],
            sources=result['files']
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing documents from folder: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing documents from folder: {str(e)}"
        )


@router.post("/ingest/folder/reset")
async def reset_folder_tracking():
    """
    Reset document tracking (forces reprocessing of all documents on next ingest)
    """
    try:
        monitor = get_document_monitor()
        monitor.reset_tracking()
        
        logger.info("Document tracking reset")
        return {
            "status": "success",
            "message": "Document tracking reset. All files will be reprocessed on next ingest."
        }
        
    except Exception as e:
        logger.error(f"Error resetting tracking: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error resetting tracking: {str(e)}"
        )


@router.post("/ingest/url", response_model=IngestResponse)
async def ingest_url(request: URLIngestRequest):
    """
    Scrape and ingest content from a URL
    
    Args:
        request: URLIngestRequest with the URL to scrape
        
    Returns:
        IngestResponse with processing status and statistics
    """
    try:
        url = str(request.url)
        logger.info(f"[INGEST_URL_START] Received URL: {url}")
        logger.info(f"[INGEST_URL_START] scrape_full_site={request.scrape_full_site}")
        
        # Scrape the URL or entire website
        web_scraper = get_web_scraper()
        
        if request.scrape_full_site:
            logger.info(f"[INGEST_URL_SCRAPE] Starting full website scrape from: {url}")
            documents = web_scraper.scrape_website(url)
            logger.info(f"[INGEST_URL_SCRAPE] Full site scrape returned {len(documents)} documents")
        else:
            logger.info(f"[INGEST_URL_SCRAPE] Starting single URL scrape: {url}")
            documents = web_scraper.scrape_multiple_urls_simple([url])
            logger.info(f"[INGEST_URL_SCRAPE] Single URL scrape returned {len(documents)} documents")
        
        if not documents:
            logger.warning(f"[INGEST_URL_FAIL] No content scraped from {url}")
            raise HTTPException(
                status_code=400,
                detail=f"Could not scrape content from URL: {url}"
            )
        
        logger.info(f"[INGEST_URL_CHUNK] Chunking {len(documents)} documents")
        # Chunk the documents
        document_loader = get_document_loader()
        chunks = document_loader.chunk_documents(documents)
        logger.info(f"[INGEST_URL_CHUNK] Created {len(chunks)} chunks from documents")
        
        # Add to vector store
        logger.info(f"[INGEST_URL_VECTOR] Adding {len(chunks)} chunks to vector store")
        vectorstore_manager = get_vectorstore_manager()
        num_added = vectorstore_manager.add_documents(chunks)
        logger.info(f"[INGEST_URL_VECTOR] ✓ Added {num_added} chunks to vector store")
        
        response = IngestResponse(
            status="success",
            message=f"Successfully ingested content from {'website' if request.scrape_full_site else 'URL'}",
            documents_processed=len(documents),
            chunks_created=num_added,
            sources=[url]
        )
        
        logger.info(f"[INGEST_URL_END] ✓ Success: {len(documents)} docs, {num_added} chunks")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during URL ingestion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing URL: {str(e)}"
        )


@router.post("/ingest/url/delete")
async def delete_url_content(request: URLDeleteRequest):
    """Delete ingested URL content by exact URL or domain"""
    try:
        if not request.url and not request.domain:
            raise HTTPException(status_code=400, detail="Provide url or domain")

        vectorstore_manager = get_vectorstore_manager()
        result = vectorstore_manager.delete_by_source(
            url=str(request.url) if request.url else None,
            domain=request.domain
        )

        return {
            "status": "success",
            "message": f"Deleted {result['deleted']} vector(s)",
            "deleted": result['deleted'],
            "matched": result['matched'],
            "url": str(request.url) if request.url else None,
            "domain": request.domain
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting URL content: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting URL content: {str(e)}"
        )


@router.post("/ingest/sitemap", response_model=IngestResponse)
async def ingest_from_sitemap(request: SitemapIngestRequest):
    """
    Parse sitemap.xml and ingest all discovered URLs
    Works great on Azure and cloud environments (no ChromeDriver needed)
    
    Args:
        request: SitemapIngestRequest with domain
        
    Returns:
        IngestResponse with processing status and statistics
    """
    try:
        domain = str(request.domain).strip()
        logger.info(f"Starting sitemap crawl for: {domain}")
        
        # Parse sitemap and extract URLs
        sitemap_crawler = get_sitemap_crawler()
        urls = sitemap_crawler.parse_sitemap(domain)
        
        if not urls:
            raise HTTPException(
                status_code=400,
                detail=f"No URLs found in sitemap for {domain}"
            )
        
        logger.info(f"Found {len(urls)} URLs from sitemap. Starting ingestion...")
        
        # Scrape and ingest each URL
        web_scraper = get_web_scraper()
        document_loader = get_document_loader()
        vectorstore_manager = get_vectorstore_manager()
        
        total_chunks = 0
        successful_urls = []
        failed_urls = []
        
        for idx, url in enumerate(urls, 1):
            try:
                logger.info(f"[SITEMAP_INGEST] [{idx}/{len(urls)}] Processing: {url}")
                # Scrape the URL (cloud-safe, no Selenium)
                documents = web_scraper.scrape_multiple_urls_simple([url])
                logger.info(f"[SITEMAP_INGEST] [{idx}/{len(urls)}] Scraped {len(documents)} documents from {url}")
                # DEBUG: Log document content length
                if documents:
                    logger.info(f"[SITEMAP_DEBUG] Document page_content length: {len(documents[0].page_content)} chars")
                    logger.info(f"[SITEMAP_DEBUG] Document page_content preview: {documents[0].page_content[:200]}")

                if documents:
                    # Chunk the documents
                    chunks = document_loader.chunk_documents(documents)
                    logger.info(f"[SITEMAP_INGEST] [{idx}/{len(urls)}] Created {len(chunks)} chunks")
                                        # DEBUG: Log chunk content
                                        if chunks:
                                            logger.info(f"[SITEMAP_DEBUG] First chunk page_content length: {len(chunks[0].page_content)} chars")
                                            logger.info(f"[SITEMAP_DEBUG] First chunk page_content preview: {chunks[0].page_content[:200]}")
                    
                    # Add to vector store
                    num_added = vectorstore_manager.add_documents(chunks)
                    total_chunks += num_added
                    successful_urls.append(url)
                    logger.info(f"[SITEMAP_INGEST] [{idx}/{len(urls)}] ✓ Added {num_added} chunks to vector store")
                else:
                    failed_urls.append(url)
                    logger.warning(f"[SITEMAP_INGEST] [{idx}/{len(urls)}] ✗ No documents from {url}")
                    
            except Exception as e:
                failed_urls.append(url)
                logger.error(f"[SITEMAP_INGEST] [{idx}/{len(urls)}] ✗ Exception for {url}: {type(e).__name__}: {str(e)[:120]}")
        
        response = IngestResponse(
            status="success" if successful_urls else "partial",
            message=f"Ingested {len(successful_urls)}/{len(urls)} URLs from sitemap",
            documents_processed=len(successful_urls),
            chunks_created=total_chunks,
            sources=successful_urls[:50]  # Return first 50 for response size
        )
        
        logger.info(f"[SITEMAP_END] ✓ Complete: {len(successful_urls)}/{len(urls)} successful, {total_chunks} total chunks")
        
        if failed_urls:
            logger.warning(f"[SITEMAP_END] Failed URLs: {failed_urls[:10]}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during sitemap ingestion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing sitemap: {str(e)}"
        )
