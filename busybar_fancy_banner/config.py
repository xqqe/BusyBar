"""Everything you are normally expected to edit."""

from screens.banner import BannerScreen

from screens.clock import ClockScreen
from screens.fancy_banner import FancyBannerScreen


DEFAULT_CONNECTION = "wifi"  # "wifi" or "usb"

WIFI_IP = "192.168.1.62"
WIFI_API_TOKEN = "4040"

USB_IP = "10.0.4.20"
APPLICATION_NAME = "my-busybar"
REQUEST_TIMEOUT_SECONDS = 5


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

    FancyBannerScreen(
        name="fancy text",
        message="WHADDUP MY DUDES",
        font_path=r"C:\Windows\Fonts\arialbd.ttf",
        font_size=11,
        text_color="#00FFFFFF",
        background_color="#000000FF",
        horizontal_align="center",
        vertical_align="center",
    ),

    # PNG-only example:
    #
    # FancyBannerScreen(
    #     name="png banner",
    #     png_path="assets/example.png",
    #     background_color="#000000FF",
    #     image_fit="contain",
    # ),
]

SCREEN_COUNT = len(SCREENS)
