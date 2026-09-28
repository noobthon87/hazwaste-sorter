/**
 * HazWaste Sorter - Client Application
 * Aircraft Maintenance Hangar Waste Classification Interface
 */

// Aircraft Hangar Waste Streams Definition
const HANGAR_STREAMS = [
  {
    id: "contaminated_rags",
    name: "Contaminated Rags & Absorbents",
    bin_colour: "Yellow",
    badge_class: "chip-yellow",
    swatch_class: "swatch-yellow",
    keywords: ["rag", "rags", "wipe", "wipes", "kimwipe", "kimwipes", "cloth", "towel", "absorbent", "pig mat", "spill pad", "ppe", "nitrile glove", "gloves", "tyvek", "oily rag", "solvent soaked rag", "contaminated wipe", "shop towel"],
    safety_reminder: "Dispose in self-closing, foot-operated fire-safe cans to prevent spontaneous combustion.",
    examples: "MEK solvent wipes, Skydrol saturated rags, oily paper towels, contaminated nitrile gloves"
  },
  {
    id: "flammable_solvents",
    name: "Flammable Solvents & Thinners",
    bin_colour: "Red",
    badge_class: "chip-red",
    swatch_class: "swatch-red",
    keywords: ["mek", "methyl ethyl ketone", "mpk", "acetone", "toluene", "xylene", "isopropyl alcohol", "ipa", "paint thinner", "lacquer thinner", "solvent", "alodine", "degreaser", "mineral spirits", "naphtha", "flammable liquid"],
    safety_reminder: "Keep sealed in grounded FM-approved containers away from ignition sources; vapors are volatile.",
    examples: "Leftover MEK, Acetone wash liquid, paint gun cleaning solvents, alcohol wash"
  },
  {
    id: "hydraulic_fluids",
    name: "Aviation Hydraulic Fluids (Skydrol)",
    bin_colour: "Purple",
    badge_class: "chip-purple",
    swatch_class: "swatch-purple",
    keywords: ["skydrol", "hydraulic fluid", "phosphate ester", "hyjet", "bms 3-11", "mil-prf-5606", "mil-prf-83282", "hydraulic line", "hydraulic filter", "skydrol ld-4", "skydrol 500b-4", "actuator fluid", "reservoir drain"],
    safety_reminder: "Severe eye and skin irritant; wear butyl rubber gloves and full face shield.",
    examples: "Drained Skydrol LD-4, BMS 3-11 phosphate ester, contaminated hydraulic filter bowls"
  },
  {
    id: "oils_hydrocarbons",
    name: "Aviation Oils & Turbine Lubricants",
    bin_colour: "Black",
    badge_class: "chip-black",
    swatch_class: "swatch-black",
    keywords: ["engine oil", "turbine oil", "mobil jet", "jet oil ii", "bp turbo", "royco", "aeroshell", "grease", "lubricant", "jet-a", "jet fuel", "avgas", "fuel sump", "mil-prf-23699", "mil-prf-7808", "oil filter"],
    safety_reminder: "Do not mix with chlorinated solvents or Skydrol; store in sealed waste oil drum.",
    examples: "Mobil Jet Oil II, Royco 808, turbine engine oil filter elements, drained Jet-A fuel samples"
  },
  {
    id: "sealants_adhesives",
    name: "Sealants, Adhesives & Resins",
    bin_colour: "Orange",
    badge_class: "chip-orange",
    swatch_class: "swatch-orange",
    keywords: ["pro-seal", "proseal", "prc", "pr-1422", "pr-1776", "b-1/2", "b-2", "polysulfide", "polythioether", "sealant", "silicone", "rtd", "epoxy", "resin", "loctite", "adhesive", "ea 9394", "potting compound", "curing agent"],
    safety_reminder: "Contains toxic isocyanates/curing agents; ensure waste cures in ventilated zone before disposal.",
    examples: "Expired PRC Pro-Seal 890 tubes, uncured polysulfide cartridges, EA 9394 epoxy resin"
  },
  {
    id: "aerosol_cans",
    name: "Aerosol Cans & Pressurized Sprays",
    bin_colour: "Blue",
    badge_class: "chip-blue",
    swatch_class: "swatch-blue",
    keywords: ["aerosol", "spray can", "lps", "lps 1", "lps 2", "lps 3", "contact cleaner", "penetrant", "developer spray", "dykem", "brake cleaner", "dry lube", "corrosion inhibitor spray", "primer spray"],
    safety_reminder: "Do not puncture manually; place intact in aerosol drum or depressurize via filtered puncturing unit.",
    examples: "Spent LPS 3 rust inhibitor cans, contact cleaner sprays, NDT penetrant inspection cans"
  },
  {
    id: "universal_waste",
    name: "Universal Waste (Batteries & Electronics)",
    bin_colour: "White",
    badge_class: "chip-white",
    swatch_class: "swatch-white",
    keywords: ["battery", "batteries", "ni-cad", "nickel-cadmium", "lead-acid", "lithium", "elt battery", "emergency light power unit", "circuit board", "avionics box", "fluorescent tube", "mercury switch", "relay"],
    safety_reminder: "Tape terminals to prevent short circuit and thermal runaway; electrolyte is highly corrosive.",
    examples: "Main aircraft Ni-Cad batteries, 24V lead-acid units, ELT batteries, avionics LRUs"
  },
  {
    id: "scrap_metal",
    name: "Scrap Metal & Clean Hardware",
    bin_colour: "Green",
    badge_class: "chip-green",
    swatch_class: "swatch-green",
    keywords: ["lockwire", "safety wire", "rivet", "rivets", "bolt", "nut", "screw", "cotter pin", "bracket", "aluminum scrap", "titanium scrap", "swarf", "metal shavings", "dry cardboard", "clean packaging"],
    safety_reminder: "Verify zero chemical or hydrocarbon contamination before placing in metal recycling.",
    examples: "Clipped MS20995 safety lockwire, sheared solid rivets, uncontaminated sheet aluminum"
  }
];

const AMBIGUOUS_WORDS = [
  "unknown", "unlabeled", "unmarked", "mystery", "not sure", "strange",
  "cloudy", "sludge", "residue", "weird", "unidentified", "leaking fluid",
  "mixture", "puddle", "smelly", "suspicious", "found on floor", "unmarked cup"
];

// Initial mock log data for demo and audit verification
const DEFAULT_LOGS = [
  {
    id: "log-1",
    timestamp: "10:15:22",
    description: "Kimwipes soaked in MEK used during leading edge flap track cleaning",
    photoUrl: "",
    category: "Contaminated Rags & Absorbents",
    bin_colour: "Yellow",
    confidence: 0.94,
    safety_reminder: "Dispose in self-closing, foot-operated fire-safe cans to prevent spontaneous combustion.",
    status: "Sorted"
  },
  {
    id: "log-2",
    timestamp: "10:48:09",
    description: "Drained hydraulic fluid from Boeing 737 elevator PCU",
    photoUrl: "",
    category: "Aviation Hydraulic Fluids (Skydrol)",
    bin_colour: "Purple",
    confidence: 0.96,
    safety_reminder: "Severe eye and skin irritant; wear butyl rubber gloves and full face shield.",
    status: "Sorted"
  },
  {
    id: "log-3",
    timestamp: "11:20:45",
    description: "Unknown cloudy amber liquid found in unlabeled plastic cup near test bench",
    photoUrl: "",
    category: "Refer to supervisor",
    bin_colour: "Quarantine / Yellow-Black Stripe",
    confidence: 0.20,
    safety_reminder: "Uncertain waste identification. Do not dispose in regular bins; isolate in HazMat Quarantine and alert Shift Supervisor or EHS.",
    status: "Refer to supervisor"
  }
];

// State
let selectedImageFile = null;
let currentImageDataUrl = "";
let lastClassificationResult = null;
let hangarLogs = [];

// DOM Elements
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const cameraInput = document.getElementById("cameraInput");
const uploadPlaceholder = document.getElementById("uploadPlaceholder");
const previewContainer = document.getElementById("previewContainer");
const imagePreview = document.getElementById("imagePreview");
const previewFilename = document.getElementById("previewFilename");
const removePhotoBtn = document.getElementById("removePhotoBtn");
const wasteDescription = document.getElementById("wasteDescription");
const classifyForm = document.getElementById("classifyForm");
const classifyBtn = document.getElementById("classifyBtn");
const resetBtn = document.getElementById("resetBtn");
const presetChips = document.querySelectorAll(".preset-chip");

// Result Card DOM
const resultEmptyState = document.getElementById("resultEmptyState");
const resultContent = document.getElementById("resultContent");
const resultTimestamp = document.getElementById("resultTimestamp");
const resultBanner = document.getElementById("resultBanner");
const bannerIcon = document.getElementById("bannerIcon");
const bannerTitle = document.getElementById("bannerTitle");
const bannerSubtitle = document.getElementById("bannerSubtitle");
const resultCategory = document.getElementById("resultCategory");
const binColourIndicator = document.getElementById("binColourIndicator");
const resultBinColour = document.getElementById("resultBinColour");
const confidencePercentage = document.getElementById("confidencePercentage");
const confidenceBar = document.getElementById("confidenceBar");
const resultSafetyReminder = document.getElementById("resultSafetyReminder");
const supervisorActionBox = document.getElementById("supervisorActionBox");
const jsonCodeView = document.getElementById("jsonCodeView");
const copyJsonBtn = document.getElementById("copyJsonBtn");
const logItemBtn = document.getElementById("logItemBtn");

// Log Table DOM
const logTableBody = document.getElementById("logTableBody");
const logCountBadge = document.getElementById("logCountBadge");
const filterStatus = document.getElementById("filterStatus");
const exportCsvBtn = document.getElementById("exportCsvBtn");
const clearLogBtn = document.getElementById("clearLogBtn");
const emptyTableMessage = document.getElementById("emptyTableMessage");

// Modals DOM
const streamsModal = document.getElementById("streamsModal");
const streamsGuideBtn = document.getElementById("streamsGuideBtn");
const closeStreamsModalBtn = document.getElementById("closeStreamsModalBtn");
const streamsRefContainer = document.getElementById("streamsRefContainer");

const settingsModal = document.getElementById("settingsModal");
const settingsBtn = document.getElementById("settingsBtn");
const closeSettingsModalBtn = document.getElementById("closeSettingsModalBtn");
const closeSettingsBtn = document.getElementById("closeSettingsBtn");
const saveSettingsBtn = document.getElementById("saveSettingsBtn");
const apiKeyInput = document.getElementById("apiKeyInput");
const engineStatusText = document.getElementById("engineStatusText");

// Mobile QR Code Modal DOM
const mobileModal = document.getElementById("mobileModal");
const mobileShareBtn = document.getElementById("mobileShareBtn");
const closeMobileModalBtn = document.getElementById("closeMobileModalBtn");
const qrCodeImage = document.getElementById("qrCodeImage");
const qrLoading = document.getElementById("qrLoading");
const mobileUrlDisplay = document.getElementById("mobileUrlDisplay");
const copyMobileUrlBtn = document.getElementById("copyMobileUrlBtn");

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  loadLogs();
  loadSettings();
  renderStreamsGuide();
  setupEventListeners();
  renderLogTable();
});

// Event Listeners
function setupEventListeners() {
  // File Upload Drag & Drop
  ["dragenter", "dragover"].forEach(name => {
    dropZone.addEventListener(name, (e) => {
      e.preventDefault();
      dropZone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach(name => {
    dropZone.addEventListener(name, (e) => {
      e.preventDefault();
      dropZone.classList.remove("dragover");
    });
  });

  dropZone.addEventListener("drop", (e) => {
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  });

  if (cameraInput) {
    cameraInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files[0]) {
        handleFileSelect(e.target.files[0]);
      }
    });
  }

  removePhotoBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    clearPhoto();
  });

  // Preset quick fill
  presetChips.forEach(chip => {
    chip.addEventListener("click", () => {
      wasteDescription.value = chip.dataset.text;
      wasteDescription.focus();
    });
  });

  // Reset Button
  resetBtn.addEventListener("click", () => {
    clearPhoto();
    wasteDescription.value = "";
  });

  // Form Submit / Classify
  classifyForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    await handleClassification();
  });

  // Copy JSON button
  copyJsonBtn.addEventListener("click", () => {
    if (lastClassificationResult) {
      navigator.clipboard.writeText(JSON.stringify(lastClassificationResult, null, 2)).then(() => {
        const origText = copyJsonBtn.innerHTML;
        copyJsonBtn.innerHTML = `✓ Copied!`;
        setTimeout(() => copyJsonBtn.innerHTML = origText, 1800);
      });
    }
  });

  // Log Item to Table
  logItemBtn.addEventListener("click", () => {
    if (lastClassificationResult) {
      addLogEntry(lastClassificationResult);
      showToast("Logged to Hangar Table");
    }
  });

  // Filter Table
  filterStatus.addEventListener("change", renderLogTable);

  // Export CSV
  exportCsvBtn.addEventListener("click", exportLogsToCSV);

  // Clear Log
  clearLogBtn.addEventListener("click", () => {
    if (confirm("Are you sure you want to clear all log entries from this station?")) {
      hangarLogs = [];
      saveLogs();
      renderLogTable();
    }
  });

  // Modals
  streamsGuideBtn.addEventListener("click", () => streamsModal.classList.remove("hidden"));
  closeStreamsModalBtn.addEventListener("click", () => streamsModal.classList.add("hidden"));

  // Mobile Share & QR Modal
  if (mobileShareBtn) {
    mobileShareBtn.addEventListener("click", openMobileModal);
  }
  if (closeMobileModalBtn) {
    closeMobileModalBtn.addEventListener("click", () => mobileModal.classList.add("hidden"));
  }
  if (copyMobileUrlBtn) {
    copyMobileUrlBtn.addEventListener("click", () => {
      const url = mobileUrlDisplay.textContent;
      navigator.clipboard.writeText(url).then(() => {
        const orig = copyMobileUrlBtn.textContent;
        copyMobileUrlBtn.textContent = "Copied!";
        setTimeout(() => copyMobileUrlBtn.textContent = orig, 1800);
        showToast("Mobile link copied to clipboard!");
      });
    });
  }

  settingsBtn.addEventListener("click", () => {
    const savedKey = localStorage.getItem("hazwaste_gemini_api_key") || "";
    apiKeyInput.value = savedKey;
    updateEngineStatusDisplay(savedKey);
    settingsModal.classList.remove("hidden");
  });

  closeSettingsModalBtn.addEventListener("click", () => settingsModal.classList.add("hidden"));
  closeSettingsBtn.addEventListener("click", () => settingsModal.classList.add("hidden"));

  saveSettingsBtn.addEventListener("click", () => {
    const key = apiKeyInput.value.trim();
    localStorage.setItem("hazwaste_gemini_api_key", key);
    updateEngineStatusDisplay(key);
    settingsModal.classList.add("hidden");
    showToast("Settings saved successfully");
  });

  // Click outside modal to close
  window.addEventListener("click", (e) => {
    if (e.target === streamsModal) streamsModal.classList.add("hidden");
    if (e.target === settingsModal) settingsModal.classList.add("hidden");
    if (e.target === mobileModal) mobileModal.classList.add("hidden");
  });
}

// Open Mobile QR Code Modal
async function openMobileModal() {
  mobileModal.classList.remove("hidden");
  qrLoading.classList.remove("hidden");
  qrCodeImage.classList.add("hidden");

  let mobileUrl = window.location.href;

  // Try to query server's LAN IP if running on a local desktop/laptop
  try {
    const resp = await fetch("/api/network-info");
    if (resp.ok) {
      const info = await resp.json();
      if (info.mobile_url) {
        mobileUrl = info.mobile_url;
      }
    }
  } catch (err) {
    console.log("Using current page URL for mobile QR code");
  }

  mobileUrlDisplay.textContent = mobileUrl;
  const qrApiUrl = `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(mobileUrl)}&margin=10`;
  
  qrCodeImage.onload = () => {
    qrLoading.classList.add("hidden");
    qrCodeImage.classList.remove("hidden");
  };
  qrCodeImage.onerror = () => {
    qrLoading.textContent = "Scan URL or click copy link below";
  };
  qrCodeImage.src = qrApiUrl;
}

// File handling
function handleFileSelect(file) {
  if (!file.type.startsWith("image/")) {
    alert("Please select a valid image file (JPG, PNG, WebP).");
    return;
  }
  selectedImageFile = file;
  previewFilename.textContent = file.name;

  const reader = new FileReader();
  reader.onload = (e) => {
    currentImageDataUrl = e.target.result;
    imagePreview.src = currentImageDataUrl;
    uploadPlaceholder.classList.add("hidden");
    previewContainer.classList.remove("hidden");
  };
  reader.readAsDataURL(file);
}

function clearPhoto() {
  selectedImageFile = null;
  currentImageDataUrl = "";
  fileInput.value = "";
  imagePreview.src = "";
  previewContainer.classList.add("hidden");
  uploadPlaceholder.classList.remove("hidden");
}

// Classification Trigger
async function handleClassification() {
  const desc = wasteDescription.value.trim();
  if (!desc && !selectedImageFile) {
    alert("Please provide either a waste description or upload a photo of the item.");
    return;
  }

  // Set Loading UI
  setLoading(true);

  try {
    let result = null;
    const apiKey = localStorage.getItem("hazwaste_gemini_api_key") || "";

    // First attempt to call the backend API if available
    try {
      const formData = new FormData();
      if (desc) formData.append("description", desc);
      if (selectedImageFile) formData.append("photo", selectedImageFile);
      if (apiKey) formData.append("apiKey", apiKey);

      const resp = await fetch("/api/classify", {
        method: "POST",
        body: formData
      });

      if (resp.ok) {
        result = await resp.json();
      }
    } catch (apiErr) {
      console.warn("Backend API not reachable; using client-side aviation engine fallback:", apiErr);
    }

    // Client-side fallback if server didn't answer (e.g. running statically)
    if (!result) {
      result = clientSideClassify(desc, selectedImageFile ? selectedImageFile.name : "");
    }

    // Strictly enforce the rule: If confidence is below 0.7, return 'Refer to supervisor' instead of guessing
    if (result.confidence < 0.70 || result.category === "Refer to supervisor") {
      result.category = "Refer to supervisor";
      result.bin_colour = "Quarantine / Yellow-Black Stripe";
      if (!result.safety_reminder) {
        result.safety_reminder = "Uncertain waste identification. Do not dispose in regular bins; isolate in HazMat Quarantine and alert Shift Supervisor or EHS.";
      }
    }

    // Render result
    lastClassificationResult = {
      ...result,
      sourceDescription: desc || "(Photo submission)",
      photoDataUrl: currentImageDataUrl || ""
    };

    renderResultCard(lastClassificationResult);

  } catch (err) {
    console.error("Classification error:", err);
    alert("Failed to classify item. Please check the logs or supervisor.");
  } finally {
    setLoading(false);
  }
}

// Client-Side Heuristic Aviation Expert Engine
function clientSideClassify(description, filename) {
  const combined = `${description} ${filename}`.toLowerCase();
  
  // Ambiguity detection
  const ambiguityCount = AMBIGUOUS_WORDS.filter(w => combined.includes(w)).length;
  const isSolidWipe = ["rag", "rags", "wipe", "wipes", "kimwipe", "kimwipes", "towel", "cloth", "pad", "glove", "ppe"].some(w => combined.includes(w));

  const scores = HANGAR_STREAMS.map(stream => {
    let score = 0;
    let matches = [];
    stream.keywords.forEach(kw => {
      const reg = new RegExp(`\\b${kw}\\b`, 'i');
      if (reg.test(combined)) {
        score += 3;
        matches.push(kw);
      } else if (combined.includes(kw)) {
        score += 1;
        matches.push(kw);
      }
    });

    if (isSolidWipe && stream.id === "contaminated_rags") {
      score += 6;
    }

    return { stream, score, matches };
  });

  scores.sort((a, b) => b.score - a.score);
  const best = scores[0];
  const runnerUp = scores[1];

  let confidence = 0.0;
  if (best.score === 0) {
    confidence = 0.20;
  } else {
    const numMatches = best.matches.length;
    if (numMatches >= 3) confidence = 0.96;
    else if (numMatches === 2) confidence = 0.91;
    else {
      const highSpec = ["skydrol", "mek", "pro-seal", "proseal", "ni-cad", "mobil jet", "lockwire", "safety wire", "lps 3"];
      if (best.matches.some(m => highSpec.includes(m))) {
        confidence = 0.89;
      } else {
        confidence = 0.74;
      }
    }

    if (isSolidWipe && best.stream.id === "contaminated_rags") {
      confidence = Math.max(confidence, 0.94);
    } else if (runnerUp && runnerUp.score > 0) {
      if ((runnerUp.score / best.score) >= 0.8) {
        confidence -= 0.18;
      }
    }

    if (ambiguityCount > 0) {
      confidence -= (0.30 * ambiguityCount);
    }
  }

  confidence = Math.round(Math.max(0.05, Math.min(0.99, confidence)) * 100) / 100;

  // Strict Rule Check (< 0.70)
  if (confidence < 0.70) {
    return {
      category: "Refer to supervisor",
      bin_colour: "Quarantine / Yellow-Black Stripe",
      confidence: confidence,
      safety_reminder: "Uncertain waste identification. Do not dispose in regular bins; isolate in HazMat Quarantine and alert Shift Supervisor or EHS."
    };
  }

  return {
    category: best.stream.name,
    bin_colour: best.stream.bin_colour,
    confidence: confidence,
    safety_reminder: best.stream.safety_reminder
  };
}

// Render Result Card
function renderResultCard(data) {
  resultEmptyState.classList.add("hidden");
  resultContent.classList.remove("hidden");

  const now = new Date();
  resultTimestamp.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

  const confVal = Math.round(data.confidence * 100);
  confidencePercentage.textContent = `${confVal}%`;
  confidenceBar.style.width = `${confVal}%`;

  // Color bar styling based on confidence
  confidenceBar.className = "progress-bar-fill";
  if (data.confidence >= 0.85) {
    confidenceBar.classList.add("fill-green");
  } else if (data.confidence >= 0.70) {
    confidenceBar.classList.add("fill-amber");
  } else {
    confidenceBar.classList.add("fill-red");
  }

  // Safety Reminder Text
  resultSafetyReminder.textContent = data.safety_reminder || "Follow standard hangar EHS safety protocol.";

  // Rule Check: Confidence < 0.70 OR Category is 'Refer to supervisor'
  if (data.confidence < 0.70 || data.category === "Refer to supervisor") {
    // Hazard Banner
    resultBanner.className = "result-banner banner-hazard";
    bannerIcon.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`;
    bannerTitle.textContent = "REFER TO SUPERVISOR";
    bannerSubtitle.textContent = `Confidence (${confVal}%) is below 0.70 safety threshold — Do not guess!`;

    resultCategory.textContent = "Refer to supervisor";
    resultCategory.className = "detail-value text-referral";

    resultBinColour.textContent = "Quarantine / Yellow-Black Stripe";
    binColourIndicator.className = "bin-swatch swatch-quarantine";

    supervisorActionBox.classList.remove("hidden");
    logItemBtn.className = "btn btn-danger btn-block";
    logItemBtn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg> Log Quarantine Hold`;

  } else {
    // Success Banner
    resultBanner.className = "result-banner banner-success";
    bannerIcon.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`;
    bannerTitle.textContent = "STREAM MATCH CONFIRMED";
    bannerSubtitle.textContent = `High confidence (${confVal}%) classification verified for hangar`;

    resultCategory.textContent = data.category;
    resultCategory.className = "detail-value text-category";

    resultBinColour.textContent = data.bin_colour;
    binColourIndicator.className = `bin-swatch swatch-${data.bin_colour.toLowerCase()}`;

    supervisorActionBox.classList.add("hidden");
    logItemBtn.className = "btn btn-success btn-block";
    logItemBtn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> Log Disposal to Hangar Table`;
  }

  // Haptic feedback for mobile phones
  if ("vibrate" in navigator) {
    try {
      if (data.confidence < 0.70 || data.category === "Refer to supervisor") {
        navigator.vibrate([100, 80, 100]); // Dual warning pulse
      } else {
        navigator.vibrate(60); // Subtle confirmation pulse
      }
    } catch (e) {
      // Ignored if vibration not permitted
    }
  }

  // Display JSON Contract strictly matching user specification:
  // category, bin_colour, confidence (0-1), and a one-line safety reminder
  const cleanJsonContract = {
    category: data.category,
    bin_colour: data.bin_colour,
    confidence: data.confidence,
    safety_reminder: data.safety_reminder
  };
  jsonCodeView.textContent = JSON.stringify(cleanJsonContract, null, 2);
}

// Log Management
function loadLogs() {
  const saved = localStorage.getItem("hazwaste_sorter_logs");
  if (saved) {
    try {
      hangarLogs = JSON.parse(saved);
    } catch (e) {
      hangarLogs = [...DEFAULT_LOGS];
    }
  } else {
    hangarLogs = [...DEFAULT_LOGS];
    saveLogs();
  }
}

function saveLogs() {
  localStorage.setItem("hazwaste_sorter_logs", JSON.stringify(hangarLogs));
}

function addLogEntry(data) {
  const now = new Date();
  const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

  const newEntry = {
    id: `log-${Date.now()}`,
    timestamp: timeStr,
    description: data.sourceDescription || "Aircraft waste item",
    photoUrl: data.photoDataUrl || "",
    category: data.category,
    bin_colour: data.bin_colour,
    confidence: data.confidence,
    safety_reminder: data.safety_reminder,
    status: (data.confidence < 0.70 || data.category === "Refer to supervisor") ? "Refer to supervisor" : "Sorted"
  };

  hangarLogs.unshift(newEntry);
  saveLogs();
  renderLogTable();
}

function deleteLogEntry(id) {
  hangarLogs = hangarLogs.filter(item => item.id !== id);
  saveLogs();
  renderLogTable();
}

function renderLogTable() {
  const filter = filterStatus.value;
  let items = hangarLogs;

  if (filter === "sorted") {
    items = hangarLogs.filter(i => i.confidence >= 0.70 && i.category !== "Refer to supervisor");
  } else if (filter === "supervisor") {
    items = hangarLogs.filter(i => i.confidence < 0.70 || i.category === "Refer to supervisor");
  }

  logCountBadge.textContent = `${items.length} Entries`;

  if (items.length === 0) {
    logTableBody.innerHTML = "";
    emptyTableMessage.classList.remove("hidden");
    return;
  }

  emptyTableMessage.classList.add("hidden");
  logTableBody.innerHTML = items.map(item => {
    const isSupervisor = item.confidence < 0.70 || item.category === "Refer to supervisor";
    const confVal = Math.round(item.confidence * 100);
    const confClass = item.confidence >= 0.70 ? "conf-high" : "conf-low";

    const binClass = isSupervisor 
      ? "chip-black" 
      : `chip-${item.bin_colour.toLowerCase()}`;

    const statusBadge = isSupervisor 
      ? `<span class="status-badge status-quarantine">HOLD / SUPERVISOR</span>` 
      : `<span class="status-badge status-disposed">DISPOSED</span>`;

    const mediaThumb = item.photoUrl 
      ? `<img src="${item.photoUrl}" class="table-thumb" alt="Item preview">` 
      : `<div class="table-thumb-placeholder"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg></div>`;

    return `
      <tr>
        <td class="table-time">${escapeHtml(item.timestamp)}</td>
        <td>${mediaThumb}</td>
        <td><strong>${escapeHtml(item.description)}</strong></td>
        <td><span style="font-weight: 700; ${isSupervisor ? 'color: #facc15;' : ''}">${escapeHtml(item.category)}</span></td>
        <td>
          <span class="bin-chip ${binClass}">
            <span class="dot"></span>
            ${escapeHtml(item.bin_colour)}
          </span>
        </td>
        <td>
          <span class="table-conf-pill ${confClass}">${confVal}%</span>
        </td>
        <td style="font-size: 0.8rem; color: var(--text-muted);">${escapeHtml(item.safety_reminder)}</td>
        <td>
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            ${statusBadge}
            <button class="btn btn-ghost btn-xs" style="color: #f87171;" onclick="deleteLogEntry('${item.id}')" title="Delete entry">&times;</button>
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

// Export CSV
function exportLogsToCSV() {
  if (hangarLogs.length === 0) {
    alert("No log entries to export.");
    return;
  }

  const headers = ["Time", "Waste Description", "Category", "Bin Colour", "Confidence", "Safety Reminder", "Status"];
  const rows = hangarLogs.map(item => [
    `"${item.timestamp}"`,
    `"${(item.description || '').replace(/"/g, '""')}"`,
    `"${(item.category || '').replace(/"/g, '""')}"`,
    `"${(item.bin_colour || '').replace(/"/g, '""')}"`,
    item.confidence,
    `"${(item.safety_reminder || '').replace(/"/g, '""')}"`,
    `"${item.status}"`
  ]);

  const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `hazwaste_hangar4_log_${new Date().toISOString().slice(0,10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Streams Reference Guide Modal Rendering
function renderStreamsGuide() {
  streamsRefContainer.innerHTML = HANGAR_STREAMS.map(stream => `
    <div class="stream-ref-card">
      <div class="stream-ref-header">
        <span class="stream-ref-name">${stream.name}</span>
        <span class="bin-chip ${stream.badge_class}">
          <span class="dot"></span>
          ${stream.bin_colour} Bin
        </span>
      </div>
      <div class="stream-ref-examples">
        <strong>Common Hangar Items:</strong> ${stream.examples}
      </div>
      <div class="stream-ref-safety">
        <strong>Safety:</strong> ${stream.safety_reminder}
      </div>
    </div>
  `).join("");
}

// Settings
function loadSettings() {
  const savedKey = localStorage.getItem("hazwaste_gemini_api_key") || "";
  updateEngineStatusDisplay(savedKey);
}

function updateEngineStatusDisplay(key) {
  if (key) {
    engineStatusText.textContent = "Gemini Multimodal Vision API (Connected)";
    engineStatusText.style.color = "#34d399";
  } else {
    engineStatusText.textContent = "Aviation Expert Heuristics Engine (Offline Active)";
    engineStatusText.style.color = "#38bdf8";
  }
}

// Helpers
function setLoading(isLoading) {
  const btnText = classifyBtn.querySelector(".btn-text");
  const spinner = classifyBtn.querySelector(".spinner");
  if (isLoading) {
    classifyBtn.disabled = true;
    btnText.classList.add("hidden");
    spinner.classList.remove("hidden");
  } else {
    classifyBtn.disabled = false;
    btnText.classList.remove("hidden");
    spinner.classList.add("hidden");
  }
}

function showToast(msg) {
  const toast = document.createElement("div");
  toast.textContent = msg;
  toast.style.position = "fixed";
  toast.style.bottom = "20px";
  toast.style.right = "20px";
  toast.style.background = "#0ea5e9";
  toast.style.color = "#fff";
  toast.style.padding = "10px 18px";
  toast.style.borderRadius = "8px";
  toast.style.fontSize = "0.85rem";
  toast.style.fontWeight = "600";
  toast.style.boxShadow = "0 4px 15px rgba(0,0,0,0.5)";
  toast.style.zIndex = "9999";
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.transition = "opacity 0.4s";
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 400);
  }, 2200);
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
