# "NDAA-compliant" manufacturing for StackF765

Dated 2026-11-19. Web research plus a read of the three BOMs in `fab/`. No quotes were requested, no files were
uploaded and no accounts were created. Nothing here is legal advice; where a point is a legal judgement it says so.

How to read the labels:

- **[PRIMARY]** = read from the statute, regulation or agency notice itself in this session.
- **[SECONDARY]** = law-firm, trade-press or distributor summary.
- **[VENDOR]** = the vendor's own claim on its own website.
- **[MEMORY]** = general knowledge, not re-checked against a source in this session.
- **UNCONFIRMED** = looked for and not found.

---

## 1. What "NDAA compliant" means for a flight controller

### 1.1 Short answer

"NDAA compliant" is not a certificate. It is shorthand for "this drone, or this part, would not trip the Defense
Department's ban in Section 848 of the FY2020 NDAA as amended by Section 817 of the FY2023 NDAA". That ban names four
countries (China, Russia, Iran, North Korea) and a short list of parts, and **the flight controller is on the list**.
The test in the statute is where the flight controller is *manufactured* and whether the maker is *domiciled* in one of
those countries. The statute says nothing about bare PCBs, integrated circuits or passive components, and nobody in
government certifies a bare-board or assembly vendor as "NDAA compliant". A vendor that advertises it is making a
self-declaration.

Three other rules now sit beside Section 848 and are stricter in different ways: the American Security Drone Act
(all federal agencies, keyed to listed companies), the FCC Covered List action of December 2025 (all *foreign-produced*
flight controllers, not only Chinese ones, with an exemption for US-made "domestic end products"), and 10 U.S.C. 4873
(a DoD ban on covered-country printed circuit boards, effective 2027, not yet implemented by regulation).

### 1.2 The rules, one by one

| Rule | Who it binds | Countries / entities | What it looks at | Status |
|---|---|---|---|---|
| FY2020 NDAA §848 as amended by FY2023 NDAA §817 (note under 10 U.S.C. 4871) | Department of Defense; from 2024-10-01 also DoD contractors that operate covered-company equipment | China, Russia, Iran, North Korea | A UAS made in a covered country or by an entity domiciled there; **or** one that uses "flight controllers, radios, data transmission devices, cameras, or gimbals" made in a covered country or by an entity domiciled there; **or** a ground control system or operating software developed there; **or** network connectivity or data storage located there or run by an entity domiciled there | In force. [PRIMARY, read via Cornell LII] |
| American Security Drone Act of 2023 (FY2024 NDAA, Pub. L. 118-31, §§1821–1833; FAR subpart 40.2, clause 52.240-1) | All federal agencies; federal funds (grants, contracts) from 2025-12-22 | Companies on a list kept by the Federal Acquisition Security Council (Consolidated Screening List entities, PRC-domiciled or PRC-controlled entities, their subsidiaries and affiliates) | A UAS "manufactured or assembled by" a listed entity. It is keyed to the *company*, not to parts. The UAS definition includes "the components that control the unmanned aircraft", but the prohibition is not extended part by part | In force; expires 2028-12-22. [PRIMARY, FAR 40.2] |
| FCC Covered List, DA 25-1086 (2025-12-22) with exemptions DA 26-22 (2026-01-07) and DA 26-761 (2026-07-21) | Anyone who needs an FCC equipment authorization to import or sell a device in the US | **Every foreign country** (identified "by place of production, not by entity") | "UAS and UAS critical components produced in a foreign country". Critical components "includes but is not limited to": data transmission devices, communications systems, **flight controllers**, ground control stations and UAS controllers, navigation systems, sensors and cameras, batteries and battery management systems, motors — "and any associated software" | In force. Exempt until 2028-01-01: items on the Blue UAS list, and items that are "domestic end products" under the Buy American rule, 48 CFR 25.101(a). "Produced in a foreign country" is not defined in the notices read. [PRIMARY] |
| 10 U.S.C. 4873 (printed circuit boards) | Department of Defense acquisitions above the micro-purchase threshold | China, Russia, Iran, North Korea | A "partially manufactured or complete bare printed circuit board" or a "fully or partially assembled printed circuit board" from a covered nation, where it performs a mission-critical function in a non-commercial product, or is part of a system the contract marks as national-security sensitive. Commercial and COTS items may be exempted by the Secretary | Statutory effective date 2027-01-01, but it applies only to contracts signed after a final rule. DoD issued only an advance notice of proposed rulemaking on 2026-07-02 (DFARS Case 2022-D011). [PRIMARY for the statute; SECONDARY for the rulemaking status] |
| FCC "logic-bearing hardware" rule (Third Report and Order, effective 2026-10-13) | FCC equipment authorization applicants | Named Covered List entities and their affiliates | Devices containing logic-bearing hardware (anything clocked above 9 kHz) made by a *named* Covered List entity. Resistors, wiring, fasteners and other passive or mechanical parts are outside the definition. The FCC declined "at this time" to extend it beyond named entities | In force. [SECONDARY, Holland & Knight] |

### 1.3 What the Blue UAS programme adds

- The **Blue UAS Cleared List** is a list of whole aircraft. The **Blue UAS Framework** is a parallel list of components
  and software (flight controllers, radios, cameras, gimbals, ground control). Both were run by the Defense Innovation
  Unit and moved to the Defense Contract Management Agency in December 2025. [SECONDARY for the transfer date; the FCC
  notice DA 26-22 itself refers to "DCMA's Blue UAS list", PRIMARY]
- Getting on either list takes two things: an NDAA assessment (Section 848 / 817) and a cybersecurity review. Since
  2025 the NDAA assessment can be bought from a "recognized assessor" approved by DIU; the government then reviews the
  report. [PRIMARY, DIU announcement of 2025-05-16]
- AUVSI's **Green UAS** is a private certification that DIU accepts as input. It is not a government clearance.
- Trade press reports that Blue-listed aircraft "can and do" contain Chinese motors, batteries and ESCs, because those
  are not on the Section 848 list. [SECONDARY]
- The Drone Dominance Program (DoD, 2026–2027) is reported to set tighter sourcing rules for thirteen component areas in
  steps to August 2027, and to treat the flight controller's processor, IMU, sensors and PCB as items of interest.
  I could not open the article (HTTP 403) or find the government framework document, so the actual PCB and chip rules
  in that programme are **UNCONFIRMED**.

### 1.4 The four questions asked

| Question | Section 848 / 817 | FCC Covered List | 10 U.S.C. 4873 |
|---|---|---|---|
| Does it matter where the **bare board is fabricated**? | Not stated. The statute speaks only of a flight controller "manufactured in" a covered country. A board fabricated in China and assembled in the US is a grey area that assessors and buyers decide; a cautious reading avoids it | Not stated. The exemption needs the finished flight controller to be "manufactured in the United States" | **Yes**, explicitly, for covered DoD buys once a rule exists |
| Does it matter where the **board is assembled**? | Yes in practice. Assembly is where a flight controller is "manufactured" | **Yes.** Assembly outside the US makes it "produced in a foreign country" unless Blue-listed or conditionally approved. Assembly in Germany or Taiwan does *not* satisfy the FCC exemption | **Yes** (assembled boards are named) |
| Does it matter where the **ICs and passives are made**? | Not stated in the statute. In practice assessors look at the bill of materials, and a Chinese-brand programmable or signal-processing chip is the kind of line that gets questioned | Indirectly. A "domestic end product" needs more than 65 % of component cost to be US-origin (75 % from 2029), **but that cost test is waived for commercially available off-the-shelf items**. Passives are expressly outside the separate logic-bearing-hardware rule | No |
| Does **company ownership** matter? | **Yes.** "An entity domiciled in a covered foreign country" counts wherever its factory is. For DoD contractors, "covered UAS company" also includes entities under unmitigated foreign ownership, control or influence | Only for the named-entity rules | The test is "from a covered nation" |

### 1.5 What this means for StackF765

1. Have the boards **assembled in the United States** by a US-owned company. That one choice satisfies the plain reading
   of Section 848, keeps the board outside the FCC "produced in a foreign country" category, and is what every
   customer who asks for "NDAA compliant" will check first.
2. Have the **bare boards fabricated in the United States** as well (or at least outside the four countries). No rule
   in force today requires it for a commercial product, but 10 U.S.C. 4873 shows where DoD is going, and a
   Chinese-fabricated bare board is the first thing an assessor would query.
3. Take the **Chinese-brand parts off the BOM**, starting with anything that carries logic or sits in a signal path.
   On this design that is one part above all: the AT7456E OSD chip (section 3).
4. Keep **paperwork**: a BOM listing manufacturer, manufacturer's country, and the country of origin printed on each
   distributor label or packing slip; certificates of conformance from the fab and the assembler stating where the work
   was done; parts bought only from authorised distributors. This file is what an assessor, or a customer, will ask for.
5. **Firmware and ground software** are also on the Section 848 list ("operating software developed in a covered foreign
   country"). ArduPilot is an international open-source project. Whether an open-source autopilot with contributors
   worldwide raises a question is a matter for the assessor; ArduPilot-based controllers are reported to be on the
   Framework list [SECONDARY], so it has not been a bar.
6. What assembly in an **allied country** (Germany, Taiwan, Japan) gets you: it meets Section 848, which names only
   four countries. It does **not** meet the FCC exemption, which requires US manufacture. For an open-hardware board
   with no radio that the owner builds for his own use this may never matter; for a product sold in the US as a UAS
   flight controller it could. Whether this board needs any FCC authorization at all (it has no intentional radiator)
   is a legal question I did not resolve.

### 1.6 Not verified

- The enacted FY2026 NDAA text. Trade press describes more drone provisions (ground vehicles, "clone" companies,
  counter-drone authority); I did not read the statute and cannot say whether it changes the component list.
- The FCC Covered List web page itself (HTTP 403); the entries above come from the FCC public notices.
- Any official definition of "produced in a foreign country".
- The current Blue UAS Framework list (the portal was not opened).

### 1.7 Sources for section 1

- Section 848 as amended (note under 10 U.S.C. 4871): https://www.law.cornell.edu/uscode/text/10/4871
- Section 848 original text (China only): https://wifcon.com/dodauth20/dod20_848.htm
- FAR subpart 40.2 (American Security Drone Act): https://www.acquisition.gov/far/subpart-40.2
- GSA summary of the Act: https://smartpay.gsa.gov/resources/american-security-drone-act/
- FCC DA 25-1086 (2025-12-22): https://docs.fcc.gov/public/attachments/DA-25-1086A1.txt
- FCC DA 26-22 (2026-01-07): https://docs.fcc.gov/public/attachments/DA-26-22A1.pdf
- FCC DA 26-761 (2026-07-21): https://docs.fcc.gov/public/attachments/DA-26-761A1.pdf
- FCC DA 26-758 (2026-07-21, proposal on "military-grade" drones): https://docs.fcc.gov/public/attachments/DA-26-758A1.txt
- FCC fact sheet (existing authorizations unaffected): https://docs.fcc.gov/public/attachments/DOC-416839A1.txt
- Holland & Knight on the October 2026 rules: https://www.hklaw.com/en/insights/publications/2026/09/fcc-moves-to-restrict-foreign-made-drones
- FAR 25.101 (Buy American test): https://www.acquisition.gov/far/25.101
- 10 U.S.C. 4873: https://www.law.cornell.edu/uscode/text/10/4873
- DFARS advance notice on PCBs: https://www.govinfo.gov/content/pkg/FR-2026-07-02/pdf/2026-13375.pdf (found by search, not opened); summaries at https://www.wiley.law/alert-DoD-Considers-Certification-Based-Framework-for-Restricting-Certain-Printed-Circuit-Boards-in-Defense-Systems and https://crowell.com/en/insights/client-alerts/at-long-last-dow-signals-rule-implementing-pcb-prohibition-and-commercial-exemptions
- DIU on the Blue UAS changes: https://www.diu.mil/latest/blue-uas-to-evolve-to-meet-broader-department-of-defense-needs
- DIU on recognized assessors: https://www.diu.mil/latest/diu-seeking-recognized-assessors-to-support-blue-uas-ndaa-compliance
- Trade press on what each label certifies: https://unmanned-aerial.com/blue-uas-green-uas-ndaa-compliant-what-each-list-certifies/
- Trade press on the Drone Dominance supply chain (not opened, 403): https://insideunmannedsystems.com/inside-the-drone-dominance-supply-chain-what-every-u-s-drone-company-must-source-and-by-when/
- PCB industry advocacy column: https://iconnect007.com/article/148809/american-made-advocacy-restore-the-domestic-pcb-industry-to-support-national-drone-initiatives/148806/pcb

---

## 2. Fabrication and assembly houses

Board areas used below: upper and lower 31.5 × 48 mm = 15.1 cm² = 2.34 in² each; service 18 × 32 mm = 5.8 cm² = 0.89 in².

One design detail matters at several fabs: the upper board's vias are 0.3 mm holes in 0.5 mm pads, an annular ring of
0.10 mm (3.9 mil). Several US "standard" services want 4 or 5 mil. Where that is the case it is noted.

None of the vendors below makes any NDAA, Blue UAS or drone-programme statement on the pages read, except where noted
in 2.2. None publishes prices for an assembled order of this kind: every instant-quote tool needs a login, a file
upload, or both, so none was run. Vendor pages were read through a summarising tool; re-check any number on the live
page before ordering.

### 2.1 Main US candidates

| Vendor | Where boards are made | Where assembled | Fit to the three boards | Parts | Certifications claimed | Minimum / lead time | Source |
|---|---|---|---|---|---|---|---|
| **AdvancedPCB** (formerly Advanced Circuits) | Its own six US plants: Aurora CO, Santa Clara CA, Chandler AZ, Anaheim/Orange CA, Maple Grove MN, Placentia CA. States "all of our printed circuit boards are manufactured in USA facilities" and that it is "not a broker". (A search snippet mentioned offshore partners for high-volume non-ITAR work; not found on any page read. Ask for a written domestic-build statement.) | Aurora, CO | Upper: the 5 mil gap is under the 5.5 mil standard for 1 oz copper, and the via pad is only 8 mil over the drill against a +10 to +15 mil rule, so it probably needs the "Advanced" tier; UNCONFIRMED. Lower passes (2 oz at 7/7 mil). Service passes. Assembly: 0201, BGA to 0.4 mm | Full turnkey, partial, or kitted. Locking the BOM to named part numbers / distributors UNCONFIRMED | ITAR, AS9100D, ISO 9001:2015, CMMC Level 2; MIL-PRF-31032 / 55110 at three plants | "No minimum order quantity … can assemble even one board". Boards 5 days standard (multilayer), 1-day available. Assembly 3, 5 or 10 days | https://www.advancedpcb.com/en-us/contact-us/facilities/ ; https://www.advancedpcb.com/en-us/resources/manufacturing-capabilities/ ; https://www.advancedpcb.com/en-us/company/faqs/ |
| **ASC Sunstone** (boards) with **Screaming Circuits** (assembly) | Sunstone's own plants: Mulino, OR and West Chicago, IL. No offshore mentioned. (Its laminate supplier list includes Shengyi, a Chinese laminate maker, among others.) | Screaming Circuits, Canby, OR (inferred from the ship-to address). Parent Milwaukee Electronics also has a plant in Tecate, Mexico; no link to prototype orders found | Upper: via pad is 8 mil over the hole against a 16 mil rule and a reported 5 mil ring minimum, so a custom quote is likely; UNCONFIRMED. Lower: pad is 15.7 mil over the hole, marginal against 16; 2 oz fine. Service passes. Assembly: 0201, IC pitch to 0.35 mm. Reflowed standoffs UNCONFIRMED | Full turnkey, partial, or customer-supplied; BOM by manufacturer part number with approved alternates in their own column | Screaming: ISO 9001:2015, AS9100, ITAR handling, CMMC Level 2 (self-assessed). Sunstone: ITAR, AS9100D, ISO 9001, MIL-PRF-31032 | "The minimum order size is one". Assembly 5 or 10 days, 24 h and 48 h options. Boards 1 day to 3 weeks | https://www.screamingcircuits.com/faq ; https://www.sunstone.com/pcb-manufacturing-capabilities/detailed-capabilities |
| **Sierra Circuits** (protoexpress.com) | Its own plant, Sunnyvale, CA | "Manufactured in the USA, fully assembled"; city of the assembly plant not named on the pages read | Upper **fails the standard "Turnkey PRO" service**: 6 mil annular ring minimum (design has 4) and inner copper 1 oz only. It would need a custom quote; custom limits UNCONFIRMED. Lower and service pass on paper. Assembly: both sides, 0201, 0.4 mm pitch. Arrays not allowed; reflowed standoffs UNCONFIRMED | Turnkey from Mouser, DigiKey, Arrow and others; consignment possible | ITAR, AS9100D, ISO 9001:2015, ISO 13485, MIL-PRF-31032 | Turnkey PRO 2–100 boards in 7, 10 or 15 days | https://www.protoexpress.com/kb/turnkey-pro-pcb-specs/ ; https://www.protoexpress.com/pcb-certificates/ |
| **MacroFab** (Houston, TX) | **Not its own.** "We source bare PCBs from our network of vetted" makers. Country for ordinary orders is not stated anywhere readable. "US-built" bare boards are offered for ITAR builds | "At the optimal factory in our network" across North America; the network includes Mexico and Canada. An "audited, ITAR-registered US facility" is used for ITAR orders | **All three pass the published limits** (3/3 mil, 3 mil annular ring, 2 oz, ENIG, double-sided by default, 0.4 mm LGA, 01005). Reflowed standoffs UNCONFIRMED | Turnkey, typically from Mouser or DigiKey; alternates definable per line; consignment supported | ISO 9001:2015, ITAR registered. No AS9100. Has a drone page naming flight controllers; no NDAA statement | "No contracts, no minimums". About 10 days (search snippet) | https://www.macrofab.com/capabilities ; https://www.macrofab.com/blog/bare-pcb-launch ; https://macrofab.com/industries/drone |
| **Summit Interconnect** (Royal Circuits is now "Summit Hollister") | Hollister, CA. Summit also has a Toronto plant and says work can be split across sites | Summit Denver, Aurora, CO (formerly Advanced Assembly) | No numbers published; UNCONFIRMED. Assembly to 0201 / 0.4 mm pitch | Turnkey and consigned | Hollister: ISO 9001, ITAR. Denver: AS9100D, ISO 9001 | Boards from 24 h; assembly 3, 5 or 10 days. Quote by form only | https://summitinterconnect.com/pcb-prototypes/ ; https://summitinterconnect.com/certifications/ |
| **CircuitHub** | **Brokered.** "Bare PCB's will generally be manufactured in the US for short lead times. For longer lead time's and/or higher quantity the bare boards will be manufactured in China." Writing "US FABRICATION" in the custom-requirements field restricts the job to US fabricators | South Deerfield, MA | Upper sits exactly at the limits (4 mil ring, 12 mil drill); 0.5 oz inner and 2 oz outer are non-default and need manual review. Its cheap "Value Proto" tier excludes through-hole and mechanical parts, which may rule out the standoffs and the USB-C shell tabs | Turnkey; DigiKey, Mouser and others preferred; LCSC "possible" — tell them not to | ISO 9001 only. States it has **no** ITAR registration | From 1 unit; from 3 days | https://docs.circuithub.com/getting-started/where-we-operate ; https://docs.circuithub.com/faq/how-to-make-sure-boards-are-fabricated-in-the-us |
| **OSH Park** (bare boards only) | "Manufactured in the United States" | None | Upper: the 6-layer service is 5/5 mil, 8 mil drill, **4 mil annular ring**; the design's ring is 0.10 mm = 3.94 mil, a hair under. Ask, or expect a design-rule warning. Stack is 1 oz / 0.5 oz, ENIG, 1.6 mm, as designed. **Lower cannot be made**: no 2 oz option on 4 layers. Service fits the 2-layer service | – | None stated | Sets of 3. 6-layer 12–21 calendar days; 2-layer 9–12 | https://docs.oshpark.com/services/ |

Published OSH Park prices, worked out for these boards: upper, 6-layer at $15 per square inch × 2.34 = **$35.15 for
three boards**; service, 2-layer at $5 per square inch × 0.89 = **$4.46 for three**, shipping included.

### 2.2 Other US and Canadian vendors

| Vendor | Where boards are made | Where assembled | Fit to the three boards | Parts | Certifications claimed | Price / lead time | Source |
|---|---|---|---|---|---|---|---|
| **Bay Area Circuits** (Fremont, CA) | In-house, Fremont, CA [VENDOR] | Through "trusted EMS partners"; partner and location UNCONFIRMED | Upper: 0.10 mm via ring fails the Standard tier (5 mil), needs the Advanced tier (3 mil). Lower and service fit Standard (2 oz at 6 mil) | Turnkey marketed | ISO, ITAR logos. AS9100 not mentioned | No published prices (upload needed). Quick-turn "24 hours+" | https://bayareacircuits.com/capabilities/ |
| **Imagineering** (pcbnet.com) | Elk Grove Village, IL, **and Taiwan**; site also mentions "offshore facilities" | Elk Grove Village, IL; Fort Worth, TX | All three fit electrically (4 mil at 1 oz, 6 mil at 2 oz). Listed minimum board size is 50 × 50 mm, so these would be panelised; handling UNCONFIRMED | Turnkey and consigned | ITAR, AS9100D, ISO 9001:2015 | No usable published price. "Same-day prototypes" | https://www.pcbnet.com/capabilities/ ; https://iconnect007.com/article/139638/imagineering-driven-by-customer-demand/139635/design |
| **Epec** (New Bedford, MA) | "USA, China, Taiwan, and Malaysia". US sites: New Bedford MA, Irving TX, Sherburne NY. Which site builds an order is UNCONFIRMED; US-only must be requested | PCB assembly not found on the pages read; UNCONFIRMED | No detailed table retrieved; likely fits; UNCONFIRMED | – | ITAR, ISO 9001, mentions MIL-PRF / AS9100 | Quote needs registration. Standard 20 working days; quick-turn 1–15 | https://www.epectec.com/pcb/delivery-lead-times.html |
| **San Francisco Circuits** | A broker by its own description ("network of fully qualified partners", "worldwide network"). Says it has domestic partners with traceability; domestic-only must be specified | Same | No table retrieved; UNCONFIRMED | Turnkey, partial, consigned | ISO 9001:2015, ITAR, CMMC Level 2 | Quote needs login | https://www.sfcircuits.com/about-us ; https://www.sfcircuits.com/system-integrators |
| **PCB Unlimited** | Three tiers: "USA Quickturn" (2–8 layers, 5 mil), Taiwan partners, China partners. US facility city and ownership not given | "USA printed circuit board assembly services"; location UNCONFIRMED | Upper sits exactly at the US tier's 5 mil limit; ring minimum not published | UNCONFIRMED | None stated for the US tier | Instant-quote form on site, not run. US plants closed 2026-11-23 to 27 | https://www.pcbunlimited.com/ |
| **Green Circuits** (San Jose, CA) | Bare-board source not stated; UNCONFIRMED | San Jose, CA (also London, Ontario) | Assembly house for prototype to low volume | Turnkey | ITAR, AS9100D, ISO 9001, ISO 13485 | "Quotes in as low as 4 hours" | https://www.greencircuits.com/ |
| **Amtech Electrocircuits** (Troy, MI) | Bare-board source UNCONFIRMED | Troy, MI | The only assembler found that explicitly advertises "NDAA-compliant drone and UAS manufacturing" and paperwork "ready to drop straight into a Blue UAS submission". It does not claim to be Blue-listed. Small-run acceptance UNCONFIRMED | Assembly, box build, harness | ISO 9001, ISO 13485. ITAR and AS9100 not mentioned | Upload-based quote | https://buildamtech.com/uas/ |
| **Bittele** (Toronto) | **Shenzhen, China** ("our PCB Fabrication facility in Shenzhen") | Markham, Ontario or Shenzhen, customer's choice | **Fails** the requirement: the bare board is Chinese even when assembled in Canada. A Malaysia assembly page exists; Malaysian bare-board fabrication UNCONFIRMED | Turnkey | ISO 9001, ISO 13485 | – | https://www.7pcb.com/blog/pcb-assembly-in-canada-vs-china |

Out of the Box Manufacturing (Renton, WA) appears in third-party sources as an AS9100 / ITAR prototype assembler; no
drone or NDAA claim was found and its link to any existing NDAA flight controller is UNCONFIRMED.

### 2.3 Allied-country vendors

Remember section 1.5 point 6: these satisfy Section 848 but not the FCC "domestic end product" exemption.

| Vendor | Where made | Fit | Parts | Price / lead time | Notes | Source |
|---|---|---|---|---|---|---|
| **AISLER** (Germany) | "Manufactured and delivered from Germany"; assembly "Made in Europe" through a European network, plants not named. No US manufacturing | **All three fit the published rules.** 6-layer: 0.10 mm track/space, via ring 0.10 mm, ENIG, but 35 µm copper on all layers (inner is not 0.5 oz). 4-layer with 70 µm outer copper is a listed product: 0.175 mm track/space, via ring 0.15 mm (the lower board has 0.20). Component-hole rings must be 0.30 mm: check headers and mounting holes | Turnkey from distributors; customer parts accepted for a fee; from 1 piece; double-sided, down to 0201. 0.5 mm LGA and reflowed standoffs not explicitly listed: UNCONFIRMED | Published 2023 table (may be out of date): 4-layer ENIG €14 job + €0.13/cm² per board; 2-layer ENIG €12 + €0.097/cm². That gives about €20 for three 4-layer boards of this size and €14 for three service boards. Current 6-layer and 70 µm rates UNCONFIRMED. Boards in multiples of 3. Assembly "within 6 business days" | US delivery by UPS, 2–10 business days. US duty is not collected at checkout; the carrier bills it | https://community.aisler.net/t/pcb-portfolio/101 ; https://community.aisler.net/t/6l-layer-35-m-enig-design-rules/5467 ; https://community.aisler.net/t/4-layer-70-m-enig-design-rules/5772 ; https://community.aisler.net/t/our-simple-pricing/102 ; https://community.aisler.net/t/shipping-methods/672 |
| **Eurocircuits** (Belgium; plants in Eger, Hungary and near Aachen, Germany) | In-house European plants for both fab and assembly | Upper fits the pool (0.10 mm track/space, ENIG), **but** the pool wants pad = finished hole + 0.30 mm, so a 0.5 mm pad needs a finished hole of 0.2 mm or less. Lower: 70 µm outer copper is listed for 1–2 layer pooling only; on 4 layers it is non-pool, UNCONFIRMED. Service fits | Eurocircuits buys the parts; from 1 board; both sides; X-ray | Price calculator exists (reported usable without login; not run). 5 working days bare, 10 assembled | Shipping to the US UNCONFIRMED | https://www.eurocircuits.com/services/standard-pool/ |
| **Würth WEdirekt** (Germany) | German factories | Bare boards only, no assembly | – | – | Sells to businesses only; USA not in the country selector. Not usable here | https://www.wedirekt.com/en/ |
| **P-ban.com** (Japan) | Partner plants in Japan, Korea, Taiwan **and China**; which one builds an order must be asked in writing | – | – | No English online ordering (planned for 2027); order by email | Not practical today | https://www.p-ban.com/order/global_service.html |
| **PCB-togo** (Taipei) | Factory location not stated; UNCONFIRMED | – | – | – | Not verified as Taiwan-made | https://www.pcb-togo.com/ |

No Korean self-service prototype house with English ordering was found.

### 2.4 What to ask any of them, in writing, before ordering

1. Country and site where the bare board is fabricated, and the laminate maker.
2. Site where assembly is done.
3. A certificate of conformance stating both.
4. Acceptance of the upper board's 0.10 mm via annular ring (0.3 mm hole, 0.5 mm pad).
5. Whether they will place and reflow the M2 standoffs on the lower board.
6. That the BOM is locked to the listed manufacturer part numbers, bought from authorised distributors, with no
   substitution without approval, and that the reels' country-of-origin labels are recorded or returned.
7. No-clean flux and no ultrasonic cleaning (barometer and IMU; see `docs/manufacturing.md`).

---

## 3. Bill of materials review

Read from `fab/upper/upper-bom.csv`, `fab/lower/lower-bom.csv`, `fab/service/service-bom.csv`. No design file was changed.

Two cautions before the tables:

- **Brand is not origin.** A Western, Japanese, Korean or Taiwanese brand often still builds or packages in China
  (examples seen in this session are in section 3.4). For Section 848 the statute does not look at discrete parts at
  all; for a customer's BOM review, the manufacturer's nationality is what is usually checked first, and the country of
  origin on the distributor's label second. The alternates below fix the first; record the second when the parts arrive.
- **"Drop-in" is marked honestly.** "Same footprint" in the table means the package is a standard one (0402, SOT-23,
  SMB, 3225 crystal). Where the footprint is specific to the part (inductor, shunt, USB-C, switch, buzzer, standoff),
  the table says what must be compared before ordering.

Company locations are [MEMORY] unless a source is given.

### 3.1 The one that matters most: U4, AT7456E OSD chip

AT7456E (Zhongkewei, Hangzhou [per `research/parts.md`]) is a Chinese clone of the Maxim MAX7456. It is an active,
SPI-controlled chip in the video path of a flight controller: exactly the kind of line a BOM review stops at.

**There is no in-production non-Chinese drop-in.** The original MAX7456EUI+ is obsolete: DigiKey lists it as
obsolete, and Analog Devices' own FAQ says there is no replacement and none is planned. Stock offered by brokers is
not from authorised channels and should not be trusted.

Options, in order of practicality:

1. **Do not fit U4 and Y2** (and their decoupling capacitors if wished) on NDAA builds. Analog OSD is only needed for
   analog video. Digital video systems (DJI, HDZero, Walksnail) take the OSD over a serial port using MSP DisplayPort
   and need no OSD chip. The firmware would need the OSD device made optional; that is a firmware/hwdef matter outside
   this report.
2. Fit a genuine MAX7456EUI+ from documented old stock, if any can be found with traceability. It is the same
   TSSOP-28-EP pinout. Note it needs 4.75–5.25 V (the AT7456E works from 3.15 V), and pin 13 is not connected on it.
3. Keep the AT7456E and declare it. Honest, but it defeats the purpose.

Sources: https://www.digikey.fr/en/products/detail/analog-devices-inc-maxim-integrated/MAX7456EUI/1701658 ;
https://ez.analog.com/power/battery-management-system/a/documents/do7300/what-is-maxim-s-closest-equivalent-part-to-obsolete-part-number-max7456eui

### 3.2 Parts from covered-country manufacturers, with alternates

| Board | Ref | Now (maker) | Suggested alternate | Same footprint? | Where | Checked this session? |
|---|---|---|---|---|---|---|
| Upper | U4 | AT7456E (Zhongkewei, China) | None in production. See 3.1 | – | – | Yes (obsolescence) |
| Upper | Y2 | 27 MHz 10 pF 3225 (YXC, Shenzhen) | ECS **ECS-270-10-33B-CKM-TR** (27 MHz, 10 pF, 3.2 × 2.5 mm, 4-pad). Not needed if U4 is left off | Yes (standard 3225 4-pad) | DigiKey (1,944 shown) | Listing seen. ECS is a US company; factory country UNCONFIRMED |
| Upper | Y1 | 8 MHz 12 pF 3225 (YXC) | ECS **ECS-80-12-33-JGN-TR** (8 MHz, 12 pF, 3.2 × 2.5 mm, 4-pad, ±20 ppm) | Yes | DigiKey (about 41,000 shown), Mouser | Listing seen. ESR is shown as 100, 400 or 500 Ω in different listings: read the datasheet against the STM32 oscillator margin |
| Upper | C21 C22 | 15 pF C0G 0402 (FH / Fenghua, Guangdong) | Murata **GRM1555C1H150JA01D** | Yes | DigiKey, Mouser | [MEMORY] |
| Upper, lower | D1 (upper) | Blue LED 0603 (Nationstar, Foshan) | Würth **150060BS75000** | Yes; brightness differs, R value may want trimming | DigiKey, Mouser | [MEMORY] |
| Upper, lower | D2 (both) | Green LED 0603 (Nationstar) | Würth **150060GS75000** | Yes | DigiKey, Mouser | [MEMORY] |
| Upper | Q1 | 2N7002 (JSCJ, Jiangsu) | onsemi **2N7002LT1G** | Yes (SOT-23, G-S-D) | DigiKey, Mouser | [MEMORY]. Avoid Nexperia here: it is owned by Wingtech (China) |
| Upper | R18 | 10 Ω 1 W 1206 (RESI, China, per `research/audit-2026-11-19.md`) | Vishay **CRCW120610R0FKEAHP** (0.75 W) | Yes. Rating is 0.75 W, not 1 W; the audit calculates 0.18 W at 50 % duty and 0.37 W if held on, so it is inside the rating. Owner to accept | DigiKey, Mouser | [MEMORY] for the part; dissipation from the audit |
| Upper | R16 R17 | 4.7 Ω 1206 ½ W (UNI-ROYAL, China) | Vishay **CRCW12064R70FKEAHP** (0.75 W) | Yes | DigiKey, Mouser | [MEMORY] |
| All | 0402 1 % resistors | UNI-ROYAL 0402WGF series | Vishay CRCW0402 or Panasonic ERJ-2RKF, same value. 10 Ω **CRCW040210R0FKED**; 75 Ω **CRCW040275R0FKED**; 100 Ω **CRCW0402100RFKED**; 1 k **CRCW04021K00FKED**; 2.2 k **CRCW04022K20FKED**; 5.1 k **CRCW04025K10FKED**; 10 k **CRCW040210K0FKED**; 51 k **CRCW040251K0FKED**; 100 k **CRCW0402100KFKED**. Panasonic equivalents: ERJ-2RKF10R0X, 75R0X, 1000X, 1001X, 2201X, 5101X, 1002X, 5102X, 1003X | Yes | DigiKey, Mouser | [MEMORY] |
| Upper | J1 | 3 × 12 header from four HCTL pieces (China) | Samtec **TSW-112-08-G-T-RA** (already named in the BOM as the alternative) | Per the BOM | Samtec, DigiKey, Mouser | Already in the BOM |
| Lower | J2 | 3 × 9 header from three HCTL pieces | Samtec **TSW-109-08-G-T-RA** (same series, 9 positions) | Same series as J1; compare the drawing | Samtec, DigiKey, Mouser | By analogy; stock UNCONFIRMED |
| Lower | D1 | SMBJ15CA (Jingdao, China) | Vishay **SMBJ15CA-E3/52**, or Littelfuse **SMBJ15CA**, or Bourns **SMBJ15CA** | Yes (SMB) | DigiKey, Mouser | [MEMORY] |
| Lower | H1 H2 H3 | M2 × 8 mm reflow standoff (Sinhoo, China) | PennEngineering **PEM SMTSO-M2-8ET** | Yes: the footprint was drawn to PEM's figures (hole 3.75, pad 6.2; PEM lists C max 3.6 mm, A max 1.53 mm, pad min 6.2 mm). PEM's is tin-plated steel, the Sinhoo part is brass | Mouser (31,947 shown, $1.53 each at qty 1) | Yes |
| Lower | L1 L2 | 4.7 µH 5 A moulded, 5.5 × 5.2 × 3.0 mm (SXN, Shenzhen) | First choice Coilcraft **XGL5030-472MEC** (4.7 µH, 21.9 mΩ typ, Isat 6.7 A at 30 % drop, Irms 6.3 A at 20 °C rise). Second: Bourns **SRP5030T-4R7M** (5.7 × 5.2 × 2.8 mm, 4.6 A, 53 mΩ) | **Not confirmed.** The board's pads are 2.0 × 2.5 mm with a 3.0 mm gap. Compare each maker's land pattern before ordering. Do not use Vishay IHLP2020CZER4R7M01: DigiKey marks it discontinued | DigiKey, Coilcraft direct | Electrical data seen; land patterns not |
| Lower | R1 | 0.5 mΩ 1 % 6 W 2512 shunt (Yezhan, China) | Bourns **CSS2H-2512R-L500F** (0.5 mΩ, 1 %, 6 W at 70 °C terminal temperature, 3 W at 130 °C) | **Check.** The footprint has Kelvin taps drawn to the Yezhan land pattern; compare terminal length. Vishay WSLP2512L5000FEA is only 3 W; WSLF2512L5000FEA is the Vishay 6 W class | DigiKey, Mouser | Rating seen in distributor listings |
| Service | BZ1 | MLT-8530 magnetic buzzer (Jiangsu Huaneng, China) | Same Sky (formerly CUI Devices) **CMT-8504-100-SMT-TR**. The footprint in the design is already named for this part | Compare which pads are + and − against the Same Sky drawing (the audit found the MLT-8530 has both coil pads on one edge) | DigiKey, Mouser | [MEMORY]. Same Sky is a US company; the buzzer's factory country is UNCONFIRMED and is probably China |
| Service | D1 | 1N5819WS SOD-323 (Hottech, Shenzhen) | Diodes Inc **B5819WS-7-F**, or Toshiba **CUS10S40,H3F** | Yes (SOD-323 / USC) | DigiKey, Mouser | [MEMORY] |
| Service | J1 | USB-C TYPE-C-31-M-12 ("Korean Hroparts Elec"; despite the name, a Shenzhen company [MEMORY]) | GCT **USB4105-GF-A** (16-pin USB 2.0 Type-C, top mount) | **Not confirmed.** KiCad carries a separate footprint for it; compare shell-leg positions and pad rows before ordering. GCT is British; its factory country is UNCONFIRMED | DigiKey, Mouser | Listing seen; compatibility not found |
| Service | SW1 | TS-1187A tactile switch 5.1 × 5.1 mm (XKB, China) | Alps Alpine **SKQGABE010** (5.2 × 5.2 × 1.5 mm, 4 terminals) | Compare the land pattern. One distributor lists China as country of origin for a reel variant of this Alps part | DigiKey, Mouser | Listing seen |

### 3.3 Not Chinese companies, but worth a line in the BOM record

| Ref | Part | Maker | Note |
|---|---|---|---|
| Upper D3 | SMF5.0CA-TP | MCC (Micro Commercial Components), headquartered in California [MEMORY] | Factory country UNCONFIRMED. If a cleaner record is wanted: Littelfuse **SMF5.0CA** (SOD-123FL) [MEMORY] |
| Upper Q2 | AO3401A | Alpha & Omega Semiconductor, headquartered in California [MEMORY] | Much of AOS's packaging is in China [MEMORY]. Alternate with the same SOT-23 pinout: Infineon **IRLML9301TRPBF** (−30 V, 64 mΩ at −10 V, 103 mΩ at −4.5 V). The gate here is driven to −5 V, so it is fully on [MEMORY for the part; drive level from the audit] |
| Capacitors | CL05, CL10, CL21, CL31 series | Samsung Electro-Mechanics (Korea) | Fine by ownership. Samsung has large MLCC plants in China and the Philippines [MEMORY]; origin varies by lot |
| Capacitors | GRM155, BLM18 | Murata (Japan) | Fine |
| Lower C13 C23 | CC0402KRX7R9BB333 | Yageo (Taiwan) | Fine by ownership; Yageo has plants in China [MEMORY] |
| J5, service J2 | SM06B-SRSS-TB | JST (Japan) | Fine |
| Upper J4 | 104031-0811 | Molex (US) | Fine by ownership; factory country UNCONFIRMED |
| J3, lower J1 | FTSH / SFMC | Samtec (US) | Fine |

### 3.4 Main ICs

| Ref | Part | Maker | What is known about origin |
|---|---|---|---|
| U1 | STM32F765VIT6 | STMicroelectronics (Switzerland / France / Italy) | A change notice hosted by Mouser names ST Crolles, France as the wafer source for STM32F765 parts. Country of origin on distributor records varies: RS lists the Philippines; Octopart's aggregate shows "Mainland China, Malaysia, Taiwan". **So a given reel may have been packaged in China.** Buy from an authorised distributor and record the country on the label; ask for a non-China lot if it matters to the customer. Sources: https://www.mouser.com/PCN/STMicroelectronics_15305.pdf ; https://octopart.com/part/stmicroelectronics/STM32F765VIT6 ; https://ie.rs-online.com/web/p/microcontrollers/1962053 |
| U2 | ICM-45686 | TDK InvenSense (Japan / US) | Fab and packaging location not found. Buy genuine parts only: `research/parts.md` records Chinese clones of the sister part sold under the same number |
| U3 | BMP388 | Bosch Sensortec (Germany) | Not found |
| U5 U6 U7, lower U1 U2 U3 | LM66200, TLV755, TPS7A20, TPS62933, INA214 | Texas Instruments (US) | Not found per part. TI operates an assembly and test site in Chengdu, China [MEMORY], so origin varies by lot |
| Service U1 | USBLC6-2SC6 | STMicroelectronics | Not found |

### 3.5 Sources for section 3

- 8 MHz crystal: https://www.digikey.ca/en/products/detail/ecs-inc/ECS-80-12-33-JGN-TR/10478754
- 27 MHz crystal: https://www.digikey.co.uk/en/products/detail/ecs-inc/ECS-270-10-33B-CKM-TR/8023437
- Standoff: https://www.pemnet.com/products/product-finder/smtso-m2-8et/ ; Mouser part 153-SMTSO-M2-8ET
- Shunt: https://www.digikey.com/en/products/detail/bourns-inc/CSS2H-2512R-L500F/CSS2H-2512R-L500FCT-ND/6023730 ; series datasheet https://www.farnell.com/datasheets/2058210.pdf
- Inductors: https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xgl/xgl5030/ ; https://www.digikey.it/en/products/detail/coilcraft/XGL5030-472MEC/16817139 ; https://www.farnell.com/datasheets/2034962.pdf (Bourns SRP5030T)
- USB-C: https://www.digikey.com/en/products/detail/gct/USB4105-GF-A/11198441
- Switch: https://octopart.com/part/alps/SKQGABE010

---

## 4. Short list for this owner

### 4.1 Ranked

1. **AdvancedPCB.** One company, its own US board plants and its own US assembly line, an explicit "not a broker"
   statement, no minimum quantity, and the certifications a defence customer recognises (ITAR, AS9100D). One purchase
   order covers all three boards, and one certificate of conformance covers fabrication and assembly. The upper board
   will probably be priced in its "Advanced" tier because of the via ring.
2. **ASC Sunstone boards with Screaming Circuits assembly.** Two named US companies that already work as a pair
   (Screaming orders the boards from Sunstone for you), minimum order of one, aimed at exactly this kind of small
   prototype job. The upper board will probably need a custom board quote for the same via-ring reason. The paper trail
   is two certificates, not one.
3. **Sierra Circuits.** Own plant in Sunnyvale for boards, US assembly, the deepest certification list. Ranked third
   because the upper board does not fit its standard online service and must go through a custom quote, which usually
   costs more.

Conditional alternative: **MacroFab** is the only vendor whose *published* limits pass all three boards without an
exception, and it is the easiest to order from. It ranks below the three above only because it does not say where its
ordinary bare boards are made and its assembly network includes Mexico. If it confirms in writing a US-made bare board
and US assembly for the order, it belongs at the top.

Lowest-cost route that still keeps everything in the US: OSH Park for the upper and service bare boards (published
prices above, and ask about the 3.94 mil ring), a US fab for the 2 oz lower board, then either hand assembly (it is
then "manufactured" by the owner in the US) or kitted assembly at Screaming Circuits.

If "outside the four countries" is enough and "made in USA" is not needed: **AISLER** in Germany is the only vendor
found with published design rules that cover all three boards and published per-area prices. See the limits in 1.5
point 6.

Do not use for this purpose: Bittele (Chinese bare boards), CircuitHub without the "US FABRICATION" note, any vendor's
"offshore" tier.

### 4.2 Cost for 2–5 sets

**Published prices found** (everything else below is an estimate):

| Item | Price | Source |
|---|---|---|
| OSH Park upper bare boards, 3 pieces | $35.15 | $15 per in², docs.oshpark.com |
| OSH Park service bare boards, 3 pieces | $4.46 | $5 per in² |
| AISLER 4-layer ENIG (35 µm) at this size, 3 pieces | about €20 | 2023 price table, may be out of date |
| AISLER 2-layer ENIG service board, 3 pieces | about €14 | same |
| PEM SMTSO-M2-8ET standoff | $1.53 each at quantity 1 | Mouser |
| Parts at LCSC single-unit prices (from the BOM files) | about $44 upper, $10 lower, $1 service | `fab/*/*-bom.csv` |

**Estimate, not from any quote** (my judgement of typical US quick-turn pricing; treat as an order of magnitude and
replace with real quotes):

| Route | 2–5 sets, total |
|---|---|
| Full turnkey at a US fab-and-assembly house (options 1–3): three bare-board lots, three assembly set-ups with stencils, one board double-sided, parts from DigiKey/Mouser with attrition | **roughly $3,000 – $7,000** |
| US bare boards (OSH Park plus a US fab for the lower board), parts bought by the owner, hand assembly | **roughly $700 – $1,500** |
| AISLER boards and assembly in Europe, shipped to the US, plus duty | **roughly $800 – $2,000** |

Parts with the alternates in section 3 will cost more than the LCSC figures: allow roughly $80–110 per set at
US distributor prices in small quantities (estimate).

### 4.3 What could not be verified

- Any price from a US assembler (all need login or upload).
- Whether AdvancedPCB, Sunstone or Sierra will accept the upper board's via ring at standard pricing.
- Whether any of them will place the reflow standoffs.
- Where MacroFab's ordinary bare boards and Green Circuits', Amtech's and PCB Unlimited's US-tier boards are made.
- Sierra's assembly city; that Screaming Circuits assembles at Canby (inferred from its ship-to address).
- AISLER's current 6-layer and 70 µm prices; Eurocircuits' US shipping and 70 µm on four layers.
- Royal Circuits' own site (unreachable); Summit's design-rule numbers.
- A Taiwanese, Korean or Japanese prototype service with English ordering and confirmed non-China production.
