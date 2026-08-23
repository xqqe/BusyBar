"""Stable BUSY Bar transport, cycling, refreshing, and button handling."""

from __future__ import annotations

import asyncio
import json
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable, Protocol

from busylib import AsyncBusyBar, BusyBar

import config


class Screen(Protocol):
    name: str
    refresh_seconds: float | None

    def render(self) -> list[dict[str, Any]]:
        ...


def _argument_value(name: str) -> str | None:
    if name not in sys.argv:
        return None

    index = sys.argv.index(name)
    if index + 1 >= len(sys.argv):
        raise ValueError(f"{name} requires a value.")

    return sys.argv[index + 1]


def _has_flag(name: str) -> bool:
    return name in sys.argv


def _normalize_url(host: str) -> str:
    host = host.strip().rstrip("/")

    if not host.startswith(("http://", "https://")):
        host = "http://" + host

    return host


def resolve_connection() -> tuple[str, str | None, str]:
    host_override = _argument_value("--host")
    token_override = _argument_value("--token")

    if host_override:
        base_url = _normalize_url(host_override)
        token = token_override or config.WIFI_API_TOKEN
        return base_url, token, f"custom host {base_url}"

    if _has_flag("--usb"):
        base_url = f"http://{config.USB_IP}"
        return base_url, None, f"USB at {base_url}"

    if _has_flag("--wifi"):
        base_url = f"http://{config.WIFI_IP}"
        token = token_override or config.WIFI_API_TOKEN
        return base_url, token, f"Wi-Fi at {base_url}"

    if config.DEFAULT_CONNECTION.lower() == "usb":
        base_url = f"http://{config.USB_IP}"
        return base_url, None, f"USB at {base_url}"

    base_url = f"http://{config.WIFI_IP}"
    return base_url, config.WIFI_API_TOKEN, f"Wi-Fi at {base_url}"


BASE_URL, API_TOKEN, CONNECTION_DESCRIPTION = resolve_connection()


def _headers(content_type: str | None = None) -> dict[str, str]:
    headers = {"Accept": "application/json"}

    if content_type:
        headers["Content-Type"] = content_type

    if API_TOKEN:
        headers["X-Api-Token"] = API_TOKEN

    return headers


def http_request(
    method: str,
    path: str,
    *,
    data: bytes | None = None,
    content_type: str | None = None,
) -> bytes:
    url = BASE_URL + path

    request = urllib.request.Request(
        url=url,
        data=data,
        method=method,
        headers=_headers(content_type),
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=config.REQUEST_TIMEOUT_SECONDS,
        ) as response:
            return response.read()

    except urllib.error.HTTPError as exc:
        response_text = exc.read().decode("utf-8", errors="replace")

        if exc.code == 403:
            raise RuntimeError(
                "HTTP 403 Forbidden: the BUSY Bar was reached, but the "
                "Wi-Fi API token was rejected or missing."
            ) from exc

        raise RuntimeError(
            f"HTTP {exc.code} {exc.reason}\n"
            f"URL: {url}\n"
            f"Response: {response_text}"
        ) from exc

    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Cannot reach BUSY Bar at {BASE_URL}: {exc.reason}"
        ) from exc


def upload_asset(filename: str, data: bytes) -> None:
    """
    Upload an asset using busylib's correctly formatted request.
    """

    with BusyBar(
        _websocket_host(),
        token=API_TOKEN,
    ) as busy_bar:
        response = busy_bar.assets_upload(
            application_name=config.APPLICATION_NAME,
            filename=filename,
            data=data,
        )

    result = getattr(response, "result", None)

    if result not in (None, "OK"):
        raise RuntimeError(
            f"BUSY Bar asset upload failed: {response}"
        )
def draw_elements(elements: list[dict[str, Any]]) -> None:
    body = {
        "application_name": config.APPLICATION_NAME,
        "elements": elements,
    }

    http_request(
        "POST",
        "/api/display/draw",
        data=json.dumps(body).encode("utf-8"),
        content_type="application/json",
    )


def clear_display() -> None:
    app_name = urllib.parse.quote(config.APPLICATION_NAME, safe="")

    try:
        http_request(
            "DELETE",
            f"/api/display/draw?application_name={app_name}",
        )
    except RuntimeError:
        pass


def _websocket_host() -> str:
    return (
        BASE_URL
        .removeprefix("http://")
        .removeprefix("https://")
        .rstrip("/")
    )


class ScreenController:
    def __init__(self, screens: list[Screen]) -> None:
        if not screens:
            raise ValueError("config.SCREENS must contain at least one screen.")

        self.screens = screens
        self.index = 0
        self.lock = threading.RLock()
        self.last_draw_time = 0.0

    def draw_current(self) -> None:
        with self.lock:
            screen = self.screens[self.index]

        # Image-producing screens can optionally prepare/upload assets before
        # returning their display elements.
        prepare = getattr(screen, "prepare", None)
        if callable(prepare):
            prepare(upload_asset)

        with self.lock:
            elements = screen.render()

        draw_elements(elements)

        with self.lock:
            self.last_draw_time = time.monotonic()

    def next(self) -> None:
        with self.lock:
            self.index = (self.index + 1) % len(self.screens)
            screen_name = self.screens[self.index].name

        print(f"Screen: {screen_name}")
        self.draw_current()

    def refresh_if_due(self) -> None:
        with self.lock:
            screen = self.screens[self.index]
            interval = screen.refresh_seconds
            elapsed = time.monotonic() - self.last_draw_time

        if interval is not None and elapsed >= interval:
            self.draw_current()


def refresh_loop(
    controller: ScreenController,
    stop_event: threading.Event,
) -> None:
    while not stop_event.wait(0.1):
        try:
            controller.refresh_if_due()
        except RuntimeError as exc:
            if "HTTP 409" not in str(exc):
                print(f"Refresh error: {exc}")


async def listen_for_start_button(
    controller: ScreenController,
    stop_event: threading.Event,
) -> None:
    print("Listening for physical START-button presses...")

    async with AsyncBusyBar(
        _websocket_host(),
        token=API_TOKEN,
    ) as busy_bar:
        async for message in busy_bar.stream_status_ws():
            if stop_event.is_set():
                return

            for update in message.get("updates", []):
                button_event = (
                    update
                    .get("input", {})
                    .get("button_event")
                )

                if not button_event:
                    continue

                if button_event.get("button") != "START":
                    continue

                # Press has no action field; release has action="RELEASE".
                if button_event.get("action") is None:
                    print("Start pressed")
                    controller.next()


def run() -> None:
    stop_event = threading.Event()
    controller = ScreenController(config.SCREENS)

    print(f"Connecting through {CONNECTION_DESCRIPTION}")
    print(f"Configured screens: {config.SCREEN_COUNT}")
    print("Press START to cycle screens. Press Ctrl-C to stop.")

    controller.draw_current()

    refresh_thread = threading.Thread(
        target=refresh_loop,
        args=(controller, stop_event),
        daemon=True,
    )
    refresh_thread.start()

    try:
        asyncio.run(
            listen_for_start_button(
                controller,
                stop_event,
            )
        )
    finally:
        stop_event.set()
