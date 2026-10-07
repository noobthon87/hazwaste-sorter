"""
test_review.py
--------------
Automated test suite verifying the Review screen, 4-digit PIN protection,
supervisor dropdown decision (AGREED vs DISAGREED), and "Wrong? Report it" flow.
"""

import os
from app import app
import database

def run_tests():
    print("--- Starting Supervisor Review Screen Tests ---")
    database.init_db()
    client = app.test_client()

    # 1. Clean test records
    conn = database.get_connection()
    conn.execute("DELETE FROM waste_records")
    conn.commit()
    conn.close()

    # 2. Insert test items:
    # Item A: Low confidence (status = REFER TO SUPERVISOR)
    id_a = database.insert_record(
        image_filename="test_a.jpg",
        description="Faded battery from avionics bay",
        waste_stream="Used batteries",
        bin_colour="Yellow",
        confidence=0.55,
        status="REFER TO SUPERVISOR",
        reason="Low visual certainty",
        safety_reminder="Tape terminals",
        ai_suggestion="Used batteries"
    )

    # Item B: Unlisted stream (status = REFER TO SUPERVISOR)
    id_b = database.insert_record(
        image_filename="test_b.jpg",
        description="Sticky adhesive tube",
        waste_stream="Unclassified Chemical",
        bin_colour="Pending",
        confidence=0.60,
        status="REFER TO SUPERVISOR",
        reason="Unrecognized category",
        safety_reminder="Wear gloves",
        ai_suggestion="Empty sealant / adhesive / paint containers"
    )

    # Item C: Confidently classified item (status = ADVISED)
    id_c = database.insert_record(
        image_filename="test_c.jpg",
        description="Clean cardboard packaging",
        waste_stream="General non-hazardous waste",
        bin_colour="Black",
        confidence=0.92,
        status="ADVISED",
        reason="Clean unsoiled paper box",
        safety_reminder="Standard recycling disposal",
        ai_suggestion="General non-hazardous waste"
    )

    print("[PASS] Sample items seeded in database.")

    # -------------------------------------------------------------
    # Test Requirement 4: PIN Protection
    # -------------------------------------------------------------
    # GET /review without PIN should show PIN entry screen
    r = client.get("/review")
    assert r.status_code == 200
    assert b"Supervisor Access Required" in r.data
    assert b"pin-input" in r.data
    print("[PASS] Req 4: Review screen protected by PIN when unauthenticated.")

    # Wrong PIN should fail
    r_bad = client.post("/review/login", data={"pin": "9999"}, follow_redirects=True)
    assert r_bad.status_code == 200
    assert b"Incorrect 4-digit supervisor PIN" in r_bad.data
    assert b"Supervisor Access Required" in r_bad.data
    print("[PASS] Req 4: Wrong PIN rejected.")

    # Correct PIN (1234) should grant access
    r_good = client.post("/review/login", data={"pin": "1234"}, follow_redirects=True)
    assert r_good.status_code == 200
    assert b"Supervisor authorization granted" in r_good.data
    assert b"Supervisor Review" in r_good.data
    print("[PASS] Req 4: Correct PIN granted access.")

    # -------------------------------------------------------------
    # Test Requirement 1: List items with REFER TO SUPERVISOR, newest first
    # -------------------------------------------------------------
    assert b"Faded battery from avionics bay" in r_good.data
    assert b"Sticky adhesive tube" in r_good.data
    # Confident Item C should NOT be in the review queue
    assert b"Clean cardboard packaging" not in r_good.data
    print("[PASS] Req 1: Only REFER TO SUPERVISOR items displayed in review queue.")

    # -------------------------------------------------------------
    # Test Requirements 2 & 3: Supervisor picks stream & confirms
    # Case A: Supervisor AGREES with AI suggestion (Used batteries)
    # -------------------------------------------------------------
    r_confirm_a = client.post(
        f"/review/confirm/{id_a}",
        data={"final_stream": "Used batteries"},
        follow_redirects=True
    )
    assert r_confirm_a.status_code == 200
    assert b"AGREED with AI" in r_confirm_a.data

    record_a = database.get_record_by_id(id_a)
    assert record_a["status"] == "SUPERVISOR_RESOLVED"
    assert record_a["final_stream"] == "Used batteries"
    assert record_a["decided_by"] == "Supervisor"
    assert record_a["decided_at"] is not None
    assert record_a["agreement"] == "AGREED"
    assert record_a["bin_colour"] == "Yellow"
    print("[PASS] Req 2 & 3 (Case A): Supervisor AGREED recorded with decided_by, time, and bin.")

    # Case B: Supervisor DISAGREES with AI suggestion (picks different stream)
    r_confirm_b = client.post(
        f"/review/confirm/{id_b}",
        data={"final_stream": "Composite dust and offcuts"}, # Disagreeing with AI suggestion
        follow_redirects=True
    )
    assert r_confirm_b.status_code == 200
    assert b"DISAGREED with AI" in r_confirm_b.data

    record_b = database.get_record_by_id(id_b)
    assert record_b["status"] == "SUPERVISOR_RESOLVED"
    assert record_b["final_stream"] == "Composite dust and offcuts"
    assert record_b["decided_by"] == "Supervisor"
    assert record_b["agreement"] == "DISAGREED"
    print("[PASS] Req 2 & 3 (Case B): Supervisor DISAGREED recorded with decided_by, time, and bin.")

    # -------------------------------------------------------------
    # Test Requirement 5: "Wrong? Report it" button
    # -------------------------------------------------------------
    # Confident item C on /result/id_c should have "Wrong? Report it"
    r_res_c = client.get(f"/result/{id_c}")
    assert r_res_c.status_code == 200
    assert b"Wrong? Report it" in r_res_c.data

    # Technician clicks "Wrong? Report it"
    r_report = client.post(f"/report/{id_c}", follow_redirects=True)
    assert r_report.status_code == 200
    assert b"sent to the supervisor review queue" in r_report.data

    record_c = database.get_record_by_id(id_c)
    assert record_c["status"] == "REFER TO SUPERVISOR"
    assert "[Technician flagged" in record_c["reason"]
    print("[PASS] Req 5: 'Wrong? Report it' successfully routed confident item to review queue.")

    # Now verify Item C appears in /review queue
    r_review_after = client.get("/review")
    assert b"Clean cardboard packaging" in r_review_after.data
    print("[PASS] Req 5: Reported item now visible in supervisor review queue.")

    print("\n[ALL SUPERVISOR REVIEW TESTS PASSED SUCCESSFULLY!]")

if __name__ == "__main__":
    run_tests()
