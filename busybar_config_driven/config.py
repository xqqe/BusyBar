"""Everything you are normally expected to edit."""

from screens.banner import BannerScreen
from screens.clock import ClockScreen

DEFAULT_CONNECTION = "wifi"  # "wifi" or "usb"

WIFI_IP = "192.168.1.62"
WIFI_API_TOKEN = "4040"

USB_IP = "10.0.4.20"
APPLICATION_NAME = "my-busybar"
REQUEST_TIMEOUT_SECONDS = 5

# The number of items in this list IS the number of screens.
# START advances through this list in order.
SCREENS = [
    ClockScreen(
        name="clock",
        time_format="%H:%M:%S",
        font="extra_large",
        color="#FFFFFFFF",
        x=36,
        y=15,
        align="bottom_mid",
        refresh_seconds=1.0,
    ),
    BannerScreen(
        name="placeholder banner",
        message="whaddup",
        font="large",
        color="#00FFFFFF",
        x=36,
        y=15,
        align="bottom_mid",
    ),
]

SCREEN_COUNT = len(SCREENS)
