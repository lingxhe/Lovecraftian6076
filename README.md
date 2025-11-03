## CoC 单人模组 · LLM KP（基础框架）

### 本地运行

1. 创建并激活虚拟环境（可选，推荐）
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 设置 OpenAI API Key（三种方式任选一种）：

**方式1：使用 .env 文件（推荐，最简单）**
- 复制 `.env.example` 文件并重命名为 `.env`
- 编辑 `.env` 文件，将 `your-api-key-here` 替换为你的实际 API Key
- 格式：`OPENAI_API_KEY=sk-...`

**方式2：Windows PowerShell（临时，当前会话有效）**
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
```

**方式3：Windows 系统环境变量（永久）**
- 右键"此电脑" -> "属性" -> "高级系统设置"
- 点击"环境变量"
- 在"用户变量"中点击"新建"
- 变量名：`OPENAI_API_KEY`
- 变量值：你的 API Key（sk-开头）
- 确定后重启终端

4. 启动应用（多页结构）：
```bash
streamlit run 1Creat Character.py
```

5. 浏览器会自动打开；若未自动打开，访问：`http://localhost:8501`

### 说明
- 采用 Streamlit 多页结构：`1Creat Character.py` 为第一页（Create Character），`pages/` 目录放其它页面。
- `1Creat Character.py`：创建角色（Name, Strength, Dexterity, HP, SAN），保存到 `st.session_state`。
- `pages/2_KP_Chat.py`：KP 对话（使用 LangGraph + LLM Agent）。
- LangGraph Agent 架构位于 `agents/kp_agent.py`。

### 获取 OpenAI API Key
1. 访问 https://platform.openai.com/api-keys
2. 登录或注册账户
3. 点击"Create new secret key"
4. 复制生成的 API Key（格式为 sk-...）
