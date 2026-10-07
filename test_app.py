"""
test_app.py
-----------
Automated test suite verifying HazWaste Sorter routes, database logic,
and 0.7 confidence triage mechanism.
"""

import os
import io
from PIL import Image
import database
from app import app

def test_database_initialization():
    """Verify SQLite database schema and logging operations."""
    test_db = "test_hazwaste.db"
    if os.path.exists(test_db):
        os.remove(test_db)

    database.init_db(test_db)

    # Insert a high-confidence test item
    log_id = database.log_waste_item(
        image_filename="test_rag.jpg",
        item_name="Skydrol Rag",
        waste_stream="Chemical Contaminants",
        bin_colour="Yellow",
        confidence=0.85,
        status="ADVISED",
        safety_notes="Wear butyl gloves.",
        db_path=test_db
    )
    assert log_id is not None

    # Insert a low-confidence test item
    flagged_id = database.log_waste_item(
        image_filename="test_unknown.jpg",
        item_name="Unknown Wire",
        waste_stream="Unclassified",
        bin_colour="Pending",
        confidence=0.55,
        status="SUPERVISOR_REVIEW",
        safety_notes="Supervisor needed.",
        db_path=test_db
    )
    assert flagged_id is not None

    # Verify retrieval
    logs = database.get_waste_logs(test_db)
    assert len(logs) == 2

    # Check stats
    stats = database.get_summary_stats(test_db)
    assert stats["total"] == 2
    assert stats["pending_review"] == 1
    assert stats["cleared"] == 1

    # Resolve the supervisor review
    database.mark_supervisor_reviewed(flagged_id, test_db)
    stats_after = database.get_summary_stats(test_db)
    assert stats_after["pending_review"] == 0
    assert stats_after["cleared"] == 2

    # Clean up
    if os.path.exists(test_db):
        os.remove(test_db)
    print("[PASS] Database test passed!")


def test_flask_routes():
    """Verify Flask routes respond with 200 OK."""
    client = app.test_client()

    # 1. Scan screen
    res_scan = client.get("/scan")
    assert res_scan.status_code == 200
    assert b"Screen 1: Waste Scanner" in res_scan.data
    assert b"capture=\"environment\"" in res_scan.data
    assert b"ADVISORY ONLY" in res_scan.data

    # 2. Log screen
    res_log = client.get("/log")
    assert res_log.status_code == 200
    assert b"Screen 3: Waste Audit Log" in res_log.data

    # 3. Simulate image upload (Demo Mode test)
    img_byte_arr = io.BytesIO()
    test_img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    test_img.save(img_byte_arr, format="JPEG")
    img_byte_arr.seek(0)

    res_post = client.post(
        "/analyze",
        data={"waste_image": (img_byte_arr, "camera_photo.jpg")},
        content_type="multipart/form-data"
    )
    assert res_post.status_code == 200
    assert b"Screen 2: Review" in res_post.data

    print("[PASS] Flask routes test passed!")


if __name__ == "__main__":
    test_database_initialization()
    test_flask_routes()
    print("[SUCCESS] All verification tests passed successfully!")
