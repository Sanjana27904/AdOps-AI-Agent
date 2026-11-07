
from app.database.db import get_connection


def list_campaigns():
    """Retrieve all available campaign IDs."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT DISTINCT campaign_id
            FROM campaigns
            ORDER BY campaign_id
        """)

        campaigns = cursor.fetchall()

        return [row[0] for row in campaigns]

    finally:
        connection.close()


def get_campaign_summary(campaign_id):
    """Retrieve aggregated performance data for a campaign."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                campaign_id,
                SUM(impressions),
                SUM(clicks),
                SUM(spend),
                SUM(conversions),
                MAX(budget),
                COUNT(DISTINCT date)
            FROM campaigns
            WHERE campaign_id = ?
            GROUP BY campaign_id
        """, (campaign_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "campaign_id": row[0],
            "total_impressions": row[1],
            "total_clicks": row[2],
            "total_spend": row[3],
            "total_conversions": row[4],
            "budget": row[5],
            "reporting_days": row[6]
        }

    finally:
        connection.close()


def get_campaign_daily_data(campaign_id):
    """Retrieve daily performance records for a campaign."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                date,
                impressions,
                clicks,
                spend,
                conversions
            FROM campaigns
            WHERE campaign_id = ?
            ORDER BY date
        """, (campaign_id,))

        rows = cursor.fetchall()

        return [
            {
                "date": row[0],
                "impressions": row[1],
                "clicks": row[2],
                "spend": row[3],
                "conversions": row[4]
            }
            for row in rows
        ]

    finally:
        connection.close()
