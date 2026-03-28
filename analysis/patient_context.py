import re


def _extract_gender(text):
    if not text:
        return None

    match = re.search(r"\b(male|female)\b", text, re.IGNORECASE)
    if not match:
        return None

    return match.group(1).lower()


def _extract_age(text):
    if not text:
        return None

    patterns = [
        r"age\s*[/:-]\s*(\d{1,3})",
        r"age\s+(\d{1,3})\b",
        r"(\d{1,3})\s*(?:years|yrs)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            age = int(match.group(1))
            if 0 < age < 130:
                return age

    return None


def extract_patient_context(text):
    return {
        "gender": _extract_gender(text),
        "age": _extract_age(text),
    }
