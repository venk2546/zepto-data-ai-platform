from pathlib import Path

from sentence_transformers import SentenceTransformer
import chromadb


DOCS_DIR = Path(__file__).parent / "docs"

CHROMA_DIR = Path(__file__).parent / "chroma_db"


def load_documents():
    documents = []

    for file_path in DOCS_DIR.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        documents.append({
            "source": file_path.name,
            "text": text
        })

    return documents


def chunk_text(text, chunk_size=300, overlap=50):
    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def main():

    # --------------------------------
    # STEP 1: Load documents
    # --------------------------------

    documents = load_documents()

    print("Number of documents:", len(documents))


    # --------------------------------
    # STEP 2: Create chunks
    # --------------------------------

    all_chunks = []

    for document in documents:

        chunks = chunk_text(
            document["text"]
        )

        print(
            f"{document['source']} -> "
            f"{len(chunks)} chunks"
        )

        for chunk in chunks:

            all_chunks.append({
                "source": document["source"],
                "text": chunk
            })


    print("\nTotal chunks:", len(all_chunks))


    # --------------------------------
    # STEP 3: Load embedding model
    # --------------------------------

    print("\nLoading embedding model...")

    model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

    print(
        "Embedding model loaded successfully."
    )


    # --------------------------------
    # STEP 4: Generate embeddings
    # --------------------------------

    texts = [
        chunk["text"]
        for chunk in all_chunks
    ]

    embeddings = model.encode(
        texts
    )


    print(
        "\nNumber of embeddings:",
        len(embeddings)
    )

    print(
        "Embedding dimension:",
        embeddings.shape[1]
    )


    # --------------------------------
    # STEP 5: Connect to ChromaDB
    # --------------------------------

    print("\nConnecting to ChromaDB...")

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    collection = client.get_or_create_collection(
        name="zepto_support"
    )

    print(
        "ChromaDB collection ready."
    )


    # --------------------------------
    # STEP 6: Prepare IDs
    # --------------------------------

    ids = [
        f"chunk_{i}"
        for i in range(len(all_chunks))
    ]


    # --------------------------------
    # STEP 7: Prepare metadata
    # --------------------------------

    metadatas = [
        {
            "source": chunk["source"]
        }
        for chunk in all_chunks
    ]


    # --------------------------------
    # STEP 8: Store everything
    # --------------------------------

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )


    print(
        "\nData successfully stored in ChromaDB."
    )

    print(
        "Total records in ChromaDB:",
        collection.count()
    )


if __name__ == "__main__":
    main()