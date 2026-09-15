import asyncio
import websockets
import os

PORT = int(os.environ.get("PORT", 10000))
connected_clients = set()

async def handle_client(websocket):
    connected_clients.add(websocket)
    print("新客户端连接，在线数量：", len(connected_clients))
    try:
        async for msg in websocket:
            print(f"收到消息: {msg}")
            for conn in connected_clients:
                if conn.open:
                    await conn.send(f"服务器收到: {msg}")
    finally:
        connected_clients.remove(websocket)
        print("客户端断开，在线数量：", len(connected_clients))

async def main():
    async with websockets.serve(
        handle_client,
        "0.0.0.0",
        PORT,
        ping_interval=30
    ):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
