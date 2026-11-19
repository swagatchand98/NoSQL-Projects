# Real Atlas and local comparison

Set MONGO_URI_ATLAS to a disposable lab database connection with search-index privileges. The code uses `SearchIndexModel(type="vectorSearch")`, a `vector` field with 384 dimensions and cosine similarity, and `$vectorSearch` as the first aggregation stage. It waits for queryable index state. The embedding model is sentence-transformers/all-MiniLM-L6-v2; initial model download needs internet.

Official MongoDB documentation describes HNSW ANN, `numCandidates`, `limit`, and `exact` ENN. It does not document a native IVF index selection in this API. The genuine Atlas retrieval remains separate from the FAISS HNSW/IVF comparison. Local numbers do not satisfy an Atlas-native IVF measurement requirement.

The script records the actual created index definition. Deployment feature compatibility can only be verified after credentials are supplied; no successful Atlas result is claimed before then.

https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-stage/
https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-type/
