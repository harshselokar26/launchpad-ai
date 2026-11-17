
import asyncio
from app.scrapers.workday import scrape_workday


async def main():
    print("Testing Workday job scraper...")

    try:
        jobs = await scrape_workday(
            max_jobs=20,
            fetch_descriptions=False
        )

        print(f"\nJobs fetched: {len(jobs)}")

        for index, job in enumerate(jobs[:5], start=1):
            print(f"\n--- Job {index} ---")
            print("Title:", job["title"])
            print("Company:", job["company"])
            print("Location:", job["location"])
            print("URL:", job["source_url"])

    except Exception as error:
        print("\nScraper error:", error)


if __name__ == "__main__":
    asyncio.run(main())
