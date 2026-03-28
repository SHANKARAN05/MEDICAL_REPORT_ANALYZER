def calculate_health_score(analysis):

    score = 100

    for item in analysis:

        status = str(item.get("status") or "UNKNOWN").upper()
        flag = str(item.get("flag") or "UNKNOWN").upper()

        if flag == "HIGH":
            score -= 8
        elif flag == "LOW":
            score -= 6
        elif status == "BAD":
            score -= 6
        elif status == "UNKNOWN":
            score -= 2

    if score < 0:
        score = 0

    return score


def risk_level(score):

    if score >= 85:
        return "Low"

    elif score >= 65:
        return "Moderate"

    elif score >= 40:
        return "High"

    else:
        return "Critical"