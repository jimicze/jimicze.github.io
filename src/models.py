"""
Pydantic v2 models for the JSON Resume schema + _meta extensions.

The cv.json file is validated against these models on load.
No personal data is ever hardcoded here — all data flows from data/cv.json.
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ── JSON Resume core models ───────────────────────────────────────────────────

class Location(BaseModel):
    address: Optional[str] = None
    postalCode: Optional[str] = None
    city: Optional[str] = None
    countryCode: Optional[str] = None
    region: Optional[str] = None


class Profile(BaseModel):
    network: str
    username: Optional[str] = None
    url: Optional[str] = None


class Basics(BaseModel):
    name: str
    label: Optional[str] = None
    image: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    url: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[Location] = None
    profiles: list[Profile] = Field(default_factory=list)


class WorkEntry(BaseModel):
    name: str
    location: Optional[str] = None
    description: Optional[str] = None
    position: Optional[str] = None
    url: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    summary: Optional[str] = None
    highlights: list[str] = Field(default_factory=list)


class EducationEntry(BaseModel):
    institution: str
    url: Optional[str] = None
    area: Optional[str] = None
    studyType: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    score: Optional[str] = None
    courses: list[str] = Field(default_factory=list)


class Certificate(BaseModel):
    name: str
    date: Optional[str] = None
    issuer: Optional[str] = None
    url: Optional[str] = None


class Skill(BaseModel):
    name: str
    level: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)


class Language(BaseModel):
    language: str
    fluency: Optional[str] = None


class Interest(BaseModel):
    name: str
    keywords: list[str] = Field(default_factory=list)


class Project(BaseModel):
    name: str
    description: Optional[str] = None
    highlights: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    url: Optional[str] = None
    roles: list[str] = Field(default_factory=list)
    entity: Optional[str] = None
    type: Optional[str] = None


# ── _meta extensions ─────────────────────────────────────────────────────────

class AiPromptConfig(BaseModel):
    """Opt-in invisible prompt for AI-HR tools. Default: disabled.

    WARNING: This is a prompt-injection technique. Some employers explicitly
    forbid this. Use at your own risk. Default is always OFF.
    """
    enabled: bool = False
    techniques: list[str] = Field(
        default_factory=lambda: ["white-on-white", "pdf-metadata", "docx-properties"]
    )
    content: str = ""


class VariantConfig(BaseModel):
    photo: bool = False
    color: bool = False


class Meta(BaseModel):
    """Non-standard _meta block stored in cv.json alongside JSON Resume data."""
    version: Optional[str] = None
    extractedFrom: list[str] = Field(default_factory=list)
    extractedDate: Optional[str] = None
    crossValidated: Optional[bool] = None
    photo: Optional[str] = None
    variants: dict[str, VariantConfig] = Field(default_factory=dict)
    openToRoles: list[str] = Field(default_factory=list)
    socialLinks: dict[str, str] = Field(default_factory=dict)
    aiPrompt: AiPromptConfig = Field(default_factory=AiPromptConfig)
    # Private personal data — loaded but never rendered in templates
    cz_ico: Optional[str] = None
    cz_dic: Optional[str] = None
    dateOfBirth: Optional[str] = None
    sex: Optional[str] = None
    nationality: Optional[str] = None


# ── Root CV model ─────────────────────────────────────────────────────────────

class CvData(BaseModel):
    """Root model — matches the full JSON Resume schema + _meta extensions."""
    model_config = ConfigDict(populate_by_name=True)

    schema_: Optional[str] = Field(None, alias="$schema")
    basics: Basics
    work: list[WorkEntry] = Field(default_factory=list)
    volunteer: list[Any] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    awards: list[Any] = Field(default_factory=list)
    certificates: list[Certificate] = Field(default_factory=list)
    publications: list[Any] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    languages: list[Language] = Field(default_factory=list)
    interests: list[Interest] = Field(default_factory=list)
    references: list[Any] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    meta: Optional[Meta] = Field(None, alias="_meta")
