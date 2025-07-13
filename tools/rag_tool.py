"""
RAG Retriever Tool for the MSVA project.
Uses vector search to find similar MVPs and relevant information.
"""

import os
import json
import numpy as np
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import asyncio
from dotenv import load_dotenv
from .base_tool import BaseTool

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

class RAGRetrieverTool(BaseTool):
    """
    Tool for retrieving similar MVPs and relevant information using vector search.
    Supports both FAISS and ChromaDB.
    """
    
    def __init__(
        self, 
        db_type: str = "faiss",  # "faiss" or "chroma"
        collection_name: str = "mvp_examples",
        embedding_dim: int = 1536,  # Default for OpenAI embeddings
        verbose: bool = False,
        embedding_function: Optional[Any] = None
    ):
        super().__init__(
            name="RAG Retriever Tool",
            description="Retrieves similar MVPs and relevant information using vector search",
            verbose=verbose
        )
        self.db_type = db_type.lower()
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim
        
        # Load environment variables
        load_dotenv()
        
        # Get persistence directory from environment variables
        self.persistence_dir = os.getenv("VECTOR_DB_PERSISTENCE_DIR", "./data/vector_db")
        Path(self.persistence_dir).mkdir(parents=True, exist_ok=True)
        
        # Embedding function (this would typically be provided)
        self.embedding_function = embedding_function
        
        # Initialize the vector store
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize the vector store based on the selected database type."""
        if self.db_type == "faiss":
            if not FAISS_AVAILABLE:
                raise ImportError("FAISS is not installed. Install it with 'pip install faiss-cpu' or 'pip install faiss-gpu'")
            self._initialize_faiss()
        elif self.db_type == "chroma":
            if not CHROMA_AVAILABLE:
                raise ImportError("ChromaDB is not installed. Install it with 'pip install chromadb'")
            self._initialize_chroma()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def _initialize_faiss(self):
        """Initialize FAISS vector store."""
        self.index_file = os.path.join(self.persistence_dir, f"{self.collection_name}.index")
        self.metadata_file = os.path.join(self.persistence_dir, f"{self.collection_name}.json")
        
        # Check if the index exists, if not, create a new one
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            self.log(f"Loading existing FAISS index from {self.index_file}")
            self.index = faiss.read_index(self.index_file)
            with open(self.metadata_file, 'r') as f:
                self.documents = json.load(f)
        else:
            self.log(f"Creating new FAISS index with dimension {self.embedding_dim}")
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.documents = []
            
            # Add some example documents if we're creating a new index
            self._add_example_documents()
    
    def _initialize_chroma(self):
        """Initialize ChromaDB vector store."""
        persistent_directory = os.path.join(self.persistence_dir, "chroma_db")
        
        # Create Chroma client with persistence
        self.client = chromadb.PersistentClient(path=persistent_directory)
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            self.log(f"Loaded existing ChromaDB collection '{self.collection_name}'")
        except:
            self.log(f"Creating new ChromaDB collection '{self.collection_name}'")
            
            # Determine embedding function for Chroma
            embedding_fn = None
            if self.embedding_function:
                embedding_fn = self.embedding_function
                
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=embedding_fn
            )
            
            # Add some example documents if we're creating a new collection
            self._add_example_documents()
    
    def _add_example_documents(self):
        """Add example documents to the vector store for demonstration purposes."""
        # Example MVP data to preload
        examples = [
            {
                "id": "example_1",
                "title": "Meal Planning App MVP",
                "description": "A mobile app that helps users plan their weekly meals, create shopping lists, and find recipes based on ingredients they have.",
                "features": [
                    "Recipe search by ingredient",
                    "Weekly meal calendar", 
                    "Automatic shopping list generation",
                    "Dietary preference filters"
                ],
                "tech_stack": ["React Native", "Node.js", "MongoDB", "Express"],
                "development_time": "3-4 months",
                "cost_estimate": "$15,000 - $25,000",
                "target_audience": "Busy professionals who want to eat healthier"
            },
            {
                "id": "example_2",
                "title": "Freelancer Marketplace MVP",
                "description": "A platform connecting freelancers with clients, featuring project posting, bidding, secure payments, and review system.",
                "features": [
                    "User profiles for freelancers and clients",
                    "Project posting and bidding system",
                    "Secure payment escrow",
                    "Rating and review system"
                ],
                "tech_stack": ["React", "Django", "PostgreSQL", "Stripe API"],
                "development_time": "4-6 months",
                "cost_estimate": "$30,000 - $45,000",
                "target_audience": "Freelancers and small businesses"
            },
            {
                "id": "example_3",
                "title": "Local Event Discovery App MVP",
                "description": "A location-based app that helps users discover events happening near them with filtering, recommendations, and social features.",
                "features": [
                    "Location-based event discovery",
                    "Event filtering by category, date, and price",
                    "Save and share favorite events",
                    "Event organizer profiles"
                ],
                "tech_stack": ["Flutter", "Firebase", "Google Maps API"],
                "development_time": "2-3 months",
                "cost_estimate": "$12,000 - $18,000",
                "target_audience": "Young adults looking for local entertainment"
            }
        ]
        
        if self.db_type == "faiss":
            if not self.embedding_function:
                self.log("Warning: No embedding function provided. Using random vectors for examples.")
                for i, example in enumerate(examples):
                    # Create a random vector for demonstration
                    vector = np.random.rand(self.embedding_dim).astype('float32')
                    vector /= np.linalg.norm(vector)  # Normalize
                    
                    # Add to FAISS index
                    self.index.add(np.array([vector]))
                    
                    # Store document
                    self.documents.append({
                        "id": example["id"],
                        "content": example
                    })
                
                # Save the index and metadata
                faiss.write_index(self.index, self.index_file)
                with open(self.metadata_file, 'w') as f:
                    json.dump(self.documents, f)
            else:
                self.log("Embedding function provided. Skipping example document addition.")
        
        elif self.db_type == "chroma":
            if not self.embedding_function:
                self.log("Warning: No embedding function provided. Example documents will be added with auto-generated embeddings.")
            
            # Prepare data for Chroma
            ids = [example["id"] for example in examples]
            documents = [json.dumps(example) for example in examples]
            metadatas = [{"title": example["title"]} for example in examples]
            
            # Add to Chroma collection
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
    
    async def run(self, query: Union[str, List[float]], top_k: int = 3, **kwargs) -> Dict[str, Any]:
        """
        Retrieve similar documents from the vector store.
        
        Args:
            query: Query text or vector
            top_k: Number of results to return
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing search results
        """
        self.log(f"Searching for: {query if isinstance(query, str) else 'vector'}")
        
        try:
            # Convert query to vector if needed
            query_vector = None
            if isinstance(query, str):
                if self.embedding_function:
                    query_vector = await self._get_embedding(query)
                else:
                    return {
                        "status": "error",
                        "message": "No embedding function provided for text queries"
                    }
            else:
                query_vector = query
                
            # Perform search based on the database type
            if self.db_type == "faiss":
                return await self._search_faiss(query_vector, top_k)
            elif self.db_type == "chroma":
                return await self._search_chroma(query, top_k)
                
        except Exception as e:
            self.log(f"Error during search: {str(e)}")
            return {
                "status": "error",
                "message": f"Search failed: {str(e)}"
            }
    
    async def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for text using the provided embedding function.
        """
        if not self.embedding_function:
            raise ValueError("No embedding function provided")
            
        if asyncio.iscoroutinefunction(self.embedding_function):
            return await self.embedding_function(text)
        else:
            return self.embedding_function(text)
    
    async def _search_faiss(self, query_vector: List[float], top_k: int) -> Dict[str, Any]:
        """Search using FAISS index."""
        # Ensure query vector is numpy array with correct shape and type
        query_vector_np = np.array([query_vector]).astype('float32')
        
        # Perform search
        distances, indices = self.index.search(query_vector_np, top_k)
        
        # Format results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.documents):  # -1 indicates no match
                doc = self.documents[idx]
                results.append({
                    "id": doc.get("id", f"doc_{idx}"),
                    "content": doc.get("content", {}),
                    "score": float(distances[0][i])
                })
                
        return {
            "status": "success",
            "results": results
        }
    
    async def _search_chroma(self, query: Union[str, List[float]], top_k: int) -> Dict[str, Any]:
        """Search using ChromaDB collection."""
        # Perform search
        if isinstance(query, str):
            query_results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
        else:
            query_results = self.collection.query(
                query_embeddings=[query],
                n_results=top_k
            )
        
        # Format results
        results = []
        if query_results and "documents" in query_results and query_results["documents"]:
            documents = query_results["documents"][0]  # First query results
            ids = query_results.get("ids", [["unknown"]])[0]
            distances = query_results.get("distances", [[0.0]])[0]
            
            for i, doc_str in enumerate(documents):
                try:
                    content = json.loads(doc_str)
                except json.JSONDecodeError:
                    content = {"text": doc_str}
                    
                results.append({
                    "id": ids[i] if i < len(ids) else f"doc_{i}",
                    "content": content,
                    "score": float(distances[i]) if i < len(distances) else 0.0
                })
                
        return {
            "status": "success",
            "results": results
        }
    
    async def add_document(
        self, 
        document: Dict[str, Any], 
        document_id: Optional[str] = None,
        embedding: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Add a document to the vector store.
        
        Args:
            document: Document content
            document_id: Document ID (optional)
            embedding: Pre-computed embedding (optional)
            
        Returns:
            Dictionary with status information
        """
        try:
            doc_id = document_id or f"doc_{len(self.documents)}"
            
            # Get embedding if not provided
            if embedding is None:
                if self.embedding_function:
                    document_text = document.get("description", str(document))
                    embedding = await self._get_embedding(document_text)
                else:
                    return {
                        "status": "error",
                        "message": "No embedding function provided and no pre-computed embedding"
                    }
            
            # Add document based on the database type
            if self.db_type == "faiss":
                # Add to FAISS index
                vector = np.array([embedding]).astype('float32')
                self.index.add(vector)
                
                # Store document
                self.documents.append({
                    "id": doc_id,
                    "content": document
                })
                
                # Save the index and metadata
                faiss.write_index(self.index, self.index_file)
                with open(self.metadata_file, 'w') as f:
                    json.dump(self.documents, f)
                    
            elif self.db_type == "chroma":
                # Prepare for Chroma
                document_json = json.dumps(document)
                metadata = {"title": document.get("title", doc_id)}
                
                # Add to Chroma
                self.collection.add(
                    ids=[doc_id],
                    documents=[document_json],
                    metadatas=[metadata],
                    embeddings=[embedding] if embedding else None
                )
                
            return {
                "status": "success",
                "message": f"Document added with ID: {doc_id}"
            }
                
        except Exception as e:
            self.log(f"Error adding document: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to add document: {str(e)}"
            }
    
    async def retrieve(self, query: Union[str, List[float]], **kwargs) -> Dict[str, Any]:
        """
        Alias for run method to provide a more intuitive API.
        
        Args:
            query: Query text or vector
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing search results
        """
        return await self.run(query=query, **kwargs)
