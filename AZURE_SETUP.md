# Azure App Registration — Step-by-Step

You need to register an app in Azure to get API access to Microsoft Teams.

---

## Step 1: Register the App

1. Go to: https://portal.azure.com
2. Search for **"Azure Active Directory"** → click it
3. Left menu → **"App registrations"** → click **"New registration"**
4. Fill in:
   - Name: `vizuara-agent`
   - Supported account types: **"Accounts in this organizational directory only"**
   - Redirect URI: leave blank
5. Click **"Register"**
6. **COPY** the following (you'll need them for .env):
   - **Application (client) ID** → this is `AZURE_CLIENT_ID`
   - **Directory (tenant) ID** → this is `AZURE_TENANT_ID`

---

## Step 2: Create a Client Secret

1. Left menu → **"Certificates & secrets"**
2. Click **"New client secret"**
3. Description: `vizuara-secret`
4. Expires: 24 months
5. Click **"Add"**
6. **COPY the Value immediately** (it won't show again) → this is `AZURE_CLIENT_SECRET`

---

## Step 3: Add API Permissions

1. Left menu → **"API permissions"**
2. Click **"Add a permission"** → **"Microsoft Graph"** → **"Application permissions"**
3. Search and add these permissions:

   | Permission | Purpose |
   |---|---|
   | `Chat.Read.All` | Read all Teams chat messages |
   | `Chat.ReadBasic.All` | List all chats |
   | `ChannelMessage.Read.All` | Read channel messages |
   | `Team.ReadBasic.All` | List joined teams |
   | `User.Read.All` | Look up user by email |

4. Click **"Grant admin consent for [your org]"** → Confirm
   - This requires a Global Admin or Teams Admin to approve
   - If you are not an admin, ask your IT department to grant consent

---

## Step 4: Create the .env File

Copy `.env.example` to `.env` and fill in your values:

```
AZURE_CLIENT_ID=paste-your-client-id-here
AZURE_CLIENT_SECRET=paste-your-client-secret-here
AZURE_TENANT_ID=paste-your-tenant-id-here
GRAPH_SCOPE=https://graph.microsoft.com/.default
ANTHROPIC_API_KEY=paste-your-anthropic-key-here
TARGET_USER_EMAIL=your-email@example.com
```

---

## Step 5: Test the Connection

```bash
python platform/test_connection.py
```

Expected output:
```
[OK] Token acquired
[OK] User found: Vinoodhini D  (id: xxxx-xxxx)
[OK] Teams access: 3 teams found
[OK] Chat access: 12 chats found
All checks passed. Ready to scrape!
```

---

## If You Cannot Get Admin Consent

Use **Delegated permissions** instead of Application permissions.
This requires you to sign in interactively (browser popup).

Change the scraper auth to use:
```python
app = msal.PublicClientApplication(CLIENT_ID, authority=...)
result = app.acquire_token_interactive(scopes=["https://graph.microsoft.com/Chat.Read"])
```

The test_connection.py script supports both modes.
