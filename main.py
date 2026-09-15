import asyncio
import websockets
from websockets.server import HTTPResponse

connected_clients = set()

# 处理普通HTTP访问：返回网页HTML
async def process_request(path, request_headers):
    # 访问根路径返回监控页面
    if path == "/":
        html = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>WebSocket 实时通信监控</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:system-ui}
body{background:#111827;color:#e5e7eb;padding:24px}
.card{background:#1f2937;border-radius:12px;padding:20px;max-width:800px;margin:0 auto}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}
.title{font-size:20px;font-weight:bold}
.status{padding:4px 10px;border-radius:99px;background:#065f46;color:#86efac;font-size:14px}
.info-line{color:#9ca3af;font-size:14px;margin-bottom:16px;display:flex;justify-content:space-between}
.log-area{background:#111827;border:1px solid #374151;border-radius:8px;padding:16px;height:320px;overflow-y:auto;font-family:monospace;font-size:14px}
.log-item{margin:6px 0}
.sys-tag{color:#60a5fa;margin-right:6px}
</style>
</head>
<body>
<div class="card">
    <div class="header">
        <div class="title">WebSocket 实时通信监控</div>
        <div class="status" id="connStatus">连接中</div>
    </div>
    <div class="info-line">
        <span>服务器：<span id="wsUrl"></span></span>
        <span>在线客户端：<span id="onlineCount">0</span></span>
    </div>
    <div>通信日志</div>
    <div class="log-area" id="logBox"></div>
</div>

<script>
const host = window.location.host;
const wsUrl = `wss://${host}`;
document.getElementById("wsUrl").innerText = wsUrl;
const logBox = document.getElementById("logBox");
const statusDom = document.getElementById("connStatus");
const countDom = document.getElementById("onlineCount");
let ws;

function addLog(text, tag="sys"){
    const div = document.createElement("div");
    div.className="log-item";
    const now = new Date().toLocaleTimeString();
    div.innerHTML = `[${now}] <span class="sys-tag">${tag}</span> ${text}`;
    logBox.appendChild(div);
    logBox.scrollTop = logBox.scrollHeight;
}

function connect(){
    ws = new WebSocket(wsUrl);
    ws.onopen = ()=>{
        statusDom.innerText="已连接";
        statusDom.style.background="#065f46";
        addLog("浏览器客户端成功连接服务器");
    }
    ws.onmessage = evt=>{
        addLog(evt.data,"msg");
    }
    ws.onclose = ()=>{
        statusDom.innerText="断开，重连中";
        statusDom.style.background="#7c2d12";
        addLog("连接断开，3秒后自动重连");
        setTimeout(connect,3000);
    }
    ws.onerror = err=>{
        addLog("连接错误");
    }
}
connect();
</script>
</body>
</html>
"""
        return HTTPResponse(200, [("Content-Type", "text/html; charset=utf-8")], html.encode("utf-8"))
    # 其他路径拒绝
    return HTTPResponse(404, [], b"Not Found")

async def handle_client(websocket):
    connected_clients.add(websocket)
    print("新客户端连接，在线数量：", len(connected_clients))
    try:
        async for msg in websocket:
            print(f"收到消息: {msg}")
            for conn in connected_clients:
                if conn.open:
                    await conn.send(`服务器收到: ${msg}`)
    finally:
        connected_clients.remove(websocket)
        print("客户端断开，在线数量：", len(connected_clients))

async def main():
    async with websockets.serve(
        handle_client,
        host="0.0.0.0",
        port=10000,
        process_request=process_request
    ):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
