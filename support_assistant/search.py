from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


CHROMA_DIR = Path(__file__).parent / "chroma_db"


def main():

    # Load embedding model
    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

    # Connect to existing ChromaDB
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    # Open our collection
    collection = client.get_collection(
        name="zepto_support"
    )

    # User question
    query = "How can I return an item?"

    # Convert question into an embedding
    query_embedding = model.encode(
        [query]
    ).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3
    )

    print("User question:")
    print(query)

    print("\nRetrieved documents:")

    for i, document in enumerate(
        results["documents"][0]
    ):
        print("\nResult", i + 1)
        print("Source:", results["metadatas"][0][i]["source"])
        print("Text:", document)


if __name__ == "__main__":
    main()