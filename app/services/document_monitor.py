"""
Document Folder Monitor Service
Automatically monitors and processes new documents from the documents folder
"""
import json
import hashlib
from pathlib import Path
from typing import Dict, Set, List
from datetime import datetime
from app.core.config import get_settings
from app.services.document_loader import get_document_loader
from app.core.vectorstore import get_vectorstore_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentMonitor:
    """Service for monitoring and auto-processing documents from folder"""
    
    def __init__(self):
        self.settings = get_settings()
        self.tracking_file = Path(self.settings.documents_folder) / ".processed_files.json"
        self.processed_files: Dict[str, str] = {}
        self.load_tracking_data()
    
    def load_tracking_data(self):
        """Load tracking data of previously processed files"""
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, 'r') as f:
                    self.processed_files = json.load(f)
                logger.info(f"Loaded tracking data: {len(self.processed_files)} files previously processed")
            except Exception as e:
                logger.error(f"Error loading tracking file: {e}")
                self.processed_files = {}
        else:
            self.processed_files = {}
    
    def save_tracking_data(self):
        """Save tracking data of processed files"""
        try:
            # Ensure documents folder exists
            Path(self.settings.documents_folder).mkdir(parents=True, exist_ok=True)
            
            with open(self.tracking_file, 'w') as f:
                json.dump(self.processed_files, f, indent=2)
            logger.debug("Tracking data saved")
        except Exception as e:
            logger.error(f"Error saving tracking file: {e}")
    
    def get_file_hash(self, file_path: Path) -> str:
        """Calculate hash of file for change detection"""
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                # Read in chunks for large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def scan_for_new_documents(self) -> List[Path]:
        """
        Scan documents folder for new or modified files
        
        Returns:
            List of file paths that are new or modified
        """
        folder = Path(self.settings.documents_folder)
        
        if not folder.exists():
            logger.info(f"Creating documents folder: {folder}")
            folder.mkdir(parents=True, exist_ok=True)
            return []
        
        # Supported file extensions
        supported_extensions = [".pdf", ".txt", ".docx", ".doc"]
        
        # Find all supported files
        all_files = []
        for ext in supported_extensions:
            all_files.extend(folder.glob(f"*{ext}"))
        
        # Filter for new or modified files
        new_or_modified = []
        for file_path in all_files:
            file_str = str(file_path.name)
            current_hash = self.get_file_hash(file_path)
            
            if not current_hash:
                continue
            
            # Check if file is new or modified
            if file_str not in self.processed_files:
                logger.info(f"New document found: {file_path.name}")
                new_or_modified.append(file_path)
            elif self.processed_files[file_str] != current_hash:
                logger.info(f"Modified document found: {file_path.name}")
                new_or_modified.append(file_path)
        
        return new_or_modified
    
    def process_new_documents(self) -> Dict:
        """
        Process all new or modified documents from folder
        If any documents are modified, rebuilds the entire vector store to avoid conflicts
        
        Returns:
            Dictionary with processing statistics
        """
        try:
            new_files = self.scan_for_new_documents()
            
            if not new_files:
                logger.info("No new or modified documents found")
                return {
                    "status": "success",
                    "message": "No new documents to process",
                    "documents_processed": 0,
                    "chunks_created": 0,
                    "files": []
                }
            
            document_loader = get_document_loader()
            vectorstore_manager = get_vectorstore_manager()
            
            # Check if any files are modified (not new)
            has_modifications = any(
                file_path.name in self.processed_files 
                for file_path in new_files
            )
            
            # If we have modifications, rebuild entire index from all documents
            if has_modifications:
                logger.info("Modified documents detected - rebuilding entire vector store")
                return self._rebuild_entire_index()
            
            # Otherwise, just add new documents
            all_chunks = []
            processed_files = []
            
            for file_path in new_files:
                try:
                    logger.info(f"Processing: {file_path.name}")
                    
                    # Load and chunk the document
                    documents = document_loader.load_file(str(file_path))
                    chunks = document_loader.chunk_documents(documents)
                    
                    all_chunks.extend(chunks)
                    processed_files.append(file_path.name)
                    
                    # Update tracking
                    file_hash = self.get_file_hash(file_path)
                    self.processed_files[file_path.name] = file_hash
                    
                    logger.info(f"Created {len(chunks)} chunks from {file_path.name}")
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path.name}: {e}")
                    continue
            
            if not all_chunks:
                return {
                    "status": "error",
                    "message": "No documents could be processed successfully",
                    "documents_processed": 0,
                    "chunks_created": 0,
                    "files": []
                }
            
            # Add to vector store
            num_added = vectorstore_manager.add_documents(all_chunks)
            
            # Save tracking data
            self.save_tracking_data()
            
            result = {
                "status": "success",
                "message": f"Successfully processed {len(processed_files)} new document(s)",
                "documents_processed": len(processed_files),
                "chunks_created": num_added,
                "files": processed_files
            }
            
            logger.info(f"Auto-processing complete: {num_added} chunks from {len(processed_files)} documents")
            return result
            
        except Exception as e:
            logger.error(f"Error in auto-processing: {e}")
            return {
                "status": "error",
                "message": f"Error processing documents: {str(e)}",
                "documents_processed": 0,
                "chunks_created": 0,
                "files": []
            }
    
    def _rebuild_entire_index(self) -> Dict:
        """
        Rebuild the entire vector store from all documents in folder
        Used when documents are modified to avoid conflicts with old data
        """
        try:
            folder = Path(self.settings.documents_folder)
            supported_extensions = [".pdf", ".txt", ".docx", ".doc"]
            
            # Find all supported files
            all_files = []
            for ext in supported_extensions:
                all_files.extend(folder.glob(f"*{ext}"))
            
            if not all_files:
                logger.info("No documents found for rebuild")
                return {
                    "status": "success",
                    "message": "No documents to rebuild",
                    "documents_processed": 0,
                    "chunks_created": 0,
                    "files": []
                }
            
            logger.info(f"Rebuilding index from {len(all_files)} document(s)")
            
            document_loader = get_document_loader()
            vectorstore_manager = get_vectorstore_manager()
            
            all_chunks = []
            processed_files = []
            
            # Process all documents
            for file_path in all_files:
                try:
                    logger.info(f"Loading: {file_path.name}")
                    documents = document_loader.load_file(str(file_path))
                    chunks = document_loader.chunk_documents(documents)
                    all_chunks.extend(chunks)
                    processed_files.append(file_path.name)
                    
                    # Update tracking with current hash
                    file_hash = self.get_file_hash(file_path)
                    self.processed_files[file_path.name] = file_hash
                    
                except Exception as e:
                    logger.error(f"Error loading {file_path.name}: {e}")
                    continue
            
            if not all_chunks:
                return {
                    "status": "error",
                    "message": "No documents could be loaded",
                    "documents_processed": 0,
                    "chunks_created": 0,
                    "files": []
                }
            
            # Clear and rebuild vector store
            logger.info(f"Clearing old index and creating new one with {len(all_chunks)} chunks")
            vectorstore_manager.reset()  # Clear existing index
            num_added = vectorstore_manager.add_documents(all_chunks)
            
            # Save tracking data
            self.save_tracking_data()
            
            result = {
                "status": "success",
                "message": f"Rebuilt index from {len(processed_files)} document(s)",
                "documents_processed": len(processed_files),
                "chunks_created": num_added,
                "files": processed_files
            }
            
            logger.info(f"Index rebuild complete: {num_added} chunks from {len(processed_files)} documents")
            return result
            
        except Exception as e:
            logger.error(f"Error rebuilding index: {e}")
            return {
                "status": "error",
                "message": f"Error rebuilding index: {str(e)}",
                "documents_processed": 0,
                "chunks_created": 0,
                "files": []
            }
    
    def reset_tracking(self):
        """Reset all tracking data (forces reprocessing of all documents)"""
        self.processed_files = {}
        if self.tracking_file.exists():
            self.tracking_file.unlink()
        logger.info("Tracking data reset")


# Global monitor instance
_document_monitor: DocumentMonitor = None


def get_document_monitor() -> DocumentMonitor:
    """Get or create the global DocumentMonitor instance"""
    global _document_monitor
    
    if _document_monitor is None:
        _document_monitor = DocumentMonitor()
    
    return _document_monitor
