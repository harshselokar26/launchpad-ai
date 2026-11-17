
from fastapi import APIRouter, HTTPException, Query
from app.database import supabase

router = APIRouter()


@router.get("/")
async def get_jobs(
    search: str | None = None,
    location: str | None = None,
    job_type: str | None = None,
    limit: int = Query(default=50, ge=1, le=100)
):
    try:
        query = (
            supabase.table("jobs")
            .select("*")
            .eq("is_active", True)
        )

        if search:
            safe_search = search.replace(",", " ")
            query = query.or_(
                f"title.ilike.%{safe_search}%,"
                f"company.ilike.%{safe_search}%,"
                f"description.ilike.%{safe_search}%"
            )

        if location:
            query = query.ilike("location", f"%{location}%")

        if job_type:
            query = query.ilike("job_type", f"%{job_type}%")

        response = (
            query
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        return {
            "total": len(response.data),
            "jobs": response.data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to fetch jobs: {str(e)}"
        )


@router.get("/health")
async def jobs_health():
    return {
        "status": "healthy",
        "service": "jobs"
    }
