
def calculate_metrics(campaign):
    """Calculate campaign performance metrics."""

    impressions = campaign["total_impressions"]
    clicks = campaign["total_clicks"]
    spend = campaign["total_spend"]
    conversions = campaign["total_conversions"]
    budget = campaign["budget"]

    ctr = (clicks / impressions * 100) if impressions else 0

    conversion_rate = (
        conversions / clicks * 100
    ) if clicks else 0

    budget_usage = (
        spend / budget * 100
    ) if budget else 0

    return {
        "campaign_id": campaign["campaign_id"],
        "ctr_percent": round(ctr, 2),
        "conversion_rate_percent": round(conversion_rate, 2),
        "total_spend": round(spend, 2),
        "budget": round(budget, 2),
        "budget_usage_percent": round(budget_usage, 2),
        "over_budget": spend > budget
    }


def detect_anomalies(daily_records):
    """Identify unusually large day-to-day impression decreases."""

    anomalies = []

    for index in range(1, len(daily_records)):

        previous = daily_records[index - 1]
        current = daily_records[index]

        previous_impressions = previous["impressions"]
        current_impressions = current["impressions"]

        if previous_impressions == 0:
            continue

        decrease_percent = (
            (previous_impressions - current_impressions)
            / previous_impressions
        ) * 100

        if decrease_percent >= 40:

            anomalies.append({
                "date": current["date"],
                "previous_impressions": previous_impressions,
                "current_impressions": current_impressions,
                "decrease_percent": round(decrease_percent, 2),
                "issue": "Significant decrease in impressions"
            })

    return anomalies
