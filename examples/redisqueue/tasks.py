import requests
from flask_discord_interactions import Response


def do_screenshot(ctx, url):
    response = requests.get(
        "https://shot.screenshotapi.net/screenshot",
        params={
            "url": url,
            "output": "image",
            "file_type": "png",
            "wait_for_event": "load"
        },
        stream=True
    )

    response.raw.decode_content = True

    ctx.edit(Response(
        content="Your screenshot is ready!",
        file=("screenshot.png", response.raw, "image/png")
    ))
