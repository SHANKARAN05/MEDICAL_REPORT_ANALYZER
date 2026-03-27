from analysis.range_detector import parse_range


def detect_risks(results):

    analysis = []

    for item in results:

        value = item.get("value")
        reference = item.get("reference")

        status = "UNKNOWN"

        if reference:

            low, high = parse_range(reference)

            if low is not None and high is not None:

                if value < low:
                    status = "LOW"

                elif value > high:
                    status = "HIGH"

                else:
                    status = "NORMAL"

        analysis.append({
            "parameter": item.get("parameter"),
            "value": value,
            "status": status
        })

    return analysis