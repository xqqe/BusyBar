FANCY BANNER MODULE
===================

Install:

    python -m pip install -r requirements.txt

Run:

    python main.py


ARBITRARY-FONT TEXT
-------------------

In config.py:

    FancyBannerScreen(
        name="fancy text",
        message="HELLO",
        font_path=r"C:\Windows\Fonts\arialbd.ttf",
        font_size=11,
        text_color="#00FFFFFF",
        background_color="#000000FF",
    )


PNG ONLY
--------

    FancyBannerScreen(
        name="logo",
        png_path="assets/logo.png",
        image_fit="contain",
        background_color="#000000FF",
    )


PNG PLUS TEXT
-------------

    FancyBannerScreen(
        name="logo and text",
        png_path="assets/background.png",
        message="BUSY",
        font_path=r"C:\Windows\Fonts\arialbd.ttf",
        font_size=10,
        text_color="#FFFFFFFF",
        image_fit="cover",
    )


IMAGE FIT VALUES
----------------

contain
    Preserve aspect ratio and fit the entire image inside 72x16.

cover
    Preserve aspect ratio, fill 72x16, and crop overflow.

stretch
    Force the source image to exactly 72x16.

original
    Keep the original size and center it.


NOTES
-----

The module always produces a complete 72x16 PNG. It uploads that PNG through
/api/assets/upload, then displays it using one image element with id
"main-screen". The clock and simple banner also use "main-screen", so switching
screens replaces the previous element without deleting the application.
