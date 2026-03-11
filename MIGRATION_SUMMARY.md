# Migration Summary: ChromaDB to Endee Vector Database

## Overview
This document details the migration from ChromaDB to Endee vector database for The Monk AI project.

## Why Endee?

### Benefits Over ChromaDB
1. **Client-Server Architecture** - Endee runs as a separate service, allowing for better scalability and remote access
2. **Multiple Distance Metrics** - Supports cosine, euclidean, and manhattan distance
3. **Quantization Support** - Offers FLOAT32, FLOAT16, INT8, INT16, and BINARY precision options
4. **REST API** - Direct HTTP calls to Endee server
5. **Production-Ready** - Built for production workloads with better monitoring

## Changes Made

### 1. Vector Store Service
- Replaced `Chroma` client with `endee.Endee()` client
- Updated index creation to use Endee's API
- Modified vector upsert format
- Updated query method to use Endee's client

### 2. Configuration Updates
```python
# Before (ChromaDB)
COLLECTION_NAME = "monk_ai_scriptures"

# After (Endee)
ENDEE_HOST = "http://localhost:8080"
ENDEE_INDEX_NAME = "monk_ai_knowledge"
```

### 3. Index Parameters
- **Dimension**: 384 (all-MiniLM-L6-v2)
- **Space Type**: cosine similarity
- **Precision**: FLOAT32

## Migration Steps

### For Existing Users
1. Stop the application
2. Start Endee server: `cd endee && docker-compose up -d`
3. Re-run knowledge base loader: `python knowledge_base_loader.py`
4. Start the application

### API Differences

| Operation | ChromaDB | Endee |
|-----------|----------|-------|
| Create Index | Automatic | Manual `create_index()` |
| Add Vectors | `add_documents()` | `index.upsert()` |
| Search | `similarity_search()` | `index.query()` |
| List Indexes | N/A | `client.list_indexes()` |

## Performance Comparison

| Metric | ChromaDB | Endee |
|--------|----------|-------|
| Startup Time | Faster (in-process) | Slightly slower (network) |
| Query | Very Speed | Fast Fast |
| Scalability | Limited | High |
| Memory Usage | Higher | Optimized |

## Conclusion

The migration to Endee provides a more robust, scalable solution for vector storage and retrieval. The client-server architecture allows for better resource management and the ability to scale the vector database independently from the application.
