import os
from typing import TypedDict, List

from langgraph.graph import StateGraph, END
from openai import OpenAI

import json
from pydantic import BaseModel, Field, ValidationError

# Works both when imported as a package and when run directly
try:
    from .retriever import SupportRetriever
except ImportError:
    from retriever import SupportRetriever


# ---------------------------------------------------------
# STEP 1 — LangGraph State
# ---------------------------------------------------------

class SupportState(TypedDict, total=False):
    query: str
    intent: str
    context: str
    sources: List[str]
    confidence: float
    answer: str

class LLMResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: float = Field(ge=0.0, le=1.0)


# ---------------------------------------------------------
# STEP 2 — Configuration
# ---------------------------------------------------------

# MOCK_LLM=1 is the REQUIRED graded baseline.
# If MOCK_LLM is not present, it defaults to "1".
MOCK_LLM = os.getenv("MOCK_LLM", "1")


POLICY_KEYWORDS = [
    "delivery",
    "return",
    "refund",
    "membership",
    "tracking",
    "cancel",
    "gift card",
    "support hours",
]


retriever = SupportRetriever()


# ---------------------------------------------------------
# STEP 3 — Structured prompt for optional real LLM
# ---------------------------------------------------------

PROMPT_TEMPLATE = """
ROLE:
You are Zepto's customer-support assistant.

CONTEXT:
Use only the Zepto policy information supplied below.

{context}

TASK:
Answer the customer's question accurately using the provided context.

Customer question:
{query}

FORMAT:
Give a concise and helpful customer-support answer.

LENGTH:
Keep the response under 150 words.

NEGATIVE CONSTRAINT:
Do not answer using information that is not present in the
provided Zepto policy context.

FEW-SHOT EXAMPLE:

Customer question:
How can I track my order?

Context:
Every Zepto order shows a live rider-tracking map from the
moment it is packed until delivery.

Answer:
You can track your Zepto order using the Track Order screen,
where the live rider-tracking map and estimated delivery time
are displayed.
"""


# ---------------------------------------------------------
# STEP 4 — Optional real LLM helper
# ---------------------------------------------------------

def call_real_llm(prompt: str) -> str:
    """
    Optional extension.

    This function is called only when MOCK_LLM=0.
    The graded baseline does not require an API key.
    """

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        return (
            "Real LLM mode was requested, but "
            "OPENROUTER_API_KEY is not configured."
        )

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.choices[0].message.content

def call_real_llm_with_validation(prompt: str, sources: list[str]) -> LLMResponse:
    """
    Call the real LLM and validate its JSON output.

    If validation fails, retry up to 2 additional times
    with a corrective instruction.
    """

    corrective_instruction = """
Return ONLY valid JSON in exactly this format:

{
  "answer": "string",
  "sources": ["source1", "source2"],
  "confidence": 0.0
}

Rules:
- answer must be a string
- sources must be a list of strings
- confidence must be a number between 0 and 1
- Do not include markdown
- Do not include explanations outside the JSON
"""

    current_prompt = prompt

    for attempt in range(3):
        raw_output = call_real_llm(current_prompt)

        try:
            parsed_output = json.loads(raw_output)

            validated_output = LLMResponse(
                answer=parsed_output["answer"],
                sources=parsed_output.get("sources", sources),
                confidence=parsed_output.get("confidence", 1.0)
            )

            return validated_output

        except (
            json.JSONDecodeError,
            ValidationError,
            KeyError,
            TypeError
        ):

            if attempt < 2:
                current_prompt = (
                    prompt
                    + "\n\n"
                    + corrective_instruction
                    + "\n\nYour previous response was invalid. "
                      "Return the response again using only the required JSON."
                )

    return LLMResponse(
        answer="Error: The real LLM could not produce a valid structured response.",
        sources=[],
        confidence=0.0
    )


# ---------------------------------------------------------
# NODE 1 — classify_intent
# ---------------------------------------------------------

def classify_intent(state: SupportState):
    """
    Classifies the customer question as:

    policy_question
        or
    general_question

    In MOCK_LLM mode this uses the exact keyword-style
    heuristic required by the Capstone.
    """

    query = state["query"]
    query_lower = query.lower()

    # ---------------------------
    # REQUIRED MOCK MODE
    # ---------------------------

    if MOCK_LLM != "0":

        if any(keyword in query_lower for keyword in POLICY_KEYWORDS):
            intent = "policy_question"
        else:
            intent = "general_question"

        return {
            "intent": intent
        }

    # ---------------------------
    # OPTIONAL REAL LLM MODE
    # ---------------------------

    classification_prompt = f"""
Classify the following customer question into exactly one category:

policy_question
general_question

A policy_question concerns Zepto delivery, returns, refunds,
membership, order tracking, cancellation, gift cards,
or customer-support policies.

Question:
{query}

Return only the category name.
"""

    result = call_real_llm(classification_prompt)

    result = result.strip().lower()

    if "policy_question" in result:
        intent = "policy_question"
    else:
        intent = "general_question"

    return {
        "intent": intent
    }


# ---------------------------------------------------------
# Routing function
# ---------------------------------------------------------

def route_intent(state: SupportState):
    """
    LangGraph uses this function to decide which node
    should execute after classify_intent.
    """

    if state["intent"] == "policy_question":
        return "retrieve_and_answer"

    return "direct_answer"


# ---------------------------------------------------------
# NODE 2 — retrieve_and_answer
# ---------------------------------------------------------

def retrieve_and_answer(state: SupportState):
    """
    Retrieves the top relevant chunks from ChromaDB.

    Retrieval runs in BOTH mock and real modes.

    Only answer generation changes depending on MOCK_LLM.
    """

    query = state["query"]

    # Retrieve the top 3 matching chunks.
    results = retriever.search(query, top_k=3)

    # Safety check
    if not results:
        return {
            "context": "",
            "sources": [],
            "confidence": 0.0,
            "answer": "No relevant Zepto policy information was found.",
        }

    # Combine retrieved text
    context_parts = []

    sources = []

    for result in results:

        text = result.get("text", "")

        source = result.get("source", "unknown")

        context_parts.append(text)

        sources.append(source)

    context = "\n\n".join(context_parts)

    # Best retrieval confidence
    best_confidence = max(
        result.get("confidence", 0.0)
        for result in results
    )

    # ---------------------------------------------------------
    # MOCK MODE
    # ---------------------------------------------------------

    if MOCK_LLM == "0":

        top_chunk_snippet = results[0]["text"][:200]

        answer = (
            f"Based on the retrieved context: "
            f"{top_chunk_snippet}"
        )

        confidence = best_confidence

    # ---------------------------------------------------------
    # REAL LLM MODE
    # ---------------------------------------------------------

    else:

        prompt = PROMPT_TEMPLATE.format(
            context=context,
            query=query
        )

        validated_response = call_real_llm_with_validation(
            prompt,
            sources
        )

        answer = validated_response.answer
        sources = validated_response.sources
        confidence = validated_response.confidence

    # ---------------------------------------------------------
    # RETURN UPDATED STATE
    # ---------------------------------------------------------

    return {
        "context": context,
        "sources": sources,
        "confidence": confidence,
        "answer": answer,
    }


# ---------------------------------------------------------
# NODE 3 — direct_answer
# ---------------------------------------------------------

def direct_answer(state: SupportState):
    """
    Handles questions that do not require retrieval.
    """

    query = state["query"]

    # ---------------------------
    # REQUIRED MOCK MODE
    # ---------------------------

    if MOCK_LLM != "0":

        answer = (
            "I can only answer questions about "
            "Zepto policies right now."
        )

        sources = []
        confidence = 1.0

    # ---------------------------
    # OPTIONAL REAL LLM MODE
    # ---------------------------

    else:

        prompt = f"""
You are Zepto's customer-support assistant.

The following question was classified as a general question
that does not require retrieval from the Zepto policy corpus.

Question:
{query}

Return ONLY valid JSON in exactly this format:

{{
  "answer": "string",
  "sources": [],
  "confidence": 1.0
}}

Do not include markdown.
Do not include any text outside the JSON.
"""

        validated_response = call_real_llm_with_validation(
            prompt,
            []
        )

        answer = validated_response.answer
        sources = validated_response.sources
        confidence = validated_response.confidence

    return {
        "answer": answer,
        "sources": sources,
        "confidence": confidence,
    }

# ---------------------------------------------------------
# STEP 5 — Build LangGraph StateGraph
# ---------------------------------------------------------

workflow = StateGraph(SupportState)


# Add the 3 REQUIRED nodes

workflow.add_node(
    "classify_intent",
    classify_intent,
)

workflow.add_node(
    "retrieve_and_answer",
    retrieve_and_answer,
)

workflow.add_node(
    "direct_answer",
    direct_answer,
)


# First node

workflow.set_entry_point(
    "classify_intent"
)


# Conditional routing

workflow.add_conditional_edges(
    "classify_intent",
    route_intent,
    {
        "retrieve_and_answer": "retrieve_and_answer",
        "direct_answer": "direct_answer",
    },
)


# Both answer nodes finish the graph

workflow.add_edge(
    "retrieve_and_answer",
    END,
)

workflow.add_edge(
    "direct_answer",
    END,
)


# Compile graph

support_graph = workflow.compile()


# ---------------------------------------------------------
# STEP 6 — Helper function
# ---------------------------------------------------------

def run_support_graph(query: str):
    """
    Runs a customer question through the LangGraph workflow.
    """

    initial_state = {
        "query": query,
        "intent": "",
        "context": "",
        "sources": [],
        "confidence": 0.0,
        "answer": "",
    }

    result = support_graph.invoke(initial_state)

    return result


# ---------------------------------------------------------
# STEP 7 — Local test
# ---------------------------------------------------------

if __name__ == "__main__":

    print("\n===================================")
    print("       LangGraph Test")
    print("===================================\n")

    # Policy question
    policy_result = run_support_graph(
        "How does order tracking work?"
    )

    print("POLICY QUESTION")
    print("----------------")

    print("Intent:", policy_result["intent"])
    print("Answer:", policy_result["answer"])
    print("Sources:", policy_result["sources"])
    print("Confidence:", policy_result["confidence"])

    # print()

    # # General question
    # general_result = run_support_graph(
    #     "What is the capital of France?"
    # )

    # print("GENERAL QUESTION")
    # print("----------------")

    # print("Intent:", general_result["intent"])
    # print("Answer:", general_result["answer"])
    # print("Sources:", general_result["sources"])
    # print("Confidence:", general_result["confidence"])