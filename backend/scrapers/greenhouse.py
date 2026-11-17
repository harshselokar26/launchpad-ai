
import httpx
import logging

logger = logging.getLogger(__name__)

async def fetch_greenhouse_jobs(board_token: str):
    url = (
        f"https://boards-api.greenhouse.io/v1/"
        f"boards/{board_token}/jobs"
    )

    params = {"content": "true"}

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()

            data = response.json()

        jobs = []

        for item in data.get("jobs", []):
            offices = item.get("offices") or []

            location = ", ".join(
                office.get("location", "")
                for office in offices
                if office.get("location")
            )

            jobs.append({
                "title": item.get("title", ""),
                "company": data.get("name", board_token),
                "description": item.get("content", ""),
                "location": location,
                "source": "Greenhouse",
                "source_url": item.get("absolute_url", ""),
                "posted_at": item.get("updated_at")
            })

        return jobs

    except Exception as exc:
        logger.exception(
            "Greenhouse failed for %s: %s",
            board_token,
            exc
        )
        return []