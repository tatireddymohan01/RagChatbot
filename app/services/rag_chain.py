"""
RAG Chain Service
Implements the conversational retrieval chain for question answering
"""
from typing import List, Dict, Tuple, Optional
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from app.core.llm import get_llm, get_system_prompt
from app.core.vectorstore import get_vectorstore_manager
from app.core.config import get_settings
from app.schemas.chat_schema import ChatMessage, SourceDocument
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RAGChainService:
    """Service for RAG-based question answering with conversational memory"""
    
    def __init__(self):
        self.llm = get_llm()
        self.vectorstore_manager = get_vectorstore_manager()
        self.sessions: Dict[str, ConversationBufferMemory] = {}
        self.settings = get_settings()
    
    def _get_or_create_memory(self, session_id: str) -> ConversationBufferMemory:
        """Get or create conversation memory for a session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
            logger.info(f"Created new conversation memory for session: {session_id}")
        
        return self.sessions[session_id]
    
    def _format_chat_history(self, chat_history: List[ChatMessage]) -> List[tuple]:
        """Convert ChatMessage list to LangChain format"""
        formatted_history = []
        
        for msg in chat_history:
            if msg.role == "user":
                formatted_history.append((msg.content, ""))
            elif msg.role == "assistant" and formatted_history:
                # Add to the last tuple
                formatted_history[-1] = (formatted_history[-1][0], msg.content)
        
        return formatted_history
    
    def query(
        self,
        question: str,
        session_id: Optional[str] = None,
        chat_history: Optional[List[ChatMessage]] = None
    ) -> Tuple[str, List[SourceDocument]]:
        """
        Query the RAG system with conversational context
        
        Args:
            question: User's question
            session_id: Optional session ID for conversation tracking
            chat_history: Optional previous chat messages
            
        Returns:
            Tuple of (answer, source_documents)
        """
        try:
            # Get retriever
            retriever = self.vectorstore_manager.get_retriever()
            
            if retriever is None:
                if self.settings.allow_general_knowledge:
                    logger.warning("No documents in vector store, using general knowledge")
                    # Use LLM directly without retrieval
                    from langchain_core.prompts import ChatPromptTemplate
                    from langchain_core.output_parsers import StrOutputParser
                    
                    system_prompt = get_system_prompt(True)
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", system_prompt + "\n\nNo documents are available, so please answer using your general knowledge."),
                        ("user", "{question}")
                    ])
                    chain = prompt | self.llm | StrOutputParser()
                    answer = chain.invoke({"question": question})
                    return answer, []
                else:
                    logger.warning("No documents in vector store and general knowledge disabled")
                    return "I don't have any documents to answer from. Please ingest some documents first.", []
            
            logger.info(f"Processing query: {question[:100]}...")
            
            # Create custom prompt for better answer extraction
            from langchain_core.prompts import PromptTemplate
            
            # Check if general knowledge is allowed
            if self.settings.allow_general_knowledge:
                prompt_template = """Use the following pieces of context to answer the question at the end. 

Read the context carefully and extract specific information requested in the question.
If the answer is in the context, provide it directly and concisely in English.
If you cannot find the answer in the context, use your general knowledge to provide a helpful answer.

IMPORTANT: Always respond in English language only.

Context:
{context}

Question: {question}

Answer in English:"""
            else:
                prompt_template = """Use the following pieces of context to answer the question at the end. 

Read the context carefully and extract specific information requested in the question.
If the answer is in the context, provide it directly and concisely in English.
If you cannot find the answer in the context, say "I don't know" - do not make up an answer.

IMPORTANT: Always respond in English language only.

Context:
{context}

Question: {question}

Answer in English:"""
            
            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            # Create conversational chain with custom prompt
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                return_source_documents=True,
                verbose=False,
                chain_type="stuff",  # "stuff" method passes all context at once
                combine_docs_chain_kwargs={"prompt": PROMPT}
            )
            
            # Format chat history
            formatted_history = []
            if chat_history:
                formatted_history = self._format_chat_history(chat_history)
            
            # Query the chain using invoke instead of __call__
            result = qa_chain.invoke({
                "question": question,
                "chat_history": formatted_history
            })
            
            answer = result.get("answer", "I couldn't generate an answer.")
            source_docs = result.get("source_documents", [])
            
            # Log retrieved documents for monitoring
            logger.info(f"Retrieved {len(source_docs)} documents from vector store")
            for i, doc in enumerate(source_docs[:2], 1):
                logger.info(f"Doc {i} preview: {doc.page_content[:100]}...")
            
            # Format source documents
            sources = []
            for doc in source_docs:
                source = SourceDocument(
                    content=doc.page_content[:500],  # Limit content length
                    source=doc.metadata.get("source", "unknown"),
                    page=doc.metadata.get("page", None)
                )
                sources.append(source)
            
            logger.info(f"Generated answer with {len(sources)} source documents")
            
            return answer, sources
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise
    
    def query_with_memory(
        self,
        question: str,
        session_id: str
    ) -> Tuple[str, List[SourceDocument]]:
        """
        Query with persistent session memory
        
        Args:
            question: User's question
            session_id: Session ID for conversation tracking
            
        Returns:
            Tuple of (answer, source_documents)
        """
        try:
            retriever = self.vectorstore_manager.get_retriever()
            
            if retriever is None:
                return "I don't have any documents to answer from. Please ingest some documents first.", []
            
            memory = self._get_or_create_memory(session_id)
            
            # Create conversational chain with memory
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=memory,
                return_source_documents=True,
                verbose=False,
                chain_type="stuff"
            )
            
            # Query
            result = qa_chain({"question": question})
            
            answer = result.get("answer", "I couldn't generate an answer.")
            source_docs = result.get("source_documents", [])
            
            # Format sources
            sources = []
            for doc in source_docs:
                source = SourceDocument(
                    content=doc.page_content[:500],
                    source=doc.metadata.get("source", "unknown"),
                    page=doc.metadata.get("page", None)
                )
                sources.append(source)
            
            return answer, sources
            
        except Exception as e:
            logger.error(f"Error processing query with memory: {e}")
            raise
    
    def clear_session(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session: {session_id}")
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.sessions.keys())


# Global RAG chain instance
_rag_chain: RAGChainService = None


def get_rag_chain() -> RAGChainService:
    """Get or create the global RAGChainService instance"""
    global _rag_chain
    
    if _rag_chain is None:
        _rag_chain = RAGChainService()
    
    return _rag_chain
