# --------------------------------------------------
# PROP TYPES WE CURRENTLY UNDERSTAND
# --------------------------------------------------

PROP_TYPES = [

    # MLB
    "Home Runs",
    "Total Bases",
    "Hits",
    "RBIs",

    # NBA
    "Points",
    "Rebounds",
    "Assists",
    "Threes",
    "3-Pointers Made",

    # NFL
    "Rush + Rec Yards",
    "Rushing + Receiving Yards",
    "Receiving Yards",
    "Rushing Yards",
    "Rush Yards",
    "Passing Yards",
    "Pass Yards",
    "Receptions",
    "Passing TDs",
    "Pass TDs",
]


# --------------------------------------------------
# CLEAN ODDS
# --------------------------------------------------

def normalize_odds(odds):

    odds = (
        odds
        .replace("−", "-")
        .strip()
    )

    if odds.upper() in (
        "EV",
        "EVEN"
    ):
        return 100

    return int(odds)


# --------------------------------------------------
# SPLIT PLAYER FROM MARKET
#
# Example:
#
# "Pierre Strong Jr. Rush + Rec Yards"
#
# becomes
#
# player = "Pierre Strong Jr."
# market = "Rush + Rec Yards"
# --------------------------------------------------

def find_prop_type(
    market_name
):

    # Check longer names first
    # so partial matches don't win.
    prop_types = sorted(
        PROP_TYPES,
        key=len,
        reverse=True
    )

    for prop_type in prop_types:

        if market_name.endswith(
            prop_type
        ):

            player = market_name[
                :-len(prop_type)
            ].strip()

            player = player.rstrip(
                "- "
            )

            return (
                player,
                prop_type
            )

    return None, None


# --------------------------------------------------
# PARSE DRAFTKINGS JSON
# --------------------------------------------------

def parse_draftkings(
    data,
    main_lines_only=True
):

    if not isinstance(
        data,
        dict
    ):
        return []

    markets = data.get(
        "markets",
        []
    )

    selections = data.get(
        "selections",
        []
    )

    props = []

    for market in markets:

        market_name = market.get(
            "name",
            ""
        )

        player, prop_type = (
            find_prop_type(
                market_name
            )
        )

        # Not one of the props we
        # currently care about.
        if prop_type is None:
            continue

        # ---------------------------------
        # FIND SELECTIONS BELONGING TO
        # THIS MARKET
        # ---------------------------------

        market_selections = []

        for selection in selections:

            if (
                selection.get("marketId")
                == market.get("id")
            ):

                market_selections.append(
                    selection
                )

        # ---------------------------------
        # CHECK WHETHER DRAFTKINGS MARKED
        # A MAIN LINE
        # ---------------------------------

        has_main_line = any(

            "MainPointLine"
            in selection.get(
                "tags",
                []
            )

            for selection
            in market_selections
        )

        # ---------------------------------
        # PROCESS SELECTIONS
        # ---------------------------------

        for selection in market_selections:

            # If DraftKings gives us a
            # MainPointLine, ignore alt lines.
            if (
                main_lines_only
                and has_main_line
                and "MainPointLine"
                not in selection.get(
                    "tags",
                    []
                )
            ):
                continue

            display_odds = (
                selection
                .get(
                    "displayOdds",
                    {}
                )
                .get(
                    "american"
                )
            )

            if display_odds is None:
                continue

            try:

                odds = normalize_odds(
                    display_odds
                )

            except ValueError:
                continue

            selection_text = (
                selection.get(
                    "label",
                    ""
                )
            )

            # ---------------------------------
            # 1+, 2+, 3+ MARKETS
            #
            # 1+ = Over 0.5
            # 2+ = Over 1.5
            # ---------------------------------

            if selection_text.endswith("+"):

                try:

                    amount = int(
                        selection_text.replace(
                            "+",
                            ""
                        )
                    )

                    line = (
                        amount - 0.5
                    )

                    selection_type = (
                        "Over"
                    )

                except ValueError:

                    line = (
                        selection.get(
                            "points"
                        )
                    )

                    selection_type = (
                        selection_text
                    )

            # ---------------------------------
            # NORMAL OVER / UNDER MARKET
            # ---------------------------------

            else:

                line = selection.get(
                    "points"
                )

                selection_type = (
                    selection_text
                )

            props.append({

                "event_id":
                    market.get(
                        "eventId"
                    ),

                "player":
                    player,

                "market":
                    prop_type,

                "selection":
                    selection_type,

                "line":
                    line,

                "odds":
                    odds,

                "sportsbook":
                    "DraftKings"
            })

    return props