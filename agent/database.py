"""
Database layer: saves each daily research run to Airtable.

Each day = one row with:
  - Date
  - The email digest (plain text)
  - Number of findings (total + HIGH-relevance count)
  - Companies mentioned (searchable text)
  - Full raw findings as JSON (for deep inspection)
"""

import json
import logging
from datetime import datetime

import config

logger = logging.getLogger(__name__)


def save_daily_record(findings: list[dict], digest: str) -> None:
    """
    Write one row to the Airtable base for today's research run.
    Safe to call even when Airtable is not configured — logs a warning and returns.
    """
    if not all([config.AIRTABLE_API_KEY, config.AIRTABLE_BASE_ID, config.AIRTABLE_TABLE_NAME]):
        logger.info("Airtable not configured — skipping database save.")
        return

    try:
        from pyairtable import Api  # imported here so missing package is a soft failure
    except ImportError:
        logger.warning(
            "pyairtable is not installed. Run: pip install pyairtable\n"
            "Skipping database save."
        )
        return

    try:
        api   = Api(config.AIRTABLE_API_KEY)
        table = api.table(config.AIRTABLE_BASE_ID, config.AIRTABLE_TABLE_NAME)

        companies_mentioned = ", ".join(
            sorted({f["company"] for f in findings})
        ) if findings else "—"

        high_count = sum(1 for f in findings if f.get("relevance") == "HIGH")

        record = {
            "Date":             datetime.now().strftime("%Y-%m-%d"),
            "Digest":           digest,
            "Findings Count":   len(findings),
            "High Relevance":   high_count,
            "Companies":        companies_mentioned,
            "Raw Findings":     json.dumps(findings, indent=2),
        }

        result = table.create(record)
        logger.info("Saved to Airtable: record id %s", result.get("id", "?"))

    except Exception as exc:
        # Never let a database failure break the email send
        logger.error("Airtable save failed (email was still sent): %s", exc)
