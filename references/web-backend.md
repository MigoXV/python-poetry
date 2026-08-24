# Python 后端配套前端约定

仅在 Python 项目需要配套浏览器前端时读取并执行本文件。纯 Python、CLI 或库项目继续使用 `SKILL.md` 的普通模板。

## 初始化与目录

新项目统一采用以下结构：

```text
.
├── .vscode/
│   ├── launch.json
│   └── tasks.json
├── pyproject.toml
└── src/
    ├── <package_name>/
    │   └── web/
    │       └── app.py
    └── web/
        ├── package.json
        ├── pnpm-lock.yaml
        ├── vite.config.ts
        ├── index.html
        └── src/
```

1. 将 `templates/web/` 复制到 `src/web/`，使用 React、TypeScript、Vite 和 pnpm，不创建 npm 或 Yarn 锁文件。
2. 将 `templates/web-app.py` 复制到 `src/<package_name>/web/app.py`，并补齐各级 `__init__.py`。
3. 通过 Poetry 添加 `fastapi[standard]`，不要使用系统 Python 安装后端依赖。
4. 将 `templates/launch.web.json` 和 `templates/tasks.web.json` 复制到 `.vscode/`；既有配置应按名称和任务标签合并。
5. 提交 `src/web/pnpm-lock.yaml`，忽略 `src/web/node_modules/` 和 `src/web/dist/`。

既有项目保留已经选定的前端代码、后端框架和服务入口，避免无关迁移；但前端根目录、pnpm 构建命令、输出目录、后端托管和调试前构建行为必须统一。如果移动既有前端会破坏明确的项目约定，先向用户说明冲突并确认范围。

## MANAS 界面路由

当前端明确采用 MANAS、类纸工作空间、沿用 MANAS 风格，或目标仓库已声明采用 MANAS 时，同时读取并执行上级目录中的 `../manas-paper-ui` skill。若该目录不存在，先从 `python-poetry` skill 目录运行 `./pull_related_skills.sh` 自动补齐，再继续界面工作。

本文件负责 React/Vite 目录、依赖、构建产物、后端托管和调试集成；`manas-paper-ui` 负责工作模式、页面范式、设计判断、交互约束与界面验证。项目已有更具体的设计系统约定时，先按 MANAS skill 的映射流程理解并复用，不要直接用模板覆盖。

仅有“简洁”“现代”或“极简”等一般视觉要求时，不自动采用 MANAS，也不需要安装或加载该 skill。

## 构建与运行

从仓库根目录执行：

```bash
pnpm --dir src/web install
pnpm --dir src/web run build
poetry run uvicorn <package_name>.web.app:app
```

`src/web/package.json` 必须至少提供 `dev`、`build`、`preview` 和 `lint` 脚本。Vite 的 `build.outDir` 必须显式设置为 `dist`，因此构建结果固定为 `src/web/dist`。

`pnpm run dev` 仅用于明确需要 Vite HMR 的前端开发，不作为标准项目启动方式。标准运行、生产部署和 VS Code 后端调试均先构建前端，再由后端统一托管 `dist`。生产镜像或发布目录必须包含构建后的 `src/web/dist`。

## FastAPI 托管

新项目以 `<package_name>.web.app:app` 暴露 FastAPI 应用。使用 FastAPI 的 `app.frontend()` 托管构建目录：

```python
from pathlib import Path

from fastapi import FastAPI, HTTPException

WEB_DIST_DIR = Path(__file__).resolve().parents[2] / "web" / "dist"

app = FastAPI()

# 先定义或包含 API 路由，再阻止未知 API GET/HEAD 落入 SPA 回退。

@app.api_route(
    "/api",
    methods=["GET", "HEAD"],
    include_in_schema=False,
)
async def api_root_not_found() -> None:
    raise HTTPException(status_code=404, detail="API route not found: /api")

@app.api_route(
    "/api/{path:path}",
    methods=["GET", "HEAD"],
    include_in_schema=False,
)
async def api_not_found(path: str) -> None:
    raise HTTPException(status_code=404, detail=f"API route not found: /api/{path}")

app.frontend(
    "/",
    directory=WEB_DIST_DIR,
    fallback="index.html",
)
```

- SPA 使用 `fallback="index.html"`，使浏览器直接访问客户端路由时仍返回应用入口；多页应用省略 `fallback`。
- 保持目录检查启用。`dist` 缺失时应在后端启动阶段明确失败，不能静默提供空站点。
- FastAPI 普通路由必须在 `/api/{path:path}` 兜底和 `app.frontend()` 之前注册。API 兜底拦截未知 GET/HEAD，确保带 HTML `Accept` 头的未知 API 也返回 404；`/docs`、`/redoc`、`/openapi.json` 和实际静态文件仍由各自路由处理。
- 既有 FastAPI 版本没有 `app.frontend()` 且无法在项目约束内升级时，使用 Starlette/FastAPI 静态响应实现等价行为，并测试相同优先级和回退规则。
- 既有非 FastAPI 后端使用框架原生静态文件能力实现相同行为，不为此迁移后端框架。

## VS Code 调试

`templates/tasks.web.json` 定义 `web: build`：在 `${workspaceFolder}/src/web` 执行 `pnpm run build`。`templates/launch.web.json` 使用 debugpy 启动 `uvicorn`，并设置：

```json
"preLaunchTask": "web: build"
```

后端 Debug 配置必须保留 `"envFile": "${workspaceFolder}/.env"`。不要为调试命令添加 `--reload`，避免重载子进程干扰断点。既有 `launch.json` 只给后端服务配置追加该前置任务，不修改 CLI、测试或其他无关调试配置。

## README 与验证

中文 `README.md` 必须说明：

- Node.js、pnpm 和 Poetry 是开发依赖。
- 首次安装使用 `pnpm --dir src/web install` 和 `poetry install`。
- 标准构建使用 `pnpm --dir src/web run build`。
- 后端是标准运行入口，并统一托管 `src/web/dist`。
- VS Code 后端 Debug 会自动先执行一次前端构建。

完成前至少验证：

1. `pnpm --dir src/web run lint` 和 `pnpm --dir src/web run build` 成功，且生成 `dist/index.html`。
2. 通过 Poetry 启动或测试后端，API、首页和实际静态资源可访问。
3. SPA 项目直接访问深层路由返回 `index.html`；分别使用 JSON 和 HTML `Accept` 头访问未知 API，均保持 API 的 404 行为。
4. 临时移除或重命名 `dist` 后，后端启动给出清晰错误；验证后恢复构建产物。
5. `launch.json` 引用的 `preLaunchTask` 与 `tasks.json` 中的 `web: build` 标签完全一致。
