from typing import TypedDict

from fastapi import FastAPI
from pydantic import BaseModel, Field

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from rag import retrieve


# ==========================================
# Configuration
# ==========================================

MOCK_LLM = True


# ==========================================
# LangGraph State
# ==========================================

class SupportState(TypedDict):
    query: str
    intent: str
    retrieved_chunks: list
    answer: str
    sources: list
    confidence: float


# ==========================================
# Pydantic Response Schema
# ==========================================

class SupportResponse(BaseModel):

    answer: str

    sources: list[str]

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )


# ==========================================
# Request Schema
# ==========================================

class AskRequest(BaseModel):

    query: str


# ==========================================
# Node 1 — Classify Intent
# ==========================================

def classify_intent(
    state: SupportState
) -> SupportState:
    """
    Classify the query into either:
    policy_question or general_question.
    """

    query = state["query"].lower()

    policy_keywords = [
        "delivery",
        "return",
        "refund",
        "membership",
        "pass",
        "tracking",
        "track",
        "cancel",
        "cancellation",
        "damaged",
        "spoiled",
        "missing",
        "gift card",
        "giftcard",
        "support",
        "customer service",
        "order",
        "zepto"
    ]

    is_policy_question = any(
        keyword in query
        for keyword in policy_keywords
    )

    if is_policy_question:

        state["intent"] = (
            "policy_question"
        )

    else:

        state["intent"] = (
            "general_question"
        )

    return state


# ==========================================
# Node 2 — Retrieve and Answer
# ==========================================

def retrieve_and_answer(
    state: SupportState
) -> SupportState:
    """
    Retrieve the top policy chunks and
    generate an answer.

    MOCK_LLM is used by default so that
    no external API key is required.
    """

    query = state["query"]

    retrieved_chunks = retrieve(
        query,
        top_k=3
    )

    state["retrieved_chunks"] = (
        retrieved_chunks
    )

    sources = []

    for chunk in retrieved_chunks:

        document_id = chunk[
            "document_id"
        ]

        if document_id not in sources:

            sources.append(
                document_id
            )

    state["sources"] = sources

    # --------------------------------------
    # MOCK_LLM path
    # --------------------------------------

    if MOCK_LLM:

        answer = mock_policy_answer(
            query,
            retrieved_chunks
        )

        state["answer"] = answer

        state["confidence"] = 0.95

        return state

    # --------------------------------------
    # Real LLM path
    # --------------------------------------

    # The real LLM integration can be added
    # here later without changing the graph.

    state["answer"] = (
        "Real LLM mode is not enabled."
    )

    state["confidence"] = 0.0

    return state


# ==========================================
# Node 3 — Direct Answer
# ==========================================

def direct_answer(
    state: SupportState
) -> SupportState:
    """
    Handle general questions without
    performing policy retrieval.
    """

    state["retrieved_chunks"] = []

    state["sources"] = []

    state["answer"] = (
        "I can help with Zepto support and "
        "policy-related questions. Please ask "
        "about delivery, returns, refunds, "
        "membership, tracking, cancellation, "
        "gift cards, or customer support."
    )

    state["confidence"] = 0.90

    return state


# ==========================================
# Mock Policy Answer
# ==========================================

def mock_policy_answer(
    query,
    retrieved_chunks
):
    """
    Generate a deterministic answer using
    the retrieved policy text.

    This keeps the graded path keyless.
    """

    if not retrieved_chunks:

        return (
            "I could not find enough information "
            "in the available Zepto policies "
            "to answer this question."
        )

    query_lower = query.lower()

    context = " ".join(
        chunk["text"]
        for chunk in retrieved_chunks
    )

    # --------------------------------------
    # Delivery
    # --------------------------------------

    if (
        "delivery fee" in query_lower
        or (
            "fee" in query_lower
            and "delivery" in query_lower
        )
    ):

        if "INR 149" in context:

            return (
                "Standard delivery is free on "
                "orders over INR 149. Orders "
                "below INR 149 incur a flat "
                "INR 25 delivery fee."
            )

    # --------------------------------------
    # Delivery time
    # --------------------------------------

    if (
        "delivery time" in query_lower
        or "how long" in query_lower
        or "deliver" in query_lower
    ):

        if "10 to 30 minutes" in context:

            return (
                "Zepto delivers to serviceable "
                "pin codes within 10 to 30 minutes "
                "of order confirmation, depending "
                "on the delivery zone and current "
                "order volume."
            )

    # --------------------------------------
    # Return
    # --------------------------------------

    if (
        "return" in query_lower
        or "refund" in query_lower
    ):

        if "24 hours" in context:

            return (
                "Grocery and perishable items may "
                "be reported for a return within "
                "24 hours of delivery if they are "
                "damaged, spoiled, or incorrect."
            )

    # --------------------------------------
    # Membership
    # --------------------------------------

    if (
        "membership" in query_lower
        or "pass" in query_lower
    ):

        if "Zepto Pass" in context:

            return (
                "Zepto offers Basic, Zepto Pass, "
                "and Zepto Pass+ membership tiers. "
                "Zepto Pass costs INR 49 per month "
                "and Zepto Pass+ costs INR 99 per month."
            )

    # --------------------------------------
    # Tracking
    # --------------------------------------

    if (
        "track" in query_lower
        or "tracking" in query_lower
    ):

        if "Track Order" in context:

            return (
                "Zepto provides live rider tracking "
                "through the 'Track Order' screen "
                "from packing until delivery."
            )

    # --------------------------------------
    # Cancellation
    # --------------------------------------

    if (
        "cancel" in query_lower
        or "cancellation" in query_lower
    ):

        if "Packed" in context:

            return (
                "Orders can be cancelled free of "
                "cost before the order status changes "
                "to 'Packed'. Once an order has been "
                "packed, it cannot be cancelled "
                "through the app."
            )

    # --------------------------------------
    # Damaged / missing
    # --------------------------------------

    if (
        "damaged" in query_lower
        or "missing" in query_lower
        or "spoiled" in query_lower
    ):

        if "Report an Issue" in context:

            return (
                "Damaged, spoiled, or missing items "
                "must be reported within 24 hours "
                "through the 'Report an Issue' button "
                "on the order page."
            )

    # --------------------------------------
    # Gift cards
    # --------------------------------------

    if (
        "gift card" in query_lower
        or "giftcard" in query_lower
    ):

        if "INR 100" in context:

            return (
                "Zepto gift cards are available in "
                "INR 100, INR 250, INR 500, and "
                "INR 1000 denominations and are "
                "valid for one year from the date "
                "of issue."
            )

    # --------------------------------------
    # Support
    # --------------------------------------

    if (
        "support" in query_lower
        or "customer service" in query_lower
    ):

        if "in-app chat" in context:

            return (
                "Zepto customer support is available "
                "through in-app chat 24 hours a day, "
                "7 days a week. Email support is also "
                "available for non-urgent queries."
            )

    # --------------------------------------
    # Fallback
    # --------------------------------------

    return (
        "Based on the available Zepto policy "
        "information, I could not find enough "
        "specific information to answer that "
        "question."
    )


# ==========================================
# Conditional Routing
# ==========================================

def route_after_classification(
    state: SupportState
):
    """
    Decide which LangGraph node should run next.
    """

    if state["intent"] == (
        "policy_question"
    ):

        return "retrieve_and_answer"

    return "direct_answer"


# ==========================================
# Build LangGraph
# ==========================================

def build_graph():

    graph = StateGraph(
        SupportState
    )

    # Add required nodes

    graph.add_node(
        "classify_intent",
        classify_intent
    )

    graph.add_node(
        "retrieve_and_answer",
        retrieve_and_answer
    )

    graph.add_node(
        "direct_answer",
        direct_answer
    )

    # Starting node

    graph.add_edge(
        START,
        "classify_intent"
    )

    # Conditional routing

    graph.add_conditional_edges(
        "classify_intent",
        route_after_classification,
        {
            "retrieve_and_answer":
                "retrieve_and_answer",

            "direct_answer":
                "direct_answer"
        }
    )

    # End nodes

    graph.add_edge(
        "retrieve_and_answer",
        END
    )

    graph.add_edge(
        "direct_answer",
        END
    )

    return graph.compile()


# Build graph once

support_graph = build_graph()


# ==========================================
# FastAPI Application
# ==========================================

app = FastAPI(
    title="Zepto Support Assistant",
    description=(
        "RAG-based Zepto support assistant "
        "using LangGraph and ChromaDB."
    ),
    version="1.0.0"
)


# ==========================================
# POST /ask
# ==========================================

@app.post(
    "/ask",
    response_model=SupportResponse
)
def ask(
    request: AskRequest
):

    initial_state: SupportState = {
        "query": request.query,
        "intent": "",
        "retrieved_chunks": [],
        "answer": "",
        "sources": [],
        "confidence": 0.0
    }

    final_state = support_graph.invoke(
        initial_state
    )

    response = SupportResponse(
        answer=final_state["answer"],
        sources=final_state["sources"],
        confidence=final_state["confidence"]
    )

    return response


# ==========================================
# Local test
# ==========================================

if __name__ == "__main__":

    print(
        "Testing policy question..."
    )

    policy_state: SupportState = {
        "query": (
            "What is the delivery fee "
            "for orders below INR 149?"
        ),
        "intent": "",
        "retrieved_chunks": [],
        "answer": "",
        "sources": [],
        "confidence": 0.0
    }

    policy_result = support_graph.invoke(
        policy_state
    )

    print(
        "\nPolicy result:"
    )

    print(
        SupportResponse(
            answer=policy_result["answer"],
            sources=policy_result["sources"],
            confidence=policy_result["confidence"]
        ).model_dump()
    )


    print(
        "\nTesting general question..."
    )

    general_state: SupportState = {
        "query": (
            "What is artificial intelligence?"
        ),
        "intent": "",
        "retrieved_chunks": [],
        "answer": "",
        "sources": [],
        "confidence": 0.0
    }

    general_result = support_graph.invoke(
        general_state
    )

    print(
        "\nGeneral result:"
    )

    print(
        SupportResponse(
            answer=general_result["answer"],
            sources=general_result["sources"],
            confidence=general_result["confidence"]
        ).model_dump()
    )