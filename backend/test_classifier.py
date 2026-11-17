
import asyncio
from app.services.classifier import classify_job


sample_job = {
    "title": "Junior Python Backend Developer",
    "company": "Example Technologies",
    "location": "Bangalore, India",
    "description": """
    We are looking for a fresher Python Backend Developer.

    Requirements:
    - Knowledge of Python
    - Basic FastAPI experience
    - REST API development
    - SQL and PostgreSQL
    - 0 to 1 years of experience

    Employment type: Full-time.
    Work mode: Hybrid.
    """
}


async def main():
    print("Sending job to Ollama...")

    result = await classify_job(sample_job)

    print("\nClassification result:")
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
