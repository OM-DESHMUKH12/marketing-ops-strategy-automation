"""Pydantic response schemas used to validate local-model output."""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class StrategyOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    executive_summary: str
    business_understanding: str = ""
    objectives: List[str] = Field(default_factory=list)
    recommended_platforms: List[dict] = Field(default_factory=list)
    content_pillars: List[str] = Field(default_factory=list)
    messaging: List[str] = Field(default_factory=list)
    campaign_ideas: List[dict] = Field(default_factory=list)
    posting_frequency: dict = Field(default_factory=dict)
    roadmap_30_days: List[dict] = Field(default_factory=list)
    kpis: List[str] = Field(default_factory=list)
    risks_assumptions_missing_info: List[str] = Field(default_factory=list)

class ContentOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str
    platform: str
    content_type: str
    topic: str = ""
    objective: str = ""
    hook: str = ""
    caption: str = ""
    call_to_action: str = ""
    hashtags: List[str] = Field(default_factory=list)
    suggested_visual: str = ""
    creative_brief: str = ""
    carousel_slides: List[dict] = Field(default_factory=list)
    video_scenes: List[dict] = Field(default_factory=list)
    estimated_duration_seconds: Optional[int] = None
    source_notes: List[str] = Field(default_factory=list)
