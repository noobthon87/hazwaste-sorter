"""
seed_demo.py
------------
Inserts 30 realistic sample records for a Singapore aircraft maintenance training hangar.
All records are marked with is_demo = 1.
"""

import os
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
import database

# Ensure database is initialized
database.init_db()

# Create a clean demo placeholder image in uploads/
upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(upload_dir, exist_ok=True)
demo_img_path = os.path.join(upload_dir, "demo_waste_placeholder.jpg")

if not os.path.exists(demo_img_path):
    img = Image.new("RGB", (320, 240), color="#1e293b")
    draw = ImageDraw.Draw(img)
    draw.text((30, 105), "HAZWASTE DEMO SAMPLE", fill="#94a3b8")
    img.save(demo_img_path, "JPEG", quality=85)

DEMO_RECORDS = [
    # 1. Fuel soaked absorbent
    {
        "days_ago": 0, "hours_ago": 1,
        "description": "AVGAS 100LL fuel testing sample wipe from sump drain",
        "stream": "Oily / contaminated rags and absorbents", "bin": "Red",
        "confidence": 0.94, "status": "ADVISED",
        "reason": "Blue-dyed aviation gasoline stains on cellulose absorbent",
        "safety_reminder": "Flammable hydrocarbon. Keep away from ignition sources.",
        "ai_suggestion": "Oily / contaminated rags and absorbents",
        "final_stream": "Oily / contaminated rags and absorbents",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 2. Skydrol hydraulic wipe
    {
        "days_ago": 0, "hours_ago": 2,
        "description": "Purple fluid soaked wipe from A320 nose landing gear bay",
        "stream": "Oily / contaminated rags and absorbents", "bin": "Red",
        "confidence": 0.91, "status": "ADVISED",
        "reason": "Phosphate ester hydraulic fluid (Skydrol) residue detected",
        "safety_reminder": "Wear butyl gloves and goggles. Eye irritant.",
        "ai_suggestion": "Oily / contaminated rags and absorbents",
        "final_stream": "Oily / contaminated rags and absorbents",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 3. Emergency transmitter battery
    {
        "days_ago": 0, "hours_ago": 3,
        "description": "Expired ELT lithium-sulfur dioxide battery pack",
        "stream": "Used batteries", "bin": "Yellow",
        "confidence": 0.96, "status": "ADVISED",
        "reason": "Marked LiSO2 aviation battery with warning label",
        "safety_reminder": "Tape terminals with vinyl electrical tape before binning.",
        "ai_suggestion": "Used batteries",
        "final_stream": "Used batteries",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 4. Lockwire clippings
    {
        "days_ago": 0, "hours_ago": 4,
        "description": "MS20995C32 stainless steel safety wire clippings",
        "stream": "Metal swarf and scrap", "bin": "Blue",
        "confidence": 0.95, "status": "ADVISED",
        "reason": "Twisted unsoiled lockwire scraps from brake assembly",
        "safety_reminder": "Puncture risk. Use gloves and place directly in scrap bin.",
        "ai_suggestion": "Metal swarf and scrap",
        "final_stream": "Metal swarf and scrap",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 5. Composite carbon dust collection bag
    {
        "days_ago": 1, "hours_ago": 1,
        "description": "Fine black dust collected during rudder skin trim",
        "stream": "Composite dust and offcuts", "bin": "Yellow",
        "confidence": 0.89, "status": "ADVISED",
        "reason": "Carbon-fiber composite particulate from high-speed rotary cut",
        "safety_reminder": "Inhalation hazard. Keep bag sealed and wear N95 mask.",
        "ai_suggestion": "Composite dust and offcuts",
        "final_stream": "Composite dust and offcuts",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 6. PRC Sealant tube
    {
        "days_ago": 1, "hours_ago": 3,
        "description": "Empty Pro-Seal 890 fuel tank sealant cartridge",
        "stream": "Empty sealant / adhesive / paint containers", "bin": "Yellow",
        "confidence": 0.93, "status": "ADVISED",
        "reason": "Polysulfide chemical sealant container with nozzle",
        "safety_reminder": "Hazardous chemical packaging. Dispose in Yellow bin.",
        "ai_suggestion": "Empty sealant / adhesive / paint containers",
        "final_stream": "Empty sealant / adhesive / paint containers",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 7. Unsoiled parts packaging
    {
        "days_ago": 1, "hours_ago": 5,
        "description": "Clean corrugated cardboard box from Honeywell filter delivery",
        "stream": "General non-hazardous waste", "bin": "Black",
        "confidence": 0.98, "status": "ADVISED",
        "reason": "Dry, clean, uncontaminated packaging material",
        "safety_reminder": "Flatten box before placing in general recycling.",
        "ai_suggestion": "General non-hazardous waste",
        "final_stream": "General non-hazardous waste",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 8. Pending supervisor item: Faded aerosol can
    {
        "days_ago": 1, "hours_ago": 6,
        "description": "Dented metal spray can without label, found near spray booth",
        "stream": "Empty sealant / adhesive / paint containers", "bin": "Yellow",
        "confidence": 0.58, "status": "REFER TO SUPERVISOR",
        "reason": "Missing product label and warning symbols. Visual certainty below threshold.",
        "safety_reminder": "Do not puncture. Hold in quarantine staging tray for inspection.",
        "ai_suggestion": "Empty sealant / adhesive / paint containers",
        "final_stream": None,
        "decided_by": None, "agreement": None
    },
    # 9. Pending supervisor item: Unknown liquid stained rag
    {
        "days_ago": 2, "hours_ago": 1,
        "description": "Discolored rag with pungent solvent odor near engine cowl",
        "stream": "Oily / contaminated rags and absorbents", "bin": "Red",
        "confidence": 0.64, "status": "REFER TO SUPERVISOR",
        "reason": "Multiple conflicting chemical odors and discolored residue.",
        "safety_reminder": "Place in dedicated flammable quarantine tray.",
        "ai_suggestion": "Oily / contaminated rags and absorbents",
        "final_stream": None,
        "decided_by": None, "agreement": None
    },
    # 10. Supervisor resolved: AGREED with battery
    {
        "days_ago": 2, "hours_ago": 4,
        "description": "Corroded D-cell batteries removed from hangar flashlight",
        "stream": "Used batteries", "bin": "Yellow",
        "confidence": 0.67, "status": "SUPERVISOR_RESOLVED",
        "reason": "Heavy corrosion obscured brand markings.",
        "safety_reminder": "Hazardous heavy metal waste.",
        "ai_suggestion": "Used batteries",
        "final_stream": "Used batteries",
        "decided_by": "Supervisor", "agreement": "AGREED"
    },
    # 11. Supervisor resolved: DISAGREED (AI guessed General Waste, Supervisor set Sealant)
    {
        "days_ago": 2, "hours_ago": 7,
        "description": "Plastic squeeze tube covered in grey dried compound",
        "stream": "Empty sealant / adhesive / paint containers", "bin": "Yellow",
        "confidence": 0.52, "status": "SUPERVISOR_RESOLVED",
        "reason": "Tube appeared generic; supervisor confirmed RTV silicone sealant.",
        "safety_reminder": "Chemical adhesive waste.",
        "ai_suggestion": "General non-hazardous waste",
        "final_stream": "Empty sealant / adhesive / paint containers",
        "decided_by": "Supervisor", "agreement": "DISAGREED"
    },
    # 12. Aluminum rivet shanks
    {
        "days_ago": 3, "hours_ago": 2,
        "description": "2024-T3 aluminum solid rivet shanks from skin replacement",
        "stream": "Metal swarf and scrap", "bin": "Blue",
        "confidence": 0.95, "status": "ADVISED",
        "reason": "Clean aviation aluminum alloy fasteners",
        "safety_reminder": "Recyclable scrap metal.",
        "ai_suggestion": "Metal swarf and scrap",
        "final_stream": "Metal swarf and scrap",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 13. Prepreg composite offcuts
    {
        "days_ago": 3, "hours_ago": 4,
        "description": "Uncured carbon fiber prepreg scrap tape with backing paper",
        "stream": "Composite dust and offcuts", "bin": "Yellow",
        "confidence": 0.92, "status": "ADVISED",
        "reason": "Epoxy-resin pre-impregnated carbon weave offcuts",
        "safety_reminder": "Skin sensitizer. Wear disposable nitrile gloves.",
        "ai_suggestion": "Composite dust and offcuts",
        "final_stream": "Composite dust and offcuts",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 14. Acetone solvent wipe
    {
        "days_ago": 3, "hours_ago": 6,
        "description": "Kimwipe soaked in technical acetone from surface degreasing",
        "stream": "Oily / contaminated rags and absorbents", "bin": "Red",
        "confidence": 0.88, "status": "ADVISED",
        "reason": "Acetone solvent residue on low-lint wipe",
        "safety_reminder": "High vapor pressure and flammability. Red bin only.",
        "ai_suggestion": "Oily / contaminated rags and absorbents",
        "final_stream": "Oily / contaminated rags and absorbents",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 15. Clean paper towel
    {
        "days_ago": 4, "hours_ago": 1,
        "description": "Clean brown paper hand towel from washroom",
        "stream": "General non-hazardous waste", "bin": "Black",
        "confidence": 0.97, "status": "ADVISED",
        "reason": "Unsoiled domestic paper waste",
        "safety_reminder": "Standard disposal in Black bin.",
        "ai_suggestion": "General non-hazardous waste",
        "final_stream": "General non-hazardous waste",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 16. Turbine oil absorbent
    {
        "days_ago": 4, "hours_ago": 3,
        "description": "Eastman 2380 synthetic turbine engine oil sorbent pad",
        "stream": "Oily / contaminated rags and absorbents", "bin": "Red",
        "confidence": 0.93, "status": "ADVISED",
        "reason": "Synthetic ester engine lubricant saturation",
        "safety_reminder": "Combustible liquid residue. Dispose in Red bin.",
        "ai_suggestion": "Oily / contaminated rags and absorbents",
        "final_stream": "Oily / contaminated rags and absorbents",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 17. Titanium turnings
    {
        "days_ago": 4, "hours_ago": 5,
        "description": "Ti-6Al-4V metal shavings from bracket drilling",
        "stream": "Metal swarf and scrap", "bin": "Blue",
        "confidence": 0.91, "status": "ADVISED",
        "reason": "Curled metallic swarf from titanium drilling",
        "safety_reminder": "Sharp edges. Segregate from flammable contaminants.",
        "ai_suggestion": "Metal swarf and scrap",
        "final_stream": "Metal swarf and scrap",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 18. Pending supervisor item: Black rubber chunk
    {
        "days_ago": 5, "hours_ago": 2,
        "description": "Shredded elastomeric seal with fuel smell from wing tank door",
        "stream": "Oily / contaminated rags and absorbents", "bin": "Red",
        "confidence": 0.61, "status": "REFER TO SUPERVISOR",
        "reason": "Elastomer contaminated with kerosene. Borderline classification.",
        "safety_reminder": "Supervisor inspection required.",
        "ai_suggestion": "Oily / contaminated rags and absorbents",
        "final_stream": None,
        "decided_by": None, "agreement": None
    },
    # 19. Supervisor resolved: AGREED with composite dust
    {
        "days_ago": 5, "hours_ago": 4,
        "description": "Grey dust scraped from trailing edge fairing",
        "stream": "Composite dust and offcuts", "bin": "Yellow",
        "confidence": 0.66, "status": "SUPERVISOR_RESOLVED",
        "reason": "Dust appearance uncertain; supervisor confirmed fiberglass sanding dust.",
        "safety_reminder": "Hazardous composite dust.",
        "ai_suggestion": "Composite dust and offcuts",
        "final_stream": "Composite dust and offcuts",
        "decided_by": "Supervisor", "agreement": "AGREED"
    },
    # 20. Paint spray touch-up cup
    {
        "days_ago": 5, "hours_ago": 7,
        "description": "Disposable plastic liner with polyurethane topcoat residue",
        "stream": "Empty sealant / adhesive / paint containers", "bin": "Yellow",
        "confidence": 0.89, "status": "ADVISED",
        "reason": "Aviation polyurethane coating residual crust",
        "safety_reminder": "Hazardous chemical paint waste.",
        "ai_suggestion": "Empty sealant / adhesive / paint containers",
        "final_stream": "Empty sealant / adhesive / paint containers",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 21. Food container
    {
        "days_ago": 6, "hours_ago": 2,
        "description": "Empty plastic beverage cup and straw from technician break",
        "stream": "General non-hazardous waste", "bin": "Black",
        "confidence": 0.99, "status": "ADVISED",
        "reason": "Domestic canteen waste",
        "safety_reminder": "Black general waste bin.",
        "ai_suggestion": "General non-hazardous waste",
        "final_stream": "General non-hazardous waste",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 22. MEK solvent rag
    {
        "days_ago": 6, "hours_ago": 5,
        "description": "Methyl ethyl ketone wipe used for bonding prep",
        "stream": "Oily / contaminated rags and absorbents", "bin": "Red",
        "confidence": 0.93, "status": "ADVISED",
        "reason": "Volatile organic solvent residue on lint-free cloth",
        "safety_reminder": "Flammable vapor hazard. Red safety bin only.",
        "ai_suggestion": "Oily / contaminated rags and absorbents",
        "final_stream": "Oily / contaminated rags and absorbents",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 23. Disputed item (Reported by technician & resolved by supervisor)
    {
        "days_ago": 7, "hours_ago": 1,
        "description": "Cured sealant peelings from windscreen perimeter",
        "stream": "Empty sealant / adhesive / paint containers", "bin": "Yellow",
        "confidence": 0.74, "status": "SUPERVISOR_RESOLVED",
        "reason": "[Technician flagged via 'Wrong? Report it'] Supervisor confirmed chemical sealant.",
        "safety_reminder": "Dispose in Yellow bin.",
        "ai_suggestion": "General non-hazardous waste",
        "final_stream": "Empty sealant / adhesive / paint containers",
        "decided_by": "Supervisor", "agreement": "DISAGREED"
    },
    # 24. Cotter pins scrap
    {
        "days_ago": 7, "hours_ago": 4,
        "description": "Bent cadmium-plated split cotter pins from wheel axle nut",
        "stream": "Metal swarf and scrap", "bin": "Blue",
        "confidence": 0.94, "status": "ADVISED",
        "reason": "Steel scrap fastener hardware",
        "safety_reminder": "Metal scrap recycling bin.",
        "ai_suggestion": "Metal swarf and scrap",
        "final_stream": "Metal swarf and scrap",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 25. Lithium coin cell battery
    {
        "days_ago": 8, "hours_ago": 2,
        "description": "CR2032 clock battery from avionics display unit",
        "stream": "Used batteries", "bin": "Yellow",
        "confidence": 0.95, "status": "ADVISED",
        "reason": "Lithium metal 3V coin cell battery",
        "safety_reminder": "Tape both sides before disposing in Yellow battery bin.",
        "ai_suggestion": "Used batteries",
        "final_stream": "Used batteries",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 26. Supervisor resolved: AGREED with scrap metal
    {
        "days_ago": 9, "hours_ago": 3,
        "description": "Broken HSS drill bit fragments from wing spar hole",
        "stream": "Metal swarf and scrap", "bin": "Blue",
        "confidence": 0.68, "status": "SUPERVISOR_RESOLVED",
        "reason": "Fragmented tooling piece; supervisor confirmed high-speed steel.",
        "safety_reminder": "Wrap sharp edges before placing in Blue metal bin.",
        "ai_suggestion": "Metal swarf and scrap",
        "final_stream": "Metal swarf and scrap",
        "decided_by": "Supervisor", "agreement": "AGREED"
    },
    # 27. Masking tape
    {
        "days_ago": 10, "hours_ago": 1,
        "description": "Clean green 3M 233+ masking tape peeled from dry canopy",
        "stream": "General non-hazardous waste", "bin": "Black",
        "confidence": 0.96, "status": "ADVISED",
        "reason": "Uncontaminated adhesive masking paper",
        "safety_reminder": "General workshop waste bin.",
        "ai_suggestion": "General non-hazardous waste",
        "final_stream": "General non-hazardous waste",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 28. Cured epoxy adhesive mixing stick
    {
        "days_ago": 11, "hours_ago": 4,
        "description": "Wooden tongue depressor with hardened Araldite 2011",
        "stream": "Empty sealant / adhesive / paint containers", "bin": "Yellow",
        "confidence": 0.88, "status": "ADVISED",
        "reason": "Two-part epoxy adhesive applicator with cured chemical resin",
        "safety_reminder": "Chemical adhesive waste.",
        "ai_suggestion": "Empty sealant / adhesive / paint containers",
        "final_stream": "Empty sealant / adhesive / paint containers",
        "decided_by": "AI", "agreement": "N/A"
    },
    # 29. Pending supervisor item: Burnt circuit trace piece
    {
        "days_ago": 12, "hours_ago": 2,
        "description": "Charred relay board fragment with capacitor leakage",
        "stream": "Used batteries", "bin": "Yellow",
        "confidence": 0.55, "status": "REFER TO SUPERVISOR",
        "reason": "Thermal damage and chemical electrolyte leakage require inspection.",
        "safety_reminder": "Hold in quarantine staging tray.",
        "ai_suggestion": "Used batteries",
        "final_stream": None,
        "decided_by": None, "agreement": None
    },
    # 30. Supervisor resolved: AGREED with rags
    {
        "days_ago": 14, "hours_ago": 5,
        "description": "Heavy red-grease smeared cloth from flap actuator jack screw",
        "stream": "Oily / contaminated rags and absorbents", "bin": "Red",
        "confidence": 0.69, "status": "SUPERVISOR_RESOLVED",
        "reason": "Mobilgrease 28 hydrocarbon grease on shop towel.",
        "safety_reminder": "Red bin for oil-saturated textiles.",
        "ai_suggestion": "Oily / contaminated rags and absorbents",
        "final_stream": "Oily / contaminated rags and absorbents",
        "decided_by": "Supervisor", "agreement": "AGREED"
    }
]

def seed():
    conn = database.get_connection()
    conn.execute("DELETE FROM waste_records WHERE is_demo = 1")
    conn.commit()
    conn.close()

    print(f"Seeding {len(DEMO_RECORDS)} realistic demo records...")
    now = datetime.now()
    count = 0

    for item in DEMO_RECORDS:
        record_time = now - timedelta(days=item["days_ago"], hours=item["hours_ago"])
        time_str = record_time.strftime("%Y-%m-%d %H:%M:%S")

        database.insert_record(
            image_filename="demo_waste_placeholder.jpg",
            description=item["description"],
            waste_stream=item["stream"],
            bin_colour=item["bin"],
            confidence=item["confidence"],
            status=item["status"],
            reason=item["reason"],
            safety_reminder=item["safety_reminder"],
            ai_suggestion=item["ai_suggestion"],
            final_stream=item["final_stream"],
            decided_by=item["decided_by"],
            decided_at=time_str if item["decided_by"] else None,
            agreement=item["agreement"],
            is_demo=1,
            timestamp=time_str
        )
        count += 1

    print(f"[SUCCESS] Successfully seeded {count} demo records marked with is_demo = 1.")

if __name__ == "__main__":
    seed()
