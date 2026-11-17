
import asyncio
import logging
import os
import sys

from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

load_dotenv(ROOT / "backend" / ".env")

from app.scrapers.greenhouse import fetch_greenhouse_jobs
from app.scrapers.lever import fetch_lever_jobs
from app.services.classifier import classify_job
from app.services.deduplicator import generate_content_hash
from app.database import supabase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)

def get_existing_hashes():
    response = (
        supabase.table("jobs")
        .select("content_hash")
        .execute()
    )

    return {
        row["content_hash"]
        for row in response.data
        if row.get("content_hash")
    }

async def collect_jobs():
    all_jobs = []

    greenhouse_boards = [
        x.strip()
        for x in os.getenv("GREENHOUSE_BOARDS", "").split(",")
        if x.strip()
    ]

    lever_sites = [
        x.strip()
        for x in os.getenv("LEVER_SITES", "").split(",")
        if x.strip()
    ]

    for board in greenhouse_boards:
        jobs = await fetch_greenhouse_jobs(board)
        all_jobs.extend(jobs)

        logger.info(
            "Greenhouse %s: %s jobs",
            board,
            len(jobs)
        )

    for site in lever_sites:
        jobs = await fetch_lever_jobs(site)
        all_jobs.extend(jobs)

        logger.info(
            "Lever %s: %s jobs",
            site,
            len(jobs)
        )

    return all_jobs

async def main():
    logger.info("Starting daily ingestion")

    jobs = await collect_jobs()

    logger.info("Collected %s raw jobs", len(jobs))

    existing_hashes = get_existing_hashes()

    inserted = 0
    duplicates = 0
    failed = 0

    for job in jobs:

        if not job.get("title") or not job.get("source_url"):
            failed += 1
            continue

        content_hash = generate_content_hash(job)

        if content_hash in existing_hashes:
            duplicates += 1
            continue

        classification = await classify_job(job)

        if classification is None:
            failed += 1
            continue

        if (
            classification["country"].lower()
            not in ("india", "unknown")
        ):
            continue

        record = {
            **job,
            **classification,
            "content_hash": content_hash,
            "is_active": True
        }

        try:
            supabase.table("jobs").upsert(
                record,
                on_conflict="content_hash"
            ).execute()

            existing_hashes.add(content_hash)
            inserted += 1

        except Exception:
            logger.exception(
                "Failed saving job: %s",
                job.get("title")
            )
            failed += 1

    logger.info("Pipeline completed")
    logger.info("Inserted: %s", inserted)
    logger.info("Duplicates: %s", duplicates)
    logger.info("Failed: %s", failed)

if __name__ == "__main__":
    asyncio.run(main())