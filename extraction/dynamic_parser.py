import re

# Words to ignore (noise from reports)
IGNORE_WORDS = [
    "page", "of", "date", "time", "age", "gender",
    "patient", "name", "id", "report", "sample",
    "collection", "referral", "male", "female",
    "jan", "feb", "mar", "apr", "may", "jun", "jul",
    "aug", "sep", "oct", "nov", "dec", "dummy", "delhi"
]

MEDICAL_KEYWORDS = [
    "hemoglobin", "wbc", "rbc", "platelet", "bilirubin", "glucose",
    "cholesterol", "triglyceride", "creatinine", "urea", "albumin",
    "globulin", "lymphocyte", "neutrophil", "monocyte", "eosinophil",
    "basophil", "cd3", "cd4", "cd8", "tsh", "t3", "t4", "vitamin",
    "protein", "calcium", "sodium", "potassium", "chloride", "ast",
    "alt", "sgot", "sgpt", "count", "cells", "ratio"
]

RANGE_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:-|to|~|–|—)\s*(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)

BOUND_PATTERN = re.compile(r"(?:<|<=|>|>=)\s*\d+(?:\.\d+)?", re.IGNORECASE)

VALUE_PATTERN = re.compile(r"-?\d+(?:\.\d+)?")

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
    "method",
}

DEMOGRAPHIC_MARKERS = {
    "age",
    "gender",
    "years",
    "yrs",
    "dob",
    "patient id",
}


def is_valid_parameter(param):
    param = param.lower().strip()

    # Remove very short words
    if len(param) < 3:
        return False

    # Skip obvious units/noise labels
    if param.startswith("/"):
        return False

    # Remove noise words
    for word in IGNORE_WORDS:
        if param == word:
            return False

    # Filter obvious header-like rows.
    if param in HEADER_WORDS:
        return False

    # Exclude demographic/context rows from lab parameter output.
    if any(marker in param for marker in DEMOGRAPHIC_MARKERS):
        return False

    return True


def normalize_text(value):
    return re.sub(r"\s+", " ", str(value)).strip()


def clean_parameter(value):
    value = normalize_text(value)
    value = re.sub(r"^[\-:|.\s]+", "", value)
    value = re.sub(r"[\-:|.\s]+$", "", value)
    return value


def extract_reference(text):
    match = RANGE_PATTERN.search(text)
    if match:
        return f"{match.group(1)} - {match.group(2)}"

    bound_match = BOUND_PATTERN.search(text)
    if bound_match:
        return bound_match.group(0).replace("  ", " ").strip()

    return None


def parse_value_unit(cell_text):
    # Ignore range values when searching for the primary result value.
    text = RANGE_PATTERN.sub("", cell_text)
    text = BOUND_PATTERN.sub("", text)

    match = re.search(r"(-?\d+(?:\.\d+)?)\s*([A-Za-z/%^0-9.]+)?", text)
    if not match:
        return None, None

    value = float(match.group(1))
    unit = match.group(2).strip() if match.group(2) else None
    return value, unit


def is_medical_candidate(parameter, unit, reference):
    parameter_l = parameter.lower()
    has_keyword = any(word in parameter_l for word in MEDICAL_KEYWORDS)

    # We accept entries with strong context (keyword/range/unit).
    return has_keyword or bool(reference) or bool(unit)


def looks_like_parameter(text):
    text = clean_parameter(text)

    if not text:
        return False

    if not re.search(r"[A-Za-z]", text):
        return False

    if re.fullmatch(r"[A-Za-z]{1,3}", text):
        return False

    if text.lower() in HEADER_WORDS:
        return False

    # Exclude mostly numeric/symbolic tokens.
    alpha_count = len(re.findall(r"[A-Za-z]", text))
    if alpha_count < max(2, len(text) // 5):
        return False

    return is_valid_parameter(text)


def parse_from_parts(parts, pending_parameter=None):
    if len(parts) < 2:
        return None

    parameter = clean_parameter(parts[0])
    candidates = parts[1:]

    if not looks_like_parameter(parameter):
        if pending_parameter and looks_like_parameter(pending_parameter):
            parameter = clean_parameter(pending_parameter)
            candidates = parts
        else:
            return None

    reference = None
    value = None
    unit = None

    for cell in candidates:
        if not reference:
            reference = extract_reference(cell)

        if value is None:
            parsed_value, parsed_unit = parse_value_unit(cell)
            if parsed_value is not None:
                value = parsed_value
                unit = parsed_unit

    if value is None:
        return None

    return {
        "parameter": parameter,
        "value": value,
        "unit": unit,
        "reference": reference,
    }


def parse_inline_line(line, pending_parameter=None):
    # Pattern: "Parameter: 12.3 mg/dL 4.0 - 10.0"
    colon_match = re.search(
        r"^(?P<parameter>[A-Za-z][A-Za-z0-9 ()/+%.-]{2,}?)\s*[:=-]\s*"
        r"(?P<value>-?\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z/%^0-9.]+)?",
        line,
    )
    if colon_match:
        return {
            "parameter": clean_parameter(colon_match.group("parameter")),
            "value": float(colon_match.group("value")),
            "unit": colon_match.group("unit") or None,
            "reference": extract_reference(line),
        }

    # Pattern: "Parameter 12.3 mg/dL"
    inline_match = re.search(
        r"^(?P<parameter>[A-Za-z][A-Za-z0-9 ()/+%.-]{2,}?)\s+"
        r"(?P<value>-?\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z/%^0-9.]+)?",
        line,
    )
    if inline_match and looks_like_parameter(inline_match.group("parameter")):
        return {
            "parameter": clean_parameter(inline_match.group("parameter")),
            "value": float(inline_match.group("value")),
            "unit": inline_match.group("unit") or None,
            "reference": extract_reference(line),
        }

    # Two-line fallback: pending parameter + numeric row.
    if pending_parameter and looks_like_parameter(pending_parameter):
        value, unit = parse_value_unit(line)
        if value is not None:
            return {
                "parameter": clean_parameter(pending_parameter),
                "value": value,
                "unit": unit,
                "reference": extract_reference(line),
            }

    return None


def parse_text_results(text):

    if not text:
        return []

    results = []
    seen = set()
    pending_parameter = None

    for raw_line in text.splitlines():
        line = normalize_text(raw_line)

        if not line:
            continue

        if not re.search(r"\d", line):
            if looks_like_parameter(line):
                pending_parameter = clean_parameter(line)
            continue

        parts = [p.strip() for p in re.split(r"\t+|\s{2,}|\s*\|\s*", line) if p.strip()]
        parsed = parse_from_parts(parts, pending_parameter=pending_parameter)

        if not parsed:
            parsed = parse_inline_line(line, pending_parameter=pending_parameter)

        if not parsed:
            continue

        parameter = clean_parameter(parsed["parameter"])
        value = parsed["value"]
        unit = parsed["unit"]
        reference = parsed["reference"]

        if not is_valid_parameter(parameter):
            continue

        if not is_medical_candidate(parameter, unit, reference):
            continue

        if value <= 0:
            continue

        key = (parameter.lower(), round(value, 5), reference or "")
        if key in seen:
            continue
        seen.add(key)

        results.append(
            {
                "parameter": parameter,
                "value": value,
                "unit": unit,
                "reference": reference,
            }
        )

        # Once used, clear pending parameter so it does not leak to next rows.
        pending_parameter = None

    return results