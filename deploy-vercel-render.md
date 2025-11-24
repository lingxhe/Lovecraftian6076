# Vercel + Render 部署指南

本项目使用 **Next.js 前端** + **FastAPI 后端**。推荐架构：

- Vercel：部署 `web/` 前端
- Render（或 Railway）：部署 `api_server.py` 后端

## 一、部署 FastAPI 后端到 Render

1. 登录 https://render.com ，选择 *New +* → *Web Service*
2. 绑定 GitHub 仓库，Root Directory 选仓库根目录
3. Build 命令：
   ```
   pip install -r requirements.txt && pip install -r requirements-web.txt
   ```
4. Start 命令：
   ```
   uvicorn api_server:app --host 0.0.0.0 --port $PORT
   ```
5. 环境变量（可选）：
   - `ALLOWED_ORIGINS` = `https://your-frontend.vercel.app`
   - `OPENAI_API_KEY`（若想后端托管 API Key）
6. 部署完成后记下 Render 生成的 HTTPS URL，例如 `https://coc-api.onrender.com`

## 二、部署 Next.js 前端到 Vercel

1. 登录 https://vercel.com
2. 新建项目 → 导入仓库
3. Root Directory 选择 `web`
4. 环境变量：
   - `PYTHON_BACKEND_URL` = Render 后端 URL（例如 `https://coc-api.onrender.com`）
5. 其他配置沿用默认（Next.js 自动检测）
6. 首次部署后即可访问 `https://your-project.vercel.app`

## 三、本地联调

```bash
# 终端1：运行 FastAPI
pip install -r requirements.txt
pip install -r requirements-web.txt
uvicorn api_server:app --reload --port 8000

# 终端2：运行 Next.js
cd web
npm install
npm run dev
```

前端默认调用 `http://localhost:8000`，无需额外配置。

## 四、验证 checklist

- [ ] Render 后端 `/api/health` 返回 `{"status":"ok"}`
- [ ] Vercel 环境变量 `PYTHON_BACKEND_URL` 已配置
- [ ] 角色创建、LUCK 规则、技能预算等逻辑正常
- [ ] Keeper 聊天可触发工具调用 / 场景切换
- [ ] Markdown 日志可下载

## 常见问题

| 问题 | 解决方案 |
| ---- | -------- |
| `CORS error` | 确保 `ALLOWED_ORIGINS` 包含 Vercel 域名；Render 端重启 |
| `Unable to get KP response` | 检查 Render 服务是否在休眠；确认 API Key 有效 |
| `Download log failed` | Render 免费实例休眠时无法读取，唤醒后再次尝试 |

如需一键查看日志，可在 Render 控制台进入服务 → *Logs*。

