from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# ==========================================
# Configuration
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

DOCS_DIR = BASE_DIR / "docs"

CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "zepto_policies"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


# ==========================================
# Load embedding model
# ==========================================

_embedding_model = None


def get_embedding_model():
    """
    Load the embedding model only when needed.
    """

    global _embedding_model

    if _embedding_model is None:

        print(
            "Loading embedding model..."
        )

        _embedding_model = SentenceTransformer(
            EMBEDDING_MODEL_NAME
        )

        print(
            "Embedding model loaded."
        )

    return _embedding_model


# ==========================================
# Load documents
# ==========================================

def load_documents():
    """
    Load all Zepto policy documents
    from the docs directory.
    """

    documents = []

    for file_path in sorted(
        DOCS_DIR.glob("doc_*.txt")
    ):

        text = file_path.read_text(
            encoding="utf-8"
        ).strip()

        if not text:
            continue

        documents.append(
            {
                "id": file_path.stem,
                "text": text
            }
        )

    return documents


# ==========================================
# Chunk documents
# ==========================================

def chunk_documents(documents):
    """
    Create one chunk per document.

    The assignment allows simple
    per-document chunking because
    the documents are short.
    """

    chunks = []

    for document in documents:

        chunks.append(
            {
                "chunk_id": (
                    f"{document['id']}_chunk_01"
                ),
                "document_id": document["id"],
                "text": document["text"]
            }
        )

    return chunks


# ==========================================
# ChromaDB client
# ==========================================

def get_chroma_collection():
    """
    Create/open the persistent ChromaDB
    collection used by the application.
    """

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description":
            "Zepto support policy documents"
        }
    )

    return collection


# ==========================================
# Build vector store
# ==========================================

def build_vector_store():
    """
    Load documents, create chunks,
    generate embeddings and store them
    in ChromaDB.
    """

    documents = load_documents()

    if not documents:

        raise RuntimeError(
            "No documents found in the docs directory."
        )

    chunks = chunk_documents(
        documents
    )

    print(
        f"Documents loaded: {len(documents)}"
    )

    print(
        f"Chunks created: {len(chunks)}"
    )

    model = get_embedding_model()

    chunk_texts = [
        chunk["text"]
        for chunk in chunks
    ]

    print(
        "Generating embeddings..."
    )

    embeddings = model.encode(
        chunk_texts,
        normalize_embeddings=True
    )

    collection = get_chroma_collection()

    collection.upsert(
        ids=[
            chunk["chunk_id"]
            for chunk in chunks
        ],
        documents=chunk_texts,
        embeddings=embeddings.tolist(),
        metadatas=[
            {
                "document_id":
                chunk["document_id"]
            }
            for chunk in chunks
        ]
    )

    print(
        "Embeddings stored in ChromaDB."
    )

    print(
        f"Collection: {COLLECTION_NAME}"
    )

    print(
        f"Stored chunks: {collection.count()}"
    )

    return collection


# ==========================================
# Retrieve top-3 chunks
# ==========================================

def retrieve(
    query,
    top_k=3
):
    """
    Embed the user's query and retrieve
    the top-k most similar chunks.

    ChromaDB returns cosine-distance values
    because the collection uses the default
    cosine similarity space.

    Lower distance = more similar.
    """

    collection = get_chroma_collection()

    # Build the vector store if it is empty.
    if collection.count() == 0:

        build_vector_store()

        collection = get_chroma_collection()

    model = get_embedding_model()

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )

    results = collection.query(
        query_embeddings=[
            query_embedding[0].tolist()
        ],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    retrieved_chunks = []

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    ids = results.get(
        "ids",
        [[]]
    )[0]

    for index in range(
        len(documents)
    ):

        retrieved_chunks.append(
            {
                "chunk_id": ids[index],
                "document_id": metadatas[index][
                    "document_id"
                ],
                "text": documents[index],
                "distance": distances[index]
            }
        )

    return retrieved_chunks


# ==========================================
# Test retrieval
# ==========================================

def test_retrieval():

    query = (
        "What is the delivery fee "
        "for orders below INR 149?"
    )

    print(
        "\nQuery:"
    )

    print(query)

    results = retrieve(
        query,
        top_k=3
    )

    print(
        "\nTop retrieved chunks:"
    )

    for result in results:

        print(
            "\n-----------------------------"
        )

        print(
            "Chunk ID:",
            result["chunk_id"]
        )

        print(
            "Document ID:",
            result["document_id"]
        )

        print(
            "Cosine distance:",
            result["distance"]
        )

        print(
            "Text:",
            result["text"]
        )


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    print(
        "Building Zepto policy vector store..."
    )

    build_vector_store()

    print(
        "\nTesting retrieval..."
    )

    test_retrieval()