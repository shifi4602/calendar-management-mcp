# 📅 Calendar Management MCP Server

A **Model Context Protocol (MCP)** server that connects AI assistants to your **Microsoft 365 Calendar** via the Microsoft Graph API. Supports reading, creating, updating, deleting, and searching calendar events — all through natural language.

---

## 📁 Project Structure

```
calendar-management-mcp/
├── main.py                          # MCP server entry point — all 10 tools registered here
├── config.py                        # Environment variables & constants
├── requirements.txt                 # Python dependencies
├── .env.example                     # Template for your credentials
├── token_cache.json                 # 🔐 Auto-generated on first login (do NOT commit)
│
├── models/
│   ├── event_model.py               # Event data class + to_dict() for Graph API
│   ├── calendar_event_model.py      # CalendarEvent model with from_api_data() parser
│   └── time_slot_model.py           # TimeSlot model for available-slot results
│
├── services/
│   ├── auth_service.py              # MSAL Device Code authentication + token cache
│   └── calendar_service.py          # All Microsoft Graph API calls
│
└── tests/
    ├── test_main.py                 # Tests for all 10 MCP tool functions
    ├── test_calendar_service.py     # Unit tests for service logic + HTTP mocks
    └── event_model.py               # Unit tests for the Event model
```

---

## ⚙️ Prerequisites

| Requirement | Details |
|---|---|
| 🐍 Python | 3.10 or higher |
| ☁️ Azure App Registration | Free at [portal.azure.com](https://portal.azure.com) |
| 📋 Graph API Permission | `Calendars.ReadWrite` (Delegated) |

---

## 🚀 Setup & Installation

### 1️⃣ Clone / open the project

```bash
cd calendar-management-mcp
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Configure your Azure App

1. Go to [Azure Portal](https://portal.azure.com) → **Azure Active Directory** → **App registrations** → **New registration**
2. Name your app, choose **"Accounts in any organizational directory or personal Microsoft accounts"**
3. Under **API permissions** → **Add a permission** → **Microsoft Graph** → **Delegated** → add `Calendars.ReadWrite`
4. Copy your **Client ID**, **Tenant ID**, and create a **Client Secret**

### 4️⃣ Create your `.env` file

```bash
cp .env.example .env
```

Fill in your values:

```env
MICROSOFT_CLIENT_ID=your_client_id_here
MICROSOFT_CLIENT_SECRET=your_client_secret_here
MICROSOFT_TENANT_ID=your_tenant_id_here
```

### 5️⃣ Run the server

```bash
python main.py
```

🔐 **First run:** You'll see a message like:

```
To sign in, use a web browser to open the page https://microsoft.com/devicelogin
and enter the code XXXXXXXX to authenticate.
```

Open the link, enter the code, and log in with your Microsoft account. Your token is cached in `token_cache.json` — subsequent runs log in silently.

> ⚠️ **Never commit** `token_cache.json` or `.env` to version control.

---

## 🛠️ MCP Tools

### 📖 Read Tools

| Tool | Description | Parameters |
|---|---|---|
| `readWorkweekTasks` | Get all events for the workweek containing the given date | `start_date: datetime` |
| `listTodayEvents` | Get all events scheduled for today | *(none)* |
| `getEvent` | Get full details of a single event by its ID | `event_id: str` |
| `searchEvents` | Search events whose subject contains a keyword | `keyword: str` |
| `findAvailableSlot` | Find free time slots of a given duration over the next 7 days | `required_duration: int` (minutes), `start_date: datetime` |

### ✏️ Write Tools

| Tool | Description | Parameters |
|---|---|---|
| `createMeet` | Create a new calendar event | `subject`, `start`, `end`, `location`, `organizer` |
| `updateMeet` | Update an existing event | `event_id`, `subject`, `start`, `end`, `location` |
| `deleteMeet` | Delete an event permanently | `event_id: str` |
| `addAttendees` | Add attendees to an existing event (merges, never removes) | `event_id: str`, `attendees: List[str]` (emails) |
| `acceptDeclineEvent` | Respond to a calendar invite | `event_id: str`, `response: "accept" \| "decline" \| "tentative"` |

---

## 🧩 Architecture

```
AI Assistant (Claude, Copilot, etc.)
        │
        │  MCP Protocol
        ▼
    main.py  ←── FastMCP server (10 registered tools)
        │
        ▼
services/calendar_service.py  ←── Business logic + Microsoft Graph API calls
        │
        ├── services/auth_service.py  ←── MSAL Device Code token management
        │
        └── models/
                ├── event_model.py         ←── Event ↔ Graph API dict conversion
                ├── calendar_event_model.py ←── Parse incoming API responses
                └── time_slot_model.py     ←── Free-slot result objects
```

---

## 🔐 Authentication Flow

This project uses **MSAL Device Code Flow** (delegated permissions):

```
1. python main.py
        │
        ▼
2. Check token_cache.json  ──── ✅ Token valid? ──→ Use it silently
        │
        │ ❌ No valid token
        ▼
3. Print device code URL + code to terminal
        │
        ▼
4. User opens URL in browser, enters code, logs in
        │
        ▼
5. Token saved to token_cache.json
        │
        ▼
6. MCP server starts ✅
```

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

Expected output: **23 tests, all passing ✅**

| Test File | Coverage |
|---|---|
| `tests/test_main.py` | All 10 MCP tool functions (mocked service layer) |
| `tests/test_calendar_service.py` | Workweek logic, slot-finding, HTTP calls (mocked), auth error handling |
| `tests/event_model.py` | Event model creation and `to_dict()` serialization |

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `mcp[cli]` | FastMCP server framework |
| `httpx` | Async HTTP client for Graph API calls |
| `msal` | Microsoft Authentication Library (Device Code flow) |
| `python-dotenv` | Load credentials from `.env` file |

---

## 🗺️ Microsoft Graph API Endpoints Used

| Operation | Endpoint |
|---|---|
| List / search events | `GET /me/events` |
| Get single event | `GET /me/events/{id}` |
| Create event | `POST /me/events` |
| Update event | `PATCH /me/events/{id}` |
| Delete event | `DELETE /me/events/{id}` |
| Accept invite | `POST /me/events/{id}/accept` |
| Decline invite | `POST /me/events/{id}/decline` |
| Tentatively accept | `POST /me/events/{id}/tentativelyAccept` |

---

## 🔒 Security Notes

- 🚫 Never commit `.env` or `token_cache.json` — add both to `.gitignore`
- 🔑 Use the minimum required scope (`Calendars.ReadWrite`)
- ♻️ Tokens are refreshed automatically by MSAL when they expire
- 🛡️ All HTTP calls use `raise_for_status()` — API errors surface immediately

---

## 💡 Example `.gitignore` additions

```gitignore
.env
token_cache.json
__pycache__/
*.pyc
.pytest_cache/
```
