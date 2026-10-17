from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from .nodes.analysis import analysis_node
from .nodes.critic import critic_node
from .nodes.guard_nodes import input_guard_node, output_guard_node, route_after_input
from .nodes.planner import planner_node
from .nodes.research import web_search_node, wikipedia_node
from .nodes.synthesis import synthesis_node
from .state import GraphState


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("input_guardrails", input_guard_node)
    graph.add_node("planner", planner_node)
    graph.add_node("wikipedia", wikipedia_node)
    graph.add_node("web_search", web_search_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("critic", critic_node)
    graph.add_node("synthesis", synthesis_node)
    graph.add_node("output_guardrails", output_guard_node)

    graph.add_edge(START, "input_guardrails")
    graph.add_conditional_edges(
        "input_guardrails",
        route_after_input,
        {"continue": "planner", "blocked": END},
    )

    graph.add_edge("planner", "wikipedia")
    graph.add_edge("planner", "web_search")

    graph.add_edge("wikipedia", "analysis")
    graph.add_edge("web_search", "analysis")

    graph.add_edge("analysis", "critic")
    graph.add_edge("critic", "synthesis")
    graph.add_edge("synthesis", "output_guardrails")
    graph.add_edge("output_guardrails", END)

    return graph.compile()
