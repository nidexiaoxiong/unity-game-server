import asyncio
import websockets
import os

PORT = int(os.environ.get("PORT", 10000))
connected = set()

async def handle_client(websocket):
    connected.add(websocket)
    try:
        async for msg in websocket:
            print(f"收到消息: {msg}")
            # 广播给所有连接的客户端
            for conn in list(connected):
                if conn.open:
                    await conn.send(msg)
    finally:
        connected.remove(websocket)

async def http_handler(path, request_headers):
    # 访问网页时只返回简单文字，没有任何前端面板
    if path == "/":
        return 200, [("Content-Type", "text/plain")], b"WebSocket Server Ready. Connect via wss://unity-game-server-1.onrender.com"
    return 404, [], b"Not Found"

async def main():
    async with websockets.serve(
        handle_client,
        "0.0.0.0",
        PORT,
        process_request=http_handler
    ):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
