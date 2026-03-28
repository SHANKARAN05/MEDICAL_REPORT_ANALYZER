import re


RANGE_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:-|to|~|–|—)\s*(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)

BOUND_PATTERN = re.compile(r"(?:<|<=|>|>=)\s*\d+(?:\.\d+)?", re.IGNORECASE)

HEADER_WORDS = {
    "test",
    "tests",
    "parameter",
    "parameters",
    "investigation",
    "result",
    "results",
    "reference",
    "range",
    "unit",
}


def _normalize(value):
    return re.sub(r"\s+", " ", str(value)).strip()


def _extract_float(text):
    text = RANGE_PATTERN.sub("", text)
    text = BOUND_PATTERN.sub("", text)
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    return float(match.group())


def _extract_reference(text):
    match = RANGE_PATTERN.search(text)
    if match:
        return f"{match.group(1)} - {match.group(2)}"

    bound_match = BOUND_PATTERN.search(text)
    if bound_match:
        return bound_match.group(0).strip()

    return None


def _is_parameter_text(text):
    value = _normalize(text).lower()
    if not value or value in HEADER_WORDS:
        return False
    if not re.search(r"[a-z]", value):
        return False
    if re.fullmatch(r"[a-z]{1,3}", value):
        return False
    return True


def _is_probable_unit(text):
    value = _normalize(text)
    if not value:
        return False
    if _extract_reference(value):
        return False
    if _extract_float(value) is not None and re.search(r"[A-Za-z]", value) is None:
        return False
    return bool(re.fullmatch(r"[A-Za-z/%^0-9.\-]+", value))


def _as_rows(table):
    # Support both pandas.DataFrame and plain list-of-rows.
    if hasattr(table, "values"):
        return table.values.tolist()
    return table


def _extract_row_record(row):
    cleaned = ["" if cell is None else _normalize(cell) for cell in row]
    non_empty = [cell for cell in cleaned if cell]

    if len(non_empty) < 2:
        return None

    reference = None
    reference_idx = None
    for idx, cell in enumerate(cleaned):
        ref = _extract_reference(cell)
        if ref:
            reference = ref
            reference_idx = idx
            break

    # Candidate value columns are numeric-like cells that are not pure ranges.
    value_candidates = []
    for idx, cell in enumerate(cleaned):
        value = _extract_float(cell)
        if value is None:
            continue
        value_candidates.append((idx, value))

    if not value_candidates:
        return None

    # Prefer the first numeric value before reference column if available.
    value_idx = value_candidates[0][0]
    value = value_candidates[0][1]
    if reference_idx is not None:
        before_ref = [(idx, val) for idx, val in value_candidates if idx < reference_idx]
        if before_ref:
            value_idx, value = before_ref[0]

    # Parameter is nearest textual cell to the left of value, else first textual cell.
    parameter = None
    for idx in range(value_idx - 1, -1, -1):
        if _is_parameter_text(cleaned[idx]):
            parameter = cleaned[idx]
            break

    if not parameter:
        for cell in cleaned:
            if _is_parameter_text(cell):
                parameter = cell
                break

    if not parameter:
        return None

    unit = None
    for idx, cell in enumerate(cleaned):
        if idx in {value_idx, reference_idx}:
            continue
        if _is_probable_unit(cell):
            unit = cell
            break

    return {
        "parameter": parameter,
        "value": value,
        "unit": unit,
        "reference": reference,
    }


def parse_table_results(tables):

    results = []
    seen = set()

    for table in tables:

        rows = _as_rows(table)

        for row in rows:

            record = _extract_row_record(row)
            if not record:
                continue

            key = (
                record["parameter"].lower(),
                round(record["value"], 5),
                record["reference"] or "",
            )
            if key in seen:
                continue
            seen.add(key)

            results.append(record)

    return results