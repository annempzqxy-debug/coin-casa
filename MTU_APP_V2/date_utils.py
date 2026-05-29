from datetime import date


INVALID_DATE_MESSAGE = "Invalid date. Supported examples: 2026-05-28, 05/28/2026, 28.05.2026, 20260528, 28 May 2026, 2026 May 28."


def today_str():
    return date.today().isoformat()


def week_key(dstr):
    dt = date.fromisoformat(dstr)
    y, w, _ = dt.isocalendar()
    return f"{y}-W{w:02d}"


def month_key(dstr):
    return dstr[:7]


def year_key(dstr):
    return dstr[:4]


def _month_number(month_str):
    months = {
        "january": 1, "jan": 1,
        "february": 2, "feb": 2,
        "march": 3, "mar": 3,
        "april": 4, "apr": 4,
        "may": 5,
        "june": 6, "jun": 6,
        "july": 7, "jul": 7,
        "august": 8, "aug": 8,
        "september": 9, "sep": 9, "sept": 9,
        "october": 10, "oct": 10,
        "november": 11, "nov": 11,
        "december": 12, "dec": 12,
    }
    return months.get(month_str.strip().lower(), 0)


def parse_flexible_date(input_date):
    """Parse the Halcon lab date formats and return YYYY-MM-DD."""
    value = input_date.strip().replace(",", "")
    if not value:
        return today_str()

    year = month = day = None

    try:
        if "-" in value:
            parts = value.split("-")
            if len(parts) == 3:
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
        elif "/" in value:
            parts = value.split("/")
            if len(parts) == 3:
                month = int(parts[0])
                day = int(parts[1])
                year = int(parts[2])
        elif "." in value:
            parts = value.split(".")
            if len(parts) == 3:
                day = int(parts[0])
                month = int(parts[1])
                year = int(parts[2])
        elif value.isdigit() and len(value) == 8:
            year = int(value[0:4])
            month = int(value[4:6])
            day = int(value[6:8])
        else:
            parts = value.split()
            if len(parts) == 3:
                if parts[0].isdigit() and len(parts[0]) == 4:
                    year = int(parts[0])
                    month = _month_number(parts[1])
                    day = int(parts[2])
                elif parts[0].isdigit():
                    day = int(parts[0])
                    month = _month_number(parts[1])
                    year = int(parts[2])
                else:
                    month = _month_number(parts[0])
                    day = int(parts[1])
                    year = int(parts[2])

        if year is None or month is None or day is None:
            raise ValueError(INVALID_DATE_MESSAGE)

        return date(year, month, day).isoformat()
    except (TypeError, ValueError):
        raise ValueError(INVALID_DATE_MESSAGE)
