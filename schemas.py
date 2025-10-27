"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# Example schemas (you can keep or remove if not needed)

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# AI Business Dashboard related schemas

class DatasetIngest(BaseModel):
    """
    Tracks dataset ingest requests and metadata
    Collection name: "datasetingest"
    """
    name: str = Field(..., description="Dataset name")
    source: str = Field(..., description="Source of the data e.g., 'csv', 's3', 'api'")
    fields: List[str] = Field(default_factory=list, description="List of field names")
    rows: int = Field(0, ge=0, description="Number of rows ingested")
    notes: Optional[str] = Field(None, description="Optional notes")

class ForecastRequest(BaseModel):
    """
    Forecast request payload and results summary
    Collection name: "forecastrequest"
    """
    metric: str = Field(..., description="Metric to forecast, e.g., 'revenue'")
    horizon_days: int = Field(30, ge=1, le=365, description="Forecast horizon in days")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata/context")

class RecommendationRequest(BaseModel):
    """
    Recommendation request details
    Collection name: "recommendationrequest"
    """
    objective: str = Field(..., description="Business objective, e.g., 'increase_conversion'")
    constraints: Optional[List[str]] = Field(default_factory=list, description="List of constraints")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")

class ChatMessage(BaseModel):
    """
    Chat messages exchanged with the assistant
    Collection name: "chatmessage"
    """
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    session_id: Optional[str] = Field(None, description="Conversation/session id")
