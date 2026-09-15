import asyncio
import websockets
import os

PORT = int(os.environ.get("PORT", 10000))
connected_clients = set()

HTML_PAGE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>WebSocket 通信监控画面</title>
<style>
body {background:#111; color:#0f0; font-family:monospace; padding:20px;}
#msgBox {border:1px solid #444; min-height:300px; padding:10px; white-space:pre-wrap;}
.status {color:#aaa; margin-bottom:10px;}
</style>
</head>
<body>
<div class="status">连接状态：<span id="status">未连接</span></div>
<h3>通信日志</h3>
<div id="msgBox"></div>
<script>
const wsUrl = location.protocol === "https:" ? "wss://"+location.host : "ws://"+location.host;
const ws = new WebSocket(wsUrl);
const box = document.getElementById("msgBox");
const statusDom = document.getElementById("status");
ws.onopen = ()=>{
    statusDom.innerText = "✅已连接";
    addLog("浏览器客户端成功连接服务器");
}
ws.onmessage = (evt)=>{
    addLog("收到消息：" + evt.data);
}
ws.onclose = ()=>{
    statusDom.innerText = "❌连接断开";
    addLog("连接关闭");
}
ws.onerror = (err)=>{
    statusDom.innerText = "⚠️连接异常";
}
function addLog(text){
    const d = new Date();
    box.innerText += `[${d.toLocaleTimeString()}] ${text}\n`;
    box.scrollTop = box.scrollHeight;
}
</script>
</body>
</html>
"""

async def process_request(path, request_headers):
    if path == "/":
        return 200, {"Content-Type": "text/html; charset=utf-8"}, HTML_PAGE.encode("utf-8")
    return None

async def handle_client(websocket):
    connected_clients.add(websocket)
    print("新客户端连接成功，当前在线数量：", len(connected_clients))
    try:
        async for msg in websocket:
            print(f"收到消息: {msg}")
            for conn in connected_clients:
                if conn.open:
                    await conn.send(f"服务器收到: {msg}")
    finally:
        connected_clients.remove(websocket)
        print("客户端断开连接，在线数量：", len(connected_clients))

async def main():
    async with websockets.serve(
        handle_client,
        "0.0.0.0",
        PORT,
        process_request=process_request,
        origins=None
    ):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
