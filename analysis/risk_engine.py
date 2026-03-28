import re

from analysis.range_detector import parse_range
from analysis.reference_lookup import get_reference_for_parameter


def _parse_single_bound(reference):
    if not reference:
        return None, None

    lt_match = re.search(r"^\s*(?:<|<=)\s*(\d+(?:\.\d+)?)\s*$", reference)
    if lt_match:
        return "LT", float(lt_match.group(1))

    gt_match = re.search(r"^\s*(?:>|>=)\s*(\d+(?:\.\d+)?)\s*$", reference)
    if gt_match:
        return "GT", float(gt_match.group(1))

    return None, None


def detect_risks(results, patient_context=None):

    patient_context = patient_context or {}
    gender = patient_context.get("gender")
    age = patient_context.get("age")

    analysis = []

    for item in results:

        value = item.get("value")
        reference = item.get("reference")
        unit = item.get("unit")
        parameter = item.get("parameter")

        status = "UNKNOWN"
        flag = "UNKNOWN"

        if value is None:
            continue

        # If the report does not provide reference range, use local medical KB.
        if not reference:
            reference = get_reference_for_parameter(parameter, gender=gender, age=age)

        if reference:

            low, high = parse_range(reference)

            if low is not None and high is not None:

                if value < low:
                    status = "BAD"
                    flag = "LOW"

                elif value > high:
                    status = "BAD"
                    flag = "HIGH"

                else:
                    status = "GOOD"
                    flag = "NORMAL"

            else:
                bound_type, bound_value = _parse_single_bound(reference)

                if bound_type == "LT":
                    status = "GOOD" if value < bound_value else "BAD"
                    flag = "NORMAL" if value < bound_value else "HIGH"

                elif bound_type == "GT":
                    status = "GOOD" if value > bound_value else "BAD"
                    flag = "NORMAL" if value > bound_value else "LOW"

        analysis.append({
            "parameter": parameter,
            "value": value,
            "unit": unit,
            "reference": reference,
            "flag": flag,
            "status": status
        })

    return analysis