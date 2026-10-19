# BusyBar

**A configurable Python screen controller for the BUSY Bar — with button-driven screen switching, live updates, scrolling messages, and custom graphics.**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Hardware](https://img.shields.io/badge/Hardware-BUSY%20Bar-555555)
![Interfaces](https://img.shields.io/badge/Connection-Wi--Fi%20%7C%20USB-536D8E)
![Status](https://img.shields.io/badge/Status-Personal%20Project-informational)

BusyBar turns a **BUSY Bar** into a small, configurable display that can switch between independently defined screens. Set up the screens in `config.py`, start the Python program, and use the device's **START** button to move through them.

The project is organized around reusable screen classes and a shared controller, keeping device communication separate from display content.

## Features

- **Button-controlled screen cycling** — press START to advance through your configured screens, wrapping back to the first.
- **Declarative configuration** — add, remove, reorder, and customize screens in one `SCREENS` list.
- **Live clock** — custom time format, font, position, color, and refresh interval.
- **Text banners** — fixed messages or automatically scrolling text when the message exceeds the display width.
- **Custom graphics** — render fonts and images into 72 × 16 artwork with the extended variant.
- **Wi-Fi or USB** — connection settings in `config.py`, with command-line overrides.
- **Modular implementation** — display modules provide their own rendering behavior while the controller handles communication and updates.

## Choose a version

| Version | What it includes | Dependencies |
| --- | --- | --- |
| [`busybar_config_driven/`](busybar_config_driven/) | Clock, simple text banners, auto-scrolling, and screen cycling | `busylib` |
| [`busybar_fancy_banner/`](busybar_fancy_banner/) | All of the above, plus custom TrueType fonts, PNG images, and image/text overlays | `busylib`, `Pillow` |

**For new setups:** start with `busybar_fancy_banner` if you want graphical displays, or `busybar_config_driven` for a smaller text-focused setup. Each folder is a standalone application; run commands from inside the variant you choose.

## Getting started

### 1. Requirements

- Python **3.10+**
- A BUSY Bar accessible over Wi-Fi or USB
- The relevant dependencies from the selected variant's `requirements.txt`

### 2. Clone and install

```bash
git clone https://github.com/xqqe/BusyBar.git
cd BusyBar/busybar_fancy_banner
python -m pip install -r requirements.txt
```

To use the simpler version, replace `busybar_fancy_banner` with `busybar_config_driven`.

### 3. Configure the connection

Open `config.py` in the selected folder:

```python
DEFAULT_CONNECTION = "wifi"  # "wifi" or "usb"

WIFI_IP = "192.168.1.62"     # Change to your device's IP
WIFI_API_TOKEN = "4040"      # Change to your device's API token

USB_IP = "10.0.4.20"
APPLICATION_NAME = "my-busybar"
```

The values in the repository are **examples**, not automatically discovered settings. Replace them with the values for your device.

### 4. Run

```bash
python main.py
```

Optional connection overrides:

```bash
python main.py --usb
python main.py --wifi
python main.py --host 192.168.1.62 --token YOUR_TOKEN
```

Press the physical **START** button to switch screens, or **Ctrl+C** to stop the program. On exit, the launcher attempts to clear its application's display content.

## Configuring screens

Screens are listed in `config.py`. **Their order in the list is the order in which START cycles through them.** The screen count is derived automatically from the list length.

For example, in `busybar_config_driven/config.py`:

```python
from screens.clock import ClockScreen
from screens.banner import BannerScreen

SCREENS = [
    ClockScreen(
        name="clock",
        time_format="%H:%M:%S",
        font="extra_large",
        color="#FFFFFFFF",
        refresh_seconds=1.0,
    ),
    BannerScreen(
        name="busy",
        message="DO NOT DISTURB — WORK IN PROGRESS",
        color="#FF0000FF",
        auto_scroll=True,
        scroll_step=2,
    ),
    BannerScreen(
        name="available",
        message="AVAILABLE",
        color="#00FF00FF",
        auto_scroll=False,
    ),
]

SCREEN_COUNT = len(SCREENS)
```

### Clock screens

`ClockScreen` uses Python's `time.strftime` format strings, so you can display 24-hour or 12-hour time, include seconds, and adjust alignment and refresh frequency.

### Scrolling text banners

`BannerScreen` estimates text width relative to the device's 72-pixel-wide display. If `auto_scroll=True` and the text is too long, it scrolls horizontally. Customize `scroll_step`, `refresh_seconds`, `scroll_gap_pixels`, and `pixels_per_character` to tune the motion.

## Custom fonts and graphics

The `busybar_fancy_banner` variant adds `FancyBannerScreen`, which creates a complete **72 × 16 PNG** with Pillow before uploading it to the device.

**Custom font and message**

```python
FancyBannerScreen(
    name="status",
    message="BUSY",
    font_path=r"C:\Windows\Fonts\arialbd.ttf",
    font_size=11,
    text_color="#FFFFFFFF",
    background_color="#000000FF",
)
```

**Image-only display**

```python
FancyBannerScreen(
    name="logo",
    png_path="assets/logo.png",
    image_fit="contain",
)
```

**Image with overlaid text**

```python
FancyBannerScreen(
    name="graphic status",
    png_path="assets/background.png",
    message="BUSY",
    font_path=r"C:\Windows\Fonts\arialbd.ttf",
    font_size=10,
    image_fit="cover",
)
```

Image fit options:

| Mode | Behavior |
| --- | --- |
| `contain` | Fit the full image within 72 × 16 while preserving aspect ratio |
| `cover` | Fill the display while preserving aspect ratio; crop any overflow |
| `stretch` | Resize to exactly 72 × 16, regardless of aspect ratio |
| `original` | Center the original image without resizing |

The fancy banner module also supports text alignment, pixel offsets, background colors, and transparency. Specify an existing local file path for custom fonts and artwork.

## How it works

```text
config.py
   │
   ▼
SCREENS = [ClockScreen, BannerScreen, ...]
   │
   ▼
ScreenController ─────── WebSocket button events
   │                           │
   │                     START pressed
   │                           │
   ◄───────────────────────────┘
   │
   ├── Render selected screen
   ├── Prepare/upload image assets if needed
   ├── Send display elements via HTTP API
   └── Refresh active screen on its own interval
```

The controller uses the BUSY Bar's **WebSocket status stream** to detect START presses and the **HTTP display API** to draw elements. A background thread handles periodic refreshes for dynamic screens. Shared element IDs let one screen replace another without creating a new application for every transition.

## Repository structure

```text
BusyBar/
├── busybar_config_driven/
│   ├── main.py             # Launcher
│   ├── config.py           # Connection and screen configuration
│   ├── busybar_core.py     # Transport, button events, cycling, refresh
│   ├── requirements.txt
│   └── screens/
│       ├── clock.py
│       └── banner.py
│
└── busybar_fancy_banner/
    ├── main.py
    ├── config.py
    ├── busybar_core.py     # Also supports asset uploads
    ├── requirements.txt
    └── screens/
        ├── clock.py
        ├── banner.py
        └── fancy_banner.py
```

Each directory also contains its own `README.txt` with variant-specific notes.

## Extending the project

The core controller expects screen objects with a `name`, a `refresh_seconds` setting (or `None`), and a `render()` method returning BUSY Bar display element dictionaries. That interface allows additional screens to be implemented independently of the connection and button-handling logic.

In the graphics-enabled variant, screens can also define a `prepare(upload)` method to generate and upload assets before rendering.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| Cannot connect | Confirm the device IP, selected connection mode, and network/USB connection |
| HTTP 403 | Verify the configured Wi-Fi API token |
| A font or image fails to load | Use an existing local path; paths in the examples may need changing |
| Text scrolls unexpectedly | Set `auto_scroll=False` or adjust `pixels_per_character` |
| Nothing changes on START | Confirm the program is running and receiving device WebSocket status updates |

## Acknowledgments

Built using [`busylib`](https://pypi.org/project/busylib/) for BUSY Bar communication and [Pillow](https://python-pillow.org/) for optional image rendering.

---

<sub>Personal Python hardware-integration project. Not affiliated with the BUSY Bar manufacturer.</sub>
