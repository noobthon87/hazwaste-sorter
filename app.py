"""
app.py
------
HazWaste Sorter - Live Gemini Classification
Singapore Aircraft Maintenance Training Hangar Waste Assistant.
"""

import os
import json
import uuid
import csv
import io
from datetime import datetime
from PIL import Image, ImageOps
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, redirect, url_for, flash, send_from_directory, session, Response
)

# SQLite database helper module
import database

# Load environment variables (.env file)
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "hazwaste-sorter-live-secret-2026")

# Configure uploads directory at project root
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Automatically initialize SQLite database tables on startup
database.init_db()

# Governance Feature 3: Automatically purge photos older than 30 days on startup
purged_count = database.purge_expired_photos(app.config["UPLOAD_FOLDER"], retention_days=30)
if purged_count > 0:
    print(f"[*] Governance Retention: Purged {purged_count} expired photo(s) older than 30 days.")


def save_and_resize_image(file_storage):
    """
    Feature: Resizes photo to a maximum dimension of 1024 px before saving.
    Corrects mobile camera EXIF orientation and saves as an optimized JPEG.
    """
    img = Image.open(file_storage)

    # Correct orientation from smartphone sensors if rotated
    img = ImageOps.exif_transpose(img)

    # Resize so largest dimension does not exceed 1024 pixels
    max_size = (1024, 1024)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)

    # Convert to RGB if PNG/RGBA or other format
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Generate a unique timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_suffix = uuid.uuid4().hex[:6]
    filename = f"waste_{timestamp}_{unique_suffix}.jpg"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    # Save with 85% quality to keep file size small
    img.save(filepath, "JPEG", quality=85)
    return filename, filepath


def classify_with_gemini(image_path, description, valid_streams):
    """
    Sends the photo and description to Gemini via the official google-genai SDK.
    Prompts Gemini to select strictly from valid_streams and return structured JSON.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set. Please add your key to the .env file.")

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise RuntimeError("The google-genai SDK is not installed. Please run: pip install google-genai")

    client = genai.Client(api_key=api_key)
    pil_img = Image.open(image_path)

    # Format allowed streams from SQLite as bullet points
    streams_list_str = "\n".join([f"- {s}" for s in sorted(valid_streams)])

    prompt = f"""You are a certified aircraft maintenance waste management safety assistant for a training hangar in Singapore.
Analyze this photo of a hangar waste item.

Technician's description: "{description}"

ALLOWED WASTE STREAMS (You MUST choose EXACTLY one from this list):
{streams_list_str}

PRIVACY & SAFETY POLICY:
Carefully inspect the image. If the photo shows a person's face, a worker's name tag, or a staff ID badge, you MUST set "contains_person_or_id": true.

CLASSIFICATION RULES:
1. If "contains_person_or_id" is true, you do not need to classify.
2. Otherwise, select the single best matching waste stream from the ALLOWED WASTE STREAMS list above. Do NOT invent new stream names.
3. Assign a realistic confidence score from 0.00 to 1.00 based on visual certainty.
4. Provide a concise technical reason explaining why the item belongs to that stream.
5. Provide a safety reminder mentioning necessary PPE (gloves, eye protection, respirator) and hangar handling rules.

Respond ONLY with a valid JSON object matching this schema:
{{
  "contains_person_or_id": false,
  "waste_stream": "<exact string from allowed list>",
  "confidence": 0.85,
  "reason": "<short explanation>",
  "safety_reminder": "<safety precaution and PPE>"
}}"""

    model_name = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    # Call Gemini model
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[pil_img, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
        return json.loads(response.text)
    except Exception as primary_err:
        # Fallback to alternative model versions
        for fallback_model in ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]:
            if fallback_model != model_name:
                try:
                    response = client.models.generate_content(
                        model=fallback_model,
                        contents=[pil_img, prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.2,
                        ),
                    )
                    return json.loads(response.text)
                except Exception:
                    continue
        raise primary_err


# ==========================================
# ROUTES
# ==========================================

@app.route("/")
@app.route("/scan")
def scan_screen():
    """Screen 1: Camera capture, description input, and classify button."""
    api_key_set = bool(os.getenv("GEMINI_API_KEY", "").strip())
    if not api_key_set:
        flash("Notice: GEMINI_API_KEY is not set in .env. Live AI calls will refer to supervisor until your key is added.", "info")
    return render_template("scan.html", active_page="scan")


@app.route("/classify", methods=["POST"])
def classify_waste():
    """
    Handles photo submission from mobile camera:
    1. Validates and resizes image to <= 1024px
    2. Sends photo + description to Gemini
    3. Enforces Rules in Python:
       - Rule 1: Confidence < 0.7 -> REFER TO SUPERVISOR
       - Rule 2: Invalid waste stream -> REFER TO SUPERVISOR
       - Rule 3: Person's face / ID detected -> reject and delete photo
       - Rule 4: Gemini error / invalid JSON -> friendly error, REFER TO SUPERVISOR, no crash
    4. Saves AI result in SQLite and redirects to result screen
    """
    file = None
    if "photo" in request.files and request.files["photo"].filename != "":
        file = request.files["photo"]
    elif "upload_photo" in request.files and request.files["upload_photo"].filename != "":
        file = request.files["upload_photo"]

    if not file:
        flash("No photo provided. Please tap 'Take Photo' or 'Upload from Gallery'.", "error")
        return redirect(url_for("scan_screen"))

    description = request.form.get("description", "").strip()

    # Step 1: Resize and temporarily save image
    try:
        saved_filename, saved_filepath = save_and_resize_image(file)
    except Exception as err:
        flash(f"Could not process photo: {str(err)}", "error")
        return redirect(url_for("scan_screen"))

    # Fetch valid waste streams from SQLite
    valid_streams = database.get_valid_stream_names()

    # Step 2: Call Gemini and enforce rules in Python
    try:
        ai_data = classify_with_gemini(saved_filepath, description, valid_streams)

        # -------------------------------------------------------------
        # Rule 3 (Python Enforced):
        # If the photo shows a person's face, name tag or staff ID,
        # do not classify it. Show message and delete photo.
        # -------------------------------------------------------------
        if ai_data.get("contains_person_or_id") is True:
            if os.path.exists(saved_filepath):
                os.remove(saved_filepath)
            flash("Please retake the photo showing only the waste item", "error")
            return redirect(url_for("scan_screen"))

        # Extract AI predictions
        waste_stream = ai_data.get("waste_stream", "").strip()
        try:
            confidence = float(ai_data.get("confidence", 0.0))
        except (ValueError, TypeError):
            confidence = 0.0

        reason = ai_data.get("reason", "").strip()
        safety_reminder = ai_data.get("safety_reminder", "").strip()

        # Default initial status
        status = "ADVISED"

        # -------------------------------------------------------------
        # Rule 1 (Python Enforced):
        # If confidence < 0.7, set status = "REFER TO SUPERVISOR"
        # -------------------------------------------------------------
        if confidence < 0.70:
            status = "REFER TO SUPERVISOR"
            if not reason:
                reason = "Confidence level is below the mandatory 0.70 threshold."

        # -------------------------------------------------------------
        # Rule 2 (Python Enforced):
        # If waste_stream is not exactly one of the listed streams,
        # set status = "REFER TO SUPERVISOR"
        # -------------------------------------------------------------
        if waste_stream not in valid_streams:
            status = "REFER TO SUPERVISOR"
            reason = f"Stream '{waste_stream}' does not match standard hangar waste streams."

        # Retrieve designated bin colour from SQLite table
        bin_colour = database.get_bin_for_stream(waste_stream)

    except Exception as err:
        # -------------------------------------------------------------
        # Rule 4 (Python Enforced):
        # If Gemini call fails or returns invalid JSON, show friendly
        # error and set status = "REFER TO SUPERVISOR". Never crash.
        # -------------------------------------------------------------
        status = "REFER TO SUPERVISOR"
        waste_stream = "Unclassified Material"
        bin_colour = "Pending"
        confidence = 0.0
        reason = f"Automated classification unavailable ({str(err)})."
        safety_reminder = "Hold item in quarantine staging area and request supervisor guidance."
        flash(f"AI advisory note: {reason}", "error")

    # Step 3: Save the record to SQLite
    record_id = database.insert_record(
        image_filename=saved_filename,
        description=description,
        waste_stream=waste_stream,
        bin_colour=bin_colour,
        confidence=confidence,
        status=status,
        reason=reason,
        safety_reminder=safety_reminder,
        ai_suggestion=waste_stream
    )

    return redirect(url_for("result_screen", record_id=record_id))


@app.route("/result/<int:record_id>")
def result_screen(record_id):
    """Screen 2: Displays the classification result."""
    record = database.get_record_by_id(record_id)
    if not record:
        flash("Record not found.", "error")
        return redirect(url_for("scan_screen"))

    return render_template("result.html", record=record, active_page="scan")


@app.route("/report/<int:record_id>", methods=["POST"])
def report_item(record_id):
    """
    Requirement 5: Confidently classified items can be disputed by technicians
    via 'Wrong? Report it', routing them directly to the supervisor review queue.
    """
    record = database.get_record_by_id(record_id)
    if not record:
        flash("Record not found.", "error")
        return redirect(url_for("scan_screen"))

    database.flag_for_review(record_id, dispute_note="[Technician flagged via 'Wrong? Report it']")
    flash(f"Item #{record_id} sent to the supervisor review queue for verification.", "info")
    return redirect(url_for("result_screen", record_id=record_id))


# =========================================================================
# SUPERVISOR REVIEW QUEUE & PIN AUTHENTICATION
# NOTE: Demo-level security only: The Review screen is protected by a simple
# 4-digit PIN stored in the SUPERVISOR_PIN environment variable and verified
# via Flask session. In a production hangar environment, integrate with the
# organization's enterprise IAM/OAuth or LDAP authentication with role-based access.
# =========================================================================

@app.route("/review")
def review_screen():
    """
    Requirement 1 & 4:
    Lists all items with status 'REFER TO SUPERVISOR', newest first.
    Protected with a simple 4-digit PIN (SUPERVISOR_PIN).
    """
    if not session.get("supervisor_logged_in"):
        return render_template("review.html", needs_pin=True, active_page="review")

    pending_items = database.get_pending_review_records()
    streams = database.get_waste_streams()
    return render_template(
        "review.html", 
        needs_pin=False, 
        items=pending_items, 
        streams=streams, 
        active_page="review"
    )


@app.route("/review/login", methods=["POST"])
def supervisor_login():
    """
    Validates supervisor 4-digit PIN from SUPERVISOR_PIN environment variable.
    """
    # NOTE: Demo-level security only: Plain 4-digit PIN verification.
    entered_pin = request.form.get("pin", "").strip()
    expected_pin = os.getenv("SUPERVISOR_PIN", "1234").strip()

    if entered_pin == expected_pin:
        session["supervisor_logged_in"] = True
        flash("Supervisor authorization granted.", "success")
    else:
        flash("Incorrect 4-digit supervisor PIN. Please try again.", "error")

    return redirect(url_for("review_screen"))


@app.route("/review/logout", methods=["POST", "GET"])
def supervisor_logout():
    """Locks supervisor access by clearing session state."""
    session.pop("supervisor_logged_in", None)
    flash("Supervisor review screen locked.", "info")
    return redirect(url_for("review_screen"))


@app.route("/review/confirm/<int:record_id>", methods=["POST"])
def confirm_review(record_id):
    """
    Requirements 2 & 3:
    Supervisor picks correct stream from dropdown and confirms decision.
    Saves final_stream, decided_by='Supervisor', decided_at, and AGREED/DISAGREED.
    """
    if not session.get("supervisor_logged_in"):
        flash("Please enter supervisor PIN to confirm decisions.", "error")
        return redirect(url_for("review_screen"))

    record = database.get_record_by_id(record_id)
    if not record:
        flash("Record not found.", "error")
        return redirect(url_for("review_screen"))

    final_stream = request.form.get("final_stream", "").strip()
    if not final_stream:
        flash("Please select a valid waste stream from the dropdown.", "error")
        return redirect(url_for("review_screen"))

    # Determine assigned bin colour from SQLite table
    bin_colour = database.get_bin_for_stream(final_stream)

    # Determine whether supervisor agreed or disagreed with AI suggestion
    ai_suggestion = (record["ai_suggestion"] or record["waste_stream"] or "").strip()
    agreement = "AGREED" if final_stream.lower() == ai_suggestion.lower() else "DISAGREED"

    database.resolve_supervisor_review(
        record_id=record_id,
        final_stream=final_stream,
        bin_colour=bin_colour,
        agreement=agreement,
        decided_by="Supervisor"
    )

    flash(f"Record #{record_id} resolved as '{final_stream}' ({agreement} with AI).", "success")
    return redirect(url_for("review_screen"))


@app.route("/log")
def log_screen():
    """
    Screen 3: Historical audit log with summary analytics, CSS bar chart,
    and the 50 most recent items table.
    """
    stats = database.get_log_summary_stats()
    stream_counts = database.get_waste_stream_counts()
    records = database.get_recent_records(limit=50)
    return render_template(
        "log.html", 
        stats=stats, 
        stream_counts=stream_counts, 
        records=records, 
        active_page="log"
    )


@app.route("/log/export-csv")
@app.route("/export-csv")
def export_csv():
    """
    Requirement 4: Downloads all historical records as a CSV spreadsheet.
    """
    records = database.get_all_records()
    si = io.StringIO()
    writer = csv.writer(si)

    # Write CSV Header
    writer.writerow([
        "Record ID", "Timestamp", "Description", "Waste Stream", "Bin Colour",
        "Confidence", "Status", "AI Suggestion", "Final Stream",
        "Decided By", "Decided At", "Agreement", "Reason", "Is Demo Data"
    ])

    # Write Record Rows
    for r in records:
        writer.writerow([
            r["id"],
            r["timestamp"],
            r["description"],
            r["waste_stream"],
            r["bin_colour"],
            f"{r['confidence']:.2f}",
            r["status"],
            r["ai_suggestion"],
            r["final_stream"] or r["waste_stream"],
            r["decided_by"] or "Pending",
            r["decided_at"] or "N/A",
            r["agreement"] or "N/A",
            r["reason"],
            "Yes" if r["is_demo"] else "No"
        ])

    csv_data = si.getvalue()
    export_filename = f"hazwaste_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={export_filename}"}
    )


@app.route("/about")
def about_screen():
    """
    Governance Feature 2: 'About this AI' explanation page.
    Explains app scope, 0.7 confidence rule, supervisor authority,
    privacy protection, operational limits, and 30-day retention.
    """
    return render_template("about.html", active_page="about")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """Serves resized photos stored in the uploads/ directory."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    print("===============================================================")
    print("[*] HazWaste Sorter running at http://127.0.0.1:5000")
    print("[*] Mobile Wi-Fi Access: Check your computer's local IP (e.g. 172.19.135.138:5000)")
    print("===============================================================")
    app.run(host="0.0.0.0", port=5000, debug=True)
