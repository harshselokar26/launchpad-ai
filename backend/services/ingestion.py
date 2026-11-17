
from app.database import supabase
from app.services.classifier import classify_job
from app.services.deduplicator import (
    is_duplicate,
    generate_content_hash
)


async def process_job(job: dict) -> dict:
    """Deduplicate, classify and save a job."""

    required_fields = [
        "title",
        "company",
        "location",
        "source",
        "source_url"
    ]

    for field in required_fields:
        if not job.get(field):
            raise ValueError(f"Missing required field: {field}")

    # 1. Check for duplicates
    if is_duplicate(job):
        return {
            "status": "skipped",
            "reason": "Duplicate job",
            "title": job["title"]
        }

    # 2. Classify using Ollama
    classification = await classify_job(job)

    # 3. Generate content fingerprint
    content_hash = generate_content_hash(job)

    # 4. Prepare database record
    record = {
        **job,
        "source_url":  "https://example.com/launchpad-python-backend-test-001",
        "content_hash": content_hash,
        "role_category": classification["role_category"],
        "city": classification["city"],
        "experience_level": classification["experience_level"],
        "job_type": classification["job_type"],
        "work_mode": classification["work_mode"],
        "skills": classification["skills"],
        "is_fresher": classification["is_fresher"],
        "classification_status": "completed"
    }

    # 5. Save to Supabase
    response = (
        supabase.table("jobs")
        .insert(record)
        .execute()
    )

    return {
        "status": "success",
        "message": "Job classified and saved",
        "job": response.data[0]
    }
