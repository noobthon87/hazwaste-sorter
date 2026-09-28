"""
HazWaste Sorter - Aircraft Maintenance Hangar Waste Classification Server
Powered by Starlette and Uvicorn.
Provides:
  - POST /api/classify: Classify waste item (photo and/or description)
  - GET  /api/streams: Retrieve current hangar waste streams
  - Static file serving for web UI
"""

import os
import json
import re
import base64
import mimetypes
from typing import Dict, Any, List, Optional
import httpx
from starlette.applications import Starlette
from starlette.responses import JSONResponse, FileResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import uvicorn

# Aircraft Maintenance Hangar Waste Streams Specification
HANGAR_STREAMS = [
    {
        "id": "contaminated_rags",
        "name": "Contaminated Rags & Absorbents",
        "bin_colour": "Yellow",
        "badge_bg": "#fef08a",
        "badge_text": "#854d0e",
        "hex": "#eab308",
        "keywords": [
            "rag", "rags", "wipe", "wipes", "kimwipe", "kimwipes", "cloth", "towel", "towels",
            "absorbent", "pig mat", "spill pad", "pads", "ppe", "nitrile glove", "gloves",
            "tyvek", "oily rag", "solvent soaked rag", "contaminated wipe", "shop towel", "shop towels"
        ],
        "safety_reminder": "Dispose in self-closing, foot-operated fire-safe cans to prevent spontaneous combustion."
    },
    {
        "id": "flammable_solvents",
        "name": "Flammable Solvents & Thinners",
        "bin_colour": "Red",
        "badge_bg": "#fee2e2",
        "badge_text": "#991b1b",
        "hex": "#ef4444",
        "keywords": [
            "mek", "methyl ethyl ketone", "mpk", "acetone", "toluene", "xylene",
            "isopropyl alcohol", "ipa", "paint thinner", "lacquer thinner", "solvent", "solvents",
            "alodine", "degreaser", "mineral spirits", "naphtha", "flammable liquid", "aliphatic naphtha"
        ],
        "safety_reminder": "Keep sealed in grounded FM-approved containers away from ignition sources; vapors are volatile."
    },
    {
        "id": "hydraulic_fluids",
        "name": "Aviation Hydraulic Fluids (Skydrol)",
        "bin_colour": "Purple",
        "badge_bg": "#f3e8ff",
        "badge_text": "#6b21a8",
        "hex": "#a855f7",
        "keywords": [
            "skydrol", "hydraulic fluid", "phosphate ester", "hyjet", "bms 3-11",
            "mil-prf-5606", "mil-prf-83282", "hydraulic line", "hydraulic filter",
            "skydrol ld-4", "skydrol 500b-4", "actuator fluid", "reservoir drain", "hydraulic bowl"
        ],
        "safety_reminder": "Severe eye and skin irritant; wear butyl rubber gloves and full face shield."
    },
    {
        "id": "oils_hydrocarbons",
        "name": "Aviation Oils & Turbine Lubricants",
        "bin_colour": "Black",
        "badge_bg": "#f1f5f9",
        "badge_text": "#0f172a",
        "hex": "#1e293b",
        "keywords": [
            "engine oil", "turbine oil", "mobil jet", "jet oil ii", "bp turbo",
            "royco", "aeroshell", "grease", "lubricant", "jet-a", "jet fuel",
            "avgas", "fuel sump", "mil-prf-23699", "mil-prf-7808", "oil filter", "apu oil"
        ],
        "safety_reminder": "Do not mix with chlorinated solvents or Skydrol; store in sealed waste oil drum."
    },
    {
        "id": "sealants_adhesives",
        "name": "Sealants, Adhesives & Resins",
        "bin_colour": "Orange",
        "badge_bg": "#ffedd5",
        "badge_text": "#9a3412",
        "hex": "#f97316",
        "keywords": [
            "pro-seal", "proseal", "prc", "pr-1422", "pr-1776", "pr-1440", "b-1/2", "b-2",
            "polysulfide", "polythioether", "sealant", "silicone", "rtd", "epoxy",
            "resin", "loctite", "adhesive", "ea 9394", "potting compound", "curing agent", "sealant tube"
        ],
        "safety_reminder": "Contains toxic isocyanates/curing agents; ensure waste cures in ventilated zone before disposal."
    },
    {
        "id": "aerosol_cans",
        "name": "Aerosol Cans & Pressurized Sprays",
        "bin_colour": "Blue",
        "badge_bg": "#dbeafe",
        "badge_text": "#1e40af",
        "hex": "#3b82f6",
        "keywords": [
            "aerosol", "spray can", "lps", "lps 1", "lps 2", "lps 3", "contact cleaner",
            "penetrant", "developer spray", "dykem", "brake cleaner", "dry lube",
            "corrosion inhibitor spray", "primer spray", "can of spray"
        ],
        "safety_reminder": "Do not puncture manually; place intact in aerosol drum or depressurize via filtered puncturing unit."
    },
    {
        "id": "universal_waste",
        "name": "Universal Waste (Batteries & Electronics)",
        "bin_colour": "White",
        "badge_bg": "#f8fafc",
        "badge_text": "#334155",
        "hex": "#e2e8f0",
        "keywords": [
            "battery", "batteries", "ni-cad", "nickel-cadmium", "lead-acid", "lithium",
            "elt battery", "emergency light power unit", "circuit board", "avionics box",
            "fluorescent tube", "mercury switch", "relay", "strobe power supply"
        ],
        "safety_reminder": "Tape terminals to prevent short circuit and thermal runaway; electrolyte is highly corrosive."
    },
    {
        "id": "scrap_metal",
        "name": "Scrap Metal & Clean Hardware",
        "bin_colour": "Green",
        "badge_bg": "#dcfce7",
        "badge_text": "#166534",
        "hex": "#22c55e",
        "keywords": [
            "lockwire", "safety wire", "rivet", "rivets", "bolt", "nut", "screw",
            "cotter pin", "bracket", "aluminum scrap", "titanium scrap", "swarf",
            "metal shavings", "dry cardboard", "clean packaging", "fastener", "fasteners"
        ],
        "safety_reminder": "Verify zero chemical or hydrocarbon contamination before placing in metal recycling."
    }
]

AMBIGUOUS_KEYWORDS = [
    "unknown", "unlabeled", "unmarked", "mystery", "not sure", "strange",
    "cloudy", "sludge", "residue", "weird", "unidentified", "leaking fluid",
    "mixture", "puddle", "smelly", "suspicious", "found on floor", "unmarked cup",
    "unidentified liquid", "yellowish liquid", "brown sludge"
]

def classify_locally(description: str, filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Local heuristic aviation HazMat classification engine.
    Follows:
    1. Returns JSON with category, bin colour, confidence (0-1), and a one-line safety reminder.
    2. If confidence is below 0.7, returns 'Refer to supervisor' instead of guessing.
    """
    text = (description or "").lower().strip()
    fname = (filename or "").lower().strip()
    combined = f"{text} {fname}"

    if not combined.strip():
        return {
            "category": "Refer to supervisor",
            "bin_colour": "Quarantine / Yellow-Black Stripe",
            "confidence": 0.0,
            "safety_reminder": "No waste details or photo provided. Hold item in quarantine and notify shift supervisor."
        }

    # Count ambiguity markers
    ambiguity_count = sum(1 for kw in AMBIGUOUS_KEYWORDS if kw in combined)

    # Check specifically for solid absorbents/wipes/rags soaked in solvent or oil
    is_solid_wipe = any(w in combined for w in ["rag", "rags", "wipe", "wipes", "kimwipe", "kimwipes", "towel", "cloth", "pad", "ppe", "glove"])

    scores = {}
    for stream in HANGAR_STREAMS:
        score = 0
        matched_keywords = []
        for kw in stream["keywords"]:
            pattern = r'\b' + re.escape(kw) + r'\b'
            matches = len(re.findall(pattern, combined))
            if matches > 0:
                score += matches * 3
                matched_keywords.append(kw)
            elif kw in combined:
                score += 1
                matched_keywords.append(kw)
        
        # If the item is a wipe/rag/towel, give boost to contaminated_rags stream
        if is_solid_wipe and stream["id"] == "contaminated_rags":
            score += 6
        
        scores[stream["id"]] = {
            "stream": stream,
            "raw_score": score,
            "matched_keywords": matched_keywords
        }

    sorted_streams = sorted(scores.values(), key=lambda s: s["raw_score"], reverse=True)
    best = sorted_streams[0]
    runner_up = sorted_streams[1] if len(sorted_streams) > 1 else None

    confidence = 0.0
    if best["raw_score"] == 0:
        confidence = 0.20
    else:
        num_matches = len(best["matched_keywords"])
        if num_matches >= 3:
            confidence = 0.96
        elif num_matches == 2:
            confidence = 0.91
        elif num_matches == 1:
            high_spec = ["skydrol", "mek", "pro-seal", "proseal", "ni-cad", "mobil jet", "lockwire", "safety wire", "lps 3", "lps"]
            if any(k in best["matched_keywords"] for k in high_spec):
                confidence = 0.89
            else:
                confidence = 0.75

        # Solid wipe override confidence
        if is_solid_wipe and best["stream"]["id"] == "contaminated_rags":
            confidence = max(confidence, 0.94)
        elif runner_up and runner_up["raw_score"] > 0:
            score_ratio = runner_up["raw_score"] / best["raw_score"]
            if score_ratio >= 0.8:
                confidence -= 0.18

        # Penalize for ambiguity words
        if ambiguity_count > 0:
            confidence -= (0.30 * ambiguity_count)

    confidence = round(max(0.05, min(0.99, confidence)), 2)

    # Core Rule: If confidence is below 0.7, return 'Refer to supervisor' instead of guessing
    if confidence < 0.7:
        return {
            "category": "Refer to supervisor",
            "bin_colour": "Quarantine / Yellow-Black Stripe",
            "confidence": confidence,
            "safety_reminder": "Uncertain waste identification. Do not dispose in regular bins; isolate in HazMat Quarantine and alert Shift Supervisor or EHS."
        }
    else:
        return {
            "category": best["stream"]["name"],
            "bin_colour": best["stream"]["bin_colour"],
            "confidence": confidence,
            "safety_reminder": best["stream"]["safety_reminder"]
        }


async def classify_with_gemini(description: str, image_bytes: Optional[bytes], mime_type: Optional[str], api_key: str) -> Optional[Dict[str, Any]]:
    """
    Call Gemini API with structured prompt enforcing hangar streams and the < 0.7 threshold.
    """
    streams_summary = "\n".join([f"- {s['name']} (Bin: {s['bin_colour']}): e.g. {', '.join(s['keywords'][:6])}" for s in HANGAR_STREAMS])

    system_instruction = f"""You are the Environmental Health & Safety (EHS) Hazardous Waste Classification expert for an aircraft maintenance hangar.
The technician is submitting a photo and/or text description of a waste item.

Your job: Classify the item into EXACTLY ONE of the hangar's designated waste streams:
{streams_summary}

RULES:
1. Return JSON matching this exact structure:
{{
  "category": string,
  "bin_colour": string,
  "confidence": number between 0.00 and 1.00,
  "safety_reminder": string (one-line safety reminder for handling this waste)
}}

2. CRITICAL THRESHOLD:
If confidence is below 0.7, return 'Refer to supervisor' instead of guessing.
When confidence < 0.7:
- "category": "Refer to supervisor"
- "bin_colour": "Quarantine / Yellow-Black Stripe"
- "confidence": <float between 0.00 and 0.69>
- "safety_reminder": "Uncertain waste identification. Do not dispose in regular bins; isolate in HazMat Quarantine and alert Shift Supervisor or EHS."

Return ONLY valid raw JSON, with no markdown code fences."""

    parts = []
    if image_bytes and mime_type:
        b64_data = base64.b64encode(image_bytes).decode("utf-8")
        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": b64_data
            }
        })
    
    prompt_text = description if description else "Classify the waste item shown in this image."
    parts.append({"text": prompt_text})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": parts}],
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1
        }
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                # Parse JSON
                result = json.loads(text_content)
                # Enforce rule server-side regardless of LLM adherence
                conf = float(result.get("confidence", 0.0))
                if conf < 0.7 or result.get("category") == "Refer to supervisor":
                    return {
                        "category": "Refer to supervisor",
                        "bin_colour": "Quarantine / Yellow-Black Stripe",
                        "confidence": round(conf, 2),
                        "safety_reminder": result.get("safety_reminder", "Uncertain waste identification. Do not dispose in regular bins; isolate in HazMat Quarantine and alert Shift Supervisor or EHS.")
                    }
                return {
                    "category": result.get("category", "Refer to supervisor"),
                    "bin_colour": result.get("bin_colour", "Quarantine / Yellow-Black Stripe"),
                    "confidence": round(conf, 2),
                    "safety_reminder": result.get("safety_reminder", "Follow standard hangar EHS disposal protocols.")
                }
    except Exception as e:
        print(f"Gemini API call failed or timed out: {e}. Falling back to local expert engine.")
        return None


async def classify_endpoint(request):
    """
    HTTP POST /api/classify
    Accepts JSON body or multipart form data.
    """
    description = ""
    filename = ""
    image_bytes = None
    mime_type = None
    api_key = request.headers.get("x-gemini-api-key") or os.environ.get("GEMINI_API_KEY", "").strip()

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            data = await request.json()
            description = data.get("description", "")
            filename = data.get("filename", "")
            if data.get("apiKey"):
                api_key = data.get("apiKey").strip()
            # Support inline base64 image if sent via JSON
            if data.get("image_base64"):
                b64_str = data.get("image_base64")
                if "," in b64_str:
                    header, b64_str = b64_str.split(",", 1)
                    if "image/jpeg" in header: mime_type = "image/jpeg"
                    elif "image/png" in header: mime_type = "image/png"
                    elif "image/webp" in header: mime_type = "image/webp"
                image_bytes = base64.b64decode(b64_str)
        except Exception as e:
            return JSONResponse({"error": f"Invalid JSON payload: {str(e)}"}, status_code=400)
            
    elif "multipart/form-data" in content_type:
        try:
            form = await request.form()
            description = form.get("description", "")
            if form.get("apiKey"):
                api_key = form.get("apiKey").strip()
            upload_file = form.get("photo")
            if upload_file and hasattr(upload_file, "filename") and upload_file.filename:
                filename = upload_file.filename
                image_bytes = await upload_file.read()
                mime_type = upload_file.content_type or mimetypes.guess_type(filename)[0] or "image/jpeg"
        except Exception as e:
            return JSONResponse({"error": f"Error parsing form data: {str(e)}"}, status_code=400)
    else:
        description = request.query_params.get("description", "")

    # Attempt Gemini multimodal if API key is provided and valid
    if api_key and (image_bytes or description):
        gemini_result = await classify_with_gemini(description, image_bytes, mime_type, api_key)
        if gemini_result:
            return JSONResponse(gemini_result)

    # Use local aviation heuristic engine
    result = classify_locally(description, filename)
    return JSONResponse(result)


async def streams_endpoint(request):
    """
    HTTP GET /api/streams
    Returns the hangar's configured waste streams.
    """
    return JSONResponse({"streams": HANGAR_STREAMS})


import socket

def get_lan_ip() -> str:
    """Attempts to find the local LAN IP address accessible by other devices on the same Wi-Fi."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


async def network_info_endpoint(request):
    """
    HTTP GET /api/network-info
    Returns the server's local LAN IP and mobile connection URL.
    """
    lan_ip = get_lan_ip()
    port = int(os.environ.get("PORT", 8000))
    mobile_url = f"http://{lan_ip}:{port}"
    return JSONResponse({
        "lan_ip": lan_ip,
        "port": port,
        "mobile_url": mobile_url,
        "qr_api_url": f"https://api.qrserver.com/v1/create-qr-code/?size=240x240&data={mobile_url}"
    })


async def health_endpoint(request):
    return JSONResponse({
        "status": "ok",
        "app": "HazWaste Sorter",
        "hangar": "Hangar 4 Line & Base Maintenance",
        "version": "1.0",
        "mobile_ready": True
    })


# Web UI static route
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
os.makedirs(PUBLIC_DIR, exist_ok=True)

routes = [
    Route("/api/classify", classify_endpoint, methods=["POST"]),
    Route("/api/streams", streams_endpoint, methods=["GET"]),
    Route("/api/network-info", network_info_endpoint, methods=["GET"]),
    Route("/api/health", health_endpoint, methods=["GET"]),
    Mount("/", app=StaticFiles(directory=PUBLIC_DIR, html=True), name="public"),
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
]

app = Starlette(debug=True, routes=routes, middleware=middleware)

if __name__ == "__main__":
    lan_ip = get_lan_ip()
    port = int(os.environ.get("PORT", 8000))
    print("=" * 65)
    print("✈️  HazWaste Sorter - Aircraft Maintenance Hangar")
    print(f"   💻 Desktop Local: http://localhost:{port}")
    print(f"   📱 Student Mobile (Same Wi-Fi): http://{lan_ip}:{port}")
    print(f"   📂 Static assets: {PUBLIC_DIR}")
    print("=" * 65)
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


