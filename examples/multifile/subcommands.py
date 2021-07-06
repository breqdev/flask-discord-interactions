import threading

from flask_discord_interactions import DiscordInteractionsBlueprint, Response


bp = DiscordInteractionsBlueprint()
group = bp.command_group("group", "First Group")
sub = group.subgroup("sub", "Sub Group")

@sub.command()
def echo_delay(ctx, text: str):
    "Repeat a string on a delay"

    def do_searchData():
        ctx.send(Response(f"*Echooo 2!!!* {text}"))

    thread = threading.Thread(target=do_searchData)
    thread.start()

    return Response(f"*Echooo 1!!!* {text}")
