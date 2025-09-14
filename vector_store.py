# Vector embeddings and storage for RAG system
import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import json
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import uuid
from datetime import datetime

@dataclass
class Document:
    id: str
    content: str
    metadata: Dict[str, Any]
    filename: str = ""
    chunk_index: int = 0

@dataclass
class SearchMatch:
    document: Document
    score: float
    snippet: str

class VectorStore:
    """Vector store for document embeddings and retrieval"""
    
    def __init__(self, collection_name: str = "rag_documents", persist_directory: str = "./chroma_db"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Initialize embedding model
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Embedding model loaded.")
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"Loaded existing collection: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"Created new collection: {collection_name}")
    
    def add_document(self, content: str, metadata: Dict[str, Any], filename: str = "") -> str:
        """Add a single document to the vector store"""
        doc_id = str(uuid.uuid4())
        
        # Create document
        document = Document(
            id=doc_id,
            content=content,
            metadata=metadata,
            filename=filename
        )
        
        # Generate embedding
        embedding = self.embedding_model.encode(content).tolist()
        
        # Add to ChromaDB
        self.collection.add(
            documents=[content],
            embeddings=[embedding],
            metadatas=[{
                **metadata,
                'filename': filename,
                'doc_id': doc_id,
                'added_date': datetime.now().isoformat()
            }],
            ids=[doc_id]
        )
        
        print(f"Added document: {filename or doc_id[:8]}")
        return doc_id
    
    def add_document_chunks(self, chunks: List[str], metadata: Dict[str, Any], filename: str = "") -> List[str]:
        """Add multiple chunks from a document to the vector store"""
        doc_ids = []
        embeddings = []
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            doc_id = str(uuid.uuid4())
            doc_ids.append(doc_id)
            
            # Generate embedding for chunk
            embedding = self.embedding_model.encode(chunk).tolist()
            embeddings.append(embedding)
            documents.append(chunk)
            
            # Create metadata for chunk
            chunk_metadata = {
                **metadata,
                'filename': filename,
                'doc_id': doc_id,
                'chunk_index': i,
                'total_chunks': len(chunks),
                'added_date': datetime.now().isoformat()
            }
            metadatas.append(chunk_metadata)
            ids.append(doc_id)
        
        # Batch add to ChromaDB
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Added {len(chunks)} chunks from: {filename or 'document'}")
        return doc_ids
    
    def search(self, query: str, n_results: int = 5, filter_metadata: Optional[Dict] = None) -> List[SearchMatch]:
        """Search for similar documents"""
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata
        )
        
        # Convert results to SearchMatch objects
        matches = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                document = Document(
                    id=results['ids'][0][i],
                    content=results['documents'][0][i],
                    metadata=results['metadatas'][0][i],
                    filename=results['metadatas'][0][i].get('filename', ''),
                    chunk_index=results['metadatas'][0][i].get('chunk_index', 0)
                )
                
                score = 1 - results['distances'][0][i]  # Convert distance to similarity
                snippet = self._create_snippet(results['documents'][0][i], query)
                
                matches.append(SearchMatch(
                    document=document,
                    score=score,
                    snippet=snippet
                ))
        
        return matches
    
    def _create_snippet(self, content: str, query: str, max_length: int = 200) -> str:
        """Create a snippet highlighting query terms"""
        query_terms = query.lower().split()
        content_lower = content.lower()
        
        # Find the best position to start the snippet
        best_pos = 0
        max_matches = 0
        
        for i in range(0, len(content) - max_length, 50):
            snippet = content_lower[i:i + max_length]
            matches = sum(1 for term in query_terms if term in snippet)
            if matches > max_matches:
                max_matches = matches
                best_pos = i
        
        snippet = content[best_pos:best_pos + max_length]
        if best_pos > 0:
            snippet = "..." + snippet
        if best_pos + max_length < len(content):
            snippet = snippet + "..."
        
        return snippet.strip()
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            return {
                'document_count': count,
                'collection_name': self.collection_name,
                'embedding_model': 'all-MiniLM-L6-v2'
            }
        except:
            return {
                'document_count': 0,
                'collection_name': self.collection_name,
                'embedding_model': 'all-MiniLM-L6-v2'
            }
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the vector store"""
        try:
            self.collection.delete(ids=[doc_id])
            print(f"Deleted document: {doc_id}")
            return True
        except Exception as e:
            print(f"Error deleting document {doc_id}: {e}")
            return False
    
    def clear_collection(self):
        """Clear all documents from the collection"""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print("Collection cleared.")
        except Exception as e:
            print(f"Error clearing collection: {e}")

class RAGSystem:
    """Complete RAG system combining web search and document retrieval"""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.web_search = None  # Will be initialized when needed
    
    def add_document_from_file(self, file_path: str) -> str:
        """Add a document from file to the knowledge base"""
        from document_processor import process_document
        
        processed_doc = process_document(file_path)
        
        if processed_doc.chunks and len(processed_doc.chunks) > 1:
            # Add as chunks if document was chunked
            doc_ids = self.vector_store.add_document_chunks(
                processed_doc.chunks,
                processed_doc.metadata,
                processed_doc.filename
            )
            return f"Added {len(doc_ids)} chunks from {processed_doc.filename}"
        else:
            # Add as single document
            doc_id = self.vector_store.add_document(
                processed_doc.content,
                processed_doc.metadata,
                processed_doc.filename
            )
            return f"Added document: {processed_doc.filename}"
    
    def add_document_from_upload(self, uploaded_file) -> str:
        """Add a document from uploaded file to the knowledge base"""
        from document_processor import process_uploaded_document
        
        processed_doc = process_uploaded_document(uploaded_file)
        
        if processed_doc.chunks and len(processed_doc.chunks) > 1:
            doc_ids = self.vector_store.add_document_chunks(
                processed_doc.chunks,
                processed_doc.metadata,
                processed_doc.filename
            )
            return f"Added {len(doc_ids)} chunks from {processed_doc.filename}"
        else:
            doc_id = self.vector_store.add_document(
                processed_doc.content,
                processed_doc.metadata,
                processed_doc.filename
            )
            return f"Added document: {processed_doc.filename}"
    
    def search_documents(self, query: str, n_results: int = 3) -> List[SearchMatch]:
        """Search in the document knowledge base"""
        return self.vector_store.search(query, n_results)
    
    def search_web(self, query: str, n_results: int = 3) -> List[Any]:
        """Search the web for information"""
        if self.web_search is None:
            from real_web_search import get_web_search
            self.web_search = get_web_search()
        
        import asyncio
        
        # Create event loop if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        search_response = loop.run_until_complete(
            self.web_search.search_web(query, n_results)
        )
        return search_response.results
    
    def hybrid_search(self, query: str, doc_results: int = 3, web_results: int = 2) -> Dict[str, Any]:
        """Perform hybrid search combining documents and web results"""
        # Search documents
        doc_matches = self.search_documents(query, doc_results)
        
        # Search web
        web_matches = self.search_web(query, web_results)
        
        return {
            'document_results': doc_matches,
            'web_results': web_matches,
            'total_results': len(doc_matches) + len(web_matches)
        }

# Global instances
_vector_store = None
_rag_system = None

def get_vector_store() -> VectorStore:
    """Get or create vector store instance"""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store

def get_rag_system() -> RAGSystem:
    """Get or create RAG system instance"""
    global _rag_system
    if _rag_system is None:
        vector_store = get_vector_store()
        _rag_system = RAGSystem(vector_store)
    return _rag_system

# Test function
def test_vector_store():
    """Test the vector store functionality"""
    vs = get_vector_store()
    
    # Add some test documents
    test_docs = [
        {
            'content': 'Artificial intelligence is transforming the way we work and live.',
            'metadata': {'topic': 'AI', 'type': 'fact'},
            'filename': 'ai_facts.txt'
        },
        {
            'content': 'Machine learning algorithms can process vast amounts of data quickly.',
            'metadata': {'topic': 'ML', 'type': 'technical'},
            'filename': 'ml_info.txt'
        },
        {
            'content': 'The future of technology depends on sustainable development practices.',
            'metadata': {'topic': 'sustainability', 'type': 'opinion'},
            'filename': 'tech_future.txt'
        }
    ]
    
    # Add documents
    for doc in test_docs:
        vs.add_document(doc['content'], doc['metadata'], doc['filename'])
    
    # Test search
    results = vs.search("artificial intelligence and machine learning", n_results=2)
    
    print(f"Found {len(results)} results:")
    for i, match in enumerate(results, 1):
        print(f"{i}. Score: {match.score:.3f}")
        print(f"   Content: {match.document.content}")
        print(f"   Filename: {match.document.filename}")
        print(f"   Snippet: {match.snippet}")
        print()

if __name__ == "__main__":
    test_vector_store()