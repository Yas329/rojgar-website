from playwright.sync_api import sync_playwright
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from urllib.parse import urljoin
import time

# ==========================================
# DATABASE SETUP
# ==========================================

DATABASE_URL = "sqlite:///jobs.db"

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    link = Column(String, unique=True)
    department = Column(String)

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# ==========================================
# SCRAPER START
# ==========================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True,
        slow_mo=50
    )

    # IMPORTANT FIX: ignore SSL issues
    context = browser.new_context(
        ignore_https_errors=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
    )

    websites = [
        # UPSC / SSC
    {"name": "SSC", "url": "https://ssc.gov.in"},
    {"name": "UPSC", "url": "https://www.upsc.gov.in"},

    # Banking
    {"name": "IBPS", "url": "https://www.ibps.in"},
    {"name": "SBI", "url": "https://sbi.co.in/web/careers"},
    {"name": "RBI", "url": "https://opportunities.rbi.org.in"},
    {"name": "NABARD", "url": "https://www.nabard.org"},

    # Railways
    {"name": "RRB", "url": "https://www.rrbcdg.gov.in"},
    {"name": "RRC", "url": "https://rrcrail.in"},

    # Defense
    {"name": "Indian Army", "url": "https://joinindianarmy.nic.in"},
    {"name": "Indian Navy", "url": "https://www.joinindiannavy.gov.in"},
    {"name": "Indian Air Force", "url": "https://agnipathvayu.cdac.in"},
    {"name": "BSF", "url": "https://rectt.bsf.gov.in"},
    {"name": "CRPF", "url": "https://rect.crpf.gov.in"},
    {"name": "CISF", "url": "https://cisfrectt.cisf.gov.in"},
    {"name": "ITBP", "url": "https://recruitment.itbpolice.nic.in"},
    

    # Police
    {"name": "UP Police", "url": "https://uppbpb.gov.in"},
    {"name": "Delhi Police", "url": "https://delhipolice.gov.in"},
    {"name": "Bihar Police", "url": "https://csbc.bih.nic.in"},

    # Teaching
    {"name": "KVS", "url": "https://kvsangathan.nic.in"},
    {"name": "NVS", "url": "https://navodaya.gov.in"},
    {"name": "DSSSB", "url": "https://dsssb.delhi.gov.in"},
    {"name": "CTET", "url": "https://ctet.nic.in"},

    # PSU
    {"name": "ONGC", "url": "https://ongcindia.com"},
    {"name": "BHEL", "url": "https://careers.bhel.in"},
    {"name": "NTPC", "url": "https://careers.ntpc.co.in"},
    {"name": "IOCL", "url": "https://iocl.com"},
    {"name": "HPCL", "url": "https://hindustanpetroleum.com"},
    {"name": "BPCL", "url": "https://www.bharatpetroleum.in"},
    {"name": "GAIL", "url": "https://gailonline.com"},
    {"name": "SAIL", "url": "https://sailcareers.com"},
    {"name": "BEL", "url": "https://bel-india.in"},
    {"name": "HAL", "url": "https://hal-india.co.in"},
    {"name": "Coal India", "url": "https://www.coalindia.in"},
    {"name": "Power Grid", "url": "https://www.powergrid.in"},
    {"name": "NHPC", "url": "https://www.nhpcindia.com"},
    {"name": "DRDO", "url": "https://www.drdo.gov.in"},
    {"name": "ISRO", "url": "https://www.isro.gov.in"},

    # State PSC
    {"name": "UPPSC", "url": "https://uppsc.up.nic.in"},
    {"name": "BPSC", "url": "https://bpsc.bih.nic.in"},
    {"name": "MPPSC", "url": "https://mppsc.mp.gov.in"},
    {"name": "RPSC", "url": "https://rpsc.rajasthan.gov.in"},

    # Judiciary
    {"name": "Supreme Court", "url": "https://www.sci.gov.in"},
    {"name": "Allahabad High Court", "url": "https://www.allahabadhighcourt.in"},

    # Healthcare
    {"name": "AIIMS", "url": "https://www.aiimsexams.ac.in"},
    {"name": "ESIC", "url": "https://www.esic.gov.in"},

    # Postal
    {"name": "India Post", "url": "https://indiapostgdsonline.gov.in"},

    # Metro
    {"name": "DMRC", "url": "https://delhimetrorail.com"},
    {"name": "UPMRC", "url": "https://www.lmrcl.com"},

    # Aviation
    {"name": "AAI", "url": "https://www.aai.aero"},

    # Investigation
    {"name": "CBI", "url": "https://cbi.gov.in"},
    {"name": "NIA", "url": "https://nia.gov.in"},
    ]

    keywords = [
        "recruitment", "vacancy", "notification", "exam",
        "result", "admit", "apply", "job", "career",
        "answer key", "final result", "online form" , "AFCAT"
    ]

    bad_titles = [
        "home", "login", "contact", "about",
        "privacy", "terms"
    ]

    for site in websites:

        print("\n" + "=" * 60)
        print(f"SCRAPING : {site['name']}")
        print("=" * 60)

        page = context.new_page()

        try:
            page.goto(site["url"], timeout=90000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)

            links = page.locator("a")
            count = links.count()

            print("TOTAL LINKS:", count)

            saved = 0

            for i in range(count):

                try:
                    link = links.nth(i)

                    title = link.inner_text().strip()
                    href = link.get_attribute("href")

                    if not title or not href:
                        continue

                    if len(title) < 3:
                        continue

                    if href in ["#", "/", "javascript:void(0)"]:
                        continue

                    if any(x in href.lower() for x in ["facebook", "youtube", "instagram", "twitter", "linkedin"]):
                        continue

                    lower_title = title.lower()

                    if any(b in lower_title for b in bad_titles):
                        continue

                    if any(k in lower_title for k in keywords):

                        full_link = urljoin(site["url"], href)

                        print("\nMATCH:", title)
                        print("LINK :", full_link)

                        exists = db.query(Job).filter(Job.link == full_link).first()

                        if not exists:

                            db.add(Job(
                                title=title,
                                link=full_link,
                                department=site["name"]
                            ))
                            db.commit()

                            saved += 1
                            print("SAVED")

                except Exception:
                    continue

            print("NEW SAVED:", saved)

        except Exception as e:
            print("ERROR:", site["name"], e)

        finally:
            page.close()

    browser.close()

print("\nSCRAPING COMPLETED")