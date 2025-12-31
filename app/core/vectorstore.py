"""
Vector Store Management
Handles FAISS vector store initialization, loading, and persistence
"""
import os
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse
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
    
    def reset(self):
        """Reset the vector store (alias for clear_index)"""
        self.clear_index()

    def _normalize_domain(self, value: Optional[str]) -> str:
        if not value:
            return ""
        parsed = urlparse(value)
        candidate = parsed.netloc if parsed.netloc else value
        candidate = candidate.lower().lstrip(".")
        if candidate.startswith("www."):
            candidate = candidate[4:]
        return candidate

    def _domains_match(self, src_domain: str, meta_domain: str, target: str) -> bool:
        if not target:
            return False
        # exact match
        if src_domain == target or meta_domain == target:
            return True
        # allow subdomain matches (e.g., api.example.com matches example.com)
        if src_domain.endswith("." + target) or meta_domain.endswith("." + target):
            return True
        return False

    def delete_by_source(self, url: str = None, domain: str = None) -> dict:
        """Delete vectors whose metadata.source matches a URL or domain"""
        if self.vectorstore is None:
            return {"deleted": 0, "matched": 0}

        if not url and not domain:
            raise ValueError("Provide url or domain to delete")

        normalized_domain = self._normalize_domain(domain)
        normalized_url = url.rstrip("/") if url else None

        docstore = getattr(self.vectorstore, "docstore", None)
        id_map = getattr(self.vectorstore, "index_to_docstore_id", None)

        if docstore is None or id_map is None:
            raise RuntimeError("Vector store docstore not available")

        targets = []
        for doc_id, doc in docstore._dict.items():
            src = doc.metadata.get("source", "") if doc and doc.metadata else ""
            if not src:
                continue
            src_domain = self._normalize_domain(urlparse(src).netloc)
            meta_domain = self._normalize_domain(doc.metadata.get("domain")) if doc.metadata else ""

            match_url = False
            if normalized_url:
                src_clean = src.rstrip("/")
                match_url = src_clean == normalized_url

            match_domain = False
            if normalized_domain:
                match_domain = self._domains_match(src_domain, meta_domain, normalized_domain)

            if match_url or match_domain:
                targets.append(doc_id)

        if not targets:
            return {"deleted": 0, "matched": 0}

        self.vectorstore.delete(ids=targets)
        self.save()

        return {"deleted": len(targets), "matched": len(targets)}


# Global vector store instance
_vectorstore_manager: Optional[VectorStoreManager] = None


def get_vectorstore_manager() -> VectorStoreManager:
    """Get or create the global VectorStoreManager instance"""
    global _vectorstore_manager
    
    if _vectorstore_manager is None:
        _vectorstore_manager = VectorStoreManager()
    
    return _vectorstore_manager
