"""Streaming infrastructure for agents."""

from typing import AsyncIterator, Dict, Any

from fastapi import WebSocket
from langgraph.graph import Graph


async def stream_graph_run(
    graph: Graph, inputs: Dict[str, Any]
) -> AsyncIterator[Dict[str, Any]]:
    """Stream the execution of a graph.

    Args:
        graph: The LangGraph instance to run
        inputs: The inputs for the graph

    Yields:
        Dictionary updates from the graph execution
    """
    # This is a placeholder for actual implementation
    async for event in graph.astream(inputs):
        yield event


async def stream_to_websocket(
    websocket: WebSocket, graph: Graph, inputs: Dict[str, Any]
):
    """Stream graph execution to a websocket.

    Args:
        websocket: The websocket connection
        graph: The graph to execute
        inputs: Inputs for the graph
    """
    try:
        async for event in stream_graph_run(graph, inputs):
            await websocket.send_json(event)
    except Exception as e:
        await websocket.send_json({"error": str(e)})
