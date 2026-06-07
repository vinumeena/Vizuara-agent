"""
Microsoft Teams scraper using Microsoft Graph API.
Collects chat history, channel messages, and builds structured datasets.

Auth flow: Client Credentials (app-level) — requires admin consent in Azure portal.
"""

import os
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import msal
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID     = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
TENANT_ID     = os.getenv("AZURE_TENANT_ID")
SCOPE         = [os.getenv("GRAPH_SCOPE", "https://graph.microsoft.com/.default")]
TARGET_USER   = os.getenv("TARGET_USER_EMAIL")

GRAPH_BASE    = "https://graph.microsoft.com/v1.0"

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


# ── Auth ──────────────────────────────────────────────────────────────────────

def get_access_token() -> str:
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET,
    )
    result = app.acquire_token_for_client(scopes=SCOPE)
    if "access_token" not in result:
        raise RuntimeError(
            f"Token acquisition failed: {result.get('error_description', result)}"
        )
    return result["access_token"]


def graph_get(token: str, url: str, params: dict = None) -> dict:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ── User lookup ───────────────────────────────────────────────────────────────

def get_user_id(token: str, email: str) -> str:
    data = graph_get(token, f"{GRAPH_BASE}/users/{email}")
    return data["id"]


# ── Chat history (1-on-1 and group chats) ────────────────────────────────────

def list_chats(token: str, user_id: str) -> list[dict]:
    url = f"{GRAPH_BASE}/users/{user_id}/chats"
    params = {"$top": 50, "$expand": "members"}
    chats = []
    while url:
        data = graph_get(token, url, params)
        chats.extend(data.get("value", []))
        url = data.get("@odata.nextLink")
        params = None  # nextLink already contains params
    return chats


def get_chat_messages(token: str, user_id: str, chat_id: str, max_messages: int = 100) -> list[dict]:
    url = f"{GRAPH_BASE}/users/{user_id}/chats/{chat_id}/messages"
    params = {"$top": 50}
    messages = []
    while url and len(messages) < max_messages:
        data = graph_get(token, url, params)
        messages.extend(data.get("value", []))
        url = data.get("@odata.nextLink")
        params = None
    return messages[:max_messages]


# ── Teams channel messages ────────────────────────────────────────────────────

def list_joined_teams(token: str, user_id: str) -> list[dict]:
    url = f"{GRAPH_BASE}/users/{user_id}/joinedTeams"
    data = graph_get(token, url)
    return data.get("value", [])


def list_channels(token: str, team_id: str) -> list[dict]:
    url = f"{GRAPH_BASE}/teams/{team_id}/channels"
    data = graph_get(token, url)
    return data.get("value", [])


def get_channel_messages(token: str, team_id: str, channel_id: str, max_messages: int = 200) -> list[dict]:
    url = f"{GRAPH_BASE}/teams/{team_id}/channels/{channel_id}/messages"
    params = {"$top": 50}
    messages = []
    while url and len(messages) < max_messages:
        try:
            data = graph_get(token, url, params)
            messages.extend(data.get("value", []))
            url = data.get("@odata.nextLink")
            params = None
        except requests.HTTPError as e:
            # Some channels require special permissions — skip gracefully
            print(f"  [skip] channel {channel_id}: {e}")
            break
    return messages[:max_messages]


# ── Structuring raw data ──────────────────────────────────────────────────────

def clean_body(body: dict) -> str:
    content = body.get("content", "") or ""
    # Strip HTML tags for cleaner text
    import re
    content = re.sub(r"<[^>]+>", " ", content)
    content = re.sub(r"\s+", " ", content).strip()
    return content


def structure_chat_history(raw_messages: list[dict], context_label: str) -> list[dict]:
    """
    Pairs consecutive user messages into (query, reply) turns.
    Returns list of structured records for chat_history.jsonl.
    """
    records = []
    msgs = [
        {
            "sender": m.get("from", {}).get("user", {}).get("displayName", "Unknown"),
            "body": clean_body(m.get("body", {})),
            "ts": m.get("createdDateTime", ""),
        }
        for m in raw_messages
        if clean_body(m.get("body", {}))  # skip empty messages
    ]

    # Build (user_query, agent_reply) pairs from consecutive messages
    for i in range(len(msgs) - 1):
        curr = msgs[i]
        nxt  = msgs[i + 1]
        if curr["sender"] != nxt["sender"]:  # different people = Q&A pair
            records.append({
                "user_query": curr["body"],
                "agent_reply": nxt["body"],
                "sender":      curr["sender"],
                "responder":   nxt["sender"],
                "timestamp":   curr["ts"],
                "source":      context_label,
            })
    return records


def structure_product_knowledge(raw_messages: list[dict], context_label: str) -> list[dict]:
    """
    Extracts substantive messages (length > 80 chars) as product knowledge entries.
    """
    records = []
    for m in raw_messages:
        body = clean_body(m.get("body", {}))
        if len(body) > 80:
            records.append({
                "topic":   context_label,
                "content": body,
                "author":  m.get("from", {}).get("user", {}).get("displayName", "Unknown"),
                "timestamp": m.get("createdDateTime", ""),
                "source":  "teams_channel",
            })
    return records


# ── Save helpers ──────────────────────────────────────────────────────────────

def append_jsonl(filepath: Path, records: list[dict]):
    with open(filepath, "a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  Saved {len(records)} records → {filepath.name}")


# ── Main scraper ──────────────────────────────────────────────────────────────

def run_scraper():
    print("=" * 60)
    print("VIZUARA TEAMS SCRAPER — Step 1")
    print("=" * 60)

    if not all([CLIENT_ID, CLIENT_SECRET, TENANT_ID]):
        print("\n[ERROR] Missing Azure credentials in .env file.")
        print("Please complete AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID")
        print("See AZURE_SETUP.md for registration steps.\n")
        return

    print("\n[1/4] Authenticating with Microsoft Graph API...")
    token = get_access_token()
    print("  Token acquired successfully.")

    print(f"\n[2/4] Looking up user: {TARGET_USER}")
    user_id = get_user_id(token, TARGET_USER)
    print(f"  User ID: {user_id}")

    chat_history_path = DATA_DIR / "chat_history.jsonl"
    product_knowledge_path = DATA_DIR / "product_knowledge.jsonl"

    # Clear old data
    chat_history_path.write_text("")
    product_knowledge_path.write_text("")

    # ── Scrape 1-on-1 / group chats ──────────────────────────────────────────
    print("\n[3/4] Scraping chat messages...")
    chats = list_chats(token, user_id)
    print(f"  Found {len(chats)} chats")

    total_chat_records = 0
    for chat in chats[:20]:  # limit to 20 chats for demo
        chat_id = chat["id"]
        chat_type = chat.get("chatType", "unknown")
        label = f"chat_{chat_type}_{chat_id[:8]}"

        try:
            raw_msgs = get_chat_messages(token, user_id, chat_id, max_messages=100)
            records = structure_chat_history(raw_msgs, label)
            if records:
                append_jsonl(chat_history_path, records)
                total_chat_records += len(records)
            time.sleep(0.3)  # rate limit safety
        except Exception as e:
            print(f"  [skip] chat {chat_id[:8]}: {e}")

    print(f"  Total chat Q&A pairs collected: {total_chat_records}")

    # ── Scrape Teams channels ─────────────────────────────────────────────────
    print("\n[4/4] Scraping Teams channel messages...")
    teams = list_joined_teams(token, user_id)
    print(f"  Joined teams: {len(teams)}")

    total_knowledge_records = 0
    for team in teams:
        team_id   = team["id"]
        team_name = team.get("displayName", "Unknown Team")
        print(f"\n  Team: {team_name}")

        channels = list_channels(token, team_id)
        for channel in channels[:5]:  # top 5 channels per team
            ch_id   = channel["id"]
            ch_name = channel.get("displayName", "channel")
            label   = f"{team_name} > {ch_name}"
            print(f"    Channel: {ch_name}")

            raw_msgs = get_channel_messages(token, team_id, ch_id, max_messages=200)
            records  = structure_product_knowledge(raw_msgs, label)
            if records:
                append_jsonl(product_knowledge_path, records)
                total_knowledge_records += len(records)

            time.sleep(0.3)

    print(f"\n  Total knowledge entries collected: {total_knowledge_records}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("SCRAPING COMPLETE")
    print("=" * 60)
    print(f"  Chat history pairs : {total_chat_records}")
    print(f"  Knowledge entries  : {total_knowledge_records}")
    print(f"\n  Files written:")
    print(f"    {chat_history_path}")
    print(f"    {product_knowledge_path}")
    print("\nNext: Run Step 2 — python wiki/llm_wiki.py")


if __name__ == "__main__":
    run_scraper()
