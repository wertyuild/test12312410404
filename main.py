from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import tempfile
import shutil
import requests
import threading
import json

from .database import SessionLocal, engine, Base
from .models import Order, OrderStatus
from .notify import notify

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UsernameRequest(BaseModel):
    username: str

class OrderRequest(BaseModel):
    username: str
    stars: int
    payment_method: str

@app.post("/api/check_user")
def api_check_user(data: UsernameRequest):
    username = data.username.lstrip('@') if data.username else ''
    if not username or len(username) < 3:
        return {"ok": False, "error": "Некорректный username"}
    return {"ok": True, "username": username, "avatar_url": f"/api/avatar?username={username}"}

with open(os.path.join(os.path.dirname(__file__), 'config.json'), encoding='utf-8') as f:
    config = json.load(f)
CRYPTOBOT_TOKEN = config.get('cryptobot_token')
CRYPTOBOT_API_URL = 'https://api.cryptobot.io/v1/'

# Функция для создания инвойса через CryptoBot
def create_cryptobot_invoice(username, stars, order_id):
    amount = round(stars * 1.27, 2)
    headers = {
        'Crypto-Pay-API-Token': CRYPTOBOT_TOKEN,
        'Content-Type': 'application/json'
    }
    payload = {
        'asset': 'USDT',
        'amount': amount,
        'description': f'Покупка {stars} звёзд для @{username}',
        'hidden_message': 'Спасибо за покупку!',
        'payload': f'order_{order_id}'
    }
    resp = requests.post(CRYPTOBOT_API_URL + 'createInvoice', headers=headers, json=payload, timeout=10)
    data = resp.json()
    if data.get('ok') and data['result'].get('pay_url'):
        return data['result']['pay_url']
    else:
        print('CryptoBot invoice error:', data)
        return None

@app.post("/api/buy")
def api_buy(order: OrderRequest, db: Session = Depends(get_db)):
    db_order = Order(
        username=order.username,
        stars=order.stars,
        payment_method=order.payment_method,
        status=OrderStatus.pending
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    price = order.stars * 1.27
    notify(order.username, order.stars, order.payment_method, price)
    pay_url = None
    if order.payment_method == 'cryptobot':
        pay_url = create_cryptobot_invoice(order.username, order.stars, db_order.id)
    return {"ok": True, "order_id": db_order.id, "pay_url": pay_url}

# Webhook для CryptoBot
@app.post("/api/cryptobot_webhook")
async def cryptobot_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    payload = data.get('payload')
    status = data.get('status')
    if payload and status == 'paid' and payload.startswith('order_'):
        try:
            order_id = int(payload.replace('order_', ''))
            order = db.query(Order).filter(Order.id == order_id).first()
            if order and order.status != OrderStatus.notified:
                order.status = OrderStatus.notified
                db.commit()
                print(f"Order {order_id} marked as paid!")
                return {"ok": True}
        except Exception as e:
            print('Webhook error:', e)
    return {"ok": False}

@app.get("/api/avatar")
def get_avatar(username: str = Query(...)):
    url = f"https://t.me/i/userpic/320/{username}.jpg"
    tmpdir = tempfile.mkdtemp()
    tmpfile = os.path.join(tmpdir, f"{username}.jpg")
    try:
        r = requests.get(url, stream=True, timeout=5)
        if r.status_code == 200 and r.headers.get('Content-Type', '').startswith('image'):
            with open(tmpfile, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
            return FileResponse(tmpfile, media_type='image/jpeg', filename=f"{username}.jpg")
        else:
            default_path = os.path.join(os.path.dirname(__file__), 'default-avatar.jpg')
            if os.path.exists(default_path):
                return FileResponse(default_path, media_type='image/jpeg', filename='default-avatar.jpg')
            else:
                raise HTTPException(status_code=404, detail="Default avatar not found")
    finally:
        def cleanup():
            try:
                if os.path.exists(tmpfile): os.remove(tmpfile)
                if os.path.exists(tmpdir): os.rmdir(tmpdir)
            except Exception: pass
        threading.Timer(2, cleanup).start() 