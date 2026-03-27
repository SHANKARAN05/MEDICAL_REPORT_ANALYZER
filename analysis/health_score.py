def calculate_health_score(analysis):

    score = 100

    for item in analysis:

        if item["status"] == "HIGH":
            score -= 5

        elif item["status"] == "LOW":
            score -= 5

    if score < 0:
        score = 0

    return score
def risk_level(score):

    if score >= 85:
        return "Healthy"

    elif score >= 65:
        return "Moderate Risk"

    elif score >= 40:
        return "High Risk"

    else:
        return "Critical"