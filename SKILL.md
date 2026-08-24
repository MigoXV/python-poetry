---
name: python-poetry
description: Use this skill as the main entry point for Python project work, including creating, updating, running, testing, reviewing, or standardizing Poetry projects, Typer CLIs, FastAPI backends with React/Vite frontends, Chinese README documentation, logging, and VS Code debugging. For Python gRPC/Protobuf work, route to the protos skill. For deep learning inference work, route to the dl-inference skill. For deep learning training framework work, route to the dl-train skill. For frontends explicitly using MANAS or a paper-like workspace, also route to the manas-paper-ui skill.
metadata:
  short-description: Python project conventions with Poetry
---

# Python 工程约定

当任务涉及任何 Python 工程时，默认使用本 skill，包括创建、更新、运行、测试、调试、审查或规范化 Python 项目。修改项目文件前，先检查项目结构、入口模块、依赖工作流、日志配置和编辑器配置，确保项目约定一致。

## 沟通与编辑原则

- 默认使用中文与用户沟通。
- 修改代码前先理解项目结构、入口、调用链和已有风格。
- 优先做最小必要修改，避免无关重构。
- 如果项目已有更具体、更明确的约定，优先遵循项目内约定。
- `README.md` 必须使用中文编写。

## 标准工作流程

1. 修改前检查仓库结构、现有包名、`pyproject.toml`、CLI 模块、测试和 README。
2. 使用 Poetry 管理依赖、虚拟环境、脚本执行、测试和应用启动；不要假设系统 Python 环境可用。
3. 确保 Python CLI 入口模块位于 `<package_name>/commands/app.py`，使用 Typer，并暴露 `app = typer.Typer()`。
4. CLI 参数必须使用 `typer.Option` 和 `typer.Argument`；适合通过环境变量配置的参数必须显式设置 `envvar`。
5. 在 `app.py` 中使用 `logging.basicConfig(...)` 配置基础日志；各模块使用模块级 `logger = logging.getLogger(__name__)`。
6. 新增或更新 `.vscode/launch.json` 时，提供基于 module 的 `<package_name>.commands.app` 调试配置，并确保每个配置都包含 `"envFile": "${workspaceFolder}/.env"`。
7. 当 Python 项目作为后端并配套浏览器前端时，先完整阅读 [references/web-backend.md](references/web-backend.md)，再初始化、托管或调试前端。
8. 当前端明确采用 MANAS、类纸工作空间，或目标仓库已声明采用 MANAS 时，同时使用上级目录中的 `../manas-paper-ui` skill；缺失时先运行 `pull_related_skills.sh` 自动补齐。普通“简洁”“现代”或“极简”前端不因此自动采用 MANAS。
9. 可行时通过 Poetry 运行验证命令，例如 `poetry install`、`poetry run pytest` 或项目对应命令。
10. 完成前说明修改了哪些文件，以及运行过哪些验证命令；如果无法验证，简要说明原因。

## 项目初始化

新建或初始化 Poetry Python 项目时，必须完成本节检查，不要只创建文件后跳过配置。

首先优先使用当前 skill 的模板创建或规范化项目文件：

- `templates/pyproject.toml` -> `pyproject.toml`
- `templates/app.py` -> `src/<package_name>/commands/app.py`
- `templates/launch.json` -> `.vscode/launch.json`
- `templates/gitignore` -> `.gitignore`

后端项目需要配套前端时，还要按照 [references/web-backend.md](references/web-backend.md) 使用以下模板：

- `templates/web/` -> `src/web/`
- `templates/web-app.py` -> `src/<package_name>/web/app.py`
- `templates/launch.web.json` -> `.vscode/launch.json`
- `templates/tasks.web.json` -> `.vscode/tasks.json`

如果目标文件已经存在，合并必要配置，不要直接覆盖用户已有内容。

复制模板后，必须替换所有占位符：

- `<project-name>`：发布包名，使用 kebab-case。
- `<package_name>`：源码包名，使用有效 Python 包名，通常是 snake_case。
- `<author-name>` 和 `<author-email>`：项目作者信息。优先从 Git 配置读取 `git config user.name` 和 `git config user.email`；如果当前仓库未配置，再读取全局配置 `git config --global user.name` 和 `git config --global user.email`。如果 Git 中仍没有可用信息，随机生成一组得体、中性、明显非真实个人隐私的作者信息，例如英文名配 `example.com` 邮箱，不要留空。

模板只保留通用依赖。新增业务依赖前先检查项目实际 import、运行入口和 README，不要把其他项目的依赖带进来。

`pyproject.toml` 必须引入清华源，源配置放在 `[build-system]` 上方，即 TOML 文件的倒数第二项。`requires-python` 统一为 `>=3.10,<3.13`；如果项目已有更严格且合理的 Python 版本约束，先遵循项目内约定。

使用 Python 3.10 创建 Poetry 虚拟环境：

```bash
poetry env use python3.10
poetry install
```

创建并编辑 `.gitignore`。优先使用 `templates/gitignore`，再按项目实际产物补充必要规则。

初始化完成后提交一次：

```bash
git add .
git commit -m init
```

创建 `dev` 和 `feature/<项目名>` 分支，并切换到 `feature/<项目名>`：

```bash
git branch dev
git switch -c feature/<项目名>
```

## Poetry 与 Typer CLI

默认使用 Poetry 命令：

```bash
poetry install
poetry run python -m <package_name>.commands.app
poetry run pytest
```

不要假设系统 Python 环境可用。需要运行 Python 命令时，优先使用 Poetry 虚拟环境。

如果需要在 `pyproject.toml` 中暴露命令行入口，优先使用 Poetry scripts，并将入口指向 Typer app 对象。新项目默认使用 `templates/pyproject.toml` 中的 `[tool.poetry.scripts]`。不要把入口指向具体命令函数，例如 `:main`；Typer 项目入口应指向 `app` 对象。

如果项目已有更具体的命令名，可以保留该命令名，但入口模块仍应遵循 `<package_name>.commands.app` 约定。

如果既有项目已经使用 PEP 621 的 `[project.scripts]` 且项目约定明确，可以保留现状，避免为了统一而做无关迁移。

创建或规范化如下 CLI 入口：

```text
<package_name>/commands/app.py
```

优先使用 `templates/app.py` 作为基础模式，再按业务命令调整参数和实现。

命令必须使用 `@app.command()` 注册。尽量避免 `print(...)`；只有明确需要标准输出作为程序结果时才使用。

## VS Code 调试配置

Python 项目应提供 `.vscode/launch.json`。优先使用当前 skill 的模板创建或规范化调试配置：

```text
templates/launch.json
```

复制模板到目标项目的 `.vscode/launch.json` 后，必须将 `<package_name>` 替换为实际源码包名。该文件必须包含一个用于调试 app module 的配置。

新增任何 VS Code 调试配置时，都必须包含：

`"envFile": "${workspaceFolder}/.env"`。

对于配套 `src/web` 前端的后端项目，改用全栈调试模板。仅后端服务 Debug 配置追加 `"preLaunchTask": "web: build"`；CLI、测试等非后端配置不追加前端构建任务。具体合并规则见 [references/web-backend.md](references/web-backend.md)。

## Python 后端与配套前端

当同一项目包含 Python 后端和浏览器前端时，统一使用以下边界：

- 前端根目录固定为 `src/web`，使用 React、TypeScript、Vite 和 pnpm。
- 前端构建产物固定为 `src/web/dist`，由 Python 后端托管；不要默认把前后端作为两个长期独立服务运行。
- 新项目后端使用 FastAPI，入口为 `<package_name>.web.app:app`；既有项目保留已有框架和服务入口，只统一构建目录及托管行为。
- VS Code 启动后端调试前必须执行一次 `web: build`，确保后端托管最新构建产物。

执行这类任务前必须完整阅读 [references/web-backend.md](references/web-backend.md)。

## 任务路由

- 任务涉及 `.proto`、gRPC、Protobuf、`grpcio-tools`、`mypy-protobuf`、`*_pb2.py`、`*_pb2_grpc.py`、生成脚本或内置 proto 文件时，使用上级目录中的 `../protos` skill；本 skill 只提供 Poetry 环境和 Python 工程约定。
- 任务涉及深度学习推理、模型加载、device/dtype 处理、batch/stream 推理、runtime/runner 抽象、推理 gRPC 服务或推理验证基准时，使用上级目录中的 `../dl-inference` skill；本 skill 只提供 Poetry 环境和 Python 工程约定。
- 任务涉及深度学习训练框架、Lightning 风格训练、模型注册、数据管道、typed YAML 配置、checkpoint、resume、export、实验日志或训练测试时，使用上级目录中的 `../dl-train` skill；本 skill 只提供 Poetry 环境和 Python 工程约定。
- 任务涉及明确的 MANAS、类纸工作空间、沿用 MANAS 风格，或目标仓库已声明采用 MANAS 时，同时使用上级目录中的 `../manas-paper-ui` skill；本 skill 继续负责 Python、Poetry、前后端目录和构建集成，MANAS skill 负责界面模式、设计判断与对应验证。不要仅因普通的“简洁”“现代”或“极简”要求触发该路由。

相关 skill 仓库可用当前目录的 `pull_related_skills.sh` 拉取、更新或自动补齐；脚本默认使用各仓库的 GitHub `origin`。任务命中上述路由但对应目录不存在时，先运行该脚本，再读取并执行对应 skill。

## 最终检查

完成 Python 项目修改前，检查以下事项：

- 是否理解并遵循了项目内更具体的约定。
- 是否避免了无关重构和不必要的依赖变更。
- 是否使用 Poetry 运行安装、脚本、测试或应用启动命令。
- 深度学习推理相关任务是否联动 `dl-inference`，并保持模型加载、任务推理、runtime/runner 和服务协议边界清晰。
- CLI 入口是否位于 `<package_name>/commands/app.py`。
- Typer CLI 是否暴露 `app = typer.Typer()`，命令是否使用 `@app.command()` 注册。
- CLI 参数是否使用 `typer.Option` 或 `typer.Argument`，需要环境变量配置的参数是否显式设置 `envvar`。
- `app.py` 是否配置 `logging.basicConfig(...)`，各模块是否使用模块级 logger。
- `.vscode/launch.json` 中每个调试配置是否包含 `"envFile": "${workspaceFolder}/.env"`。
- 配套前端是否位于 `src/web`，使用 pnpm，并将构建产物输出到 `src/web/dist`。
- 后端是否托管 `src/web/dist`，API、OpenAPI 和实际静态文件请求是否不会被 SPA 回退覆盖。
- 后端 Debug 配置是否使用 `"preLaunchTask": "web: build"`，对应任务是否在 `src/web` 执行 `pnpm run build`。
- 是否提交 `pnpm-lock.yaml`，并忽略 `src/web/node_modules/` 和 `src/web/dist/`。
- 明确采用 MANAS 或类纸工作空间的前端是否联动 `manas-paper-ui`，并按其工作模式、设计基础和验证交付约定执行。
- `README.md` 是否使用中文。

最终回复中说明修改了哪些文件，以及运行过哪些验证命令。如果无法验证，简要说明原因。
