"""
Test Microsoft Graph API connection before running the full scraper.
Run this first: python platform/test_connection.py
"""

import os
import sys
from pathlib import Path

# Allow running from project root or platform/ folder
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

import msal
import requests

CLIENT_ID     = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
TENANT_ID     = os.getenv("AZURE_TENANT_ID")
TARGET_USER   = os.getenv("TARGET_USER_EMAIL")
GRAPH_BASE    = "https://graph.microsoft.com/v1.0"


def check(label: str, ok: bool, detail: str = ""):
    status = "[OK]" if ok else "[FAIL]"
    print(f"  {status} {label}" + (f": {detail}" if detail else ""))
    return ok


def get_token_app() -> str | None:
    """Client credentials flow (requires admin consent)."""
    try:
        app = msal.ConfidentialClientApplication(
            CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{TENANT_ID}",
            client_credential=CLIENT_SECRET,
        )
        result = app.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )
        if "access_token" in result:
            return result["access_token"]
        print(f"    Error: {result.get('error_description', result.get('error'))}")
        return None
    except Exception as e:
        print(f"    Exception: {e}")
        return None


def get_token_delegated() -> str | None:
    """Interactive browser login (fallback if no admin consent)."""
    try:
        app = msal.PublicClientApplication(
            CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        )
        scopes = [
            "https://graph.microsoft.com/Chat.Read",
            "https://graph.microsoft.com/Team.ReadBasic.All",
            "https://graph.microsoft.com/User.Read",
        ]
        result = app.acquire_token_interactive(scopes=scopes)
        if "access_token" in result:
            return result["access_token"]
        return None
    except Exception as e:
        print(f"    Exception: {e}")
        return None


def graph_get(token: str, url: str) -> dict | None:
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as e:
        print(f"    HTTP {e.response.status_code}: {e.response.text[:200]}")
        return None
    except Exception as e:
        print(f"    Error: {e}")
        return None


def run_tests():
    print("=" * 55)
    print("MICROSOFT GRAPH API — CONNECTION TEST")
    print("=" * 55)
    all_ok = True

    # ── Check .env variables ─────────────────────────────────
    print("\n[1] Checking .env configuration...")
    all_ok &= check("AZURE_CLIENT_ID set",     bool(CLIENT_ID))
    all_ok &= check("AZURE_CLIENT_SECRET set", bool(CLIENT_SECRET))
    all_ok &= check("AZURE_TENANT_ID set",     bool(TENANT_ID))
    all_ok &= check("TARGET_USER_EMAIL set",   bool(TARGET_USER))

    if not all([CLIENT_ID, CLIENT_SECRET, TENANT_ID]):
        print("\n  Please fill in your .env file first.")
        print("  Copy .env.example to .env and add your Azure credentials.")
        print("  See AZURE_SETUP.md for step-by-step instructions.")
        return

    # ── Try app-level token (preferred) ──────────────────────
    print("\n[2] Acquiring access token (app credentials)...")
    token = get_token_app()

    if not token:
        print("\n  App-level token failed. Trying delegated (browser login)...")
        token = get_token_delegated()
        if token:
            check("Token acquired (delegated flow)", True)
        else:
            check("Token acquired", False, "Both flows failed")
            print("\n  See AZURE_SETUP.md — you may need admin consent.")
            return
    else:
        check("Token acquired (app credentials)", True)

    # ── Check user access ─────────────────────────────────────
    print("\n[3] Checking user access...")
    user_data = graph_get(token, f"{GRAPH_BASE}/users/{TARGET_USER}")
    if user_data and "id" in user_data:
        name = user_data.get("displayName", "N/A")
        uid  = user_data.get("id", "")
        all_ok &= check("User found", True, f"{name}  (id: {uid[:8]}...)")
    else:
        all_ok &= check("User found", False, "Check User.Read.All permission")

    # ── Check Teams access ────────────────────────────────────
    print("\n[4] Checking Teams access...")
    if user_data and "id" in user_data:
        uid = user_data["id"]
        teams_data = graph_get(token, f"{GRAPH_BASE}/users/{uid}/joinedTeams")
        if teams_data and "value" in teams_data:
            count = len(teams_data["value"])
            all_ok &= check("Teams access", True, f"{count} teams found")
            for t in teams_data["value"][:3]:
                print(f"      - {t.get('displayName', 'unnamed')}")
        else:
            all_ok &= check("Teams access", False, "Check Team.ReadBasic.All permission")

    # ── Check Chat access ─────────────────────────────────────
    print("\n[5] Checking Chat access...")
    if user_data and "id" in user_data:
        uid = user_data["id"]
        chats_data = graph_get(token, f"{GRAPH_BASE}/users/{uid}/chats?$top=5")
        if chats_data and "value" in chats_data:
            count = len(chats_data["value"])
            all_ok &= check("Chat access", True, f"{count} chats found (showing first 5)")
        else:
            all_ok &= check("Chat access", False, "Check Chat.Read.All permission")

    # ── Summary ───────────────────────────────────────────────
    print("\n" + "=" * 55)
    if all_ok:
        print("ALL CHECKS PASSED — Ready to run the scraper!")
        print("\nNext step:")
        print("  python platform/teams_scraper.py")
    else:
        print("SOME CHECKS FAILED — Fix the issues above before scraping.")
        print("\nSee AZURE_SETUP.md for permission setup instructions.")
    print("=" * 55)


if __name__ == "__main__":
    run_tests()
