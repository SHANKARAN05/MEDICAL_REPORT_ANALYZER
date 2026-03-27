import re

# ❌ Words to ignore (noise from reports)
IGNORE_WORDS = [
    "page", "of", "date", "time", "age", "gender",
    "patient", "name", "id", "report", "sample",
    "collection", "referral", "male", "female",
    "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "oct", "nov", "dec"
]


def is_valid_parameter(param):
    param = param.lower().strip()

    # Remove very short words
    if len(param) < 3:
        return False

    # Remove noise words
    for word in IGNORE_WORDS:
        if param == word:
            return False

    return True


def parse_text_results(text):

    results = []

    # Improved regex
    pattern = r'([A-Za-z ()/%]+)\s+(\d{1,6}\.?\d*)'

    matches = re.findall(pattern, text)

    for match in matches:

        parameter = match[0].strip()
        value = float(match[1])

        # ✅ Filter invalid parameters
        if not is_valid_parameter(parameter):
            continue

        # ✅ Remove unrealistic values (optional safety)
        if value <= 0:
            continue

        results.append({
            "parameter": parameter,
            "value": value
        })

    return results