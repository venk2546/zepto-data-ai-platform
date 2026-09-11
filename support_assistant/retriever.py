from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


CHROMA_DIR = Path(__file__).parent / "chroma_db"


class SupportRetriever:

    def __init__(self):

        # Load the same embedding model
        # that we used during ingestion.
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        # Connect to the persistent ChromaDB.
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR)
        )

        # Open our existing collection.
        self.collection = self.client.get_collection(
            name="zepto_support"
        )

    def search(self, query, top_k=3):

        # Convert the user's question into an embedding.
        query_embedding = self.model.encode(
            [query]
        ).tolist()

        # Search ChromaDB.
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )

        retrieved_documents = []

        for i, document in enumerate(
            results["documents"][0]
        ):

            distance = results["distances"][0][i]

            # Convert distance into a simple
            # confidence score.
            confidence = max(
                0.0,
                1.0 - distance
            )

            retrieved_documents.append({
                "text": document,
                "source": results["metadatas"][0][i]["source"],
                "confidence": round(
                    confidence,
                    4
                )
            })

        return retrieved_documents


def main():

    retriever = SupportRetriever()

    query = "What should I do if my item is damaged?"

    results = retriever.search(
        query,
        top_k=3
    )

    print("User question:")
    print(query)

    print("\nRetrieved information:")

    for i, result in enumerate(results):

        print(f"\nResult {i + 1}")
        print("Source:", result["source"])
        print("Confidence:", result["confidence"])
        print("Text:", result["text"])


if __name__ == "__main__":
    main()