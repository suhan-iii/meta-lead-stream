import os
import hmac
import hashlib
import time
import httpx
from typing import List
from fastapi import FastAPI, Request, HTTPException, Query, Response, Depends, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import Lead

load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
APP_SECRET = os.getenv("APP_SECRET")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

BYPASS_SIGNATURE_FOR_DEV = True
MOCK_GRAPH_API = True

Base.metadata.create_all(bind=engine)

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/webhook")
def verify(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified successfully")
        return Response(content=challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook")
async def webhook_listener(request: Request, db: Session = Depends(get_db)):
    body_bytes = await request.body()

    if APP_SECRET and not BYPASS_SIGNATURE_FOR_DEV:
        signature = request.headers.get("X-Hub-Signature-256", "")
        if not signature.startswith("sha256="):
            raise HTTPException(status_code=400, detail="Missing or invalid signature header")
        
        expected = hmac.new(APP_SECRET.encode(), body_bytes, hashlib.sha256).hexdigest()
        actual = signature.split("sha256=")[1] if "sha256=" in signature else ""
        if not hmac.compare_digest(expected, actual):
            raise HTTPException(status_code=403, detail="Signature mismatch")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    return await process_lead_payload(payload, db)


async def process_lead_payload(payload: dict, db: Session):
    if payload.get("object") == "page":
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") == "leadgen":
                    val = change.get("value", {})
                    lead_id = val.get("leadgen_id")
                    
                    if lead_id:
                        print(f"New lead event received. Lead ID: {lead_id}")
                        lead_data = await get_lead_info(lead_id)
                        if lead_data:
                            saved_lead = save_lead_to_db(db, lead_data)
                            if saved_lead:
                                
                                await manager.broadcast({
                                    "lead_id": saved_lead.lead_id,
                                    "full_name": saved_lead.full_name,
                                    "email": saved_lead.email,
                                    "phone_number": saved_lead.phone_number
                                })
    return {"status": "EVENT_RECEIVED"}

#  Mock Endpoint
@app.post("/mock-meta-lead")
async def trigger_mock_lead(db: Session = Depends(get_db)):
    timestamp = int(time.time())
    mock_payload = {
        "object": "page",
        "entry": [{
            "id": "10009988776655",
            "time": timestamp,
            "changes": [{
                "field": "leadgen",
                "value": {
                    "created_time": timestamp,
                    "page_id": "10009988776655",
                    "form_id": "123456789",
                    "leadgen_id": f"mock_{timestamp}"
                }
            }]
        }]
    }
    return await process_lead_payload(mock_payload, db)


def save_lead_to_db(db: Session, lead_data: dict):
    lead_id = lead_data["id"]
    fields = {field["name"]: field["values"][0] for field in lead_data.get("field_data", [])}

    existing = db.query(Lead).filter(Lead.lead_id == lead_id).first()
    if existing:
        print(f"Lead {lead_id} already exists in database.")
        return existing

    new_lead = Lead(
        lead_id=lead_id,
        full_name=fields.get("full_name"),
        email=fields.get("email"),
        phone_number=fields.get("phone_number")
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    print(f"Successfully saved lead {lead_id} to database!")
    return new_lead


async def get_lead_info(lead_id: str):
    if MOCK_GRAPH_API:
        return {
            "id": lead_id,
            "field_data": [
                {"name": "full_name", "values": ["Jane Doe"]},
                {"name": "email", "values": ["janedoe@example.com"]},
                {"name": "phone_number", "values": ["+1234567890"]}
            ]
        }

    if not PAGE_ACCESS_TOKEN:
        print("Error: PAGE_ACCESS_TOKEN is missing in .env")
        return None

    url = f"https://graph.facebook.com/v19.0/{lead_id}"
    params = {"access_token": PAGE_ACCESS_TOKEN}

    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, params=params)
            if res.status_code == 200:
                return res.json()
    except Exception as e:
        print(f"Request failed: {e}")
    return None


@app.get("/leads")
def get_all_leads(db: Session = Depends(get_db)):
    return db.query(Lead).all()