CONFIG-DRIVEN BUSY BAR
======================

Edit config.py for normal use.

The SCREENS list controls:
- how many screens exist
- screen order
- screen content and appearance

Example:

SCREENS = [
    ClockScreen(time_format="%I:%M %p"),
    BannerScreen(message="BUSY", color="#FF0000FF"),
    BannerScreen(
        name="available",
        message="AVAILABLE",
        color="#00FF00FF",
    ),
]

The count is automatic: SCREEN_COUNT = len(SCREENS).

FILES
-----
main.py
    Minimal launcher.

busybar_core.py
    Stable connection, HTTP, WebSocket, cycling, and refresh functions.

config.py
    Connection values and screen list.

screens/clock.py
    Clock screen module.

screens/banner.py
    Banner screen module.

INSTALL
-------
python -m pip install -r requirements.txt

RUN
---
python main.py
python main.py --usb
python main.py --host 192.168.1.62 --token 4040
