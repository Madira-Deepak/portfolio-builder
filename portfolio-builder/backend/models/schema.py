from pydantic import BaseModel, Field
from typing import Optional


class PortfolioRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Full name of the user")
    title: str = Field(..., description="Professional title or role")
    email: str = Field(..., description="Contact email address")
    phone: Optional[str] = Field(None, description="Contact phone number")
    location: Optional[str] = Field(None, description="City, Country")
    summary: Optional[str] = Field(None, description="Short bio or personal statement")
    education: str = Field(..., description="Education background")
    skills: str = Field(..., description="Comma-separated list of skills")
    projects: str = Field(..., description="Projects description")
    experience: str = Field(..., description="Work experience description")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")
    website: Optional[str] = Field(None, description="Personal website URL")
    style: Optional[str] = Field("modern", description="Portfolio style: modern, minimal, creative")


class PortfolioResponse(BaseModel):
    content: str
    style: str
    generated_at: str