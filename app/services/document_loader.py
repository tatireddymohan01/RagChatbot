"""
Document Loader Service
Handles loading and chunking documents from various file formats
"""
import tempfile
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader
)
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentLoaderService:
    """Service for loading and processing documents"""
    
    def __init__(self):
        self.settings = get_settings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_file(self, file_path: str) -> List[Document]:
        """
        Load a document from file path
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of Document objects
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = path.suffix.lower()
        
        try:
            logger.info(f"Loading file: {file_path} (type: {file_extension})")
            
            if file_extension == ".pdf":
                loader = PyPDFLoader(file_path)
            elif file_extension == ".txt":
                loader = TextLoader(file_path, encoding="utf-8")
            elif file_extension in [".docx", ".doc"]:
                loader = Docx2txtLoader(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} document(s) from {path.name}")
            
            return documents
            
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            raise
    
    def load_multiple_files(self, file_paths: List[str]) -> List[Document]:
        """
        Load multiple document files
        
        Args:
            file_paths: List of file paths
            
        Returns:
            Combined list of Document objects
        """
        all_documents = []
        
        for file_path in file_paths:
            try:
                documents = self.load_file(file_path)
                all_documents.extend(documents)
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                # Continue with other files
        
        logger.info(f"Loaded total of {len(all_documents)} documents from {len(file_paths)} files")
        return all_documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of chunked Document objects
        """
        if not documents:
            return []
        
        try:
            logger.info(f"Splitting {len(documents)} documents into chunks")
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Created {len(chunks)} chunks from documents")
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking documents: {e}")
            raise
    
    def process_uploaded_file(self, file_content: bytes, filename: str) -> List[Document]:
        """
        Process an uploaded file from FastAPI
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            List of chunked Document objects
        """
        # Create temporary file
        file_extension = Path(filename).suffix
        
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_extension
        ) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Load and chunk the document
            documents = self.load_file(temp_file_path)
            
            # Add source metadata
            for doc in documents:
                doc.metadata["source"] = filename
            
            chunks = self.chunk_documents(documents)
            
            return chunks
            
        finally:
            # Clean up temporary file
            try:
                Path(temp_file_path).unlink()
            except Exception as e:
                logger.warning(f"Could not delete temporary file: {e}")
    
    def process_text(self, text: str, source: str = "manual_input") -> List[Document]:
        """
        Process raw text into chunked documents
        
        Args:
            text: Raw text content
            source: Source identifier
            
        Returns:
            List of chunked Document objects
        """
        try:
            # Create a document from text
            document = Document(
                page_content=text,
                metadata={"source": source}
            )
            
            # Chunk the document
            chunks = self.text_splitter.split_documents([document])
            logger.info(f"Created {len(chunks)} chunks from text input")
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            raise


# Global loader instance
_document_loader: DocumentLoaderService = None


def get_document_loader() -> DocumentLoaderService:
    """Get or create the global DocumentLoaderService instance"""
    global _document_loader
    
    if _document_loader is None:
        _document_loader = DocumentLoaderService()
    
    return _document_loader
