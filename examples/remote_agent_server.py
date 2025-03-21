from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import uvicorn
import os
from asyncio import CancelledError

from moya.agents.openai_agent import OpenAIAgent, OpenAIAgentConfig
from moya.tools.tool_registry import ToolRegistry
from moya.tools.ephemeral_memory import EphemeralMemory


app = FastAPI()


class Message(BaseModel):
    content: str
    thread_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


def setup_agent():
    """Set up OpenAI agent with memory capabilities."""
    # Set up memory components
    tool_registry = ToolRegistry()
    EphemeralMemory.configure_memory_tools(tool_registry)

    # Create and setup agent
    agent_config = OpenAIAgentConfig(
        agent_name="remote_joke_agent",
        agent_type="RemoteAgent",
        description="Remote agent specialized in humor",
        system_prompt="You are a remote agent that specializes in telling jokes and being entertaining.",
        api_key=os.getenv("OPENAI_API_KEY"),
        tool_registry=tool_registry,
        model_name="gpt-4o",
        llm_config={
            'temperature':0.8,
            'max_tokens':1000
        }
    )
    return OpenAIAgent(agent_config)
   


# Initialize agent at startup
agent = setup_agent()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agent": agent.agent_name}


@app.post("/chat")
async def chat(request: Request):
    """Handle normal chat requests using OpenAI agent."""
    data = await request.json()
    message = data['message']
    thread_id = data.get('thread_id', 'default_thread')

    # Store user message
    EphemeralMemory.store_message(thread_id=thread_id, sender="user", content=message)

    # Get response from agent
    response = agent.handle_message(message, thread_id=thread_id)

    # Store agent response
    EphemeralMemory.store_message(thread_id=thread_id, sender=agent.agent_name, content=response)
    
    return {"response": response}


async def stream_response(message: str, thread_id: str):
    """Stream response from OpenAI agent."""
    response_text = ""
    current_text = ""

    async def send_chunk(text: str):
        """Helper to format and send SSE chunks."""
        return f"data: {text}\n\n"

    try:
        # Store user message
        EphemeralMemory.store_message(thread_id=thread_id, sender="user", content=message)

        # Stream response
        for chunk in agent.handle_message_stream(message, thread_id=thread_id):
            if chunk:
                # Add chunk to current text
                current_text += chunk

                # Find word boundaries
                words = current_text.split()

                if len(words) > 1:  # If we have at least one complete word
                    # Keep the last word in case it's incomplete
                    text_to_send = ' '.join(words[:-1]) + ' '
                    current_text = words[-1]

                    response_text += text_to_send
                    yield await send_chunk(text_to_send)

                await asyncio.sleep(0.01)

        # Send any remaining text
        if current_text:
            response_text += current_text
            yield await send_chunk(current_text)

        # Store complete response
        EphemeralMemory.store_message(thread_id=thread_id, sender=agent.agent_name, content=response_text)
    except CancelledError:
        if response_text:  # Only log if we actually got some response
            print(f"Client disconnected, stored partial response of length: {len(response_text)}")
        return

    except Exception as e:
        error_msg = f"[Error: {str(e)}]"
        yield await send_chunk(error_msg)


@app.post("/chat/stream")
async def chat_stream(request: Request):
    """Handle streaming chat requests using OpenAI agent."""
    data = await request.json()
    message = data['message']
    thread_id = data.get('thread_id', 'default_thread')

    return StreamingResponse(
        stream_response(message, thread_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "Transfer-Encoding": "chunked"
        }
    )


@app.post("/generate")
async def generate_response(message: Message):
    try:
        response = agent.handle_message(
            message=message.content,
            thread_id=message.thread_id,
            metadata=message.metadata
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
