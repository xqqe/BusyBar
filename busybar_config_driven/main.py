#!/usr/bin/env python3
"""Minimal launcher. Normally, edit config.py instead."""

import sys

from busybar_core import clear_display, run


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
    finally:
        clear_display()
