
from app.database import supabase

sample_job = {
    "title": "Junior Backend Developer",
    "company": "LaunchPad Test Company",
    "location": "Bangalore, India",
    "job_type": "Full-time",
    "experience_level": "Fresher",
    "description": "Looking for a fresher Python developer with knowledge of FastAPI, REST APIs and SQL.",
    "skills": ["Python", "FastAPI", "SQL", "REST API"],
    "source": "manual_test",
    "source_url": "https://example.com/launchpad-test-job",
    "is_active": True
}

response = (
    supabase.table("jobs")
    .insert(sample_job)
    .execute()
)

print("Inserted job successfully!")
print(response.data)
