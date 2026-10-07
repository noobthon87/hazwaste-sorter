# HazWaste Sorter - Verification & Validation Test Plan (20 Test Cases)

A standardized acceptance testing protocol designed for the **HazWaste Sorter** competition prototype in a Singapore aircraft maintenance training hangar.

---

## 1. Test Case Matrix (20 Scenarios)

| Test No. | Category | What to Photograph | Expected Result | Actual Result | Pass / Fail |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **01** | Clear Item (Stream 1) | MEK / solvent-soaked white lint-free wipe cloth on stainless tray | Advised: **Oily / contaminated rags and absorbents** &bull; **Red Bin** &bull; Conf &ge; 0.70 &bull; Status: `ADVISED` | | [ ] PASS<br>[ ] FAIL |
| **02** | Clear Item (Stream 1) | Red shop rag heavily stained with dark hydraulic fluid (Skydrol) | Advised: **Oily / contaminated rags and absorbents** &bull; **Red Bin** &bull; Conf &ge; 0.70 &bull; Status: `ADVISED` | | [ ] PASS<br>[ ] FAIL |
| **03** | Clear Item (Stream 2) | Expired aircraft emergency locator transmitter (ELT) lithium battery pack | Advised: **Used batteries** &bull; **Yellow Bin** &bull; Conf &ge; 0.70 &bull; Status: `ADVISED` | | [ ] PASS<br>[ ] FAIL |
| **04** | Clear Item (Stream 2) | Depleted avionics NiCad backup battery cells with terminal caps | Advised: **Used batteries** &bull; **Yellow Bin** &bull; Conf &ge; 0.70 &bull; Status: `ADVISED` | | [ ] PASS<br>[ ] FAIL |
| **05** | Clear Item (Stream 3) | Carbon-fiber reinforced polymer (CFRP) prepreg edge trimmings | Advised: **Composite dust and offcuts** &bull; **Yellow Bin** &bull; Conf &ge; 0.70 &bull; Status: `ADVISED` | | [ ] PASS<br>[ ] FAIL |
| **06** | Clear Item (Stream 3) | Clear vacuum-bag filled with fiberglass composite sanding powder | Advised: **Composite dust and offcuts** &bull; **Yellow Bin** &bull; Conf &ge; 0.70 &bull; Status: `ADVISED` | | [ ] PASS<br>[ ] FAIL |
| **07** | Clear Item (Stream 4) | Empty PRC / Pro-Seal polysulfide fuel-tank sealant mixing cartridge | Advised: **Empty sealant / adhesive / paint containers** &bull; **Yellow Bin** &bull; Conf &ge; 0.70 &bull; Status: `ADVISED` | | [ ] PASS<br>[ ] FAIL |
| **08** | Clear Item (Stream 4) | Empty polyurethane aircraft exterior paint tin with warning label | Advised: **Empty sealant / adhesive / paint containers** &bull; **Yellow Bin** &bull; Conf &ge; 0.70 &bull; Status: `ADVISED` | | [ ] PASS<br>[ ] FAIL |
| **09** | Clear Item (Stream 5) | Coiled aluminum / titanium drill swarf and shavings from rivet hole prep | Advised: **Metal swarf and scrap** &bull; **Blue Bin** &bull; Conf &ge; 0.70 &bull; Status: `ADVISED` | | [ ] PASS<br>[ ] FAIL |
| **10** | Clear Item (Stream 5) | Clipped stainless steel safety lockwire strands in collection tin | Advised: **Metal swarf and scrap** &bull; **Blue Bin** &bull; Conf &ge; 0.70 &bull; Status: `ADVISED` | | [ ] PASS<br>[ ] FAIL |
| **11** | Clear Item (Stream 6) | Uncontaminated corrugated cardboard avionics shipping box | Advised: **General non-hazardous waste** &bull; **Black Bin** &bull; Conf &ge; 0.70 &bull; Status: `ADVISED` | | [ ] PASS<br>[ ] FAIL |
| **12** | Clear Item (Stream 6) | Clean food wrapper and disposable paper coffee cup from break room | Advised: **General non-hazardous waste** &bull; **Black Bin** &bull; Conf &ge; 0.70 &bull; Status: `ADVISED` | | [ ] PASS<br>[ ] FAIL |
| **13** | Ambiguous Item | White cloth soaked in an unidentifiable clear, odorless fluid | Low confidence (&lt; 0.70) &bull; Red meter &bull; Status: `REFER TO SUPERVISOR` &bull; Routed to Review queue | | [ ] PASS<br>[ ] FAIL |
| **14** | Ambiguous Item | Plastic bag stuffed with mixed waste: greasy rag, lockwire, drink bottle | Mixed waste detected &bull; Low confidence (&lt; 0.70) &bull; Status: `REFER TO SUPERVISOR` &bull; Routed to Review queue | | [ ] PASS<br>[ ] FAIL |
| **15** | Ambiguous Item | Melted, crushed chemical bottle with torn and illegible hazard label | Unidentifiable residue &bull; Conf &lt; 0.70 &bull; Status: `REFER TO SUPERVISOR` &bull; Routed to Review queue | | [ ] PASS<br>[ ] FAIL |
| **16** | Ambiguous Item | Waste item photographed in heavy shadow under wing root in dim hangar | Dim lighting warning &bull; Conf &lt; 0.70 &bull; Status: `REFER TO SUPERVISOR` &bull; Routed to Review queue | | [ ] PASS<br>[ ] FAIL |
| **17** | Matches No Stream | Discharged aircraft emergency escape slide squib / pyrotechnic cartridge | Out-of-whitelist item &bull; Status: `REFER TO SUPERVISOR` &bull; Mandatory explosive handling protocol | | [ ] PASS<br>[ ] FAIL |
| **18** | Matches No Stream | Calibrated workshop torque wrench or turbine blade brought to bin | Rotatable tool/part (not scrap) &bull; Status: `REFER TO SUPERVISOR` &bull; Hold in quarantine | | [ ] PASS<br>[ ] FAIL |
| **19** | Privacy Violation | Dirty wipe held by trainee with employee name badge and photo ID visible | Privacy triggered &bull; Banner: *"Please retake photo showing only waste"* &bull; **Photo not saved** | | [ ] PASS<br>[ ] FAIL |
| **20** | Privacy Violation | Sealant tube held up with trainee's full face clearly visible in frame | Privacy triggered &bull; Banner: *"Please retake photo showing only waste"* &bull; **Photo not saved** | | [ ] PASS<br>[ ] FAIL |

---

## 2. Quantitative Metric Calculations

### Metric A: AI Classification Accuracy (Clear Items)
Measures how effectively the Gemini vision model assigns the correct hangar bin when presented with unambiguous, single-item waste materials.

$$\text{Clear Item Accuracy (\%)} = \left( \frac{\text{Number of Clear Items Correctly Advised}}{\text{Total Clear Items Evaluated (12)}} \right) \times 100$$

* **Target Benchmark**: $\ge 90\%$ (at least 11 of 12 clear items correctly categorized into their designated hangar bin).

---

### Metric B: Supervisor-Referral Rate
Measures the safety mechanism that prevents guessing on ambiguous, mixed, dark, or out-of-scope items.

$$\text{Supervisor-Referral Rate (\%)} = \left( \frac{\text{Total Items Set to 'REFER TO SUPERVISOR'}}{\text{Total Saved Waste Items Evaluated (18)}} \right) \times 100$$

*(Note: The denominator is **18** because the 2 privacy-violating photos are discarded and never saved into SQLite).*

* **Expected Benchmark for this Test Set**:  
  - 4 ambiguous items + 2 out-of-stream items = **6 items** expected to refer to the supervisor.  
  - Expected Referral Rate: $\frac{6}{18} \times 100 = \mathbf{33.3\%}$.

---

### Metric C: System Safety Compliance (Overall Decision Accuracy)
In an aviation safety system, correctly **refraining from guessing** on an ambiguous item is just as important as correctly classifying a clean item.

$$\text{System Safety Compliance (\%)} = \left( \frac{\text{Correct Advisories (Clear)} + \text{Correct Supervisor Referrals} + \text{Correct Privacy Rejections}}{\text{Total Test Runs (20)}} \right) \times 100$$

* **Target Benchmark**: $\ge 95\%$ (at least 19 of 20 total actions conform strictly to safety protocols).
