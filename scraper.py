from playwright.sync_api import sync_playwright
from database import SessionLocal, Job

db = SessionLocal()

BASE_URL = "https://ssc.gov.in"
BASE_URL = "https://upsc.gov.in"

keywords = [
    "recruitment",
    "vacancy",
    "notification",
    "exam",
    "result",
    "admit",
    "candidate",
    "selection",
    "calendar"
]

bad_titles = [
    "for candidates",
    "browse by examinations",
    "departmental examination"
]

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto(BASE_URL)

    page.wait_for_timeout(5000)

    links = page.locator("a").all()

    for link in links:

        try:

            title = link.inner_text().strip()

            href = link.get_attribute("href")

            # Skip empty titles
            if not title:
                continue

            # Skip useless links
            if href is None or href == "#" or href == "/":
                continue

            # Skip social media links
            if "x.com" in str(href):
                continue

            # Make lowercase title
            lower_title = title.lower()

            # Skip bad titles
            if lower_title in bad_titles:
                continue

            # Check keywords
            if any(word in lower_title for word in keywords):

                # Create full link
                if href.startswith("/"):

                    full_link = BASE_URL + href

                else:
                    full_link = href

                # Avoid duplicates
                existing_job = db.query(Job).filter(Job.link == full_link).first()

                if not existing_job:

                    new_job = Job(
                        title=title,
                        link=full_link,
                        department="SSC"
                    )

                    db.add(new_job)
                    db.commit()

                    print("\nNEW JOB FOUND")
                    print("TITLE:", title)
                    print("LINK:", full_link)
                    print("-" * 50)

        except Exception as e:
            print("ERROR:", e)

    browser.close()