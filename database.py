"""
database.py
-----------
SQLite database management for HazWaste Sorter.
Uses Python's built-in sqlite3 module (no ORM).

Features:
- Stores configurable waste streams in `waste_streams` table.
- Stores historical classification records in `waste_records` table.
- Stores immutable governance audit trail in `audit_log` table.
- Enforces data integrity: items cannot be deleted, only corrected.
- Automatically purges photos older than 30 days while preserving text records.
"""

import sqlite3
import os
from datetime import datetime, timedelta

DB_FILENAME = "hazwaste.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_FILENAME)

# Initial configurable hangar waste streams & bin colours
DEFAULT_WASTE_STREAMS = [
    ("Oily / contaminated rags and absorbents", "Red", "Flammable solvent, oil, and hydrocarbon-soaked wipes and absorbents"),
    ("Used batteries", "Yellow", "Aircraft batteries, Li-ion, NiCad, emergency locator transmitter cells"),
    ("Composite dust and offcuts", "Yellow", "Hazardous carbon-fiber dust, prepreg scraps, fiberglass shavings"),
    ("Empty sealant / adhesive / paint containers", "Yellow", "Hazardous sealant tubes (PRC/Pro-Seal), adhesive cartridges, paint cans"),
    ("Metal swarf and scrap", "Blue", "Uncontaminated aluminum, titanium, safety lockwire clippings, metal turnings"),
    ("General non-hazardous waste", "Black", "Clean workshop packaging, food containers, non-soiled disposable trash")
]


def get_connection():
    """
    Returns an SQLite connection configured with row_factory.
    This allows column access by name (e.g. row['bin_colour']).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes tables, seeds default waste streams, and performs schema migrations.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Configurable Waste Streams Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS waste_streams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stream_name TEXT UNIQUE NOT NULL,
            bin_colour TEXT NOT NULL,
            description TEXT
        )
    """)

    # 2. Historical Waste Classification Records Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS waste_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            image_filename TEXT NOT NULL,
            description TEXT,
            waste_stream TEXT NOT NULL,
            bin_colour TEXT NOT NULL,
            confidence REAL NOT NULL,
            status TEXT NOT NULL,
            reason TEXT,
            safety_reminder TEXT,
            ai_suggestion TEXT,
            final_stream TEXT,
            decided_by TEXT,
            decided_at DATETIME,
            agreement TEXT,
            is_demo INTEGER DEFAULT 0
        )
    """)

    # 3. Governance Audit Log Table (Requirement 1)
    # Records every change: item_id, field, old_value, new_value, changed_by, timestamp.
    # Items can never be deleted, only corrected.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            field TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            changed_by TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES waste_records(id)
        )
    """)

    # Ensure backward-compatible migrations if table was created previously
    cursor.execute("PRAGMA table_info(waste_records)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    needed_cols = {
        "ai_suggestion": "TEXT",
        "final_stream": "TEXT",
        "decided_by": "TEXT",
        "decided_at": "DATETIME",
        "agreement": "TEXT",
        "is_demo": "INTEGER DEFAULT 0"
    }
    for col_name, col_type in needed_cols.items():
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE waste_records ADD COLUMN {col_name} {col_type}")

    # Seed default waste streams if table is empty
    cursor.execute("SELECT COUNT(*) FROM waste_streams")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO waste_streams (stream_name, bin_colour, description)
            VALUES (?, ?, ?)
        """, DEFAULT_WASTE_STREAMS)

    conn.commit()
    conn.close()


def log_audit_change(item_id, field, old_value, new_value, changed_by, timestamp=None, conn=None):
    """
    Requirement 1: Records an immutable audit log entry.
    Every change to an item records item_id, field, old value, new value, changed_by, and timestamp.
    """
    close_conn = False
    if conn is None:
        conn = get_connection()
        close_conn = True

    cursor = conn.cursor()
    old_str = str(old_value) if old_value is not None else None
    new_str = str(new_value) if new_value is not None else None

    if timestamp:
        cursor.execute("""
            INSERT INTO audit_log (item_id, field, old_value, new_value, changed_by, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (item_id, field, old_str, new_str, changed_by, timestamp))
    else:
        cursor.execute("""
            INSERT INTO audit_log (item_id, field, old_value, new_value, changed_by)
            VALUES (?, ?, ?, ?, ?)
        """, (item_id, field, old_str, new_str, changed_by))

    if close_conn:
        conn.commit()
        conn.close()


def get_waste_streams():
    """
    Retrieves all configured waste streams from SQLite.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM waste_streams ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_valid_stream_names():
    """
    Returns a set of all valid waste stream names for strict Python validation.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT stream_name FROM waste_streams")
    names = {row["stream_name"].strip() for row in cursor.fetchall()}
    conn.close()
    return names


def get_bin_for_stream(stream_name):
    """
    Looks up the designated bin colour for a specific waste stream.
    Defaults to 'Pending' if not matched.
    """
    if not stream_name:
        return "Pending"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT bin_colour FROM waste_streams WHERE stream_name = ?", (stream_name.strip(),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row["bin_colour"]
    return "Pending"


def insert_record(image_filename, description, waste_stream, bin_colour, confidence, status,
                  reason, safety_reminder, ai_suggestion=None, final_stream=None,
                  decided_by=None, decided_at=None, agreement=None, is_demo=0, timestamp=None):
    """
    Inserts a newly classified waste item into SQLite and records initial creation in audit_log.
    Returns the new record ID.
    """
    conn = get_connection()
    cursor = conn.cursor()

    suggestion = ai_suggestion or waste_stream
    final = final_stream if final_stream is not None else (waste_stream if status == "ADVISED" else None)
    who_decided = decided_by if decided_by is not None else ("AI" if status == "ADVISED" else None)
    when_decided = decided_at if decided_at is not None else (datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == "ADVISED" else None)
    agree = agreement if agreement is not None else ("N/A" if status == "ADVISED" else None)

    if timestamp:
        cursor.execute("""
            INSERT INTO waste_records (
                timestamp, image_filename, description, waste_stream, bin_colour, confidence, status, reason, safety_reminder,
                ai_suggestion, final_stream, decided_by, decided_at, agreement, is_demo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            image_filename,
            description or "",
            waste_stream,
            bin_colour,
            float(confidence),
            status,
            reason or "",
            safety_reminder or "",
            suggestion,
            final,
            who_decided,
            when_decided,
            agree,
            int(is_demo)
        ))
    else:
        cursor.execute("""
            INSERT INTO waste_records (
                image_filename, description, waste_stream, bin_colour, confidence, status, reason, safety_reminder,
                ai_suggestion, final_stream, decided_by, decided_at, agreement, is_demo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            image_filename,
            description or "",
            waste_stream,
            bin_colour,
            float(confidence),
            status,
            reason or "",
            safety_reminder or "",
            suggestion,
            final,
            who_decided,
            when_decided,
            agree,
            int(is_demo)
        ))

    new_id = cursor.lastrowid

    # Requirement 1: Record initial item creation in audit log
    log_audit_change(
        item_id=new_id,
        field="initial_classification",
        old_value=None,
        new_value=f"stream='{waste_stream}', status='{status}', confidence={confidence:.2f}",
        changed_by=who_decided or "System_AI",
        timestamp=timestamp,
        conn=conn
    )

    conn.commit()
    conn.close()
    return new_id


def get_pending_review_records():
    """
    Retrieves all records with status = 'REFER TO SUPERVISOR', newest first.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM waste_records 
        WHERE status = 'REFER TO SUPERVISOR' 
        ORDER BY timestamp DESC, id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def resolve_supervisor_review(record_id, final_stream, bin_colour, agreement, decided_by="Supervisor"):
    """
    Requirement 1: Updates a waste record after supervisor review and records each change in audit_log.
    """
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Fetch previous values for audit logging
    cursor.execute("SELECT waste_stream, bin_colour, status, agreement FROM waste_records WHERE id = ?", (record_id,))
    old_record = cursor.fetchone()

    cursor.execute("""
        UPDATE waste_records
        SET final_stream = ?,
            waste_stream = ?,
            bin_colour = ?,
            status = 'SUPERVISOR_RESOLVED',
            decided_by = ?,
            decided_at = ?,
            agreement = ?
        WHERE id = ?
    """, (
        final_stream,
        final_stream,
        bin_colour,
        decided_by,
        now_str,
        agreement,
        record_id
    ))

    # Log changes in audit trail
    if old_record:
        if old_record["waste_stream"] != final_stream:
            log_audit_change(record_id, "waste_stream", old_record["waste_stream"], final_stream, decided_by, now_str, conn=conn)
        if old_record["bin_colour"] != bin_colour:
            log_audit_change(record_id, "bin_colour", old_record["bin_colour"], bin_colour, decided_by, now_str, conn=conn)
        log_audit_change(record_id, "status", old_record["status"], "SUPERVISOR_RESOLVED", decided_by, now_str, conn=conn)
        log_audit_change(record_id, "agreement", old_record["agreement"], agreement, decided_by, now_str, conn=conn)

    conn.commit()
    conn.close()


def flag_for_review(record_id, dispute_note="[Technician reported classification as incorrect]", changed_by="Technician"):
    """
    Requirement 1: Flags a previously advised item for supervisor review and records change in audit_log.
    """
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("SELECT status, reason FROM waste_records WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    old_status = row["status"] if row else "ADVISED"
    old_reason = row["reason"] if row and row["reason"] else ""
    updated_reason = f"{old_reason} {dispute_note}".strip()

    cursor.execute("""
        UPDATE waste_records
        SET status = 'REFER TO SUPERVISOR',
            reason = ?
        WHERE id = ?
    """, (updated_reason, record_id))

    # Log changes in audit trail
    log_audit_change(record_id, "status", old_status, "REFER TO SUPERVISOR", changed_by, now_str, conn=conn)
    log_audit_change(record_id, "reason", old_reason, updated_reason, changed_by, now_str, conn=conn)

    conn.commit()
    conn.close()


def get_audit_logs_for_item(item_id):
    """
    Retrieves the complete audit trail for a specific waste record.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM audit_log 
        WHERE item_id = ? 
        ORDER BY timestamp DESC, id DESC
    """, (item_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_audit_logs(limit=100):
    """
    Retrieves recent audit log events across all records.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, w.waste_stream 
        FROM audit_log a
        LEFT JOIN waste_records w ON a.item_id = w.id
        ORDER BY a.timestamp DESC, a.id DESC 
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def purge_expired_photos(upload_folder, retention_days=30):
    """
    Requirement 3: Automatic deletion of photos older than retention_days (30 days).
    Deletes the physical photo file from disk while preserving the text audit record in SQLite.
    Updates image_filename to '[PURGED_30D_RETENTION]' and logs the audit event.
    """
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Find records older than retention_days that haven't been purged yet and aren't the demo placeholder
    cutoff = (datetime.now() - timedelta(days=retention_days)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        SELECT id, image_filename, timestamp FROM waste_records
        WHERE timestamp < ?
          AND image_filename NOT LIKE '[PURGED%'
          AND image_filename != 'demo_waste_placeholder.jpg'
    """, (cutoff,))
    records_to_purge = cursor.fetchall()

    purged_count = 0
    for r in records_to_purge:
        item_id = r["id"]
        filename = r["image_filename"]
        filepath = os.path.join(upload_folder, filename)

        # Delete physical file from disk if it exists
        if os.path.exists(filepath) and os.path.isfile(filepath):
            try:
                os.remove(filepath)
            except OSError:
                pass

        # Update database text record to reflect retention purge
        cursor.execute("""
            UPDATE waste_records
            SET image_filename = '[PURGED_30D_RETENTION]'
            WHERE id = ?
        """, (item_id,))

        # Record in audit log
        log_audit_change(
            item_id=item_id,
            field="image_filename",
            old_value=filename,
            new_value="[PURGED_30D_RETENTION]",
            changed_by="System_Data_Retention_Policy",
            timestamp=now_str,
            conn=conn
        )
        purged_count += 1

    conn.commit()
    conn.close()
    return purged_count


def get_record_by_id(record_id):
    """
    Fetches a single waste item by its primary key ID.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM waste_records WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def get_latest_record():
    """
    Fetches the most recently inserted waste record.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM waste_records ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row


def get_all_records():
    """
    Fetches all historical records ordered newest first.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM waste_records ORDER BY timestamp DESC, id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_recent_records(limit=50):
    """
    Requirement 3: Fetches the 50 most recent items for the log table.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM waste_records 
        ORDER BY timestamp DESC, id DESC 
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_log_summary_stats():
    """
    Requirement 1: Calculates summary metrics for the Log screen tiles:
    - total items
    - % sent to supervisor
    - % AI suggestions accepted
    - items this week
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Total items
    cursor.execute("SELECT COUNT(*) FROM waste_records")
    total_items = cursor.fetchone()[0]

    # 2. Sent to supervisor
    cursor.execute("""
        SELECT COUNT(*) FROM waste_records 
        WHERE status IN ('REFER TO SUPERVISOR', 'SUPERVISOR_RESOLVED')
           OR decided_by = 'Supervisor'
    """)
    sent_to_supervisor = cursor.fetchone()[0]
    sent_to_supervisor_pct = round((sent_to_supervisor / total_items * 100), 1) if total_items > 0 else 0.0

    # 3. % AI suggestions accepted
    cursor.execute("SELECT COUNT(*) FROM waste_records WHERE agreement = 'DISAGREED'")
    disagreed_count = cursor.fetchone()[0]
    ai_accepted_count = max(0, total_items - disagreed_count)
    ai_accepted_pct = round((ai_accepted_count / total_items * 100), 1) if total_items > 0 else 0.0

    # 4. Items this week (within the last 7 days)
    cursor.execute("""
        SELECT COUNT(*) FROM waste_records 
        WHERE datetime(timestamp) >= datetime('now', '-7 days')
    """)
    items_this_week = cursor.fetchone()[0]

    conn.close()
    return {
        "total_items": total_items,
        "sent_to_supervisor_pct": sent_to_supervisor_pct,
        "ai_accepted_pct": ai_accepted_pct,
        "items_this_week": items_this_week
    }


def get_waste_stream_counts():
    """
    Retrieves item counts grouped per waste stream for the CSS bar chart.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT stream_name, bin_colour FROM waste_streams ORDER BY id ASC")
    streams = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM waste_records")
    total_records = cursor.fetchone()[0]

    cursor.execute("""
        SELECT waste_stream, COUNT(*) as cnt 
        FROM waste_records 
        GROUP BY waste_stream
    """)
    counts_map = {row["waste_stream"]: row["cnt"] for row in cursor.fetchall()}

    results = []
    max_count = max(counts_map.values()) if counts_map else 0

    for s in streams:
        name = s["stream_name"]
        color = s["bin_colour"]
        count = counts_map.get(name, 0)
        bar_pct = round((count / max_count * 100), 1) if max_count > 0 else 0
        total_pct = round((count / total_records * 100), 1) if total_records > 0 else 0
        results.append({
            "stream_name": name,
            "bin_colour": color,
            "count": count,
            "bar_pct": bar_pct,
            "total_pct": total_pct
        })

    conn.close()
    return results
