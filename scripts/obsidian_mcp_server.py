#!/usr/bin/env python3
"""Small MCP stdio server for Obsidian Local REST API."""

from __future__ import annotations

import json
import os
import ssl
import sys
import traceback
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


SERVER_NAME = "codex-obsidian-plugin"
SERVER_VERSION = "0.2.0"


class ObsidianError(Exception):
    pass


def _api_key() -> str:
    value = os.environ.get("OBSIDIAN_LOCAL_REST_API_KEY") or os.environ.get("OBSIDIAN_API_KEY")
    if not value:
        raise ObsidianError("Missing OBSIDIAN_LOCAL_REST_API_KEY or OBSIDIAN_API_KEY.")
    return value


def _base_url() -> str:
    value = os.environ.get("OBSIDIAN_LOCAL_REST_API_URL", "https://127.0.0.1:27124").strip()
    value = value.rstrip("/")
    if value.endswith("/mcp"):
        value = value[: -len("/mcp")]
    return value


def _ssl_context() -> ssl.SSLContext | None:
    if os.environ.get("OBSIDIAN_VERIFY_TLS") == "1":
        return None
    return ssl._create_unverified_context()


def _quote_path(path: str) -> str:
    return urllib.parse.quote(path.strip("/"), safe="/")


def _target_headers(args: dict[str, Any]) -> dict[str, str]:
    headers: dict[str, str] = {}
    target_type = args.get("target_type")
    target = args.get("target")
    if target_type:
        headers["Target-Type"] = str(target_type)
    if target:
        headers["Target"] = str(target)
    if args.get("target_delimiter"):
        headers["Target-Delimiter"] = str(args["target_delimiter"])
    if args.get("create_target_if_missing") is not None:
        headers["Create-Target-If-Missing"] = "true" if args["create_target_if_missing"] else "false"
    if args.get("apply_if_content_preexists") is not None:
        headers["Apply-If-Content-Preexists"] = "true" if args["apply_if_content_preexists"] else "false"
    if args.get("trim_target_whitespace") is not None:
        headers["Trim-Target-Whitespace"] = "true" if args["trim_target_whitespace"] else "false"
    return headers


def _request(
    method: str,
    path: str,
    *,
    query: dict[str, Any] | None = None,
    body: str | bytes | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    url = _base_url() + path
    if query:
        clean_query = {key: value for key, value in query.items() if value is not None}
        url += "?" + urllib.parse.urlencode(clean_query)

    request_headers = {
        "Authorization": f"Bearer {_api_key()}",
        "Accept": "application/json, text/markdown, text/plain",
    }
    request_headers.update(headers or {})

    data = None
    if body is not None:
        if isinstance(body, str):
            data = body.encode("utf-8")
        else:
            data = body
        request_headers.setdefault("Content-Type", "text/markdown; charset=utf-8")

    request = urllib.request.Request(url, data=data, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(request, context=_ssl_context(), timeout=30) as response:
            raw = response.read()
            text = raw.decode("utf-8", errors="replace")
            return {
                "status": response.status,
                "headers": dict(response.headers.items()),
                "body": _parse_body(text, response.headers.get("Content-Type", "")),
            }
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        text = raw.decode("utf-8", errors="replace")
        raise ObsidianError(
            json.dumps(
                {
                    "status": exc.code,
                    "reason": exc.reason,
                    "body": _parse_body(text, exc.headers.get("Content-Type", "")),
                },
                ensure_ascii=False,
                indent=2,
            )
        ) from exc
    except urllib.error.URLError as exc:
        raise ObsidianError(str(exc.reason)) from exc


def _parse_body(text: str, content_type: str) -> Any:
    if not text:
        return ""
    if "application/json" in content_type:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text
    return text


def _status(_: dict[str, Any]) -> Any:
    return _request("GET", "/")


def _list_files(args: dict[str, Any]) -> Any:
    directory = str(args.get("directory", "")).strip("/")
    if directory:
        return _request("GET", f"/vault/{_quote_path(directory)}/")
    return _request("GET", "/vault/")


def _get_note(args: dict[str, Any]) -> Any:
    note_path = _required(args, "path")
    output_format = args.get("format", "markdown")
    accept = {
        "markdown": "text/markdown",
        "metadata": "application/vnd.olrapi.note+json",
        "document_map": "application/vnd.olrapi.document-map+json",
    }.get(str(output_format), "text/markdown")
    headers = {"Accept": accept}
    headers.update(_target_headers(args))
    return _request("GET", f"/vault/{_quote_path(note_path)}", headers=headers)


def _put_note(args: dict[str, Any]) -> Any:
    note_path = _required(args, "path")
    content = _required(args, "content")
    headers = {"Content-Type": "text/markdown; charset=utf-8"}
    headers.update(_target_headers(args))
    return _request("PUT", f"/vault/{_quote_path(note_path)}", body=content, headers=headers)


def _append_note(args: dict[str, Any]) -> Any:
    note_path = _required(args, "path")
    content = _required(args, "content")
    headers = {"Content-Type": "text/markdown; charset=utf-8"}
    headers.update(_target_headers(args))
    return _request("POST", f"/vault/{_quote_path(note_path)}", body=content, headers=headers)


def _patch_note(args: dict[str, Any]) -> Any:
    note_path = _required(args, "path")
    content = _required(args, "content")
    operation = str(args.get("operation", "append"))
    if operation not in {"append", "prepend", "replace"}:
        raise ObsidianError("operation must be one of: append, prepend, replace")
    headers = {
        "Content-Type": "text/markdown; charset=utf-8",
        "Operation": operation,
    }
    headers.update(_target_headers(args))
    if "Target-Type" not in headers or "Target" not in headers:
        raise ObsidianError("patch_note requires target_type and target.")
    return _request("PATCH", f"/vault/{_quote_path(note_path)}", body=content, headers=headers)


def _search_simple(args: dict[str, Any]) -> Any:
    query = _required(args, "query")
    return _request(
        "POST",
        "/search/simple/",
        query={"query": query, "contextLength": args.get("context_length", 100)},
    )


def _dataview_query(args: dict[str, Any]) -> Any:
    query = _required(args, "query")
    return _request(
        "POST",
        "/search/",
        body=query,
        headers={"Content-Type": "application/vnd.olrapi.dataview.dql+txt"},
    )


def _jsonlogic_query(args: dict[str, Any]) -> Any:
    query = args.get("query")
    if query is None:
        raise ObsidianError("Missing required argument: query")
    body = query if isinstance(query, str) else json.dumps(query, ensure_ascii=False)
    return _request(
        "POST",
        "/search/",
        body=body,
        headers={"Content-Type": "application/vnd.olrapi.jsonlogic+json"},
    )


def _required(args: dict[str, Any], name: str) -> str:
    value = args.get(name)
    if value is None or value == "":
        raise ObsidianError(f"Missing required argument: {name}")
    return str(value)


TOOLS: dict[str, dict[str, Any]] = {
    "obsidian_status": {
        "description": "Check whether Obsidian Local REST API is reachable.",
        "handler": _status,
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    "obsidian_list_files": {
        "description": "List files in the vault root or a specific vault directory.",
        "handler": _list_files,
        "inputSchema": {
            "type": "object",
            "properties": {"directory": {"type": "string", "description": "Directory relative to the vault root."}},
            "additionalProperties": False,
        },
    },
    "obsidian_get_note": {
        "description": "Read a note as Markdown, metadata JSON, or a document map.",
        "handler": _get_note,
        "inputSchema": {
            "type": "object",
            "required": ["path"],
            "properties": {
                "path": {"type": "string"},
                "format": {"type": "string", "enum": ["markdown", "metadata", "document_map"], "default": "markdown"},
                "target_type": {"type": "string", "enum": ["heading", "block", "frontmatter"]},
                "target": {"type": "string"},
                "target_delimiter": {"type": "string", "default": "::"},
            },
            "additionalProperties": False,
        },
    },
    "obsidian_put_note": {
        "description": "Create or replace a note. Without a target, this replaces the entire file.",
        "handler": _put_note,
        "inputSchema": {
            "type": "object",
            "required": ["path", "content"],
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
                "target_type": {"type": "string", "enum": ["heading", "block", "frontmatter"]},
                "target": {"type": "string"},
                "target_delimiter": {"type": "string", "default": "::"},
                "apply_if_content_preexists": {"type": "boolean"},
                "trim_target_whitespace": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
    },
    "obsidian_append_note": {
        "description": "Append Markdown to a note, creating the file if it does not exist.",
        "handler": _append_note,
        "inputSchema": {
            "type": "object",
            "required": ["path", "content"],
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
                "target_type": {"type": "string", "enum": ["heading", "block", "frontmatter"]},
                "target": {"type": "string"},
                "target_delimiter": {"type": "string", "default": "::"},
                "create_target_if_missing": {"type": "boolean"},
                "apply_if_content_preexists": {"type": "boolean"},
                "trim_target_whitespace": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
    },
    "obsidian_patch_note": {
        "description": "Append, prepend, or replace Markdown at a heading, block, or frontmatter target.",
        "handler": _patch_note,
        "inputSchema": {
            "type": "object",
            "required": ["path", "content", "operation", "target_type", "target"],
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
                "operation": {"type": "string", "enum": ["append", "prepend", "replace"]},
                "target_type": {"type": "string", "enum": ["heading", "block", "frontmatter"]},
                "target": {"type": "string"},
                "target_delimiter": {"type": "string", "default": "::"},
                "create_target_if_missing": {"type": "boolean"},
                "apply_if_content_preexists": {"type": "boolean"},
                "trim_target_whitespace": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
    },
    "obsidian_search_simple": {
        "description": "Search vault notes using Obsidian Local REST API simple text search.",
        "handler": _search_simple,
        "inputSchema": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string"},
                "context_length": {"type": "number", "default": 100},
            },
            "additionalProperties": False,
        },
    },
    "obsidian_dataview_query": {
        "description": "Run a Dataview DQL TABLE query through Obsidian Local REST API.",
        "handler": _dataview_query,
        "inputSchema": {
            "type": "object",
            "required": ["query"],
            "properties": {"query": {"type": "string"}},
            "additionalProperties": False,
        },
    },
    "obsidian_jsonlogic_query": {
        "description": "Run a JsonLogic query against Obsidian note metadata.",
        "handler": _jsonlogic_query,
        "inputSchema": {
            "type": "object",
            "required": ["query"],
            "properties": {"query": {"type": ["object", "string"]}},
            "additionalProperties": False,
        },
    },
}


def _tool_specs() -> list[dict[str, Any]]:
    return [
        {"name": name, "description": spec["description"], "inputSchema": spec["inputSchema"]}
        for name, spec in TOOLS.items()
    ]


def _format_tool_result(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, indent=2)


def _read_message() -> dict[str, Any] | None:
    headers: dict[str, str] = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        if line in (b"\r\n", b"\n"):
            break
        name, _, value = line.decode("ascii", errors="replace").partition(":")
        headers[name.lower()] = value.strip()
    content_length = int(headers.get("content-length", "0"))
    if content_length <= 0:
        return None
    body = sys.stdin.buffer.read(content_length)
    return json.loads(body.decode("utf-8"))


def _write_message(message: dict[str, Any]) -> None:
    body = json.dumps(message, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(body)}\r\n\r\n".encode("ascii"))
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()


def _response(message_id: Any, result: Any = None, error: dict[str, Any] | None = None) -> dict[str, Any]:
    message: dict[str, Any] = {"jsonrpc": "2.0", "id": message_id}
    if error is not None:
        message["error"] = error
    else:
        message["result"] = result if result is not None else {}
    return message


def _handle(message: dict[str, Any]) -> dict[str, Any] | None:
    message_id = message.get("id")
    method = message.get("method")
    if message_id is None:
        return None

    try:
        if method == "initialize":
            protocol_version = message.get("params", {}).get("protocolVersion", "2024-11-05")
            return _response(
                message_id,
                {
                    "protocolVersion": protocol_version,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                },
            )
        if method == "ping":
            return _response(message_id, {})
        if method == "tools/list":
            return _response(message_id, {"tools": _tool_specs()})
        if method == "tools/call":
            params = message.get("params", {})
            tool_name = params.get("name")
            args = params.get("arguments") or {}
            if tool_name not in TOOLS:
                raise ObsidianError(f"Unknown tool: {tool_name}")
            result = TOOLS[tool_name]["handler"](args)
            return _response(
                message_id,
                {
                    "content": [{"type": "text", "text": _format_tool_result(result)}],
                    "isError": False,
                },
            )
        return _response(message_id, error={"code": -32601, "message": f"Method not found: {method}"})
    except Exception as exc:
        if os.environ.get("OBSIDIAN_MCP_DEBUG") == "1":
            traceback.print_exc(file=sys.stderr)
        return _response(
            message_id,
            {
                "content": [{"type": "text", "text": str(exc)}],
                "isError": True,
            },
        )


def main() -> int:
    while True:
        message = _read_message()
        if message is None:
            return 0
        response = _handle(message)
        if response is not None:
            _write_message(response)


if __name__ == "__main__":
    raise SystemExit(main())
