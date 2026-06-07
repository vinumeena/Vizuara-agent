"""
Generates realistic mock Microsoft Teams conversation data
for a software/ERP company (Ramco-like context).

Produces three JSONL files:
  data/chat_history.jsonl       — Q&A pairs from Teams chats
  data/product_knowledge.jsonl  — Product/process knowledge entries
  data/user_preferences.jsonl   — Per-user preferences
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent
random.seed(42)

# ── Helpers ───────────────────────────────────────────────────────────────────

def rand_ts(days_back: int = 90) -> str:
    base = datetime(2026, 6, 7)
    delta = timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(8, 18),
        minutes=random.randint(0, 59),
    )
    return (base - delta).isoformat() + "Z"

def save_jsonl(path: Path, records: list[dict]):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  Saved {len(records):>4} records -> {path.name}")

# ── User pool ─────────────────────────────────────────────────────────────────

USERS = [
    "Vinoodhini D", "Arjun Mehta", "Priya Suresh", "Karthik R",
    "Deepa Nair", "Santhosh Kumar", "Meera Iyer", "Rahul Verma",
    "Anitha Balan", "Suresh Pillai", "Kavitha M", "Rajan T",
]

AGENTS = ["HelpDesk Bot", "IT Support", "HR Assistant", "Product Expert"]

# ── Chat history data ─────────────────────────────────────────────────────────

CHAT_QA_PAIRS = [

    # ── IT Helpdesk ──────────────────────────────────────────────────────────
    ("How do I reset my VPN password?",
     "You can reset your VPN password by visiting the IT portal at intranet.ramco.com/reset-password. Enter your employee ID and click 'Reset VPN Credentials'. You'll receive an OTP on your registered mobile. If you still face issues, raise a ticket under category IT > Network > VPN.",
     "IT Support"),

    ("My laptop is running very slow since the last Windows update. What should I do?",
     "Please try these steps: 1) Restart your laptop and check if performance improves. 2) Open Task Manager (Ctrl+Shift+Esc) and check which process is consuming high CPU. 3) Run Windows Update troubleshooter from Settings > System > Troubleshoot. If issue persists, raise a ticket and we'll schedule a remote session.",
     "IT Support"),

    ("I am unable to access the shared drive \\\\fileserver\\projects. Getting access denied.",
     "Access denied to the shared drive usually means your permissions haven't been updated. Please raise a request in the IT portal under Access Management > Shared Drive Access. Mention the folder path and your manager's name for approval. Access is typically granted within 4 business hours.",
     "IT Support"),

    ("How do I set up multi-factor authentication on my office email?",
     "To enable MFA: 1) Go to aka.ms/mfasetup and sign in with your office email. 2) Click 'Add method' and choose Authenticator App or Phone. 3) Follow the on-screen instructions. 4) Once set up, you'll be prompted for MFA on each new device login. Contact IT helpdesk if you need assistance.",
     "IT Support"),

    ("My Outlook calendar is not syncing with Teams. Meetings are not showing up.",
     "This is usually a sync issue. Try: 1) Sign out and sign back into Teams. 2) In Outlook, go to File > Account Settings and verify your Exchange account is active. 3) In Teams, click your profile picture > Settings > Calendar and ensure it's connected. If the issue continues, we'll check your Exchange mailbox settings.",
     "IT Support"),

    ("Can I install VS Code on my office laptop without admin rights?",
     "Yes! VS Code offers a user-level installer that doesn't require admin rights. Go to code.visualstudio.com, click the dropdown arrow next to 'Download for Windows' and select 'User Installer 64-bit'. This installs VS Code in your user profile folder without needing IT approval.",
     "IT Support"),

    ("The printer in the 3rd floor is showing offline. How to fix it?",
     "For the 3rd floor printer (HP LaserJet Pro M404): 1) Check if the printer is physically on (green light). 2) On your PC, go to Settings > Printers > Right-click the printer > See what's printing > Printer menu > Use Printer Online. 3) If still offline, disconnect and reconnect the printer from your PC. Raise a ticket if not resolved.",
     "IT Support"),

    ("How many GB of OneDrive storage do I have?",
     "As a Microsoft 365 E3 user, you have 1TB of OneDrive storage. To check your current usage, open OneDrive in your browser, click the gear icon > OneDrive Settings > More settings > Storage metrics. If you're running low, contact IT to archive older files to the shared drive.",
     "IT Support"),

    # ── HR Queries ───────────────────────────────────────────────────────────
    ("How do I apply for casual leave in the HRMS portal?",
     "Log in to the HRMS portal at hrms.ramco.com. Go to Leave Management > Apply Leave. Select Leave Type as 'Casual Leave', choose your from and to dates, add a reason, and click Submit. Your manager will receive an approval notification. You can track status under Leave Management > My Leave Requests.",
     "HR Assistant"),

    ("What is the maternity leave policy at Ramco?",
     "As per company policy and the Maternity Benefit Act, eligible female employees are entitled to 26 weeks of paid maternity leave for the first two children. For subsequent children, 12 weeks apply. Additional 6 weeks can be availed for medical complications. Please reach out to HR at hr@ramco.com for the complete policy document.",
     "HR Assistant"),

    ("When is the next performance appraisal cycle?",
     "The annual performance appraisal cycle begins in March every year. Self-appraisals are due by March 15th. Manager reviews are completed by March 31st. Final ratings and increments are communicated by April 30th. Mid-year check-ins happen in September. Keep your goal tracker updated in the HRMS portal.",
     "HR Assistant"),

    ("How do I update my bank account details for salary processing?",
     "To update bank account details: 1) Log into HRMS portal. 2) Go to My Profile > Financial Details > Bank Account. 3) Click Edit and enter your new account number, IFSC code, and bank name. 4) Upload a cancelled cheque as proof. 5) Submit for HR verification. Changes take effect from the next payroll cycle.",
     "HR Assistant"),

    ("I need a salary certificate for a home loan application. How to get it?",
     "You can generate a salary certificate directly from the HRMS portal. Go to My Documents > Generate Certificate > Salary Certificate. Select the purpose (Home Loan) and download the PDF — it will be auto-signed digitally by HR. If you need a physical stamp, raise a request at HR helpdesk with 2 business days notice.",
     "HR Assistant"),

    ("What are the office working hours and flexible work policy?",
     "Standard office hours are 9 AM to 6 PM, Monday to Friday. We follow a flexible work policy — core hours are 10 AM to 4 PM when all team members should be available. Employees can work from home up to 2 days per week subject to manager approval. Night shift and weekend work are compensated as per HR policy.",
     "HR Assistant"),

    ("How do I refer a candidate for an open position?",
     "To submit a referral: 1) Go to careers.ramco.com/referral or the Referrals tab in the HRMS portal. 2) Select the open position. 3) Fill in the candidate's details and upload their CV. 4) The referral bonus (if applicable) is processed 3 months after the candidate joins. You can track referral status in the portal.",
     "HR Assistant"),

    # ── Product/ERP Queries ──────────────────────────────────────────────────
    ("How do I generate a purchase order in Ramco ERP?",
     "To create a Purchase Order: Navigate to Procurement > Purchase Orders > New PO. Fill in the Vendor name (search from vendor master), add line items with material code, quantity, and unit price. Attach supporting documents if needed. Click Submit for approval — the PO workflow will route to the approving authority based on value limits set in your business rules.",
     "Product Expert"),

    ("The invoice matching is failing in accounts payable. 3-way match is not working.",
     "3-way match failures usually occur due to: 1) Price variance between PO and invoice exceeding tolerance (check tolerance setup in AP Config). 2) Quantity mismatch between GRN and invoice. 3) PO line already fully invoiced. Go to AP > Invoice Processing > Match Exceptions to see the specific mismatch. Adjust the GRN or raise a price variance approval as applicable.",
     "Product Expert"),

    ("How do I run the month-end closing process in Ramco Finance?",
     "Month-end close process: 1) Post all pending journal entries before close date. 2) Run depreciation from Fixed Assets > Period End > Calculate Depreciation. 3) Run bank reconciliation from Cash Management. 4) Clear intercompany transactions. 5) Run Trial Balance report to verify. 6) Go to General Ledger > Period Close > Close Period. Ensure all sub-ledgers are reconciled before GL close.",
     "Product Expert"),

    ("Can I configure custom approval workflows in Ramco HCM?",
     "Yes, Ramco HCM supports fully configurable approval workflows. Go to Admin > Workflow Configuration > New Workflow. Define workflow name, applicable transaction type, and conditions. Add approval levels — each level can have single approver, role-based approval, or parallel approval. You can set escalation rules with timeout periods. Contact your system admin if you need help with complex conditional routing.",
     "Product Expert"),

    ("How to set up cost center hierarchy in Ramco ERP?",
     "Cost center hierarchy setup: 1) Go to Finance > Master Data > Cost Centers. 2) Create the parent cost center (e.g., Corporate). 3) Create child cost centers and assign the parent in the 'Reports To' field. 4) Map cost centers to GL accounts in Chart of Accounts. 5) Assign employees and assets to cost centers. Changes reflect in management reports after the next posting.",
     "Product Expert"),

    ("What is the difference between a blanket PO and a standard PO in Ramco?",
     "A Standard PO is for a one-time purchase with defined quantities and delivery dates. A Blanket PO (also called a Frame Order) covers multiple deliveries over a period — you set a total value or quantity limit and release individual delivery orders against it. Blanket POs are useful for recurring purchases like office supplies or maintenance services where you negotiate a fixed price for the year.",
     "Product Expert"),

    ("How do I import employee data in bulk into Ramco HCM?",
     "For bulk employee import: 1) Go to HCM > Data Import > Employee Master Import. 2) Download the Excel template provided — fill in mandatory fields (Employee ID, Name, DOJ, Department, Designation, Grade). 3) Validate the file using the built-in validator — it highlights errors. 4) Upload the validated file. 5) Review the preview and confirm import. Errors are logged in Import History for correction.",
     "Product Expert"),

    # ── Project Management ───────────────────────────────────────────────────
    ("How do I create a project milestone in Ramco Projects?",
     "To create a milestone: Open your project in Ramco Projects > Work Breakdown Structure. Right-click any task and select 'Add Milestone'. Enter milestone name, target date, and responsible person. Milestones appear as diamond shapes on the Gantt chart. You can link milestones to deliverables and set automated alerts for upcoming milestone dates in Project Settings.",
     "HelpDesk Bot"),

    ("Can I track billable hours against a project in Ramco?",
     "Yes. In Ramco Projects, go to Time & Expense > Timesheet. Select the project and task, enter hours worked, and mark as Billable if applicable. Billable hours feed into project cost reports and can be invoiced directly through the AR module. Your project manager can view team utilization in the Resource Management dashboard.",
     "HelpDesk Bot"),

    ("How do I set up a Teams channel for a new project?",
     "To create a Teams channel: 1) Open Microsoft Teams. 2) Go to your team (e.g., Project Teams). 3) Click '...' next to the team name > Add channel. 4) Name it after your project and add a description. 5) Set privacy to Standard (team-visible) or Private (invite-only). 6) Pin relevant apps like Planner, SharePoint, or Ramco Project links as tabs in the channel.",
     "HelpDesk Bot"),

    # ── General / Access ─────────────────────────────────────────────────────
    ("How do I request access to a new software or tool?",
     "Submit a software access request through the IT portal at intranet.ramco.com > IT Requests > Software Access. Select the software from the catalog or add a new one. Provide business justification and your manager's name for approval. Once manager approves, IT provisions access within 2 business days. For licensed software, procurement approval may also be required.",
     "IT Support"),

    ("What is the process for onboarding a new team member?",
     "New joiner onboarding: 1) HR sends welcome email with first-day instructions 5 days before joining. 2) IT pre-provisions laptop, email ID, and system access based on the role profile submitted by the hiring manager. 3) Employee joins the company orientation on Day 1. 4) Manager assigns a buddy for the first 30 days. 5) Access to role-specific systems is granted based on the access matrix within 3 days.",
     "HR Assistant"),

    ("How can I check my leave balance?",
     "Log in to HRMS portal at hrms.ramco.com. Go to Leave Management > Leave Balance. You'll see a summary of all leave types — Casual Leave, Sick Leave, Earned Leave, and Compensatory Off — with used, available, and lapsed balances. Leave balances are updated real-time after approvals.",
     "HR Assistant"),

    ("I accidentally deleted a file from SharePoint. Can it be recovered?",
     "Yes! SharePoint keeps deleted files in the Recycle Bin for 93 days. Go to the SharePoint site where the file was deleted > click Recycle Bin in the left sidebar > find your file > select it and click Restore. If it's not there, check the Second-Stage Recycle Bin (site admin access needed). Contact IT if it's been more than 93 days.",
     "IT Support"),

    ("How do I schedule a recurring meeting in Microsoft Teams?",
     "To schedule a recurring meeting: 1) Open Teams Calendar. 2) Click New Meeting. 3) Set title, attendees, and date/time. 4) Under the date, click the repeat option and choose Daily, Weekly, Monthly, or Custom. 5) Set the end date or number of occurrences. 6) Add agenda in the description. 7) Click Send. All attendees get a calendar invite with Teams link.",
     "HelpDesk Bot"),

    ("What is the IT asset policy — can I take my office laptop home?",
     "Yes, employees can take assigned laptops home as per the IT Asset Policy. You are responsible for the safety of the device. Do not install personal software or disable antivirus. In case of loss or theft, report immediately to IT and your manager within 2 hours. For travelling abroad with office assets, obtain prior approval from your department head and IT security.",
     "IT Support"),

    ("How do I raise a reimbursement claim for travel expenses?",
     "To submit a travel reimbursement: 1) Log into HRMS > Expense Management > New Claim. 2) Select Trip type (Domestic/International). 3) Add expense line items with category, amount, and upload receipts. 4) Submit for manager approval. 5) Finance processes approved claims in the next payroll cycle or within 7 working days. Keep all original receipts for 6 months.",
     "HR Assistant"),

    ("What are the different modules in Ramco ERP?",
     "Ramco ERP covers the following core modules: Finance & Accounting (GL, AP, AR, Fixed Assets, Cash Management), Human Capital Management (Payroll, Leave, Recruitment, Performance), Supply Chain (Procurement, Inventory, Warehouse Management), Manufacturing (Production Planning, Shop Floor, Quality), Projects (Project Costing, Resource Management, Billing), and Analytics (dashboards, reports, MIS). All modules are integrated on a single platform.",
     "Product Expert"),

    ("How do I configure payroll for a new pay grade in Ramco HCM?",
     "To set up a new pay grade: 1) Go to HCM > Payroll Setup > Pay Grade Master. 2) Create a new grade with min, mid, and max salary bands. 3) Define pay components (Basic, HRA, Special Allowance, PF) as percentage or fixed amounts. 4) Assign the grade to employee designations in the Grade Matrix. 5) Run payroll simulation to verify the computation before going live.",
     "Product Expert"),

    ("My payslip shows wrong PF deduction this month. Who do I contact?",
     "For payslip discrepancies, first download your payslip from HRMS > Payroll > Payslips and check the PF computation (12% of Basic for employee, 12% for employer contribution). If it looks incorrect, raise a ticket in HRMS > HR Helpdesk > Payroll Query with the specific discrepancy details. Payroll team will review and correct in the next cycle or issue a supplementary payment.",
     "HR Assistant"),
]

# ── Product knowledge entries ─────────────────────────────────────────────────

PRODUCT_KNOWLEDGE = [
    {
        "topic": "ERP > Finance > General Ledger",
        "content": "Ramco ERP's General Ledger module supports multi-currency, multi-company, and multi-period accounting. It provides a unified chart of accounts with segment-based reporting. Period-end close is controlled through the Period Close Wizard which ensures all sub-ledgers (AP, AR, Fixed Assets) are reconciled before GL is closed. Audit trails are maintained for every journal entry with user stamps and timestamps. GL supports both IFRS and local GAAP standards.",
    },
    {
        "topic": "ERP > Finance > Accounts Payable",
        "content": "The Accounts Payable module handles vendor invoice processing, 3-way matching (PO-GRN-Invoice), payment runs, and vendor aging analysis. Invoice matching tolerances can be configured per vendor or globally. Automatic payment runs can be scheduled with bank-specific payment formats (NEFT, RTGS, SWIFT). Vendor statements can be auto-reconciled through the vendor portal. PO-based invoices and non-PO invoices are handled through separate workflows.",
    },
    {
        "topic": "ERP > HCM > Payroll",
        "content": "Ramco HCM Payroll supports India-specific statutory compliance including PF, ESI, PT, TDS, LWF. Payroll is processed in three steps: Pre-payroll validation (attendance, leave, loan deductions), Gross salary computation (pay components per grade), and Net salary computation (statutory deductions + recovery). Payslips are generated as PDFs and accessible from the employee self-service portal. Bank transfer files are generated in standard formats.",
    },
    {
        "topic": "ERP > HCM > Leave Management",
        "content": "Leave types supported: Casual Leave (12/year), Sick Leave (12/year), Earned Leave (accrual-based), Compensatory Off, Maternity/Paternity Leave, and Special Leave. Leave encashment is processed at year-end for earned leave balance exceeding the carry-forward limit. Leave approval is routed to the immediate manager with delegation rules for manager unavailability. Half-day leave is supported. Leave calendar shows team availability to avoid scheduling conflicts.",
    },
    {
        "topic": "IT Policy > VPN Access",
        "content": "All employees working from home must connect to the corporate network via Cisco AnyConnect VPN. VPN access is provisioned automatically for all permanent employees. Contractors require a separate access request approved by their engagement manager. VPN credentials are tied to your office email password and reset every 90 days. Split-tunneling is disabled — all traffic routes through the corporate firewall when VPN is active. VPN logs are maintained for 6 months for security audit purposes.",
    },
    {
        "topic": "IT Policy > Data Security",
        "content": "Ramco follows ISO 27001 information security standards. Employees must not store customer or business-critical data on personal devices or unauthorized cloud services. USB data transfer is disabled on office laptops by default — approved exceptions require IT Manager sign-off. Emails with sensitive data must be encrypted using built-in Microsoft Purview encryption. Annual security awareness training is mandatory for all employees and tracked in the LMS.",
    },
    {
        "topic": "IT Policy > Software Licensing",
        "content": "All software installed on office assets must be licensed. Employees must not install unlicensed software or crack/bypass license validation. The approved software catalog is available on the IT portal. To request software not in the catalog, submit a business justification. IT will evaluate licensing cost and security implications before approval. Open-source software must be cleared for license compatibility (GPL, MIT, Apache) before use in company products.",
    },
    {
        "topic": "HR Policy > Remote Work",
        "content": "Ramco's hybrid work policy allows up to 2 work-from-home days per week for permanent employees who have completed their probation period. WFH requires prior approval from the reporting manager. Employees on WFH must be available on Microsoft Teams during core hours (10 AM – 4 PM). Client-facing roles may have restricted WFH eligibility. WFH is not permitted during probation period (first 6 months). Extended WFH (more than 2 days/week) requires VP-level approval.",
    },
    {
        "topic": "HR Policy > Performance Management",
        "content": "Ramco follows a continuous performance management approach. Employees set 5-7 SMART goals at the start of the year in the HRMS portal. Mid-year check-in in September allows course correction. Annual appraisal in March covers goal achievement (70% weightage) and behavioural competencies (30% weightage). Ratings are on a 5-point scale: Outstanding (5), Exceeds Expectations (4), Meets Expectations (3), Partially Meets (2), Does Not Meet (1). Bell curve normalization is applied at department level.",
    },
    {
        "topic": "HR Policy > Travel and Expense",
        "content": "Domestic travel: economy class flights booked minimum 5 days in advance through the travel desk. Hotel accommodation is capped at INR 4000/night for tier-2 cities and INR 6000/night for metros. Daily allowance (per diem) is INR 750 for domestic travel. International travel requires VP approval and must be booked through the approved travel agency. All expenses above INR 500 require receipts. Claims must be submitted within 30 days of travel.",
    },
    {
        "topic": "ERP > Projects > Resource Management",
        "content": "Ramco Projects module provides resource planning, utilization tracking, and allocation management. Resource managers can view team skill matrices and allocate resources to projects based on availability and skill match. Utilization targets are typically 75-80% billable for consulting roles. Bench resources are flagged automatically when allocation drops below 50% for more than 2 weeks. Time captured in timesheets feeds into project cost and billing.",
    },
    {
        "topic": "ERP > Supply Chain > Procurement",
        "content": "The procurement lifecycle in Ramco ERP: Purchase Requisition (raised by department) → Approval Workflow → RFQ to vendors → Quotation Comparison → PO Generation → Vendor Acknowledgement → Goods Receipt Note (GRN) → Invoice Matching → Payment. Vendor master management includes vendor rating based on delivery performance and quality. Blanket orders can be set up for recurring purchases. Procurement analytics tracks spend by category, vendor, and department.",
    },
    {
        "topic": "Microsoft Teams > Channels and Collaboration",
        "content": "Microsoft Teams channels are used for project and team communication. Standard channels are visible to all team members. Private channels restrict access to invited members only. Shared channels allow external collaborators without guest access. Best practices: use @mentions sparingly, pin important documents as tabs, use threaded replies to keep discussions organized. Channel naming convention at Ramco: [Department]-[Project/Topic] e.g. Finance-MonthEnd, IT-Helpdesk.",
    },
    {
        "topic": "Microsoft 365 > SharePoint",
        "content": "SharePoint is the official document management and collaboration platform at Ramco. Each department has a SharePoint site. Document versioning is enabled — previous versions are retained for 1 year. Access to SharePoint sites is managed through Microsoft 365 groups. Sensitive documents (HR, Finance) are protected with sensitivity labels that prevent sharing outside the organization. The Recycle Bin retains deleted files for 93 days.",
    },
    {
        "topic": "Onboarding > New Joiner Checklist",
        "content": "New joiner setup checklist (IT): 1) Office laptop provisioned and delivered D-1. 2) Email ID created in format firstname.lastname@ramco.com. 3) Microsoft 365 license assigned (E3). 4) VPN access provisioned. 5) Added to relevant Teams channels (department + project). 6) Role-based application access granted within D+3. 7) Security awareness training assigned in LMS. 8) IT orientation scheduled for D+1. Buddy assigned by manager on Day 1.",
    },
]

# ── User preferences ──────────────────────────────────────────────────────────

USER_PREFERENCES_POOL = [
    {"preferred_language": "English", "response_format": "step-by-step", "tone": "formal",     "detail_level": "detailed"},
    {"preferred_language": "English", "response_format": "concise",       "tone": "friendly",   "detail_level": "brief"},
    {"preferred_language": "English", "response_format": "bullet-points", "tone": "formal",     "detail_level": "detailed"},
    {"preferred_language": "English", "response_format": "step-by-step",  "tone": "friendly",   "detail_level": "moderate"},
    {"preferred_language": "English", "response_format": "concise",       "tone": "formal",     "detail_level": "brief"},
]

# ── Generators ────────────────────────────────────────────────────────────────

def generate_chat_history() -> list[dict]:
    records = []
    sources = [
        "chat_personal_ab12",
        "chat_personal_cd34",
        "channel_IT-Helpdesk",
        "channel_HR-Support",
        "channel_ERP-Users",
        "channel_General",
    ]
    for i, (query, reply, agent) in enumerate(CHAT_QA_PAIRS):
        sender = random.choice(USERS)
        records.append({
            "user_query":  query,
            "agent_reply": reply,
            "sender":      sender,
            "responder":   agent,
            "timestamp":   rand_ts(),
            "source":      random.choice(sources),
            "turn_id":     i + 1,
        })
    # Add some follow-up turns for richer history
    followups = [
        ("Thanks, that worked!",           "Glad to help! Let me know if you have any other questions.", "IT Support"),
        ("Where do I find the IT portal?",  "The IT portal is at intranet.ramco.com — accessible only on the corporate network or VPN.", "IT Support"),
        ("Can I do this on mobile too?",    "Yes, the HRMS portal is mobile-responsive. You can also download the Ramco HCM app from the Play Store or App Store.", "HR Assistant"),
        ("How long will this take?",        "Typically 2-4 business hours for standard requests. You'll receive an email notification once it's done.", "HelpDesk Bot"),
        ("Is this mandatory?",              "Yes, this is mandatory for all permanent employees as per company policy. Contractors follow the same process.", "HR Assistant"),
        ("Who do I escalate to if not resolved?", "If your ticket is not resolved within the SLA, you can escalate to the IT Manager at it-manager@ramco.com or use the Escalate button in the portal.", "IT Support"),
        ("Can my manager see this request?", "Your manager receives a notification only if their approval is required. Otherwise, it's handled directly by the respective team.", "HR Assistant"),
        ("What if I'm travelling when this is due?", "You can complete this remotely via the portal or mobile app. If you need an extension, inform your manager and raise a request in the portal.", "HelpDesk Bot"),
    ]
    for query, reply, agent in followups:
        records.append({
            "user_query":  query,
            "agent_reply": reply,
            "sender":      random.choice(USERS),
            "responder":   agent,
            "timestamp":   rand_ts(),
            "source":      "channel_General",
            "turn_id":     len(records) + 1,
        })
    return records


def generate_product_knowledge() -> list[dict]:
    records = []
    for entry in PRODUCT_KNOWLEDGE:
        records.append({
            "topic":     entry["topic"],
            "content":   entry["content"],
            "author":    random.choice(AGENTS),
            "timestamp": rand_ts(180),
            "source":    "teams_channel_knowledge",
        })
    return records


def generate_user_preferences() -> list[dict]:
    records = []
    for user in USERS:
        prefs = random.choice(USER_PREFERENCES_POOL)
        records.append({
            "user_id":     user.lower().replace(" ", "_"),
            "display_name": user,
            "preferences": prefs,
            "last_updated": rand_ts(30),
        })
    return records


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("VIZUARA MOCK DATA GENERATOR")
    print("=" * 55)

    chat_records  = generate_chat_history()
    know_records  = generate_product_knowledge()
    pref_records  = generate_user_preferences()

    save_jsonl(OUTPUT_DIR / "chat_history.jsonl",       chat_records)
    save_jsonl(OUTPUT_DIR / "product_knowledge.jsonl",  know_records)
    save_jsonl(OUTPUT_DIR / "user_preferences.jsonl",   pref_records)

    print("\nSample chat Q&A:")
    print(f"  Q: {chat_records[0]['user_query'][:70]}...")
    print(f"  A: {chat_records[0]['agent_reply'][:70]}...")

    print("\nSample knowledge entry:")
    print(f"  Topic: {know_records[0]['topic']}")
    print(f"  Content: {know_records[0]['content'][:80]}...")

    print(f"\nData generation complete.")
    print(f"  {len(chat_records)} chat Q&A pairs")
    print(f"  {len(know_records)} knowledge entries")
    print(f"  {len(pref_records)} user preference profiles")
    print("\nNext: python wiki/llm_wiki.py")



if __name__ == "__main__":
    main()
