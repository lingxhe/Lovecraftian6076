## CoC Solo · LLM Keeper

当前主版本采用 **Next.js + Tailwind CSS** 前端 + **FastAPI** 后端，替代最早的 Streamlit UI。所有 Keeper 逻辑仍位于 `agents/` 目录。

### 本地运行

```bash
# 1. 安装 Python 依赖
pip install -r requirements.txt
pip install -r requirements-web.txt

# 2. 启动 FastAPI 后端
python api_server.py
# http://localhost:8000

# 3. 另开终端启动 Next.js 前端
cd web
npm install
npm run dev
# http://localhost:3000
```

也可直接运行 `start-web.bat`（Windows）或 `./start-web.sh`（macOS/Linux）。

### 项目结构

```
agents/            # LangGraph Keeper、场景与工具
utils/             # 会话状态、Markdown 日志
api_server.py      # FastAPI：供 Next.js 调用
web/               # Next.js 14 + Tailwind 前端
  ├── app/chat     # Keeper 聊天
  ├── app/create-character
  ├── app/api      # 代理 Render 后端
  ├── store        # Zustand 状态管理
  └── lib          # API 客户端
```

### 部署

- **前端**：Vercel（`web/` 目录，环境变量 `PYTHON_BACKEND_URL`）
- **后端**：Render / Railway / Fly.io（`uvicorn api_server:app --port $PORT`，环境变量 `ALLOWED_ORIGINS`）
- 详细步骤见 `deploy-vercel-render.md`

### OpenAI API Key

前端侧栏输入框仅存储在浏览器本地。也可在部署的 Python 后端通过 `OPENAI_API_KEY` 环境变量提供默认值。
