def odds_to_percentage(odds):

    if odds < 0:

        return (
            abs(odds)
            /
            (abs(odds) + 100)
        )

    elif odds > 0:

        return (
            100
            /
            (odds + 100)
        )

    else:

        raise ValueError(
            "Odds cannot be zero"
        )