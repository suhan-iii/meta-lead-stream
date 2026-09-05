# Meta Lead Stream 

A proof-of-concept system that captures Meta (Facebook) Lead Ads in real-time and streams them to a mobile application via WebSocket. This project demonstrates a full-stack solution integrating Meta's Graph API, a FastAPI backend, and a React Native mobile frontend.

## Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Architecture & Data Flow](#architecture--data-flow)
- [Installation & Setup](#installation--setup)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Features](#features)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

---

## Project Overview

**Meta Lead Stream POC** is a real-time lead capture system that:

1. **Receives webhook events** from Meta's Lead Ads forms whenever a new lead is submitted
2. **Processes lead data** by fetching detailed information from Meta's Graph API
3. **Stores leads** in a local SQLite database
4. **Streams live updates** to connected mobile clients via WebSocket
5. **Displays leads** in a React Native mobile app with live updates

This is ideal for businesses running Meta Lead Ads campaigns who need real-time visibility into captured leads across mobile and web platforms.

---

## Tech Stack

### Backend
- **Language:** Python 3.9+
- **Framework:** FastAPI 0.100.0+
- **Database:** SQLite (via SQLAlchemy 2.0+)
- **Web Server:** Uvicorn
- **Key Libraries:**
  - `fastapi` - Modern web framework for building APIs
  - `sqlalchemy` - SQL toolkit and ORM
  - `httpx` - Async HTTP client (for Meta Graph API calls)
  - `websockets` - WebSocket protocol support
  - `python-dotenv` - Environment variable management

### Frontend
- **Language:** JavaScript (ES6+)
- **Framework:** React Native 0.73.6
- **Meta Framework:** Expo 50.0.14
- **Runtime:** React 18.2.0
- **Platforms Supported:** iOS, Android, Web

---

## Project Structure

```
meta-lead-stream-poc/
│
├── backend/                    # FastAPI backend service
│   ├── main.py                # Main application entry point & route handlers
│   ├── models.py              # SQLAlchemy ORM models
│   ├── database.py            # Database configuration & session management
│   ├── requirements.txt        # Python dependencies
│   └── .gitignore             # Git ignore patterns
│
├── frontend/                   # React Native Expo mobile app
│   ├── App.js                 # Main React component
│   ├── app.json               # Expo configuration
│   ├── index.js               # Entry point
│   ├── babel.config.js        # Babel transpiler configuration
│   ├── package.json           # NPM dependencies
│   ├── package-lock.json      # Dependency lock file
│   └── .expo/                 # Expo build metadata (auto-generated)
│
└── [root configuration files]  # (if any)
```

### Backend Details

**main.py**
- FastAPI application instance
- Webhook verification endpoint (`/webhook` GET)
- Webhook listener endpoint (`/webhook` POST)
- Mock lead trigger endpoint (`/mock-meta-lead` POST)
- WebSocket endpoint (`/ws`)
- Lead retrieval endpoint (`/leads` GET)
- Business logic for processing lead payloads
- Meta Graph API integration

**models.py**
- `Lead` SQLAlchemy model with fields:
  - `lead_id` (Primary Key)
  - `full_name`
  - `email`
  - `phone_number`
  - `created_at` (Auto-timestamp)

**database.py**
- SQLite connection setup
- Session factory configuration
- Database dependency injection helper

### Frontend Details

**App.js**
- Main React component
- WebSocket connection management
- HTTP lead fetching on mount
- Real-time lead updates via WebSocket
- Lead display using FlatList
- Responsive styling for mobile & web

---

## Architecture & Data Flow

### Request Flow Diagram

```
Meta Lead Ads Form
       ↓
   (user submits)
       ↓
Meta Graph API Webhook
       ↓
Backend /webhook endpoint (POST)
       ↓
Verify signature + Parse JSON
       ↓
Extract lead_id from payload
       ↓
Fetch lead details via Graph API
       ↓
Save to SQLite database
       ↓
Broadcast via WebSocket to all connected clients
       ↓
React Native app receives data
       ↓
Update local state & re-render UI
```

### Component Interaction

1. **Webhook Reception**: Meta sends POST to `/webhook` with lead event
2. **Signature Verification**: Request signature validated (optional for dev)
3. **Lead Enrichment**: Lead ID used to fetch full details from Meta Graph API
4. **Data Persistence**: Lead saved to SQLite
5. **Real-time Broadcasting**: WebSocket broadcasts lead to all connected clients
6. **Mobile Display**: Frontend receives broadcast, updates FlatList in real-time

### WebSocket Connection

The frontend maintains a persistent WebSocket connection to the backend:
- **Endpoint**: `ws://<BACKEND_HOST>/ws`
- **Message Format**: JSON objects with lead data
- **Auto-reconnect**: Frontend handles disconnections gracefully

---

## Installation & Setup

### Prerequisites

- **Python 3.9+** (for backend)
- **Node.js 18+** & **npm** (for frontend)
- **Expo CLI** (for React Native development)
- **Git**
- Meta Business Account with Lead Ads campaign configured

### Backend Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/suhan-iii/meta-lead-stream-poc.git
cd meta-lead-stream-poc/backend
```

#### 2. Create Python Virtual Environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

#### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Dependency Breakdown:**
- `fastapi>=0.100.0` - Web framework
- `uvicorn[standard]>=0.22.0` - ASGI server with uvloop
- `sqlalchemy>=2.0.0` - Database ORM
- `python-dotenv>=1.0.0` - Env variable loading
- `httpx>=0.24.0` - Async HTTP client
- `websockets>=11.0` - WebSocket support

#### 4. Create `.env` File

Create a `.env` file in the `backend/` directory with the following variables:

```bash
# Meta Configuration
VERIFY_TOKEN=your_verify_token_here
APP_SECRET=your_app_secret_here
PAGE_ACCESS_TOKEN=your_page_access_token_here

# Development Mode (disable for production)
BYPASS_SIGNATURE_FOR_DEV=True
MOCK_GRAPH_API=True
```

**Getting Meta Credentials:**
1. Go to [Meta for Developers](https://developers.facebook.com)
2. Create/select an App
3. Add "Webhooks" product
4. Set up Lead Ads subscription
5. Generate `PAGE_ACCESS_TOKEN` from Settings > Basic
6. Set custom `VERIFY_TOKEN` (any string you choose)
7. Find `APP_SECRET` in Settings > Basic

#### 5. Initialize Database

```bash
python main.py
```

This creates `leads.db` SQLite database automatically. Press `Ctrl+C` to stop.

---

### Frontend Setup

#### 1. Navigate to Frontend Directory

```bash
cd meta-lead-stream-poc/frontend
```

#### 2. Install Node Dependencies

```bash
npm install
```

This installs:
- React & React Native
- Expo runtime
- All necessary polyfills and transpilers

#### 3. Install Expo CLI (if not already installed)

```bash
npm install -g expo-cli
```

Or use `npx` (included with npm 5.2+):

```bash
npx expo --version
```

#### 4. Configure Backend Host

Open `App.js` and update the `BACKEND_HOST` if needed:

```javascript
// For local development
const BACKEND_HOST = Platform.OS === 'android' ? '10.0.2.2:8000' : 'localhost:8000';

// For remote server, use your server IP/domain:
// const BACKEND_HOST = 'your-server-ip:8000';
```

---

## Configuration

### Environment Variables (Backend)

| Variable | Description | Example |
|----------|-------------|---------|
| `VERIFY_TOKEN` | Token for webhook verification | `my_secret_token_123` |
| `APP_SECRET` | App secret for signature validation | From Meta dashboard |
| `PAGE_ACCESS_TOKEN` | Token to access Meta Graph API | From Meta dashboard |
| `BYPASS_SIGNATURE_FOR_DEV` | Skip signature check in development | `True` or `False` |
| `MOCK_GRAPH_API` | Use mock data instead of real API | `True` or `False` |

### Frontend Configuration

**app.json** (Expo config):
```json
{
  "expo": {
    "name": "frontend",
    "slug": "frontend",
    "version": "1.0.0",
    "orientation": "portrait",
    "userInterfaceStyle": "light"
  }
}
```

Customize:
- `name` - App display name
- `slug` - URL-safe identifier
- `version` - Semantic version
- `orientation` - `portrait`, `landscape`, or `default`

---

## Running the Application

### Start Backend Server

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

The backend runs on `http://localhost:8000`

**Available Routes:**
- `GET /webhook` - Webhook verification
- `POST /webhook` - Receive lead events
- `GET /leads` - Fetch all leads
- `POST /mock-meta-lead` - Trigger test lead (for development)
- `WS /ws` - WebSocket connection

### Start Frontend (Choose One)

#### Option 1: Expo Web (Easiest for Testing)

```bash
cd frontend
npm start
# Or:
npx expo start --web
```

Opens browser at `http://localhost:19006`

#### Option 2: Android Emulator

```bash
cd frontend
npx expo start --android
```

Requirements: Android Studio + emulator installed

#### Option 3: iOS Simulator (macOS only)

```bash
cd frontend
npx expo start --ios
```

Requirements: Xcode installed

#### Option 4: Physical Device

```bash
cd frontend
npx expo start
```

Then:
- Scan QR code with **Expo Go** app (iOS/Android)
- App opens on your phone

---

## API Endpoints

### Webhook Endpoints

#### Verify Webhook (GET)

Meta calls this to verify the webhook URL.

```bash
GET /webhook?hub.mode=subscribe&hub.verify_token=your_token&hub.challenge=challenge_string
```

**Response:** Returns the challenge as plain text if token matches

---

#### Receive Lead Event (POST)

Meta sends POST whenever a lead is submitted.

```bash
POST /webhook

{
  "object": "page",
  "entry": [
    {
      "id": "page_id",
      "time": 1234567890,
      "changes": [
        {
          "field": "leadgen",
          "value": {
            "created_time": 1234567890,
            "page_id": "123456",
            "form_id": "789012",
            "leadgen_id": "lead_123456"
          }
        }
      ]
    }
  ]
}
```

**Response:**
```json
{
  "status": "EVENT_RECEIVED"
}
```

---

### Data Endpoints

#### Get All Leads (GET)

Fetch all leads from the database.

```bash
GET /leads
```

**Response:**
```json
[
  {
    "lead_id": "lead_123456",
    "full_name": "Jane Doe",
    "email": "janedoe@example.com",
    "phone_number": "+1234567890",
    "created_at": "2024-01-15T10:30:00"
  },
  ...
]
```

---

#### Trigger Mock Lead (POST)

For development/testing without a real Meta form submission.

```bash
POST /mock-meta-lead
```

**Response:**
```json
{
  "status": "EVENT_RECEIVED"
}
```

Creates a mock lead and broadcasts via WebSocket.

---

### WebSocket Endpoint

#### Connect to Live Stream (WS)

Establish persistent WebSocket connection for real-time updates.

```
WS ws://localhost:8000/ws
```

**Incoming Message Format:**
```json
{
  "lead_id": "lead_123456",
  "full_name": "Jane Doe",
  "email": "janedoe@example.com",
  "phone_number": "+1234567890"
}
```

---

## Features

### ✅ Current Features

- **Real-time Lead Capture**: Webhook integration with Meta Lead Ads
- **WebSocket Streaming**: Live lead broadcasts to connected clients
- **Lead Enrichment**: Fetches full lead data from Meta Graph API
- **Persistent Storage**: SQLite database for lead history
- **Multi-device Broadcasting**: All connected clients receive updates simultaneously
- **Mock Data Support**: Test without Meta integration
- **Signature Verification**: Security layer for webhook validation
- **Cross-platform Mobile**: iOS, Android, and Web support via Expo
- **Responsive UI**: Mobile-optimized card-based lead display
- **Connection Status**: Real-time connection state indicator

### 🚀 Potential Enhancements

- **PostgreSQL Support**: Replace SQLite for production scalability
- **Lead Filtering**: Search/filter by name, email, phone
- **Lead Details View**: Expand view for individual lead information
- **Export Functionality**: CSV/PDF export of leads
- **Authentication**: User login & permission-based access
- **Lead Assignment**: Assign leads to team members
- **Webhook Retry Logic**: Failed event retry mechanism
- **Database Migrations**: Alembic for schema versioning
- **API Rate Limiting**: Protect against abuse
- **Monitoring & Analytics**: Dashboards and metrics
- **Notification System**: Email/SMS/push notifications for new leads
- **Mobile Push Notifications**: Expo push notifications for new leads

---

## Development

### Backend Development

#### Run in Development Mode

```bash
cd backend
source venv/bin/activate
python main.py
```

#### Code Structure Best Practices

- **main.py**: Route handlers and API logic
- **models.py**: Data models (separate file per model for larger projects)
- **database.py**: Database configuration
- **services/** (future): Business logic separation
- **schemas/** (future): Request/response validation with Pydantic

#### Add New Dependencies

```bash
pip install new_package
pip freeze > requirements.txt
```

#### Database Debugging

```bash
# Connect to SQLite DB
sqlite3 backend/leads.db

# View all leads
SELECT * FROM leads;

# Delete all data (careful!)
DELETE FROM leads;

.exit
```

---

### Frontend Development

#### Hot Reload

Changes to `App.js` automatically reload on save (when using `npm start` or `npx expo start`).

#### Debug in Browser

When running web:
- Open DevTools (F12)
- View network requests
- Check console for errors
- Inspect React component hierarchy

#### Mobile Debug

- Shake device → open Developer Menu
- Select "Debug Remote JS"
- Open DevTools at `http://localhost:19000`

---

## Troubleshooting

### Backend Issues

#### Backend won't start

```bash
# Check if port 8000 is in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or use different port:
python main.py --port 8001
```

#### WebSocket connection fails

- Ensure backend is running on correct host
- Check firewall rules
- Verify `BACKEND_HOST` in `App.js` matches backend address
- For remote connections, ensure `/ws` is not blocked by proxy

#### Lead data not saving

- Check database file permissions
- Verify SQLite installation
- Review backend logs for errors
- Ensure `Lead` model matches database schema

#### Meta API errors

- Verify `PAGE_ACCESS_TOKEN` is valid
- Check token hasn't expired
- Ensure app is installed on the correct page
- Test with `MOCK_GRAPH_API=True` to isolate issues

---

### Frontend Issues

#### App won't connect to backend

```bash
# Check backend is running
curl http://localhost:8000/leads

# For Android emulator, use 10.0.2.2 instead of localhost
# For physical device, use actual machine IP
ipconfig getifaddr en0  # macOS
hostname -I  # Linux
```

#### Build errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Expo cache
npx expo start --clear
```

#### WebSocket keeps disconnecting

- Check network stability
- Verify backend `/ws` endpoint is accessible
- Review browser console for errors
- Increase timeout values if network is slow

---

### Database Issues

#### "Database locked" errors

```bash
# Close other connections
# Restart backend
# Or delete leads.db and restart (data loss!)
rm backend/leads.db
```

#### Schema mismatch

```bash
# Backup and reset
cp backend/leads.db backend/leads.db.bak
rm backend/leads.db
python main.py  # Creates fresh schema
```

---

## Common Tasks

### Testing with Mock Lead

While backend is running:

```bash
curl -X POST http://localhost:8000/mock-meta-lead
```

Watch for the new lead to appear in the mobile app (if connected via WebSocket).

---

### Viewing Leads via API

```bash
curl http://localhost:8000/leads | jq .
```

---

### Connecting Mobile App to Remote Backend

1. Get server IP address:
   ```bash
   # macOS/Linux
   ifconfig
   
   # Windows
   ipconfig
   ```

2. Update `App.js`:
   ```javascript
   const BACKEND_HOST = '192.168.1.100:8000';  // Your server IP
   ```

3. Restart Expo app

---

## Deployment

### Backend Deployment (Production)

1. **Use PostgreSQL instead of SQLite**
   ```bash
   pip install psycopg2-binary
   ```

2. **Environment-specific config**
   ```bash
   DATABASE_URL=postgresql://user:password@host:5432/db
   ```

3. **Deploy with Gunicorn + Nginx**
   ```bash
   pip install gunicorn
   gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
   ```

4. **Enable HTTPS/SSL**

5. **Set secure env variables** on hosting platform

### Frontend Deployment

1. **Build APK/IPA/AAB**
   ```bash
   eas build --platform android
   eas build --platform ios
   ```

2. **Build for web**
   ```bash
   npx expo export --platform web
   # Deploy 'dist/' folder to web server
   ```

3. **Update backend URL** for production

---

## License

This project is open source. Specify your license here if needed.

## Support & Contribution

For issues, questions, or contributions, please open a GitHub issue or submit a pull request.

---

## Quick Reference

### Starting Both Services

**Terminal 1 (Backend):**
```bash
cd backend
source venv/bin/activate
python main.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm start
```

Then open `http://localhost:19006` in browser or scan QR code with Expo Go app.

### Test Flow

1. Backend running on `localhost:8000`
2. Frontend running on Expo
3. Call `/mock-meta-lead` endpoint
4. See new lead appear in app within seconds

---

**Happy coding!** 🚀
