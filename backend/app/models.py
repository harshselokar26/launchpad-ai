
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl, Field


class JobCreate(BaseModel):
    title: str
    company: str
    location: str

    job_type: Optional[str] = None
    experience_level: Optional[str] = None

    description: Optional[str] = None
    skills: list[str] = Field(default_factory=list)

    source: str
    source_url: HttpUrl

    posted_at: Optional[datetime] = None


class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    location: str

    job_type: Optional[str] = None
    experience_level: Optional[str] = None

    description: Optional[str] = None
    skills: list[str] = Field(default_factory=list)

    source: str
    source_url: str

    posted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
