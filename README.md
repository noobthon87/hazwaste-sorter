# ✈️ HazWaste Sorter

**HazWaste Sorter** is a specialized web application engineered for aircraft maintenance hangars (line & base MRO facilities). It enables hangar technicians to upload a photo or type a description of a maintenance waste item, automatically classifying it into the hangar's designated hazardous and industrial waste streams.

---

## 📋 Hangar Waste Streams & Designated Bin Colours

| Waste Stream | Bin Colour | Examples & Chemical Notes | One-Line Safety Reminder |
| :--- | :---: | :--- | :--- |
| **Contaminated Rags & Absorbents** | **Yellow** | Kimwipes with MEK, solvent wipes, oily shop towels, PPE, contaminated nitrile gloves | *Dispose in self-closing, foot-operated fire-safe cans to prevent spontaneous combustion.* |
| **Flammable Solvents & Thinners** | **Red** | MEK, Acetone, MPK, Isopropyl Alcohol (IPA), paint thinners, degreasers, toluene | *Keep sealed in grounded FM-approved containers away from ignition sources; vapors are volatile.* |
| **Aviation Hydraulic Fluids (Skydrol)** | **Purple** | Skydrol LD-4, Skydrol 500B-4, Exxon HyJet IV/V, hydraulic filter elements | *Severe eye and skin irritant; wear butyl rubber gloves and full face shield.* |
| **Aviation Oils & Turbine Lubricants** | **Black** | Mobil Jet Oil II, Royco turbine oils, grease tubes, drained Jet-A fuel sumps | *Do not mix with chlorinated solvents or Skydrol; store in sealed waste oil drum.* |
| **Sealants, Adhesives & Resins** | **Orange** | PRC Pro-Seal 890 / 870, polysulfide, epoxy resin (EA 9394), uncured sealant tubes | *Contains toxic isocyanates/curing agents; ensure waste cures in ventilated zone before disposal.* |
| **Aerosol Cans & Pressurized Sprays** | **Blue** | LPS 1/2/3, contact cleaner, NDT penetrant spray cans, primer sprays | *Do not puncture manually; place intact in aerosol drum or depressurize via filtered puncturing unit.* |
| **Universal Waste (Batteries & Electronics)** | **White** | Aircraft Ni-Cad batteries, lead-acid batteries, ELTs, avionics boxes, fluorescent tubes | *Tape terminals to prevent short circuit and thermal runaway; electrolyte is highly corrosive.* |
| **Scrap Metal & Clean Hardware** | **Green** | Clipped MS20995 safety lockwire, sheared rivets, AN bolts, clean aluminum scrap | *Verify zero chemical or hydrocarbon contamination before placing in metal recycling.* |

---

## 🛡️ Critical Safety Rule: `< 0.70` Supervisor Routing

In aviation maintenance, incorrect waste segregation creates severe chemical reaction, fire, and regulatory compliance hazards. 

> **Mandatory Rule**: If classification confidence is **below 0.70**, the system will **never guess**. It returns `'Refer to supervisor'` and marks the item for **Quarantine Hold (Yellow-Black Stripe)**.

### JSON Response Schema

#### When Confidence &ge; 0.70 (Confirmed Stream Match)
```json
{
  "category": "Contaminated Rags & Absorbents",
  "bin_colour": "Yellow",
  "confidence": 0.94,
  "safety_reminder": "Dispose in self-closing, foot-operated fire-safe cans to prevent spontaneous combustion."
}
```

#### When Confidence &lt; 0.70 (Supervisor Referral Triggered)
```json
{
  "category": "Refer to supervisor",
  "bin_colour": "Quarantine / Yellow-Black Stripe",
  "confidence": 0.20,
  "safety_reminder": "Uncertain waste identification. Do not dispose in regular bins; isolate in HazMat Quarantine and alert Shift Supervisor or EHS."
}
```

---

## 🚀 How to Run the Web App

### Option 1: Full-Stack Web Server (Recommended)
From the project folder:
```bash
python run.py
```
Or with `server.py`:
```bash
python server.py
```
Open your browser at **`http://localhost:8000`**.

### Option 2: Direct Browser Execution (Zero Dependencies)
You can directly open `public/index.html` in Chrome, Edge, or Firefox. The built-in client-side aviation engine will perform instant classification without requiring any server.

---

## 🛠️ Key Interface Features

1. **Intake Panel (Step 1)**:
   - **Upload Button & Drag-and-Drop Zone**: Upload or drag any waste photo (JPEG, PNG, WebP) with live preview and removal.
   - **Description Textarea**: Input chemical names, part numbers, or inspection notes.
   - **Quick Test Presets**: One-click chips for rapid testing (including both high-confidence standard hangar items and low-confidence mystery items).
2. **Classification Result Card (Step 2)**:
   - **Stream Match vs. Supervisor Alert Banner**: Color-coded status.
   - **Visual Bin Color Swatch**: Big color badge indicating the physical bin colour.
   - **Confidence Meter**: Visual bar calibrated against the 0.70 threshold.
   - **One-Line Safety Reminder**: Direct safety handling instructions.
   - **Returned JSON Inspector**: Live formatted JSON view with one-click **Copy JSON** button.
   - **Log Disposal CTA**: Appends the item directly to the table below.
3. **Hangar Sorting Log Table**:
   - Stores all sorted items with timestamps, thumbnails, descriptions, stream, bin colour, confidence score, and status.
   - Filter by All, Sorted, or Referred to Supervisor.
   - **Export CSV** button: Instant download for EHS and OSHA/FAA audit compliance.
   - Persistent `localStorage` caching across sessions.

---

## 📱 Deploying for Students on Mobile Phones

### Method 1: Instant Classroom Wi-Fi (No Setup, Works Right Now)
When your computer and students' phones are connected to the same Wi-Fi or classroom network:
1. Run `python server.py`.
2. Open `http://localhost:8000` on your desktop and click the **📱 Student Mobile QR** button in the header.
3. Show/project the QR code on screen. Students open their phone camera, scan the QR code, and immediately access the app (e.g. `http://<your-lan-ip>:8000`).

### Method 2: 100% Free Public Web Hosting (GitHub Pages / Netlify / Vercel)
The `public/` directory is an independent Progressive Web App (PWA) with full camera capture, offline caching, and instant classification:
- **Netlify Drop (Easiest, 30 seconds)**:
  1. Open [app.netlify.com/drop](https://app.netlify.com/drop).
  2. Drag and drop the `public` folder onto the browser window.
  3. Netlify generates an instant public `https://....netlify.app` URL with free SSL!
- **GitHub Pages**:
  1. Push the repo to GitHub.
  2. In your repo settings, go to **Pages** and set the source to deploy `/public` folder or the main branch.
  3. Free URL: `https://<your-username>.github.io/hazwaste-sorter/`.

### Method 3: Container Cloud Deployment (Render.com / Google Cloud Run)
- Deploy the Python API and web interface to [Render.com](https://render.com) using the included `Dockerfile` and `render.yaml`.

### 📲 Mobile App Installation (PWA):
- **iPhone / iPad (iOS)**: Open link in Safari &rarr; tap **Share** button &rarr; tap **"Add to Home Screen"**.
- **Android**: Open link in Chrome &rarr; tap **⋮** (three dots) &rarr; tap **"Add to Home Screen"** or **"Install App"**.

