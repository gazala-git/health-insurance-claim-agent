from langgraph.graph import StateGraph, START, END

from src.state import AgentState
from src.agent import (
    policy_retriever,
    claim_analyzer,
    report_generator,
)

graph_builder = StateGraph(AgentState)

graph_builder.add_node(
    "policy_retriever",
    policy_retriever,
)

graph_builder.add_node(
    "claim_analyzer",
    claim_analyzer,
)

graph_builder.add_node(
    "report_generator",
    report_generator,
)

graph_builder.add_edge(
    START,
    "policy_retriever",
)

graph_builder.add_edge(
    "policy_retriever",
    "claim_analyzer",
)

graph_builder.add_edge(
    "claim_analyzer",
    "report_generator",
)

graph_builder.add_edge(
    "report_generator",
    END,
)

graph = graph_builder.compile()