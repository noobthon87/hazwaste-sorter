# ✈️ HazWaste Sorter (Singapore Hangar Prototype)

An AI-assisted hazardous waste sorting prototype designed for aircraft maintenance training hangars in Singapore.

---

## 📋 Features

- **Mobile-First Design**: Optimized for smartphone browsers with large, glove-friendly touch targets.
- **Direct Rear Camera Trigger**: Uses `<input type="file" accept="image/*" capture="environment">` to open the rear camera directly.
- **Singapore Hangar 4-Bin Standard**:
  - 🔴 **Red Bin**: Flammable & Solvents (e.g., fuel/MEK rags, absorbents)
  - 🟡 **Yellow Bin**: Chemical & Hazardous Contaminants (e.g., Skydrol rags, sealant tubes, batteries)
  - 🔵 **Blue Bin**: General Recyclables & Metal Scrap (e.g., clean cardboard, wire clippings)
  - ⚫ **Black Bin**: General Waste (e.g., workshop trash)
- **Live Gemini Classification**: Multimodal visual identification using Google's `google-genai` SDK.
- **Python Safety Rule Enforcement**:
  1. Confidence $< 0.70$ automatically sets `status = "REFER TO SUPERVISOR"`.
  2. Waste streams not in the official whitelist set `status = "REFER TO SUPERVISOR"`.
  3. Privacy filter: if a person's face, name tag, or staff ID card is detected, the photo is deleted immediately and not saved.
  4. Robust error handling ensures the app never crashes.
- **Supervisor Review Queue & PIN Protection**:
  - 4-digit PIN protection (`SUPERVISOR_PIN`, default `1234`).
  - Lists items needing decision, newest first, with photo, description, AI suggestion, reason, and confidence.
  - Dropdown to assign final stream; records `decided_by = "Supervisor"`, timestamp, and whether supervisor `AGREED` or `DISAGREED` with AI.
- **"Wrong? Report it" Dispute Action**: Confidently classified items can be disputed by technicians, immediately sending them to the review queue.
- **Auditing & Logging**: Stored in a lightweight SQLite database (`hazwaste.db`) using Python's built-in `sqlite3` module.
- **Safety Governance & Compliance Features**:
  1. **Immutable Audit Trail (`audit_log`)**: Every modification (technician dispute, supervisor resolution, stream correction, data retention purge) is recorded with `item_id`, `field`, `old_value`, `new_value`, `changed_by`, and `timestamp`. Items can never be deleted from the database—only corrected.
  2. **"About this AI & Safety Governance" Page (`/about`)**: Accessible from the persistent footer on every screen, explaining in plain English what the app does/does not do, supervisor authority, the 0.70 confidence threshold rationale, privacy/PDPA rules, operational limitations, and data retention.
  3. **Automated 30-Day Photo Deletion Policy**: Uploaded photos older than 30 days are automatically unlinked and permanently deleted from disk on startup/maintenance, while preserving the full anonymized text audit log in SQLite.

---

## 🚀 Quick Start Guide

### 1. Configure Your `.env` File
Open `.env` in the project folder:
```env
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-2.5-flash
SUPERVISOR_PIN=1234
```

### 2. Activate the Virtual Environment
Open PowerShell inside the project directory:
```powershell
cd C:\Users\ajmea\.gemini\antigravity\scratch\hazwaste-sorter
.\venv\Scripts\Activate.ps1
```

### 3. Run the App
```powershell
python app.py
```
The app will start at `http://127.0.0.1:5000`.

---

## 📱 How to Open on Your Mobile Phone

1. Connect your phone to the **same Wi-Fi network**.
2. Find your laptop's local IPv4 address (e.g., via `ipconfig` in PowerShell).
3. Open your mobile browser and go to:
   ```text
   http://<YOUR_LOCAL_IP>:5000
   ```
4. **Screens & Flows:**
   - **Scan**: Snap a photo of a waste item, add an optional description, tap **Classify**.
   - **Review**: Tap **Review** in bottom nav &rarr; Enter 4-digit PIN (`1234`) &rarr; Assign stream from dropdown &rarr; Tap **Confirm**.
   - **Log**: View summary tiles, CSS horizontal bar chart, 50 most recent items table, and tap **Export CSV** to download records.
   - **About / Governance**: Tap **ℹ️ About this AI & Safety Governance** in the footer of any screen.
   - **Demo Data**: Populate 30 realistic hangar sample records anytime by running:
     ```powershell
     python seed_demo.py
     ```

---

## 🧪 Run Automated Tests

To verify all features, rules, review workflow, analytics, and governance:
```powershell
python test_rules.py
python test_review.py
python test_log_screen.py
python test_governance.py
```
