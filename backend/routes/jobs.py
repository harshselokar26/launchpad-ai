
from fastapi import APIRouter, Query, HTTPException

from app.database import supabase

router = APIRouter()

@router.get("/")
def get_jobs(
    search: str | None = None,
    city: str | None = None,
    role: str | None = None,
    job_type: str | None = None,
    fresher_only: bool = False,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    try:
        start = (page - 1) * limit
        end = start + limit - 1

        query = (
            supabase.table("jobs")
            .select("*", count="exact")
            .eq("is_active", True)
        )

        if search:
            query = query.or_(
                f"title.ilike.%{search}%,"
                f"company.ilike.%{search}%,"
                f"skills.cs.{{{search}}}"
            )

        if city:
            query = query.ilike("city", f"%{city}%")

        if role:
            query = query.eq("role", role)

        if job_type:
            query = query.eq("job_type", job_type)

        if fresher_only:
            query = query.eq("fresher_eligible", True)

        response = (
            query
            .order("fetched_at", desc=True)
            .range(start, end)
            .execute()
        )

        return {
            "jobs": response.data,
            "total": response.count or 0,
            "page": page,
            "limit": limit
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve jobs"
        ) from exc

@router.get("/stats")
def get_stats():
    try:
        response = (
            supabase.table("jobs")
            .select("id, fresher_eligible, job_type, city")
            .eq("is_active", True)
            .execute()
        )

        jobs = response.data

        return {
            "total_jobs": len(jobs),
            "fresher_jobs": sum(
                j["fresher_eligible"] is True for j in jobs
            ),
            "internships": sum(
                j["job_type"] == "Internship" for j in jobs
            ),
            "cities": len({
                j["city"] for j in jobs if j["city"]
            })
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve statistics"
        ) from exc