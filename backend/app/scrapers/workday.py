
import asyncio
import httpx
from bs4 import BeautifulSoup


# Workday career board configuration
HOST = "https://workday.wd5.myworkdayjobs.com"
TENANT = "workday"
SITE = "Workday"

BASE_URL = f"{HOST}/wday/cxs/{TENANT}/{SITE}"
JOBS_URL = f"{BASE_URL}/jobs"

PAGE_SIZE = 20
MAX_RETRIES = 3


def clean_html(content: str) -> str:
    """Convert HTML job descriptions into readable text."""
    if not content:
        return ""

    return BeautifulSoup(
        content,
        "html.parser"
    ).get_text(separator=" ", strip=True)


async def post_with_retry(
    client: httpx.AsyncClient,
    url: str,
    payload: dict
) -> httpx.Response:
    """Retry requests when Workday returns HTTP 429."""

    for attempt in range(MAX_RETRIES):
        response = await client.post(url, json=payload)

        if response.status_code != 429:
            response.raise_for_status()
            return response

        retry_after = response.headers.get("Retry-After")

        try:
            wait_time = (
                min(int(retry_after), 60)
                if retry_after
                else 15 * (2 ** attempt)
            )
        except ValueError:
            wait_time = 15 * (2 ** attempt)

        if attempt == MAX_RETRIES - 1:
            raise RuntimeError(
                "Workday is rate-limiting requests (HTTP 429). "
                f"Response: {response.text[:300]}"
            )

        print(
            f"Workday returned 429. "
            f"Retrying after {wait_time} seconds..."
        )

        await asyncio.sleep(wait_time)

    raise RuntimeError("Workday request failed after retries.")


async def fetch_job_description(
    client: httpx.AsyncClient,
    external_path: str
) -> str:
    """Fetch an individual job description."""

    try:
        response = await client.get(
            f"{BASE_URL}{external_path}"
        )

        if not response.is_success:
            print(
                f"Could not fetch description: "
                f"{external_path} ({response.status_code})"
            )
            return ""

        data = response.json()
        job_info = data.get("jobPostingInfo", {})

        return clean_html(
            job_info.get("jobDescription", "")
        )

    except (httpx.HTTPError, ValueError) as error:
        print(f"Description fetch failed: {error}")
        return ""


async def scrape_workday(
    max_jobs: int = 500,
    fetch_descriptions: bool = True
) -> list[dict]:
    """
    Fetch job listings from the Workday career board.

    Args:
        max_jobs: Maximum number of jobs to retrieve.
        fetch_descriptions: Whether to fetch individual descriptions.

    Returns:
        List of normalized job dictionaries.
    """

    jobs = []
    seen_ids = set()
    offset = 0

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    async with httpx.AsyncClient(
        timeout=30,
        headers=headers,
        follow_redirects=True
    ) as client:

        while len(jobs) < max_jobs:

            payload = {
                "appliedFacets": {},
                "limit": PAGE_SIZE,
                "offset": offset,
                "searchText": ""
            }

            print(f"Fetching Workday jobs: offset {offset}")

            response = await post_with_retry(
                client,
                JOBS_URL,
                payload
            )

            data = response.json()
            postings = data.get("jobPostings", [])

            if not postings:
                print("No more job postings found.")
                break

            for item in postings:

                title = item.get("title")
                external_path = item.get("externalPath")

                if not title or not external_path:
                    continue

                if external_path in seen_ids:
                    continue

                seen_ids.add(external_path)

                description = ""

                if fetch_descriptions:
                    description = await fetch_job_description(
                        client,
                        external_path
                    )

                    await asyncio.sleep(1)

                job_url = (
                    f"{HOST}/en-US/{SITE}{external_path}"
                )

                job = {
                    "title": title,
                    "company": "Workday",
                    "location": item.get(
                        "locationsText",
                        "Not specified"
                    ),
                    "description": description,
                    "source": "workday",
                    "source_url": job_url,
                    "is_active": True
                }

                jobs.append(job)

                if len(jobs) >= max_jobs:
                    break

            offset += PAGE_SIZE

            total = data.get("total")

            if isinstance(total, int) and offset >= total:
                break

            await asyncio.sleep(3)

    print(f"Total Workday jobs fetched: {len(jobs)}")

    return jobs
