"""TCP transport helpers. By design, targets must resolve to loopback addresses."""
from __future__ import annotations
import socket
import ipaddress

class TargetError(ValueError):
    pass

def validate_loopback_target(host: str, port: int) -> None:
    if not (1 <= int(port) <= 65535):
        raise TargetError("Port must be between 1 and 65535.")
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)}
    except socket.gaierror as exc:
        raise TargetError(f"Cannot resolve target host: {host}") from exc
    if not addresses:
        raise TargetError("Target did not resolve to an IP address.")
    if not all(ipaddress.ip_address(addr).is_loopback for addr in addresses):
        raise TargetError(
            "Safety restriction: ProtoFuzz only connects to localhost/loopback "
            "(127.0.0.1 or ::1). Use an isolated local lab service."
        )

def send_tcp(host: str, port: int, payload: bytes, timeout: float) -> dict:
    """Send one payload and capture a bounded response."""
    result = {"status": "ok", "response_hex": "", "response_text": "", "error": None}
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            sock.sendall(payload)
            try:
                response = sock.recv(4096)
            except socket.timeout:
                result["status"] = "timeout"
                result["error"] = "Response timeout"
                return result
            result["response_hex"] = response.hex()
            result["response_text"] = response.decode("utf-8", errors="replace")
    except (OSError, TimeoutError) as exc:
        result["status"] = "connection_error"
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result

def heartbeat(host: str, port: int, message: bytes, timeout: float) -> bool:
    result = send_tcp(host, port, message, timeout)
    return result["status"] == "ok"
