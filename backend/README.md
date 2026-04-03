# 后端模块  

## 目录说明  

**注意：** 如果想要使用 HTTPS 协议，需要在 `config/web_config.cfg` 中配置证书与密钥路径，并在前端 `common.js` 中同步调整协议。  
**当前仓库中使用的是HTTP协议，未提供SSL证书，生产环境请替换为HTTPS协议并配备正式SSL证书。**

```text
backend                             # 后端模块根目录
├─ config/                          # 配置文件目录
│  ├─ .env                          # 大模型、Neo4j 等环境变量配置
│  └─ web_config.cfg                # Web 服务与数据库连接配置
├─ ssl/                             # 证书目录
│  ├─ *.crt                         # 服务端证书
│  └─ *.key                         # 服务端私钥
├─ agent.py                         # Agent 编排与模型调用入口
├─ tools.py                         # Agent 工具定义（图谱检索、身体指标读写）
├─ web.py                           # Flask Web 应用与路由
├─ run.py                           # 服务启动入口
├─ sql.py                           # MySQL 数据库访问层
├─ graph_.py                        # 图谱相关辅助逻辑
├─ parse.py                         # 问句解析逻辑
├─ functionsAndClasses.py           # 通用函数与配置类封装
└─ README.md                        # 后端模块说明文档
```  
