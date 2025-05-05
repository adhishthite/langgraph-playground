"""FastAPI application entry point."""

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config.settings import settings
from app.core.registry import registry

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    description="LangGraph Playground API",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LangGraph Playground API",
        "available_agents": registry.list_agents(),
    }


@app.websocket("/ws/agent/{agent_name}")
async def websocket_agent(websocket: WebSocket, agent_name: str):
    """WebSocket endpoint for agent interactions."""
    await websocket.accept()
    try:
        # Initial message
        await websocket.send_json({"status": "connected", "agent": agent_name})

        # Get agent from registry
        try:
            agent_factory = registry.get(agent_name)
        except KeyError:
            await websocket.send_json({"error": f"Agent '{agent_name}' not found"})
            await websocket.close()
            return

        # Create agent (placeholder logic)
        agent_factory()

        # Process messages
        while True:
            # Receive message
            data = await websocket.receive_json()

            # Send acknowledgment
            await websocket.send_json({"status": "received", "message_id": id(data)})

            # Process with agent (placeholder)
            response = {
                "result": f"Response from {agent_name} (placeholder)",
                "input": data,
            }

            # Send response
            await websocket.send_json(response)

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for agent {agent_name}")
    except Exception as e:
        print(f"Error in WebSocket: {str(e)}")
        try:
            await websocket.send_json({"error": str(e)})
            await websocket.close()
        except Exception:
            pass


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
