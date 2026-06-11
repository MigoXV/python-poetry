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
