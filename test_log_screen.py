"""
test_log_screen.py
------------------
Automated test suite verifying the Log screen analytics tiles,
CSS horizontal bar chart, 50-item table with Demo data badge, and CSV export.
"""

import io
import csv
from app import app
import database

def run_tests():
    print("--- Starting Log Screen & Analytics Verification ---")
    database.init_db()
    client = app.test_client()

    # 1. Verify summary stats computation
    stats = database.get_log_summary_stats()
    assert stats["total_items"] >= 30, f"Expected at least 30 items, got {stats['total_items']}"
    assert "sent_to_supervisor_pct" in stats
    assert "ai_accepted_pct" in stats
    assert "items_this_week" in stats
    print(f"[PASS] Summary stats verified: Total={stats['total_items']}, Sent to Supervisor={stats['sent_to_supervisor_pct']}%, AI Accepted={stats['ai_accepted_pct']}%, This Week={stats['items_this_week']}")

    # 2. Verify waste stream counts for CSS bar chart
    stream_counts = database.get_waste_stream_counts()
    assert len(stream_counts) == 6, f"Expected 6 streams, got {len(stream_counts)}"
    for sc in stream_counts:
        assert "stream_name" in sc
        assert "bin_colour" in sc
        assert "count" in sc
        assert "bar_pct" in sc
        assert 0 <= sc["bar_pct"] <= 100
    print("[PASS] Waste stream distribution counts & bar percentage widths verified.")

    # 3. Verify GET /log renders HTML tiles, chart, and table
    resp = client.get("/log")
    assert resp.status_code == 200
    assert b"Waste Audit Log" in resp.data
    assert b"Total Items" in resp.data
    assert b"Sent to Supervisor" in resp.data
    assert b"AI Accepted" in resp.data
    assert b"Items This Week" in resp.data

    # Check CSS bar chart elements in HTML
    assert b"Waste Stream Distribution" in resp.data
    assert b"chart-track" in resp.data
    assert b"chart-fill" in resp.data

    # Check table columns
    assert b"Date / Time" in resp.data
    assert b"Waste Stream" in resp.data
    assert b"Confidence" in resp.data
    assert b"Status" in resp.data
    assert b"Decided By" in resp.data

    # Check Demo data badge
    assert b"Demo data" in resp.data
    print("[PASS] GET /log rendered summary tiles, CSS bar chart, recent items table, and Demo data badges.")

    # 4. Verify CSV Export
    resp_csv = client.get("/log/export-csv")
    assert resp_csv.status_code == 200
    assert resp_csv.mimetype == "text/csv"
    assert "Content-Disposition" in resp_csv.headers

    csv_text = resp_csv.data.decode("utf-8")
    csv_reader = csv.reader(io.StringIO(csv_text))
    rows = list(csv_reader)
    header = rows[0]
    assert "Record ID" in header
    assert "Waste Stream" in header
    assert "Confidence" in header
    assert "Status" in header
    assert "Is Demo Data" in header
    assert len(rows) >= 31 # header + 30 rows
    print(f"[PASS] CSV Export verified: {len(rows)-1} records exported with correct headers.")

    print("\n[ALL LOG SCREEN TESTS PASSED SUCCESSFULLY!]")

if __name__ == "__main__":
    run_tests()
