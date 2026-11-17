
import asyncio

from app.services.ingestion import process_job


sample_job = {
    "title": "Python Backend Developer - Fresher",
    "company": "TechNova India",
    "location": "Pune, India",
    "description": """
    We are hiring fresh graduates for a Python Backend Developer role.

    Requirements:
    - Python programming
    - FastAPI
    - REST API development
    - PostgreSQL
    - 0 to 1 years of experience

    Employment: Full-time
    Work mode: Hybrid
    """,
    "source": "manual_test",
    "source_url": "https://example.com/laun​chpad-python-backend-test-001",
    "is_active": True
}


async def main():
    print("Starting LaunchPad AI ingestion...")

    result = await process_job(sample_job)

    print("\nPipeline result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
