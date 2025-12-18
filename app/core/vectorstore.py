"""
Vector Store Management
Handles FAISS vector store initialization, loading, and persistence
"""
import os
from pathlib import Path
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from app.core.embeddings import get_embeddings
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class VectorStoreManager:
    """Manages FAISS vector store operations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.embeddings = get_embeddings()
        self.vectorstore: Optional[FAISS] = None
        self.index_path = Path(self.settings.faiss_index_path)
        
        # Ensure index directory exists
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        # Try to load existing index
        self._load_or_create_vectorstore()
    
    def _load_or_create_vectorstore(self):
        """Load existing FAISS index or create a new one"""
        try:
            index_file = self.index_path / "index.faiss"
            
            if index_file.exists():
                logger.info(f"Loading existing FAISS index from {self.index_path}")
                self.vectorstore = FAISS.load_local(
                    str(self.index_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True  # Required for loading pickled data
                )
                logger.info("FAISS index loaded successfully")
            else:
                logger.info("No existing FAISS index found. Will create new one on first document ingestion.")
                self.vectorstore = None
                
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            logger.info("Will create new index on first document ingestion")
            self.vectorstore = None
    
    def add_documents(self, documents: List[Document]) -> int:
        """
        Add documents to the vector store
        
        Args:
            documents: List of LangChain Document objects
            
        Returns:
            Number of documents added
        """
        if not documents:
            logger.warning("No documents to add")
            return 0
        
        try:
            if self.vectorstore is None:
                # Create new vector store
                logger.info(f"Creating new FAISS index with {len(documents)} documents")
                self.vectorstore = FAISS.from_documents(
                    documents=documents,
                    embedding=self.embeddings
                )
            else:
                # Add to existing vector store
                logger.info(f"Adding {len(documents)} documents to existing FAISS index")
                self.vectorstore.add_documents(documents)
            
            # Save to disk
            self.save()
            
            logger.info(f"Successfully added {len(documents)} documents to vector store")
            return len(documents)
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    def save(self):
        """Persist vector store to disk"""
        if self.vectorstore is None:
            logger.warning("No vector store to save")
            return
        
        try:
            logger.info(f"Saving FAISS index to {self.index_path}")
            self.vectorstore.save_local(str(self.index_path))
            logger.info("FAISS index saved successfully")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
            raise
    
    def get_retriever(self, k: int = None):
        """
        Get a retriever from the vector store
        
        Args:
            k: Number of documents to retrieve (default from settings)
            
        Returns:
            VectorStoreRetriever instance
        """
        if self.vectorstore is None:
            logger.warning("Vector store not initialized. No documents have been ingested yet.")
            return None
        
        if k is None:
            k = self.settings.retrieval_k
        
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": k}
        )
        
        logger.info(f"Retriever created with k={k}")
        return retriever
    
    def similarity_search(self, query: str, k: int = None) -> List[Document]:
        """
        Perform similarity search
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant documents
        """
        if self.vectorstore is None:
            logger.warning("Vector store not initialized")
            return []
        
        if k is None:
            k = self.settings.retrieval_k
        
        try:
            results = self.vectorstore.similarity_search(query, k=k)
            logger.info(f"Found {len(results)} similar documents for query")
            return results
        except Exception as e:
            logger.error(f"Error during similarity search: {e}")
            return []
    
    def clear_index(self):
        """Clear the entire vector store index"""
        try:
            logger.warning("Clearing FAISS index")
            
            # Delete index files
            index_file = self.index_path / "index.faiss"
            pkl_file = self.index_path / "index.pkl"
            
            if index_file.exists():
                index_file.unlink()
            if pkl_file.exists():
                pkl_file.unlink()
            
            self.vectorstore = None
            logger.info("FAISS index cleared successfully")
            
        except Exception as e:
            logger.error(f"Error clearing FAISS index: {e}")
            raise


# Global vector store instance
_vectorstore_manager: Optional[VectorStoreManager] = None


def get_vectorstore_manager() -> VectorStoreManager:
    """Get or create the global VectorStoreManager instance"""
    global _vectorstore_manager
    
    if _vectorstore_manager is None:
        _vectorstore_manager = VectorStoreManager()
    
    return _vectorstore_manager
