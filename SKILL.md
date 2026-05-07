---
name: create-poetry-project
description: Use this skill when creating, updating, or reviewing a Python project that should use Poetry, Typer CLI entry points, Chinese README documentation, logging conventions, and VS Code debugging configuration.
metadata:
  short-description: Create Poetry Python CLI projects
---

# 创建 Poetry 项目

当任务涉及创建、更新或规范化使用 Poetry 的 Python 项目时，使用本 skill。修改项目文件前，先按本文检查项目结构、入口模块、依赖工作流、日志配置和编辑器配置，确保项目约定一致。

## 沟通要求

- 默认使用中文与用户沟通。
- 修改代码前先理解项目结构、入口、调用链和已有风格。
- 优先做最小必要修改，避免无关重构。
- 如果项目已有更具体、更明确的约定，优先遵循项目内约定。
- `README.md` 必须使用中文编写。

## 工作流程

1. 修改前检查仓库结构、现有包名、`pyproject.toml`、CLI 模块、测试和 README。
2. 使用 Poetry 管理依赖、虚拟环境、脚本执行、测试和应用启动。
3. 确保 Python CLI 入口模块位于 `<package_name>/commands/app.py`。
4. 确保 CLI 模块使用 Typer，并暴露 `app = typer.Typer()`。
5. CLI 参数必须使用 `typer.Option` 和 `typer.Argument`；适合通过环境变量配置的参数必须显式设置 `envvar`。
6. 在 `app.py` 中使用 `logging.basicConfig(...)` 配置基础日志；各模块使用模块级 `logger = logging.getLogger(__name__)`。
7. 新增或更新 `.vscode/launch.json`，提供基于 module 的 `<package_name>.commands.app` 调试配置，并确保每个配置都包含 `"envFile": "${workspaceFolder}/.env"`。
8. 可行时通过 Poetry 运行验证命令，例如 `poetry install`、`poetry run pytest` 或项目对应命令。

## Poetry 使用约定

默认使用 Poetry 命令：

```bash
poetry install
poetry run python -m <package_name>.commands.app
poetry run pytest
```

不要假设系统 Python 环境可用。需要运行 Python 命令时，优先使用 Poetry 虚拟环境。

如果需要在 `pyproject.toml` 中暴露命令行入口，优先使用 Poetry scripts，并将入口指向 Typer app 对象：

```toml
[tool.poetry.scripts]
app = "<package_name>.commands.app:app"
```

如果项目已有更具体的命令名，可以保留该命令名，但入口模块仍应遵循 `<package_name>.commands.app` 约定。

## CLI 模块模式

创建或规范化如下 CLI 入口：

```text
<package_name>/commands/app.py
```

使用以下基础模式：

```python
from __future__ import annotations

import logging
from pathlib import Path

import typer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = typer.Typer()


@app.command()
def main(
    input_path: Path = typer.Argument(
        ...,
        help="输入文件路径",
        envvar="APP_INPUT_PATH",
    ),
    output_dir: Path = typer.Option(
        Path("outputs"),
        "--output-dir",
        "-o",
        help="输出目录",
        envvar="APP_OUTPUT_DIR",
    ),
) -> None:
    logger.info("Starting app")
    logger.info("Input path: %s", input_path)
    logger.info("Output dir: %s", output_dir)


if __name__ == "__main__":
    app()
```

命令必须使用 `@app.command()` 注册。尽量避免 `print(...)`；只有明确需要标准输出作为程序结果时才使用。

## VS Code 调试配置

Python 项目应提供 `.vscode/launch.json`。

该文件必须包含一个用于调试 app module 的配置：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: App Module",
      "type": "python",
      "request": "launch",
      "module": "<package_name>.commands.app",
      "console": "integratedTerminal",
      "justMyCode": true,
      "envFile": "${workspaceFolder}/.env",
      "args": []
    }
  ]
}
```

新增任何 VS Code 调试配置时，都必须包含：

```json
"envFile": "${workspaceFolder}/.env"
```

## 最终检查

完成前，说明修改了哪些文件，以及运行过哪些验证命令。如果无法验证，简要说明原因。
