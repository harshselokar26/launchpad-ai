
import json
import httpx

from app.config import settings


async def classify_job(job: dict) -> dict:
    prompt = f"""
You are a job classification assistant for an Indian fresher jobs platform.

Analyze this job:

Title: {job.get("title", "")}
Company: {job.get("company", "")}
Location: {job.get("location", "")}
Description: {job.get("description", "")}

Return valid JSON only:
{{
    "role_category": "Backend Developer",
    "city": "Bangalore",
    "experience_level": "Fresher",
    "job_type": "Full-time",
    "work_mode": "Hybrid",
    "skills": ["Python", "FastAPI"],
    "is_fresher": true
}}

Do not invent information. Use null for unknown fields.
Use an empty array for unknown skills.
Only mark is_fresher true if suitable for 0-1 years experience.
"""

    payload = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "format": "json",
        "stream": False,
        "options": {"temperature": 0}
    }

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{settings.ollama_url.rstrip('/')}/api/chat",
            json=payload
        )
        response.raise_for_status()

    result = response.json()
    classification = json.loads(result["message"]["content"])

    required = [
        "role_category", "city", "experience_level",
        "job_type", "work_mode", "skills", "is_fresher"
    ]

    for field in required:
        if field not in classification:
            raise ValueError(f"Missing field: {field}")

    if not isinstance(classification["skills"], list):
        raise ValueError("Skills must be a list")

    if not isinstance(classification["is_fresher"], bool):
        raise ValueError("is_fresher must be boolean")

    return classification
