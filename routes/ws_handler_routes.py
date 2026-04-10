from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import json
import asyncio
import websockets
from app.database import SessionLocal
from models.users import User
from utils.security import decode_access_token
from utils.ws_manager import manager

FINNHUB_API_KEY = "d7biqb9r01qgc9t7id6gd7biqb9r01qgc9t7id70"

latest_data = {"data": []}

router = APIRouter()

symbols = [
    "BINANCE:BTCUSDT",
    "BINANCE:ETHUSDT",
    "BINANCE:SOLUSDT",
    "OANDA:EUR_USD",
    "OANDA:USD_JPY",
    "OANDA:GBP_USD",
    "OANDA:USD_CHF",
    "OANDA:AUD_USD",
    "OANDA:USD_CAD",
    "OANDA:NZD_USD",
    "OANDA:EUR_GBP",
    "OANDA:EUR_JPY",
    "OANDA:GBP_JPY",
    "OANDA:USD_INR",
    "BINANCE:BTCUSDT",
    "BINANCE:ETHUSDT",
    "BINANCE:BNBUSDT",
    "BINANCE:SOLUSDT",
    "BINANCE:XRPUSDT",
    "BINANCE:ADAUSDT",
    "BINANCE:DOGEUSDT",
    "BINANCE:MATICUSDT",
    "BINANCE:AVAXUSDT",
    "BINANCE:DOTUSDT",
    "BINANCE:LTCUSDT",
    "BINANCE:TRXUSDT",
    "BINANCE:LINKUSDT",
    "BINANCE:ATOMUSDT",
    "BINANCE:SHIBUSDT",
    "AAPL",
    "TSLA",
    "MSFT",
    "GOOGL",
    "AMZN",
    "META",
    "NVDA" "NFLX",
    "AMD",
    "INTC",
    "UBER",
    "SHOP",
    "COIN" "PYPL",
]


@router.websocket("/ws")
async def websocket_proxy(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    uri = f"wss://ws.finnhub.io?token={FINNHUB_API_KEY}"

    async with websockets.connect(uri) as finnhub_ws:
        for symbol in symbols:
            await finnhub_ws.send(json.dumps({"type": "subscribe", "symbol": symbol}))

        while True:
            try:
                data = await finnhub_ws.recv()
                parsed_data = json.loads(data)
                print(data)
                if parsed_data.get("type") == "trade":
                    global latest_data
                    latest_data = parsed_data
                await websocket.send_text(json.dumps(parsed_data))
            except Exception as e:
                print("ERROR:", e)
                break

            # await asyncio.sleep(10)


@router.websocket("/ws/notifications")
async def notification_socket(websocket: WebSocket, token: str = Query(...)):
    try:
        payload = decode_access_token(token)
    except HTTPException:
        await websocket.close(code=1008)
        return

    email = payload.get("sub")
    if not email:
        await websocket.close(code=1008)
        return

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            await websocket.close(code=1008)
            return

        await manager.connect(user.id, websocket)
        try:
            while True:
                # Keep socket alive and consume any incoming messages/pings.
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(user.id, websocket)
    finally:
        db.close()


@router.get("/price-stream")
async def price_stream():

    async def event_generator():
        while True:
            if latest_data:
                yield f"data: {json.dumps(latest_data)}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
