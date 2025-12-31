"""
Document and URL Ingestion Endpoints
Handles uploading documents and scraping web content
"""
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.ingest_schema import URLIngestRequest, URLDeleteRequest, IngestResponse
from app.services.document_loader import get_document_loader
from app.services.web_scraper import get_web_scraper
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
        logger.info(f"Received URL for ingestion: {url}")
        
        # Scrape the URL or entire website
        web_scraper = get_web_scraper()
        
        if request.scrape_full_site:
            logger.info(f"Scraping entire website from: {url}")
            documents = web_scraper.scrape_website(url)
        else:
            logger.info(f"Scraping single URL: {url}")
            documents = web_scraper.scrape_multiple_urls_selenium([url])
        
        if not documents:
            raise HTTPException(
                status_code=400,
                detail=f"Could not scrape content from URL: {url}"
            )
        
        # Chunk the documents
        document_loader = get_document_loader()
        chunks = document_loader.chunk_documents(documents)
        
        logger.info(f"Created {len(chunks)} chunks from URL content")
        
        # Add to vector store
        vectorstore_manager = get_vectorstore_manager()
        num_added = vectorstore_manager.add_documents(chunks)
        
        response = IngestResponse(
            status="success",
            message=f"Successfully ingested content from {'website' if request.scrape_full_site else 'URL'}",
            documents_processed=len(documents),
            chunks_created=num_added,
            sources=[url]
        )
        
        logger.info(f"URL ingestion complete: {num_added} chunks added")
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
