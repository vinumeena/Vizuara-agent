"""
Ramco Aviation Suite — mock data module.
Contains Q&A pairs and knowledge entries covering MRO, parts,
maintenance scheduling, compliance, and crew management.
"""

AVIATION_CHAT_QA = [

    # ── MRO / Work Orders ────────────────────────────────────────────────────
    ("How do I create a work order for scheduled maintenance in Ramco Aviation?",
     "To create a work order: Navigate to MRO > Work Orders > New Work Order. Select the Aircraft Registration, Task Type (Scheduled/Unscheduled), and reference the applicable Task Card or Maintenance Program. Assign the Work Center and estimated man-hours. Once submitted, the work order is routed for planning approval. You can track real-time status under MRO > Work Order Monitor.",
     "Product Expert"),

    ("How do I close a work order in Ramco Aviation after maintenance is complete?",
     "To close a work order: Go to MRO > Work Orders > search your WO number. Verify all task cards are signed off, all parts issued are accounted for, and findings are documented. Click 'Close Work Order' — the system will auto-update the aircraft maintenance record, update the next due date in the Maintenance Program, and generate a Certificate of Release to Service (CRS) for regulatory compliance.",
     "Product Expert"),

    ("What is the process to raise a defect in Ramco Aviation Suite?",
     "To raise a defect: Go to Line Maintenance > Defect Recording > New Defect. Enter the Aircraft Registration, ATA Chapter (e.g., ATA 28 for Fuel, ATA 32 for Landing Gear), defect description, and deferred or immediate action. Attach any supporting evidence (photos, NDT reports). The defect is automatically linked to the aircraft's open defect log and triggers a work order if immediate action is required.",
     "Product Expert"),

    ("How do I track aircraft utilisation hours in Ramco?",
     "Aircraft utilisation is tracked automatically through Flight Operations > Aircraft Utilisation. Each flight entry updates flying hours, cycles, and landings in real time. You can view the current hours/cycles in Technical Records > Aircraft Master > Life Parameters. Alerts are triggered automatically when the aircraft approaches a maintenance threshold (e.g., 500-hour check, 1000-cycle check). Run the Utilisation Report from Reports > Maintenance > Aircraft Utilisation.",
     "Product Expert"),

    ("How is the Maintenance Programme managed in Ramco Aviation?",
     "The Maintenance Programme (MP) is managed under Maintenance Planning > Maintenance Programme. Load the approved MP from the OEM (e.g., AMM, MPD) as a task library. Each task has intervals defined in Flight Hours (FH), Flight Cycles (FC), Calendar Days (CD), or a combination. Ramco calculates the next due date automatically based on current aircraft parameters. Programme revisions are version-controlled and require authorised sign-off before going live.",
     "Product Expert"),

    ("How do I issue aircraft parts from the store in Ramco?",
     "To issue parts: Go to Inventory > Part Issue > New Issue. Select the Work Order reference, search for the Part Number, enter quantity, and select the storage location. The system validates the part's serviceable status, shelf life, and certification (Certificate of Conformity or Form 1). Once issued, stock levels update in real time and the part is linked to the work order for traceability. Batch/serial number tracking is mandatory for life-limited parts.",
     "Product Expert"),

    ("What is the process for receiving aircraft parts into Ramco inventory?",
     "To receive parts: Go to Inventory > Goods Receipt > New Receipt. Enter the Purchase Order reference or create an unplanned receipt. Scan or enter the Part Number, Serial/Batch Number, and quantity. Attach the Certificate of Conformity (CoC) or EASA Form 1 / FAA 8130-3. The system performs a quarantine check — parts remain in 'Received' status until the Quality team inspects and moves them to 'Serviceable'. Non-conforming parts are moved to quarantine store.",
     "Product Expert"),

    ("How do I manage life-limited parts (LLPs) in Ramco Aviation?",
     "LLPs are tracked under Technical Records > Component Management > Life Limited Parts. Each LLP has an OEM-defined life limit in flight cycles, flight hours, or calendar time. Ramco automatically decrements the remaining life after each flight. When a part reaches 90% of its life limit, an alert is raised in the Planning module. At 100%, the part is auto-quarantined and cannot be issued for flight. Full traceability from manufacture to removal is maintained per regulatory requirements.",
     "Product Expert"),

    # ── Compliance / Airworthiness ───────────────────────────────────────────
    ("How are Airworthiness Directives (ADs) tracked in Ramco?",
     "ADs are managed under Compliance > Airworthiness Directives. Import the AD from the regulatory authority (FAA, EASA, DGCA). Ramco matches the AD against affected aircraft in your fleet using the applicability criteria (Aircraft Type, Model, Serial Number, Engine type). Compliance status shows as Open, In-Progress, Complied, or Not Applicable. Each AD is linked to a work order for the corrective action. Recurring ADs automatically generate the next compliance due date.",
     "Product Expert"),

    ("What is the process for managing Service Bulletins (SBs) in Ramco?",
     "Service Bulletins are managed under Compliance > Service Bulletins. Load the SB from the OEM, define applicability, and categorise as Mandatory or Optional. For mandatory SBs, the system raises a compliance task. For optional SBs, fleet managers review and approve or defer. Compliance records are maintained for each aircraft with the incorporation date, work order reference, and technician sign-off. SB status is reported in the Compliance dashboard for CAMO oversight.",
     "Product Expert"),

    ("How do I generate an aircraft maintenance forecast in Ramco?",
     "Go to Maintenance Planning > Maintenance Forecast. Select the aircraft registration and forecast period (30, 60, 90, or 180 days). Ramco calculates projected due dates for all maintenance tasks based on current utilisation rates (average daily FH and FC). The forecast report shows tasks due in each time window, estimated man-hours, and parts requirements. This feeds directly into hangar planning and material procurement to avoid aircraft-on-ground (AOG) situations.",
     "Product Expert"),

    # ── Crew / HR ────────────────────────────────────────────────────────────
    ("How is crew licensing and medical validity tracked in Ramco?",
     "Crew qualifications are managed in Crew Management > Crew Records > Licences & Medicals. Upload each crew member's licence (ATPL, CPL, Type Rating) and medical certificate with issue and expiry dates. Ramco sends automatic alerts 60, 30, and 7 days before expiry to the crew member and their supervisor. Expired licence holders are flagged in the rostering module and cannot be assigned to flights. The CAMO can pull a fleet-wide licence validity report at any time.",
     "Product Expert"),

    ("How do I roster crew for a maintenance task in Ramco Aviation?",
     "Go to Crew Management > Rostering > New Assignment. Select the maintenance event (Work Order or Check), assign the Licensed Aircraft Maintenance Engineer (LAME), and verify their currency on the aircraft type. Ramco validates the crew's availability (no leave, no training conflict), licence validity, and fatigue/duty hour limits. Once confirmed, the assignment is locked and a task card is generated with the technician's name for their sign-off.",
     "Product Expert"),

    # ── Finance Integration ──────────────────────────────────────────────────
    ("How does Ramco Aviation integrate with the Finance module?",
     "Ramco Aviation is fully integrated with Ramco ERP Finance. When a work order is closed, maintenance costs (labour, parts, services) are automatically posted to the relevant cost centre in the GL. Lease aircraft maintenance reserves (MR) are calculated per flight hour and accrued in Finance. Part purchases flow from Aviation Procurement through AP with 3-way matching. Engine shop visit costs are capitalised against the asset in Fixed Assets. All transactions carry the work order reference for traceability.",
     "Product Expert"),

    ("How do I create a purchase requisition for AOG parts in Ramco?",
     "For AOG (Aircraft on Ground) parts: Go to Procurement > Purchase Requisition > New PR and flag it as AOG Priority. This triggers a high-priority workflow that bypasses standard approval levels up to a pre-configured AOG value limit (e.g., USD 5,000). The system alerts the Procurement Manager and Supply Chain on-call contact via email and Teams notification. AOG PRs are processed within 2 hours. A dedicated AOG PO is generated and tracked separately in the AOG dashboard.",
     "Product Expert"),

    # ── Reporting ────────────────────────────────────────────────────────────
    ("What key reports are available in Ramco Aviation Suite?",
     "Ramco Aviation Suite offers the following key reports: (1) Aircraft Utilisation Report — flying hours, cycles, landings by tail and fleet. (2) Maintenance Forecast Report — upcoming tasks in 30/60/90 days. (3) AD/SB Compliance Report — status across the fleet. (4) Inventory Valuation Report — stock value by part type and location. (5) Work Order Cost Report — labour and material costs per maintenance event. (6) Component Life Status Report — LLP remaining life. (7) Crew Licence Expiry Report. All reports can be scheduled for auto-email delivery.",
     "Product Expert"),

    ("How do I handle a technical log entry in Ramco Aviation?",
     "Technical Log entries are recorded in Line Maintenance > Technical Log. For each flight, the crew enters departure/arrival details, fuel uplift, oil consumption, and any defects observed. Each entry is timestamped and digitally signed by the Captain. Defects raised in the technical log automatically create entries in the open defect log and trigger work orders for maintenance action. The technical log is a regulatory document — Ramco maintains an audit trail and supports export in PDF format for authority inspections.",
     "Product Expert"),
]


AVIATION_KNOWLEDGE = [
    {
        "topic": "Ramco Aviation > MRO Overview",
        "content": "Ramco Aviation Suite is an integrated MRO (Maintenance, Repair & Overhaul) software platform used by airlines, MRO providers, defence, and helicopter operators globally. Key modules include: Line Maintenance, Base Maintenance, Engine Shop, Component Workshop, Inventory & Procurement, Technical Records, Compliance Management, Crew Management, and Finance Integration. The platform is certified for EASA Part-145, Part-CAMO, FAA, DGCA, and other regulatory frameworks.",
    },
    {
        "topic": "Ramco Aviation > Technical Records",
        "content": "Technical Records in Ramco Aviation maintains the complete airworthiness history of each aircraft tail. Records include: Aircraft Master (registration, serial, configuration), Component Tree (installed components with part/serial numbers), Life Parameters (total FH, FC, landings), Maintenance Programme compliance, AD/SB status, Work Order history, and Modification records. All records are digitally signed and tamper-proof. Records can be exported for aircraft sale, lease return, or authority audit in standard formats.",
    },
    {
        "topic": "Ramco Aviation > Inventory Management",
        "content": "Ramco Aviation Inventory manages aviation parts across multiple stores and locations. Features include: Part Master with ATA classification, Multi-location stock management, Batch and serial number traceability, Shelf-life monitoring, Quarantine management for non-conforming parts, Min-max reorder triggers, Part interchangeability and substitution, Loan/borrow tracking between operators, and Scrap/disposal management. All parts require valid certification documents (EASA Form 1, FAA 8130-3, CoC) before being moved to serviceable stock.",
    },
    {
        "topic": "Ramco Aviation > Compliance & Airworthiness",
        "content": "Ramco's Compliance module manages all mandatory and optional regulatory requirements for the fleet. It covers: Airworthiness Directives (ADs) from FAA, EASA, DGCA and other authorities; OEM Service Bulletins (SBs) and Service Letters; Continued Airworthiness Management (CAMO) oversight; Operator-defined maintenance requirements; and Modification embodiment tracking. The system automatically determines applicability based on aircraft type, model, series, and configuration, and raises compliance tasks when due.",
    },
    {
        "topic": "Ramco Aviation > Line Maintenance",
        "content": "Line Maintenance in Ramco covers daily and transit check operations. Key capabilities: Digital Technical Log with crew sign-off; Pre-flight, Transit, and Daily check task cards; Defect recording and deferred defect management; MEL/CDL (Minimum Equipment List / Configuration Deviation List) management; Fuel and oil uplift recording; Component replacement tracking; and Certificate of Release to Service (CRS) generation. Mobile access allows technicians to sign off tasks on tablets at the aircraft gate.",
    },
    {
        "topic": "Ramco Aviation > Maintenance Planning",
        "content": "Ramco Maintenance Planning provides long-range planning for heavy maintenance and short-range planning for line operations. Features: Maintenance Programme task management with multi-interval due date calculation; Maintenance forecast for 30/60/90/180-day windows; Hangar visit planning with man-hour and material requirements; Critical path analysis for base maintenance checks (A-Check, C-Check, D-Check); Resource and skill requirement planning; and Package building to optimise task grouping during planned maintenance visits.",
    },
    {
        "topic": "Ramco Aviation > Crew Management",
        "content": "Ramco Crew Management handles aviation maintenance engineer (AME/LAME) and operational crew qualifications, scheduling, and compliance. Key features: Licence and type rating management with expiry alerts; Medical certificate tracking; Training records and currency management; Duty hour and fatigue risk management per CAR/OPS rules; Shift rostering for maintenance operations; Crew cost tracking integrated with payroll; and Regulatory reports on crew qualification status for authority submissions.",
    },
    {
        "topic": "Ramco Aviation > AOG Management",
        "content": "AOG (Aircraft on Ground) management in Ramco provides end-to-end support for aircraft recovery situations. When an AOG is declared: A high-priority work order is auto-created; AOG parts procurement is triggered with expedited workflow; Relevant personnel (Engineering Manager, Procurement, on-call AME) are notified via Teams and SMS; A dedicated AOG dashboard shows real-time recovery status; Costs are tracked separately for insurance claims. Average AOG resolution time is tracked as a KPI in the Operations dashboard.",
    },
]
