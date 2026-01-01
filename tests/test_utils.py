"""
Test utilities and helpers
Common test functions and data generators
"""
import random
import string
from typing import List, Dict, Any


def generate_random_string(length: int = 10) -> str:
    """Generate a random string of given length"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_test_query(query_type: str = "simple") -> str:
    """
    Generate test queries
    
    Args:
        query_type: 'simple', 'complex', 'short', 'long'
    """
    simple_queries = [
        "What is machine learning?",
        "Explain neural networks",
        "How does deep learning work?",
        "What are embeddings?",
        "Tell me about transformers"
    ]
    
    complex_queries = [
        "Can you explain how machine learning algorithms work, " +
        "specifically focusing on neural networks and their applications in NLP?",
        "What are the differences between supervised and unsupervised learning, " +
        "and how do they apply to different domains?"
    ]
    
    short_queries = [
        "What is AI?",
        "Explain ML",
        "How?",
        "Why?"
    ]
    
    long_queries = [
        "I want to understand everything about artificial intelligence, including " +
        "machine learning, deep learning, neural networks, transformers, and their " +
        "applications in natural language processing, computer vision, and other domains. " +
        "Can you provide a comprehensive overview?"
    ]
    
    if query_type == "simple":
        return random.choice(simple_queries)
    elif query_type == "complex":
        return random.choice(complex_queries)
    elif query_type == "short":
        return random.choice(short_queries)
    elif query_type == "long":
        return random.choice(long_queries)
    
    return random.choice(simple_queries)


def generate_test_session_id() -> str:
    """Generate a test session ID"""
    return f"test-session-{generate_random_string(8)}"


def generate_test_chat_history(num_turns: int = 2) -> List[Dict[str, str]]:
    """
    Generate test chat history
    
    Args:
        num_turns: Number of conversation turns
    """
    history = []
    for i in range(num_turns):
        history.append({
            "role": "user",
            "content": generate_test_query("simple")
        })
        history.append({
            "role": "assistant",
            "content": f"Response to question {i+1}"
        })
    
    return history


def generate_test_urls(num_urls: int = 1) -> List[str]:
    """Generate test URLs"""
    domains = [
        "https://example.com",
        "https://github.com",
        "https://stackoverflow.com",
        "https://docs.python.org",
        "https://pytorch.org"
    ]
    
    paths = [
        "/article",
        "/tutorial",
        "/guide",
        "/documentation",
        "/blog/post"
    ]
    
    urls = []
    for i in range(num_urls):
        domain = random.choice(domains)
        path = random.choice(paths)
        urls.append(f"{domain}{path}{i}")
    
    return urls


def generate_test_filenames(num_files: int = 1, format: str = "pdf") -> List[str]:
    """
    Generate test filenames
    
    Args:
        num_files: Number of filenames to generate
        format: 'pdf', 'txt', 'docx', 'doc', 'all'
    """
    base_names = ["document", "article", "report", "notes", "data", "summary"]
    extensions = []
    
    if format == "pdf":
        extensions = [".pdf"]
    elif format == "txt":
        extensions = [".txt"]
    elif format == "docx":
        extensions = [".docx"]
    elif format == "doc":
        extensions = [".doc"]
    elif format == "all":
        extensions = [".pdf", ".txt", ".docx", ".doc"]
    
    filenames = []
    for i in range(num_files):
        base = random.choice(base_names)
        ext = random.choice(extensions)
        filenames.append(f"{base}_{i+1}{ext}")
    
    return filenames


def generate_mock_response(
    status: str = "success",
    documents: int = 1,
    chunks: int = 5,
    sources: List[str] = None
) -> Dict[str, Any]:
    """Generate mock ingest response"""
    if sources is None:
        sources = generate_test_filenames(documents)
    
    return {
        "status": status,
        "message": f"Processed {documents} document(s)",
        "documents_processed": documents,
        "chunks_created": chunks,
        "sources": sources
    }


def generate_mock_chat_response(
    answer: str = "This is a test answer.",
    num_sources: int = 2,
    session_id: str = None
) -> Dict[str, Any]:
    """Generate mock chat response"""
    if session_id is None:
        session_id = generate_test_session_id()
    
    sources = [
        {
            "content": f"Source content {i+1}",
            "source": f"document_{i+1}.pdf",
            "page": i + 1
        }
        for i in range(num_sources)
    ]
    
    return {
        "answer": answer,
        "sources": sources,
        "session_id": session_id
    }


class TestDataBuilder:
    """Builder class for creating test data"""
    
    def __init__(self):
        self.query = None
        self.session_id = None
        self.chat_history = None
    
    def with_query(self, query: str) -> "TestDataBuilder":
        """Set query"""
        self.query = query
        return self
    
    def with_session_id(self, session_id: str) -> "TestDataBuilder":
        """Set session ID"""
        self.session_id = session_id
        return self
    
    def with_chat_history(self, num_turns: int) -> "TestDataBuilder":
        """Set chat history"""
        self.chat_history = generate_test_chat_history(num_turns)
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build request data"""
        data = {}
        
        if self.query:
            data["query"] = self.query
        else:
            data["query"] = generate_test_query()
        
        if self.session_id:
            data["session_id"] = self.session_id
        
        if self.chat_history is not None:
            data["chat_history"] = self.chat_history
        
        return data
