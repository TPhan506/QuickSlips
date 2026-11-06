from playwright.sync_api import sync_playwright
from datetime import datetime, timezone
from pathlib import Path
import json


MLB_URL = "https://sportsbook.draftkings.com/leagues/baseball/mlb"
NBA_URL = "https://sportsbook.draftkings.com/leagues/basketball/nba"
NFL_URL = "https://sportsbook.draftkings.com/leagues/football/nfl"


# PROP BUTTONS TO COLLECT

MLB_PROPS = [
    "Home Runs",
    "Hits",
    "Total Bases",
    "RBIs",
]


NBA_PROPS = [
    "Points",
    "Rebounds",
    "Assists",
    "Threes",
    "Pts + Reb + Ast",
]


NFL_PROPS = [
    "Pass Yards",
    "Receiving Yards",
    "Rush Yards",
    "Receptions",
    "Pass TDs",
    "Rush + Rec Yards",
]



# DRAFTKINGS SCRAPER


def scrape_draftkings(
    url,
    buttons,
    first_category=None,
    sport="unknown",
    headless=False
):

    captured_json = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=headless
        )

        page = browser.new_page()

   
        # WATCH ALL DRAFTKINGS JSON
        # RESPONSES
       

        def handle_response(response):

            try:

                resource_type = (
                    response.request.resource_type
                )

                content_type = (
                    response.headers.get(
                        "content-type",
                        ""
                    )
                )

                if (
                    resource_type in ("xhr", "fetch")
                    and "json" in content_type.lower()
                    and "draftkings" in response.url.lower()
                ):

                    body = response.json()

                    captured_json.append({
                        "url": response.url,
                        "data": body
                    })

            except Exception:
                pass


        page.on(
            "response",
            handle_response
        )

        # LOAD SPORT PAGE

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(3000)

        # OPEN CATEGORY
        # MLB -> Batter
        # NBA -> Player Props
        # NFL -> Player Props

        if first_category:

            category_button = (
                page.get_by_text(
                    first_category,
                    exact=True
                )
            )

            print(
                first_category,
                "matches:",
                category_button.count()
            )

            if category_button.count() > 0:

                print(
                    "Opening:",
                    first_category
                )

                category_button.first.click()

                page.wait_for_timeout(2000)

            else:

                print(
                    "Could not find category:",
                    first_category
                )

        # CLICK THROUGH PROP MARKETS

        for button_name in buttons:

            button = page.get_by_text(
                button_name,
                exact=True
            )

            print(
                button_name,
                "matches:",
                button.count()
            )

            if button.count() == 0:

                print(
                    "Could not find:",
                    button_name
                )

                continue

            print(
                "Collecting:",
                button_name
            )

            try:

                # Wait for the actual market
                with page.expect_response(
                    lambda response:
                        "/markets?" in response.url
                        and "sportscontent" in response.url,
                    timeout=10000
                ) as response_info:

                    button.first.click()

                market_response = (
                    response_info.value
                )

                print(
                    "Market URL:",
                    market_response.url
                )

            except Exception:

                print(
                    "No new market response for:",
                    button_name
                )

        browser.close()

    # PACKAGE RAW DATA

    result = {

        "sportsbook": "DraftKings",

        "sport": sport,

        "url": url,

        "scraped_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "network_json": captured_json
    }

    save_raw_data(
        result,
        sport
    )

    return result


# MLB

def scrape_draftkings_mlb(
    headless=False
):

    return scrape_draftkings(
        url=MLB_URL,
        first_category="Batter",
        buttons=MLB_PROPS,
        sport="mlb",
        headless=headless
    )


# NBA

def scrape_draftkings_nba(
    headless=False
):

    return scrape_draftkings(
        url=NBA_URL,
        first_category="Player Props",
        buttons=NBA_PROPS,
        sport="nba",
        headless=headless
    )


# NFL

def scrape_draftkings_nfl(
    headless=False
):

    return scrape_draftkings(
        url=NFL_URL,
        first_category="Player Props",
        buttons=NFL_PROPS,
        sport="nfl",
        headless=headless
    )


# SAVE RAW JSON

def save_raw_data(
    data,
    sport
):

    folder = Path(
        f"data/raw/draftkings/{sport}"
    )

    folder.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = folder / (
        f"draftkings_{sport}_{timestamp}.json"
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2
        )

    print(
        f"\nSaved raw DraftKings {sport.upper()} data:",
        filename
    )