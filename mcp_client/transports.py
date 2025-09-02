"""Minimal transport utilities."""

from fastmcp.client.transports import StdioTransport, StreamableHttpTransport


def create_stdio_transport(command: str, args: list) -> StdioTransport:
    return StdioTransport(command=command, args=args)


def create_http_transport(base_url: str, headers: dict) -> StreamableHttpTransport:
    return StreamableHttpTransport(base_url=base_url, headers=headers)