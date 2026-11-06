from kalshi_scrape import scrape_kalshi
from polymarket_scrape import scrape_polymarket

# Uncomment after you have the required credentials:
# from prophetx_scrape import scrape_prophetx
# from betfair_scrape import scrape_betfair
# from matchbook_scrape import scrape_matchbook


def main():

    print("\n--- KALSHI ---")
    kalshi = scrape_kalshi()
    print(
        "Kalshi markets:",
        len(kalshi["markets"])
    )

    print("\n--- POLYMARKET ---")
    polymarket = scrape_polymarket()
    print(
        "Polymarket markets:",
        len(polymarket["markets"])
    )

    # Example ProphetX:
    #
    # prophetx = scrape_prophetx(
    #     tournaments=["NBA", "NFL", "MLB"]
    # )

    # Example Betfair:
    #
    # betfair = scrape_betfair(
    #     sport_name="Basketball"
    # )

    # Example Matchbook:
    #
    # matchbook = scrape_matchbook(
    #     sport_name="Basketball"
    # )


if __name__ == "__main__":
    main()
