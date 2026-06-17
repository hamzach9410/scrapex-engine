from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ScrapedItem(BaseModel):
    """Expanded schema for comprehensive data extraction."""
    id: str = Field(description="Unique identifier for deduplication (e.g., hash)")
    url: str = Field(description="Source URL")
    element_type: str = Field(description="Type: heading, paragraph, button, link, etc.")
    text: str = Field(description="Visible text content")
    href: Optional[str] = Field(default=None, description="URL of the link element")
    scraped_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp in ISO-8601")
    raw_html: Optional[str] = Field(default=None, exclude=True, description="Raw HTML for debugging")
