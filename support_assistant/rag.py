from retriever import SupportRetriever
from llm import LLMClient


CONFIDENCE_THRESHOLD = 0.15


def build_context(results):

    context_parts = []

    for result in results:

        source = result["source"]
        text = result["text"]
        confidence = result["confidence"]

        context_parts.append(
            f"Source: {source}\n"
            f"Confidence: {confidence}\n"
            f"Information: {text}"
        )

    return "\n\n".join(context_parts)


def build_conversation_history(history):

    if not history:
        return "No previous conversation."

    history_parts = []

    for turn in history:

        role = turn["role"]
        content = turn["content"]

        history_parts.append(
            f"{role}: {content}"
        )

    return "\n".join(history_parts)


def build_search_query(query, history):

    if not history:
        return query

    previous_customer_question = ""

    for turn in reversed(history):

        if turn["role"] == "Customer":
            previous_customer_question = turn["content"]
            break

    if previous_customer_question:

        return (
            f"{previous_customer_question} "
            f"Current follow-up: {query}"
        )

    return query


def main():

    # Create retriever
    retriever = SupportRetriever()

    # Create LLM client
    llm = LLMClient()

    # Store conversation history
    history = []

    print("===================================")
    print("       SupportAI Helpdesk Agent")
    print("===================================")
    print("Type 'exit' to stop the assistant.")

    while True:

        # Get question from user
        query = input(
            "\nCustomer: "
        )

        # Exit
        if query.lower() == "exit":

            print(
                "\nSupportAI: Goodbye!"
            )

            break

        # Empty question
        if not query.strip():

            print(
                "SupportAI: Please enter a question."
            )

            continue

        # Create a contextual search query
        search_query = build_search_query(
            query,
            history
        )

        # Retrieve relevant information
        results = retriever.search(
            search_query,
            top_k=3
        )

        # Get strongest match
        best_confidence = results[0]["confidence"]

        print(
            f"\nBest confidence: "
            f"{best_confidence}"
        )

        # Confidence check
        if best_confidence < CONFIDENCE_THRESHOLD:

            print("\nSupportAI:")

            print(
                "I don't have enough information "
                "in the support documents to answer "
                "your question."
            )

            print(
                "\nThis question will be "
                "escalated to human support."
            )

            continue

        # Build context
        context = build_context(
            results
        )

        # Build conversation history
        conversation_history = (
            build_conversation_history(
                history
            )
        )

        # Create LLM prompt
        prompt = f"""
You are a helpful customer support assistant.

Answer the customer's question using only the
information provided in the context.

Rules:
1. Do not invent information.
2. Do not use outside knowledge.
3. Give a clear and concise answer.
4. If the context does not contain enough information,
   say that you do not have enough information.
5. Use previous conversation when it helps understand
   the customer's current question.
6. Do not mention that you are an AI model.

Previous conversation:
{conversation_history}

Context:
{context}

Current customer question:
{query}
"""

        # Generate answer
        answer = llm.generate(
            prompt
        )

        # Display answer
        print("\nSupportAI:")
        print(answer)

        # Display sources
        print("\nSources:")

        for result in results:

            print(
                "-",
                result["source"]
            )

        # Save customer question
        history.append(
            {
                "role": "Customer",
                "content": query
            }
        )

        # Save assistant answer
        history.append(
            {
                "role": "SupportAI",
                "content": answer
            }
        )


if __name__ == "__main__":
    main()