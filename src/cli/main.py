from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Literal

import typer
from pydantic import BaseModel

from src.application.orchestrators.mode_registry import MODE_REGISTRY
from src.cli.transports import TransportError, build_transport
from src.domain.formatters.output_formatter import format_output
from src.domain.models.schemas import AnalysisRequest

app = typer.Typer(help="Thin client for PR Reviewer + Test Assistant")


class CliOptions(BaseModel):
    diff: str | None = None
    metadata: str | None = None
    context: str | None = None
    existing_tests: str | None = None
    output: str = "text"
    json_flag: bool = False
    transport: Literal["http", "local"] = "http"
    server_url: str | None = None


def _load_json_file(path: str | None) -> dict | None:
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _read_diff(diff_path: str | None) -> str:
    if diff_path:
        return Path(diff_path).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise typer.BadParameter("Provide --diff path or pipe diff via stdin")


def _run(mode: str, opts: CliOptions) -> None:
    diff = _read_diff(opts.diff)
    request = AnalysisRequest(
        diff=diff,
        metadata=_load_json_file(opts.metadata),
        context=_load_json_file(opts.context),
        existing_tests=_load_json_file(opts.existing_tests),
    )
    try:
        transport = build_transport(transport=opts.transport, server_url=opts.server_url)
        response = transport.send(mode, request)
    except TransportError as exc:
        raise typer.BadParameter(str(exc))

    as_json = opts.json_flag or opts.output.lower() == "json"
    typer.echo(format_output(response, as_json=as_json))


def _add_mode_command(mode: str):
    def _cmd(
        diff: str | None = typer.Option(None, "--diff", help="Patch file path. If omitted reads stdin."),
        metadata: str | None = typer.Option(None, "--metadata", help="Path to metadata JSON"),
        context: str | None = typer.Option(None, "--context", help="Path to context JSON"),
        existing_tests: str | None = typer.Option(None, "--existing-tests", help="Path to existing tests JSON"),
        output: str = typer.Option("text", "--output", help="text or json"),
        json_flag: bool = typer.Option(False, "--json", help="Output JSON"),
        transport: Literal["http", "local"] = typer.Option("http", "--transport", help="http or local"),
        server_url: str | None = typer.Option(None, "--server-url", help="Remote server URL for http transport"),
    ):
        _run(
            mode,
            CliOptions(
                diff=diff,
                metadata=metadata,
                context=context,
                existing_tests=existing_tests,
                output=output,
                json_flag=json_flag,
                transport=transport,
                server_url=server_url,
            ),
        )

    app.command(name=mode)(_cmd)


for mode_name in MODE_REGISTRY:
    _add_mode_command(mode_name)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
