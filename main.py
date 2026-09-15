import asyncio
import websockets
import os

PORT = int(os.environ.get("PORT", 10000))
connected_clients = set()

HTML_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>WebSocket 实时通信监控</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: radial-gradient(circle at top, #1f2937 0%, #0b1020 45%, #05070f 100%);
    color: #e5e7eb;
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    min-height: 100vh;
    padding: 40px 24px;
    display: flex;
    justify-content: center;
    align-items: flex-start;
  }
  .panel {
    width: 100%;
    max-width: 900px;
    background: rgba(17, 24, 39, 0.78);
    border: 1px solid rgba(129, 140, 248, 0.35);
    border-radius: 22px;
    box-shadow:
      0 0 0 1px rgba(99, 102, 241, 0.08) inset,
      0 30px 80px rgba(0, 0, 0, 0.45),
      0 0 60px rgba(99, 102, 241, 0.18);
    overflow: hidden;
    backdrop-filter: blur(14px);
  }
  .panel-header {
    padding: 22px 26px;
    background: linear-gradient(135deg, rgba(79, 70, 229, 0.22), rgba(14, 165, 233, 0.18));
    border-bottom: 1px solid rgba(129, 140, 248, 0.25);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
  }
  .panel-title {
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #f9fafb;
  }
  .panel-title span {
    background: linear-gradient(90deg, #a5b4fc, #22d3ee);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }
  .status {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 9px 14px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 14px;
    color: #d1d5db;
  }
  .status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #f87171;
    box-shadow: 0 0 12px rgba(248, 113, 113, 0.7);
    transition: all 0.3s ease;
  }
  .status-dot.online {
    background: #4ade80;
    box-shadow: 0 0 14px rgba(74, 222, 128, 0.8);
  }
  .status-text { font-weight: 600; }
  .info-bar {
    padding: 14px 26px;
    background: rgba(255, 255, 255, 0.02);
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    font-size: 13px;
    color: #9ca3af;
    display: flex;
    justify-content: space-between;
    gap: 16px;
    flex-wrap: wrap;
  }
  .info-bar b { color: #e5e7eb; font-weight: 600; }
  .log-box { padding: 22px 26px 26px; }
  .log-title {
    font-size: 14px;
    color: #9ca3af;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .log-title::before {
    content: "";
    width: 4px;
    height: 14px;
    background: linear-gradient(180deg, #818cf8, #22d3ee);
    border-radius: 3px;
  }
  #msgBox {
    min-height: 340px;
    max-height: 460px;
    overflow-y: auto;
    padding: 18px;
    border-radius: 14px;
    background: rgba(2, 6, 23, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.12);
    font-family: "Cascadia Code", "Fira Code", Consolas, monospace;
    font-size: 13px;
    line-height: 1.7;
    color: #e5e7eb;
    white-space: pre-wrap;
    word-break: break-word;
  }
  #msgBox .time { color: #60a5fa; margin-right: 10px; }
  #msgBox .tag {
    display: inline-block;
    padding: 1px 8px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    margin-right: 10px;
  }
  .tag-system { background: rgba(148, 163, 184, 0.18); color: #cbd5e1; }
  .tag-recv { background: rgba(74, 222, 128, 0.18); color: #86efac; }
  .tag-error { background: rgba(248, 113, 113, 0.18); color: #fca5a5; }
  .footer {
    padding: 14px 26px;
    background: rgba(255, 255, 255, 0.02);
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    font-size: 12px;
    color: #6b7280;
    display: flex;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
  }
  #msgBox::-webkit-scrollbar { width: 8px; }
  #msgBox::-webkit-scrollbar-track { background: transparent; }
  #msgBox::-webkit-scrollbar-thumb { background: rgba(129, 140, 248, 0.35); border-radius: 999px; }
  #msgBox::-webkit-scrollbar-thumb:hover { background: rgba(129, 140, 248, 0.55); }
</style>
</head>
<body>
  <div class="panel">
    <div class="panel-header">
      <div class="panel-title">WebSocket <span>实时通信监控</span></div>
      <div class="status">
        <div class="status-dot" id="statusDot"></div>
        <div class="status-text" id="statusText">未连接</div>
      </div>
    </div>
    <div class="info-bar">
      <div>服务器：<b id="serverUrl">wss://unity-game-server-1.onrender.com</b></div>
      <div>在线客户端：<b id="clientCount">0</b></div>
    </div>
    <div class="log-box">
      <div class="log-title">通信日志</div>
      <div id="msgBox"></div>
    </div>
    <div class="footer">
      <div>Unity 客户端连接后，消息将实时显示在此面板。</div>
      <div>同一网址同时提供网页与 WebSocket 服务。</div>
    </div>
  </div>

<script>
  const wsUrl = "wss://unity-game-server-1.onrender.com";
  const ws = new WebSocket(wsUrl);
  const box = document.getElementById("msgBox");
  const statusText = document.getElementById("statusText");
  const statusDot = document.getElementById("statusDot");
  const clientCount = document.getElementById("clientCount");

  function setStatus(text, online) {
    statusText.textContent = text;
    statusDot.classList.toggle("online", online);
  }

  function addLog(text, type) {
    const time = new Date().toLocaleTimeString();
    const tagClass = type === "recv" ? "tag-recv" : type === "error" ? "tag-error" : "tag-system";
    const tagText = type === "recv" ? "RECV" : type === "error" ? "ERROR" : "SYS";
    const line = document.createElement("div");
    line.innerHTML = `<span class="time">[${time}]</span><span class="tag ${tagClass}">${tagText}</span>${text}`;
    box.appendChild(line);
    box.scrollTop = box.scrollHeight;
  }

  ws.onopen = () => {
    setStatus("已连接", true);
    addLog("浏览器客户端成功连接服务器");
  };

  ws.onmessage = (evt) => {
    addLog("收到消息：" + evt.data, "recv");
  };

  ws.onclose = () => {
    setStatus("连接断开", false);
    addLog("连接关闭", "error");
  };

  ws.onerror = () => {
    setStatus("连接异常", false);
    addLog("连接异常，请等待服务器唤醒后刷新", "error");
  };

  setInterval(() => {
    clientCount.textContent = ws.readyState === WebSocket.OPEN ? "1 (浏览器在线)" : "0";
  }, 2000);
</script>
</body>
</html>
"""


async def process_request(path, request_headers):
    if path == "/":
        return 200, [("Content-Type", "text/html; charset=utf-8")], HTML_PAGE.encode("utf-8")
    return 404, [("Content-Type", "text/plain; charset=utf-8")], b"Not Found"


async def handle_client(websocket):
    connected_clients.add(websocket)
    print("新客户端连接，在线数量：", len(connected_clients))
    try:
        async for msg in websocket:
            print("收到消息: " + msg)
            for conn in list(connected_clients):
                if conn.open:
                    await conn.send("服务器收到: " + msg)
    finally:
        connected_clients.discard(websocket)
        print("客户端断开，在线数量：", len(connected_clients))


async def main():
    server = await websockets.serve(
        handle_client,
        "0.0.0.0",
        PORT,
        process_request=process_request,
        origins=None,
        ping_interval=30
    )
    print("Server started on port", PORT)
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
