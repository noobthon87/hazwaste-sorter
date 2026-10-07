"""
test_governance.py
------------------
Automated test suite verifying the three governance features:
1. audit_log table tracking all item changes (immutable records, no deletion).
2. "About this AI" page (/about) and footer link explaining governance principles.
3. Automatic 30-day photo deletion (unlinks file, preserves text records in SQLite).
"""

import os
import sys
from datetime import datetime, timedelta
from app import app
import database

def run_tests():
    print("=============================================================")
    print("[*] Running HazWaste Sorter Governance Verification Tests")
    print("=============================================================\n")

    client = app.test_client()

    # -------------------------------------------------------------
    # TEST 1: "About this AI" Screen & Footer Link
    # -------------------------------------------------------------
    print("[1] Testing 'About this AI' page and governance footer...")
    res = client.get("/about")
    assert res.status_code == 200, f"Expected 200 from /about, got {res.status_code}"
    html = res.get_data(as_text=True)

    # Check 6 required points in /about
    required_phrases = [
        ("What the App Does & Does NOT Do", "Section 1: App scope and boundaries"),
        ("Supervisor & SOP Have the Final Say", "Section 2: Supervisor authority"),
        ("0.70", "Section 3: 0.7 confidence threshold rule"),
        ("No Faces, Name Tags, or Staff IDs", "Section 4: Privacy protection"),
        ("Known Operational Limitations", "Section 5: Operational limits"),
        ("30-Day Retention Policy", "Section 6: 30-day photo deletion policy")
    ]

    for phrase, desc in required_phrases:
        assert phrase in html, f"Missing {desc} in /about page"
        print(f"  [PASS] {desc}")

    # Check footer link on home / scan page
    scan_res = client.get("/")
    scan_html = scan_res.get_data(as_text=True)
    assert 'href="/about"' in scan_html, "Footer link to /about missing on scan screen"
    print("  [PASS] Footer link to /about present in base layout")

    # -------------------------------------------------------------
    # TEST 2: audit_log table and immutable record corrections
    # -------------------------------------------------------------
    print("\n[2] Testing audit_log tracking and change history...")
    
    # 2a. Insert a new record
    item_id = database.insert_record(
        image_filename="test_gov_item.jpg",
        description="Hydraulic fluid absorbent rag",
        waste_stream="Oily / contaminated rags and absorbents",
        bin_colour="Red",
        confidence=0.88,
        status="ADVISED",
        reason="Hydraulic fluid staining detected",
        safety_reminder="Wear chemical resistant nitrile gloves"
    )
    assert item_id > 0, "Failed to insert test item"
    print(f"  [PASS] Created test item #{item_id}")

    # Check initial classification was logged in audit_log
    logs = database.get_audit_logs_for_item(item_id)
    assert len(logs) >= 1, "audit_log did not record initial item creation"
    initial_log = [l for l in logs if l["field"] == "initial_classification"][0]
    assert initial_log["changed_by"] == "AI" or initial_log["changed_by"] == "System_AI"
    print("  [PASS] Initial classification recorded in audit_log")

    # 2b. Technician disputes item (Wrong? Report it)
    database.flag_for_review(item_id, dispute_note="[Technician tested dispute flag]", changed_by="Technician")
    logs = database.get_audit_logs_for_item(item_id)
    status_log = [l for l in logs if l["field"] == "status" and l["new_value"] == "REFER TO SUPERVISOR"][0]
    assert status_log["changed_by"] == "Technician"
    assert status_log["old_value"] == "ADVISED"
    print("  [PASS] Technician dispute recorded in audit_log")

    # 2c. Supervisor resolves item
    database.resolve_supervisor_review(
        record_id=item_id,
        final_stream="Metal swarf and scrap",
        bin_colour="Blue",
        agreement="DISAGREED",
        decided_by="Supervisor_Tan"
    )
    logs = database.get_audit_logs_for_item(item_id)
    stream_log = [l for l in logs if l["field"] == "waste_stream"][0]
    assert stream_log["old_value"] == "Oily / contaminated rags and absorbents"
    assert stream_log["new_value"] == "Metal swarf and scrap"
    assert stream_log["changed_by"] == "Supervisor_Tan"
    print("  [PASS] Supervisor correction and stream change recorded in audit_log")

    # Verify item cannot be deleted: check record still exists
    record = database.get_record_by_id(item_id)
    assert record is not None, "Record was unexpectedly deleted"
    assert record["waste_stream"] == "Metal swarf and scrap"
    assert record["status"] == "SUPERVISOR_RESOLVED"
    print("  [PASS] Item integrity verified (record is updated, never deleted)")

    # -------------------------------------------------------------
    # TEST 3: Automatic 30-Day Photo Deletion Policy
    # -------------------------------------------------------------
    print("\n[3] Testing automatic 30-day photo deletion...")

    upload_dir = app.config["UPLOAD_FOLDER"]

    # 3a. Create an old expired photo (45 days old)
    old_filename = "test_expired_photo_45d.jpg"
    old_filepath = os.path.join(upload_dir, old_filename)
    with open(old_filepath, "wb") as f:
        f.write(b"SIMULATED_EXPIRED_IMAGE_DATA")

    old_timestamp = (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d %H:%M:%S")
    old_item_id = database.insert_record(
        image_filename=old_filename,
        description="45-day-old solvent can",
        waste_stream="Empty sealant / adhesive / paint containers",
        bin_colour="Yellow",
        confidence=0.91,
        status="ADVISED",
        reason="Solvent label visible",
        safety_reminder="Venting protocol",
        timestamp=old_timestamp
    )

    # 3b. Create a recent photo (2 days old)
    recent_filename = "test_recent_photo_2d.jpg"
    recent_filepath = os.path.join(upload_dir, recent_filename)
    with open(recent_filepath, "wb") as f:
        f.write(b"SIMULATED_RECENT_IMAGE_DATA")

    recent_timestamp = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
    recent_item_id = database.insert_record(
        image_filename=recent_filename,
        description="2-day-old clean rag",
        waste_stream="General non-hazardous waste",
        bin_colour="Black",
        confidence=0.89,
        status="ADVISED",
        reason="Clean packing material",
        safety_reminder="Dispose safely",
        timestamp=recent_timestamp
    )

    # Verify both files exist prior to purge
    assert os.path.exists(old_filepath), "Old image file not created"
    assert os.path.exists(recent_filepath), "Recent image file not created"

    # 3c. Run purge with retention_days = 30
    purged = database.purge_expired_photos(upload_dir, retention_days=30)
    assert purged >= 1, f"Expected at least 1 purged photo, got {purged}"
    print(f"  [PASS] Purged {purged} photo(s) older than 30 days")

    # Verify old file was unlinked from disk
    assert not os.path.exists(old_filepath), "Old photo was NOT deleted from disk!"
    print("  [PASS] Physical photo file was unlinked from disk")

    # Verify recent file is STILL on disk
    assert os.path.exists(recent_filepath), "Recent photo was incorrectly deleted!"
    print("  [PASS] Recent photo (<30 days) remains safely on disk")

    # Clean up recent test file
    if os.path.exists(recent_filepath):
        os.remove(recent_filepath)

    # Verify old record text data in SQLite is PRESERVED
    old_record = database.get_record_by_id(old_item_id)
    assert old_record is not None, "Text record was incorrectly deleted from database!"
    assert old_record["image_filename"] == "[PURGED_30D_RETENTION]", "image_filename was not updated to purged tag"
    assert old_record["description"] == "45-day-old solvent can", "Text description was corrupted"
    assert old_record["waste_stream"] == "Empty sealant / adhesive / paint containers"
    print("  [PASS] SQLite text record preserved with [PURGED_30D_RETENTION] placeholder")

    # Verify purge event was logged in audit_log
    old_item_logs = database.get_audit_logs_for_item(old_item_id)
    purge_log = [l for l in old_item_logs if l["field"] == "image_filename"][0]
    assert purge_log["old_value"] == old_filename
    assert purge_log["new_value"] == "[PURGED_30D_RETENTION]"
    assert purge_log["changed_by"] == "System_Data_Retention_Policy"
    print("  [PASS] Data retention purge event logged in audit_log")

    # 3d. Test UI rendering for purged item
    res_purged_view = client.get(f"/result/{old_item_id}")
    assert res_purged_view.status_code == 200
    purged_html = res_purged_view.get_data(as_text=True)
    assert "Photo Purged by 30-Day Retention Policy" in purged_html
    print("  [PASS] Result screen displays clean data retention notice for purged photos")

    print("\n=============================================================")
    print("[ALL GOVERNANCE TESTS PASSED SUCCESSFULLY!]")
    print("=============================================================")

if __name__ == "__main__":
    run_tests()
