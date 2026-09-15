import asyncio
import websockets
import signal

async def handler(websocket):
    print("Unity客户端已连接")
    try:
        async for msg in websocket:
            print(f"收到Unity发来消息: {msg}")
            if msg == "start":
                await websocket.send("move_right")
            elif msg == "stop":
                await websocket.send("stop")
            else:
                await websocket.send("move_left")
    finally:
        print("客户端断开连接")

async def main():
    stop = asyncio.get_running_loop().create_future()
    async def on_shutdown():
        stop.set_result(None)
    signal.signal(signal.SIGTERM, lambda *_: asyncio.create_task(on_shutdown()))

    async with websockets.serve(handler, "0.0.0.0", 8080):
        await stop

if __name__ == "__main__":
    asyncio.run(main())
