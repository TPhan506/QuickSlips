from probability import odds_to_percentage

from draft_kings_scrape import (
    scrape_draftkings_mlb,
    scrape_draftkings_nba,
    scrape_draftkings_nfl
)

from draft_kings_parser import parse_draftkings


SPORT = "nfl"

TOP_RESULTS = 100

MIN_ODDS = -130
MAX_ODDS = 140

#get draftking props

def get_draftkings_props(sport):

    if sport == "mlb":

        raw_data = scrape_draftkings_mlb(
            headless=False
        )

    elif sport == "nba":

        raw_data = scrape_draftkings_nba(
            headless=False
        )

    elif sport == "nfl":

        raw_data = scrape_draftkings_nfl(
            headless=False
        )

    else:

        raise ValueError(
            f"Unknown sport: {sport}"
        )

    all_props = []

    for response in raw_data["network_json"]:

        if (
            "sportscontent" in response["url"]
            and "/markets?" in response["url"]
        ):

            props = parse_draftkings(
                response["data"],
                main_lines_only=True
            )

            all_props.extend(
                props
            )

    # Add implied probability to every prop
    for prop in all_props:

        prop["probability"] = (
            odds_to_percentage(
                prop["odds"]
            )
        )

    return all_props



# FILTER ODDS


def filter_odds(
    props,
    min_odds,
    max_odds
):

    filtered_props = []

    for prop in props:

        if (
            min_odds
            <= prop["odds"]
            <= max_odds
        ):

            filtered_props.append(
                prop
            )

    return filtered_props



# SORT


def sort_props(
    props,
    sort_value
):

    return sorted(
        props,
        key=lambda prop:
            prop[sort_value],
        reverse=True
    )


# CREATE UNDER LOOKUP

def get_under_lookup(props):

    under_lookup = {}

    for prop in props:

        if prop["selection"] == "Under":

            key = (
                prop["event_id"],
                prop["player"],
                prop["market"],
                prop["line"]
            )

            under_lookup[key] = prop

    return under_lookup


# PRINT TOP OVER PROPS WITH MATCHING UNDER

def print_top_props(
    filtered_props,
    all_props,
    top_results
):



    under_lookup = get_under_lookup(
        all_props
    )

    # Only rank Overs
    overs = []

    for prop in filtered_props:

        if prop["selection"] == "Over":

            overs.append(
                prop
            )

    overs = sort_props(
        overs,
        "probability"
    )

    print(
        f"\nTOP {top_results} PLAYER PROPS\n"
    )

    for prop in overs[:top_results]:

        key = (
            prop["event_id"],
            prop["player"],
            prop["market"],
            prop["line"]
        )

        under = under_lookup.get(
            key
        )

        if under:

            print(
                prop["player"],
                "|",
                prop["market"],
                prop["line"],
                "| OVER:",
                prop["odds"],
                f'({prop["probability"]:.2%})',
                "| UNDER:",
                under["odds"],
                f'({under["probability"]:.2%})'
            )

        else:

            print(
                prop["player"],
                "|",
                prop["market"],
                prop["line"],
                "| OVER:",
                prop["odds"],
                f'({prop["probability"]:.2%})',
                "| UNDER: N/A"
            )


# MAIN

def main():

    all_props = get_draftkings_props(
        SPORT
    )

    print(
        "\nTOTAL BEFORE FILTER:",
        len(all_props)
    )

    # Filter only for which props
    filtered_props = filter_odds(
        all_props,
        MIN_ODDS,
        MAX_ODDS
    )

    print(
        "TOTAL AFTER FILTER:",
        len(filtered_props)
    )

    print_top_props(
        filtered_props,
        all_props,
        TOP_RESULTS
    )


if __name__ == "__main__":
    main()