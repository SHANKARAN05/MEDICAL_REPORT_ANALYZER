from extraction.dynamic_parser import parse_text_results
from extraction.table_parser import parse_table_results


EXCLUDED_PARAMETER_MARKERS = {
    "age",
    "gender",
    "years",
    "yrs",
    "dob",
    "patient id",
}


def _is_excluded_parameter(parameter):
    text = str(parameter or "").strip().lower()
    if not text:
        return True
    return any(marker in text for marker in EXCLUDED_PARAMETER_MARKERS)


def parse_report(text, tables=None):
    """
    Master parser controller
    Decides whether to parse tables or raw text
    """

    table_results = parse_table_results(tables) if tables else []
    text_results = parse_text_results(text)

    # Merge both sources and de-duplicate by parameter/value/reference.
    merged = []
    seen = set()

    for item in table_results + text_results:
        if _is_excluded_parameter(item.get("parameter")):
            continue

        key = (
            str(item.get("parameter", "")).strip().lower(),
            round(float(item.get("value", 0)), 5),
            str(item.get("reference") or "").strip(),
        )

        if key in seen:
            continue

        seen.add(key)
        merged.append(item)

    return merged