from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

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

active_connections: set[WebSocket] = set()

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return HTML_PAGE

@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    print("新客户端连接，在线数量：", len(active_connections))
    try:
        while True:
            data = await websocket.receive_text()
            print(f"收到消息: {data}")
            # 广播给所有客户端(Unity + 浏览器)
            for conn in active_connections:
                await conn.send_text(f"服务器收到: {data}")
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print("客户端断开，在线数量：", len(active_connections))

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
