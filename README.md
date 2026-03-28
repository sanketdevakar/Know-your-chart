# Celestial Agent

## Project Overview

`Celestial Agent` is an AI agent implemented using the Google ADK. It connects to an MCP tool server that computes astronomical data, retrieves structured chart information, and uses that data to generate a natal chart response.

This project fulfills the submission requirements by:
- implementing a single AI agent with ADK
- using MCP to connect to an external tool/data source
- retrieving structured astronomical data
- using that data in the final generated response

## Architecture

- `agent/agent.py` — defines the ADK agent pipeline and model configuration.
- `mcp_server/server.py` — runs the MCP tool server exposing astrology tools.
- `main.py` — exposes a FastAPI API that forwards user messages to the ADK agent.
- `.env` — environment variables for local development.
- `Dockerfile` — containerizes the app for Cloud Run.

## Key Features

- `@app.post("/chat")` endpoint for agent interaction
- uses the `google.adk` and `google.genai` packages
- MCP tools compute:
  - planet positions
  - moon phase
  - rising sign
  - Rahu/Ketu positions
- Cloud Run deployment ready

## Requirements

- Python 3.11
- `google-adk`
- `google-generativeai`
- `fastapi`
- `uvicorn`
- `ephem`
- `mcp`
- `fastmcp`
- `python-dotenv`

Install dependencies:

```bash
python -m venv venv
venv/bin/python -m pip install --upgrade pip
venv/bin/python -m pip install -r requirements.txt
```

On Windows PowerShell use:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file with the following example values:

```dotenv
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=true
MCP_SERVER_URL=http://localhost:8081/sse
MCP_PORT=8081
```

If using Cloud Run, set these env vars via deploy command.

## Local Development

### Start the MCP tool server

```bash
python mcp_server/server.py
```

### Start the API server

```bash
python main.py
```

The local API will be available at `http://localhost:8000`.

### Test the API

Root:

```bash
curl http://localhost:8000/
```

Chat endpoint:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","session_id":"default"}'
```

## Cloud Run Deployment

Build and push the container image:

```bash
gcloud builds submit --tag gcr.io/$PROJECT_ID/jyotish-verify .
```

Deploy to Cloud Run:

```bash
gcloud run deploy jyotish-verify \
  --image gcr.io/$PROJECT_ID/jyotish-verify \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --service-account $SERVICE_ACCOUNT \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=us-central1,GOOGLE_GENAI_USE_VERTEXAI=true,MCP_SERVER_URL=http://localhost:8081/sse,MCP_PORT=8081" \
  --memory 512Mi
```

## Using the Deployed Service

Open the Cloud Run URL in a browser to verify the service is running.

- `GET /` should return service metadata
- `POST /chat` should return the agent response

Example POST request:

```bash
curl -X POST https://YOUR-SERVICE-URL/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","session_id":"default"}'
```

## Notes

- The Cloud Run URL is an API endpoint, not the ADK local developer UI.
- Use the `/chat` POST endpoint for interaction.
- `GET /chat` will return `405 Method Not Allowed`.

## Submission

Submit the Cloud Run service URL and this repository. The project demonstrates:
- ADK-based agent implementation
- MCP integration with one external tool
- structured data retrieval and response generation

---

## Files to Review

- `main.py`
- `agent/agent.py`
- `mcp_server/server.py`
- `Dockerfile`
- `requirements.txt`
- `.env`
