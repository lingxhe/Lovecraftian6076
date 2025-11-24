# CoC Solo Web (Next.js + Tailwind CSS)

现代化的 Lovecraftian 单人模组前端，复刻 Streamlit 版本的全部功能，并支持部署到 **Vercel（前端）** + **Render（Python 后端）** 等平台。

## 功能

- 角色创建（头像、属性、技能、LUCK 规则）
- Keeper 聊天（LangGraph + OpenAI 工具，场景切换）
- Markdown 日志下载
- API Key 管理（浏览器本地储存）
- 状态持久化（Zustand + LocalStorage）
- Tailwind CSS 暗色界面

## 快速开始

```bash
# 安装依赖
cd web
npm install

# 开发模式
npm run dev
# http://localhost:3000
```

Python 后端需单独启动：

```bash
pip install -r requirements.txt
pip install -r requirements-web.txt
python api_server.py
# FastAPI 默认运行在 http://localhost:8000
```

## 目录结构

```
web/
├── app/
│   ├── api/          # Next.js Route Handlers，代理 Python 后端
│   ├── chat/         # KP 聊天界面
│   ├── create-character/  # 角色创建界面
│   ├── layout.tsx
│   └── page.tsx      # 重定向逻辑
├── store/            # Zustand 状态管理
├── lib/              # API 客户端
├── tailwind.config.ts
└── tsconfig.json
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `PYTHON_BACKEND_URL` | Next.js API 调用的 Python 后端地址 | `http://localhost:8000` |
| `NEXT_PUBLIC_API_BASE` | 前端 fetch 的 API 前缀 | `/api` |

## 部署建议

1. **Render / Railway**：部署 `api_server.py`（FastAPI）
   - 启动命令：`uvicorn api_server:app --host 0.0.0.0 --port $PORT`
   - 设置 `ALLOWED_ORIGINS` 为 Vercel 前端域名

2. **Vercel**：部署 `web/` Next.js 前端
   - 环境变量 `PYTHON_BACKEND_URL` 指向后端
   - 自动构建：`npm install && npm run build`

更详细的部署步骤见仓库根目录的 `deploy-vercel-render.md`。

