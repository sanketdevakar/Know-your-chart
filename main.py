import os
import uvicorn
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent.agent import root_agent

load_dotenv()

session_service = InMemorySessionService()
APP_NAME = "jyotish-verify"


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    session_id: str




@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Jyotish Verify",
    description=(
        "Free natal chart readings from real astronomical data. "
        "Know your chart before you consult an astrologer."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "service": "Jyotish Verify",
        "status":  "running",
        "usage":   "POST /chat with {message, session_id}",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:

        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service,
        )

        # Create session (ignored if it already exists)
        try:
            await session_service.create_session(
                app_name=APP_NAME,
                user_id="user",
                session_id=request.session_id,
            )
        except Exception:
            pass

        content = types.Content(
            role="user",
            parts=[types.Part(text=request.message)],
        )

        response_text = ""
        async for event in runner.run_async(
            user_id="user",
            session_id=request.session_id,
            new_message=content,
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text

        if not response_text:
            raise HTTPException(status_code=500, detail="Agent returned empty response")

        return ChatResponse(response=response_text, session_id=request.session_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=False,
    )