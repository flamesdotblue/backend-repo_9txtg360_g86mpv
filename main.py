import os
from datetime import datetime, timezone, timedelta
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from schemas import DatasetIngest, ForecastRequest, RecommendationRequest, ChatMessage
from database import create_document, get_documents, db

app = FastAPI(title="AI-Powered Business Decision Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response: Dict[str, Any] = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = getattr(db, "name", "✅ Connected")
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:  # noqa: BLE001
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:  # noqa: BLE001
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# --- AI Business Dashboard Endpoints ---

@app.post("/api/ingest")
def ingest_dataset(payload: DatasetIngest):
    """Record a dataset ingest event and return a summary."""
    doc_id = None
    try:
        doc_id = create_document("datasetingest", payload)
    except Exception as _:
        # Database might be unavailable; continue with non-persistent response
        pass

    return {
        "status": "ok",
        "id": doc_id,
        "name": payload.name,
        "source": payload.source,
        "fields": payload.fields,
        "rows": payload.rows,
        "message": "Dataset ingest recorded",
    }


@app.post("/api/forecast")
def forecast(payload: ForecastRequest):
    """Generate a simple baseline forecast (mock) and store the request."""
    try:
        _ = create_document("forecastrequest", payload)
    except Exception:
        pass

    # Create a very simple mock forecast trajectory
    today = datetime.now(timezone.utc)
    base = 100.0
    horizon = payload.horizon_days
    points = []
    for i in range(horizon):
        date = today + timedelta(days=i + 1)
        value = base * (1 + 0.01 * i)  # simple 1% daily growth mock
        points.append({"date": date.date().isoformat(), "value": round(value, 2)})

    return {
        "status": "ok",
        "metric": payload.metric,
        "horizon_days": horizon,
        "series": points,
        "note": "Mock forecast. Replace with your ML model later.",
    }


@app.post("/api/recommend")
def recommend(payload: RecommendationRequest):
    """Return simple rule-based recommendations and save the request."""
    try:
        _ = create_document("recommendationrequest", payload)
    except Exception:
        pass

    suggestions = [
        "Increase top-of-funnel campaigns by 10% for A/B test",
        "Optimize pricing tiers based on elasticity",
        "Prioritize retention with targeted win-back emails",
    ]

    return {
        "status": "ok",
        "objective": payload.objective,
        "suggestions": suggestions,
        "constraints": payload.constraints or [],
    }


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


@app.post("/api/chat")
def chat(req: ChatRequest):
    """Very small echo-style assistant with persistence of messages when DB available."""
    user_msg = ChatMessage(role="user", content=req.message, session_id=req.session_id)
    assistant_reply = ChatMessage(
        role="assistant",
        content=f"You said: {req.message}. For forecasting, try POST /api/forecast.",
        session_id=req.session_id,
    )

    try:
        _ = create_document("chatmessage", user_msg)
        _ = create_document("chatmessage", assistant_reply)
    except Exception:
        pass

    return {"reply": assistant_reply.content, "session_id": req.session_id}


@app.get("/schema")
def get_schema_info():
    """Return a lightweight description of available models for tooling."""
    return {
        "models": {
            "datasetingest": list(DatasetIngest.model_fields.keys()),
            "forecastrequest": list(ForecastRequest.model_fields.keys()),
            "recommendationrequest": list(RecommendationRequest.model_fields.keys()),
            "chatmessage": list(ChatMessage.model_fields.keys()),
        }
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
