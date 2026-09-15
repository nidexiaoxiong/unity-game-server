import asyncio
import websockets
import os

PORT = int(os.environ.get("PORT", 10000))

async def handle_client(websocket):
    print("客户端连接成功")
    async for msg in websocket:
        print(f"收到消息: {msg}")
        await websocket.send(f"服务器收到：{msg}")

async def main():
    async with websockets.serve(handle_client, "0.0.0.0", PORT):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
