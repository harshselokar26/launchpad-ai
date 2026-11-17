
import hashlib
import re
import unicodedata

from app.database import supabase


def normalize_text(value: str | None) -> str:
    """Normalize text before comparing job listings."""

    if not value:
        return ""

    value = unicodedata.normalize("NFKC", value)
    value = value.lower().strip()
    value = re.sub(r"\s+", " ", value)

    return value


def generate_content_hash(job: dict) -> str:
    """
    Generate a stable fingerprint from the job title,
    company and location.
    """

    parts = [
        normalize_text(job.get("title")),
        normalize_text(job.get("company")),
        normalize_text(job.get("location"))
    ]

    fingerprint = "|".join(parts)

    return hashlib.sha256(
        fingerprint.encode("utf-8")
    ).hexdigest()


def is_duplicate(job: dict) -> bool:
    """
    Check whether the source URL or content hash
    already exists in Supabase.
    """

    source_url = job.get("source_url")
    content_hash = generate_content_hash(job)

    if source_url:
        url_result = (
            supabase.table("jobs")
            .select("id")
            .eq("source_url", str(source_url))
            .limit(1)
            .execute()
        )

        if url_result.data:
            return True

    hash_result = (
        supabase.table("jobs")
        .select("id")
        .eq("content_hash", content_hash)
        .limit(1)
        .execute()
    )

    return bool(hash_result.data)
