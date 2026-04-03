# 糖尿病智能问答系统

本项目是一个面向糖尿病场景的智能问答与用户健康指标管理系统，是对 [基于知识图谱的糖尿病智能健康处方系统](https://github.com/ZBX05/Intelligent-Health-Prescription-System) 的二次开发，用于学习 Agent 系统。系统采用 Flask + LangChain Agent 架构，融合 Neo4j 知识图谱检索与关系型数据库中的用户身体指标数据，支持对话问答、历史记录、账户管理、身体指标维护和图谱可视化。

## 核心功能

1. 智能问答（Agent）  

- 通过 LangChain create_agent 组织多工具协作。
- 可调用图谱检索工具，将 Neo4j 查询结果作为回答依据。
- 可调用身体指标读取/更新工具，结合用户个人数据进行辅助分析。

2. 账户与权限  

- 用户注册、登录、退出。
- 管理员可创建账号、封禁/解封用户、处理消息。

3. 身体指标管理  

- 支持维护性别、年龄、身高、体重、FPG、OGTT、HbA1c。
- 前端表单支持默认值回填与基本输入约束。

4. 历史记录与图谱页面  

- 对话历史持久化保存并展示。
- 提供知识图谱检索和可视化页面。

## 技术架构

- 后端：Flask、Flask-Session、Gevent
- Agent：LangChain、langchain-openai、langchain-neo4j
- 图数据库：Neo4j（知识图谱）
- 关系数据库：MySQL（用户、历史、消息、身体指标）
- 前端：原生 HTML/CSS/JS + Bootstrap + Font Awesome + D3.js

## 开发环境需求

### 基础软件

| 名称 | 建议版本 | 说明 |
| :-- | :-- | :-- |
| Python | >= 3.10 | 建议使用 Conda 虚拟环境 |
| MySQL | >= 8.0 | 存储用户与历史数据 |
| Neo4j | >= 4.4 | 存储糖尿病知识图谱 |
| OpenSSL | >= 3.0 | 可选，仅 HTTPS 本地开发需要 |

### Python 主要依赖（按当前代码）

| 包名 | 用途 |
| :-- | :-- |
| flask | Web 应用 |
| flask-session | 会话存储 |
| gevent | WSGI 服务 |
| python-dotenv | 环境变量加载 |
| pymysql | MySQL 访问 |
| py2neo | Neo4j 浏览/查询辅助 |
| langchain | Agent 框架 |
| langchain-openai | LLM 调用 |
| langchain-neo4j | 图谱连接与查询 |
| langchain-community | 对话历史等组件 |

## 配置说明

1. 后端应用配置  

- 文件：backend/config/web_config.cfg
- 需配置：  
   - app.host / app.port
   - sql.host / sql.port / sql.user / sql.password / sql.db
   - cert_dir / key_dir（启用 HTTPS 时）

2. 大模型与图谱配置  

- 文件：backend/config/.env
- 需配置：
   - CHAT_API_KEY / CHAT_BASE_URL / CHAT_MODEL
   - GRAPH_API_KEY / GRAPH_BASE_URL / GRAPH_MODEL
   - NEO4J_URL / NEO4J_USERNAME / NEO4J_PASSWORD / NEO4J_DATABASE

3. 数据库初始化  

- 文件：database/create.sql
- 在 MySQL 中执行该脚本创建基础表。

## 启动方式

1. 安装依赖

```bash
pip install flask flask-session gevent python-dotenv pymysql py2neo \
   langchain langchain-openai langchain-neo4j langchain-community
```

2. 启动后端  

```bash
cd backend
python run.py
```

3. 访问系统  

- 默认地址以 web_config.cfg 的 host/port 为准。

## HTTPS 说明

- 开发环境可使用自签名证书。
- 证书与私钥默认路径由 web_config.cfg 中 cert_dir 和 key_dir 控制。
- 生产环境请替换为受信任证书，并关闭调试配置。

## 仓库目录说明（当前）

```text
health_agentic_system/
├─ backend/                 # Flask 后端与 Agent 主逻辑
├─ chat/                    # 独立聊天/实验模块
├─ database/                # MySQL 建库脚本
├─ frontend/                # 前端页面与静态资源
├─ graph/                   # 知识图谱构建与数据处理脚本
├─ nlp/                     # NLP 与模型相关数据/脚本
├─ framwork/                # 设计文档与流程图文件
├─ main.py                  # 顶层示例脚本
└─ README.md                # 项目说明文档
```
