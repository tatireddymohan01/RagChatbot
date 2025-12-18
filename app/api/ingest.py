"""
Document and URL Ingestion Endpoints
Handles uploading documents and scraping web content
"""
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.ingest_schema import URLIngestRequest, IngestResponse
from app.services.document_loader import get_document_loader
from app.services.web_scraper import get_web_scraper
from app.core.vectorstore import get_vectorstore_manager
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
        
        # Scrape the URL
        web_scraper = get_web_scraper()
        documents = web_scraper.scrape_url(url)
        
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
            message=f"Successfully ingested content from URL",
            documents_processed=1,
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
