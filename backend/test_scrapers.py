
import asyncio

from app.scrapers.greenhouse import scrape_greenhouse
from app.scrapers.lever import scrape_lever


# Keep empty until we have verified company identifiers.
GREENHOUSE_BOARDS = []
LEVER_SITES = []


async def main():
    for board in GREENHOUSE_BOARDS:
        try:
            jobs = await scrape_greenhouse(board)
            print(f"\nGreenhouse: {board}")
            print(f"Jobs found: {len(jobs)}")

            if jobs:
                print(jobs[0])

        except Exception as error:
            print(f"Greenhouse error for {board}: {error}")

    for site in LEVER_SITES:
        try:
            jobs = await scrape_lever(site)
            print(f"\nLever: {site}")
            print(f"Jobs found: {len(jobs)}")

            if jobs:
                print(jobs[0])

        except Exception as error:
            print(f"Lever error for {site}: {error}")


if __name__ == "__main__":
    asyncio.run(main())
