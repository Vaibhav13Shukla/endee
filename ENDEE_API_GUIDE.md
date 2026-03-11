# Endee API Usage Guide for The Monk AI

This guide explains how Endee is used in the current codebase and how to interact with it.

---

## 1. Client Initialization

### Setup
```python
from config.config import Config
import endee
from endee import Precision

# Initialize Endee client
client = endee.Endee()
client.set_base_url(f"{Config.ENDEE_HOST}/api/v1")
```

**Configuration (from config.py):**
```python
ENDEE_HOST = os.getenv("ENDEE_HOST", "http://localhost:8080")
ENDEE_API_PREFIX = os.getenv("ENDEE_API_PREFIX", "/api/v1")
ENDEE_INDEX_NAME = os.getenv("ENDEE_INDEX_NAME", "monk_ai_knowledge")
```

---

## 2. Index Creation

### Create Index
```python
async def initialize_vectorstore(self):
    try:
        # List existing indexes
        indexes = self.client.list_indexes()
        index_names = [idx['name'] for idx in indexes.get('indexes', [])]

        # Create if doesn't exist
        if self.index_name not in index_names:
            self.client.create_index(
                name=self.index_name,
                dimension=384,                      # all-MiniLM-L6-v2 embedding size
                space_type='cosine',                # Distance metric
                precision=Precision.FLOAT32         # Quantization level
            )
            logger.info(f"Index '{self.index_name}' created successfully")
        
        # Get index reference
        self._index = self.client.get_index(name=self.index_name)
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error initializing vector store: {e}")
        return {"error": str(e)}
```

### Index Parameters
| Parameter | Value | Description |
|-----------|-------|-------------|
| `name` | "monk_ai_knowledge" | Unique index identifier |
| `dimension` | 384 | Vector size (matches embedding model) |
| `space_type` | "cosine" | Distance metric for similarity |
| `precision` | FLOAT32 | Quantization level (BINARY, INT8, INT16, FLOAT16, FLOAT32) |

---

## 3. Data Ingestion (Upsert)

### Add Documents
```python
async def add_documents(self, documents: List[Document], batch_size: int = 50):
    """Add documents to Endee vector store"""
    try:
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            vectors = []

            for doc in batch:
                # Generate embedding for document
                embedded_vector = self.embedding_model.embed_query(doc.page_content)

                # Combine metadata with content
                metadata_dict = dict(doc.metadata)
                metadata_dict["page_content"] = doc.page_content

                # Prepare vector object
                vectors.append({
                    "id": str(uuid.uuid4()),
                    "vector": embedded_vector,  # 384-dimensional vector
                    "meta": metadata_dict       # Metadata for retrieval
                })

            # Upsert batch to Endee
            self.index.upsert(vectors)
            logger.info(f"Added batch {i // batch_size + 1}")

    except Exception as e:
        logger.error(f"Error adding documents: {e}")
        raise
```

### Vector Format
```python
{
    "id": "uuid-string",           # Unique identifier
    "vector": [0.2, 0.15, ...],   # 384-dimensional embedding
    "meta": {                       # Metadata object
        "book_name": "Bhagavad Gita",
        "chapter": "Chapter 2",
        "verse_number": "47",
        "page_content": "Full text..."
    }
}
```

### Metadata Structure
All documents store metadata including:
- `book_name` - Source scripture (e.g., "Bhagavad Gita")
- `chapter` - Chapter or section
- `verse_number` - Verse or text ID
- `page_content` - Full text (stored in metadata for retrieval)
- Any other custom fields from source

---

## 4. Vector Search

### Similarity Search
```python
async def similarity_search(self, query: str, k: int = Config.TOP_K_RETRIEVAL) -> List[Document]:
    """Perform similarity search"""
    try:
        # Embed the query using same model as documents
        query_vector = self.embedding_model.embed_query(query)

        # Search Endee index
        results = self.index.query(
            vector=query_vector,
            top_k=k                    # Return top K similar vectors
        )

        # Convert results to LangChain Documents
        documents = []
        for result in results:
            metadata = result.get('meta', {})
            # Extract content from metadata
            page_content = metadata.pop("page_content", "")

            documents.append(Document(
                page_content=page_content,
                metadata=metadata
            ))

        return documents

    except Exception as e:
        logger.error(f"Error in similarity search: {e}")
        raise
```

### Search Parameters
| Parameter | Value | Description |
|-----------|-------|-------------|
| `vector` | [float] | 384-dim query embedding |
| `top_k` | 15 (default) | Number of results to return |

### Search Result Format
```python
{
    'id': 'vector-id',
    'score': 0.87,                  # Cosine similarity score
    'meta': {
        'book_name': 'Bhagavad Gita',
        'chapter': 'Chapter 2',
        'page_content': 'Verse text...'
    }
}
```

---

## 5. Re-ranking Pipeline

### Combined Search & Re-rank
```python
async def search_and_rerank(self, query: str) -> List[Dict[str, Any]]:
    """Combined search and rerank pipeline"""
    try:
        # Step 1: Initial BM25/Dense retrieval
        initial_results = await self.similarity_search(query, Config.TOP_K_RETRIEVAL)
        
        # Step 2: Re-rank with CrossEncoder
        return self.rerank_documents(query, initial_results, Config.TOP_K_RERANK)
        
    except Exception as e:
        logger.error(f"Error in search and rerank: {e}")
        raise

def rerank_documents(self, query: str, documents: List[Document], 
                     top_k: int = Config.TOP_K_RERANK) -> List[Dict[str, Any]]:
    """Re-rank documents using cross-encoder"""
    try:
        # Create query-document pairs
        pairs = [(query, doc.page_content) for doc in documents]
        
        # Score with CrossEncoder
        scores = self.reranker.predict(pairs)

        # Create result objects with scores
        results = [
            {
                'content': doc.page_content,
                'metadata': doc.metadata,
                'score': float(score),
                'rank': i + 1
            }
            for i, (doc, score) in enumerate(zip(documents, scores))
        ]

        # Sort by score descending
        results = sorted(results, key=lambda x: x['score'], reverse=True)
        
        # Return top-k
        return results[:top_k]

    except Exception as e:
        logger.error(f"Error in reranking: {e}")
        # Fallback to unranked results
        return [...]
```

### Re-ranking Flow
```
Initial Search (Endee)
├── Returns: 15 most similar documents (fast vector search)
└── Scores: Cosine similarity (0-1)
            ↓
Re-ranking (CrossEncoder)
├── Re-scores the 15 documents
├── Uses: cross-encoder/ms-marco-MiniLM-L-6-v2
└── Returns: Top 5 most relevant documents
            ↓
LLM Pipeline (Groq)
└── Generates answer based on top 5 results
```

---

## 6. Index Management

### List All Indexes
```python
indexes = self.client.list_indexes()
# Returns: {'indexes': [{'name': 'monk_ai_knowledge', 'total_elements': 5234, ...}]}
```

### Get Index Statistics
```python
async def get_collection_stats(self) -> Dict[str, Any]:
    """Get statistics about the vector store"""
    try:
        indexes = self.client.list_indexes()
        index_list = indexes.get('indexes', [])

        for idx in index_list:
            if idx['name'] == self.index_name:
                return {
                    "index_name": self.index_name,
                    "total_documents": idx.get("total_elements", 0),
                    "embedding_model": Config.EMBEDDING_MODEL,
                    "reranker_model": Config.RERANKER_MODEL
                }
        
        return {"error": f"Index '{self.index_name}' not found"}

    except Exception as e:
        logger.error(f"Error getting collection stats: {e}")
        return {"error": str(e)}
```

### Reset Index
```python
async def reset_vectorstore(self):
    """Delete the existing Endee index and reset"""
    try:
        self.client.delete_index(name=self.index_name)
        logger.warning(f"Index '{self.index_name}' deleted")
        self._index = None
        
        # Recreate
        await self.initialize_vectorstore()

    except Exception as e:
        logger.error(f"Error resetting vector store: {e}")
        raise
```

---

## 7. Complete RAG Pipeline

### Full Query Processing
```python
class RAGPipeline:
    async def process_query(self, query_request: QueryRequest, user_id: str) -> QueryResponse:
        """Complete RAG pipeline"""
        try:
            # Initialize vector store
            await self.initialize()
            
            # Step 1: Retrieve & Rerank
            relevant_docs = await self.vector_store.search_and_rerank(query_request.query)
            
            # Step 2: Generate Answer with LLM
            llm_response = await self.llm_service.generate_response(
                query_request.query, 
                relevant_docs,        # Top 5 re-ranked documents
                query_request.mode
            )
            
            # Step 3: Translate to Hindi
            hindi_translation = await self.llm_service.translate_to_hindi(
                llm_response["response"]
            )
            
            # Step 4: Save to Chat History
            session_id = await self.handle_chat_session(
                user_id=user_id,
                session_id=query_request.session_id,
                query=query_request.query,
                response=llm_response["response"],
                mode=query_request.mode,
                citations=llm_response["citations"],
                hindi_translation=hindi_translation
            )
            
            # Return complete response
            return QueryResponse(
                answer=llm_response["response"],
                hindi_translation=hindi_translation,
                citations=llm_response["citations"],
                recommendations=llm_response["recommendations"],
                session_id=session_id
            )
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            raise
```

### Query Flow Diagram
```
User Query
    ↓
[1] Embed Query (HuggingFace embeddings)
    ↓
[2] Similarity Search (Endee)
    ├── Returns 15 similar documents
    
[3] Re-rank (CrossEncoder)
    └── Returns top 5 refined documents
    
[4] Generate Answer (Groq LLM)
    ├── Uses: llama-3.3-70b-versatile
    └── Returns: Answer + Citations + Recommendations
    
[5] Translate (Google Translate)
    └── Hindi translation
    
[6] Save Chat Session (MongoDB)
    └── Store conversation history
    
Response to User
```

---

## 8. Configuration Parameters

### Vector Store Parameters
```python
# From config.py
EMBEDDING_MODEL = "all-MiniLM-L6-v2"      # 384-dim embeddings
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
CHUNK_SIZE = 700                           # Document chunk size
CHUNK_OVERLAP = 140                        # Chunk overlap for context
TOP_K_RETRIEVAL = 15                       # Initial retrieval count
TOP_K_RERANK = 5                           # Final result count
```

### Endee Server Parameters
```python
# From .env
ENDEE_HOST = "http://localhost:8080"
ENDEE_API_PREFIX = "/api/v1"
ENDEE_INDEX_NAME = "monk_ai_knowledge"
```

---

## 9. Example: Using Endee Directly

### Python Example
```python
import endee
from endee import Precision

# Connect to Endee
client = endee.Endee()
client.set_base_url("http://localhost:8080/api/v1")

# Create index
client.create_index(
    name="test_index",
    dimension=384,
    space_type="cosine",
    precision=Precision.FLOAT32
)

# Get index
index = client.get_index("test_index")

# Upsert vectors
vectors = [
    {
        "id": "doc1",
        "vector": [0.1, 0.2, ..., 0.3],  # 384 dimensions
        "meta": {"text": "Some scripture text", "source": "Bhagavad Gita"}
    }
]
index.upsert(vectors)

# Query
results = index.query(vector=[0.15, 0.25, ..., 0.35], top_k=5)
for result in results:
    print(f"ID: {result['id']}, Score: {result['score']}, Meta: {result['meta']}")

# List indexes
indexes = client.list_indexes()
print(indexes)

# Delete index
client.delete_index("test_index")
```

---

## 10. Troubleshooting

### Connection Issues
```python
# Check if Endee server is running
import requests
try:
    response = requests.get("http://localhost:8080/health")
    if response.status_code == 200:
        print("Endee server is running")
except requests.ConnectionError:
    print("Cannot connect to Endee server")
```

### Index Not Found
```python
# List all indexes
indexes = self.client.list_indexes()
print("Available indexes:", [idx['name'] for idx in indexes['indexes']])

# Recreate if missing
await self.initialize_vectorstore()
```

### Search Not Returning Results
```python
# Check if vectors are in index
stats = await self.get_collection_stats()
print(f"Total documents: {stats['total_documents']}")

# Ensure embeddings are correct dimension
test_query = "test query"
embedding = self.embedding_model.embed_query(test_query)
print(f"Embedding dimension: {len(embedding)}")  # Should be 384
```

---

## References

- **Endee Docs:** https://endee.ai/docs
- **HuggingFace Embeddings:** https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- **CrossEncoder:** https://huggingface.co/cross-encoders/ms-marco-MiniLM-L-6-v2

---

*Generated: March 10, 2026*
