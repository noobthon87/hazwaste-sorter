"""
test_rules.py
-------------
Automated verification of the 4 Python-enforced rules,
SQLite configurable waste streams, and confidence bar rendering.
"""

import io
import os
from unittest.mock import patch
from PIL import Image
from app import app
import database

def run_tests():
    print("--- Starting Rule Verification Tests ---")
    database.init_db()

    # Verify configurable streams table
    streams = database.get_waste_streams()
    assert len(streams) == 6, f"Expected 6 default streams, got {len(streams)}"
    stream_names = database.get_valid_stream_names()
    assert "Oily / contaminated rags and absorbents" in stream_names
    assert "Used batteries" in stream_names
    assert "Composite dust and offcuts" in stream_names
    assert "Empty sealant / adhesive / paint containers" in stream_names
    assert "Metal swarf and scrap" in stream_names
    assert "General non-hazardous waste" in stream_names
    print("[PASS] SQLite waste_streams table verified with 6 hangar categories.")

    client = app.test_client()

    def make_dummy_img():
        img = Image.new("RGB", (200, 200), color="red")
        b = io.BytesIO()
        img.save(b, "JPEG")
        b.seek(0)
        return b

    # Test Rule 1: Confidence < 0.7 forces status = "REFER TO SUPERVISOR"
    with patch("app.classify_with_gemini") as mock_gemini:
        mock_gemini.return_value = {
            "contains_person_or_id": False,
            "waste_stream": "Used batteries",
            "confidence": 0.62, # < 0.70
            "reason": "Battery label faded",
            "safety_reminder": "Tape terminals"
        }
        resp = client.post("/classify", data={"photo": (make_dummy_img(), "bat.jpg"), "description": "old cell"}, content_type="multipart/form-data", follow_redirects=True)
        assert resp.status_code == 200
        latest = database.get_latest_record()
        assert latest["status"] == "REFER TO SUPERVISOR", f"Expected REFER TO SUPERVISOR, got {latest['status']}"
        assert b"REFER TO SUPERVISOR" in resp.data
        assert b"bar-red" in resp.data
        print("[PASS] Rule 1 Verified: Confidence < 0.7 correctly sets status = REFER TO SUPERVISOR and red bar.")

    # Test Rule 2: Waste stream not in allowed streams forces status = "REFER TO SUPERVISOR"
    with patch("app.classify_with_gemini") as mock_gemini:
        mock_gemini.return_value = {
            "contains_person_or_id": False,
            "waste_stream": "Invented Nuclear Waste", # NOT in allowed streams
            "confidence": 0.95,
            "reason": "Test unlisted category",
            "safety_reminder": "Handle carefully"
        }
        resp = client.post("/classify", data={"photo": (make_dummy_img(), "unknown.jpg")}, content_type="multipart/form-data", follow_redirects=True)
        assert resp.status_code == 200
        latest = database.get_latest_record()
        assert latest["status"] == "REFER TO SUPERVISOR", f"Expected REFER TO SUPERVISOR, got {latest['status']}"
        print("[PASS] Rule 2 Verified: Unlisted waste stream correctly sets status = REFER TO SUPERVISOR.")

    # Test Rule 3: Person's face, name tag or staff ID detected
    with patch("app.classify_with_gemini") as mock_gemini:
        mock_gemini.return_value = {
            "contains_person_or_id": True, # Privacy violation!
            "waste_stream": "",
            "confidence": 0.0,
            "reason": "",
            "safety_reminder": ""
        }
        count_before = len(database.get_all_records())
        resp = client.post("/classify", data={"photo": (make_dummy_img(), "face.jpg")}, content_type="multipart/form-data", follow_redirects=True)
        assert resp.status_code == 200
        assert b"Please retake the photo showing only the waste item" in resp.data
        count_after = len(database.get_all_records())
        assert count_after == count_before, "Record should NOT be saved when privacy check fails"
        print("[PASS] Rule 3 Verified: Person/ID triggers retake message and does not save photo or record.")

    # Test Rule 4: Gemini failure or invalid response does NOT crash
    with patch("app.classify_with_gemini") as mock_gemini:
        mock_gemini.side_effect = Exception("Simulated Gemini API 503 Overloaded")
        resp = client.post("/classify", data={"photo": (make_dummy_img(), "rag.jpg")}, content_type="multipart/form-data", follow_redirects=True)
        assert resp.status_code == 200
        latest = database.get_latest_record()
        assert latest["status"] == "REFER TO SUPERVISOR"
        assert b"REFER TO SUPERVISOR" in resp.data
        print("[PASS] Rule 4 Verified: Exception handled gracefully without crash, set to REFER TO SUPERVISOR.")

    # Test Valid Classification with High Confidence (Green Bar >= 0.85)
    with patch("app.classify_with_gemini") as mock_gemini:
        mock_gemini.return_value = {
            "contains_person_or_id": False,
            "waste_stream": "Oily / contaminated rags and absorbents",
            "confidence": 0.92, # >= 0.85 -> Green
            "reason": "Solvent-soaked fabric weave",
            "safety_reminder": "Wear nitrile gloves and dispose in red bin."
        }
        resp = client.post("/classify", data={"photo": (make_dummy_img(), "rag.jpg")}, content_type="multipart/form-data", follow_redirects=True)
        assert resp.status_code == 200
        latest = database.get_latest_record()
        assert latest["status"] == "ADVISED"
        assert latest["bin_colour"] == "Red"
        assert b"bar-green" in resp.data
        print("[PASS] High Confidence Verified: status = ADVISED, bin = Red, green bar.")

    # Clean up uploaded test images
    for fname in os.listdir(app.config["UPLOAD_FOLDER"]):
        if fname.endswith(".jpg"):
            try:
                os.remove(os.path.join(app.config["UPLOAD_FOLDER"], fname))
            except Exception:
                pass

    print("[ALL TESTS PASSED SUCCESSFULLY!]")

if __name__ == "__main__":
    run_tests()
