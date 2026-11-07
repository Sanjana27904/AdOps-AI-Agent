
from app.tools.campaign_tools import (
    get_campaign_summary,
    get_campaign_daily_data
)
from app.tools.analysis_tools import (
    calculate_metrics,
    detect_anomalies
)


def run_evaluations():
    passed = 0
    failed = 0

    print("\nAdOps Agent - Evaluation Results")
    print("--------------------------------")

    # Test 1: CMP103 should be identified as over budget
    campaign = get_campaign_summary("CMP103")
    metrics = calculate_metrics(campaign)

    if (
        metrics["over_budget"] is True
        and metrics["total_spend"] == 1350
        and metrics["budget"] == 900
        and metrics["budget_usage_percent"] == 150.0
    ):
        print("[PASS] CMP103 budget overrun detection")
        passed += 1
    else:
        print("[FAIL] CMP103 budget overrun detection")
        failed += 1

    # Test 2: CMP102 should detect an impression drop
    daily_data = get_campaign_daily_data("CMP102")
    anomalies = detect_anomalies(daily_data)

    if (
        len(anomalies) == 1
        and anomalies[0]["date"] == "2026-11-04"
        and anomalies[0]["decrease_percent"] == 69.57
    ):
        print("[PASS] CMP102 impression drop detection")
        passed += 1
    else:
        print("[FAIL] CMP102 impression drop detection")
        failed += 1

    # Test 3: CMP101 should have no detected anomalies
    daily_data = get_campaign_daily_data("CMP101")
    anomalies = detect_anomalies(daily_data)

    if len(anomalies) == 0:
        print("[PASS] CMP101 no-anomaly detection")
        passed += 1
    else:
        print("[FAIL] CMP101 no-anomaly detection")
        failed += 1

    print("\n--------------------------------")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("--------------------------------")


if __name__ == "__main__":
    run_evaluations()
