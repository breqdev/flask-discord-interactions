from flask_discord_interactions import DiscordInteractionsBlueprint


bp = DiscordInteractionsBlueprint()


@bp.command()
def echo(ctx, text: str):
    "Repeat a string"
    return f"*Echooo!!!* {text}"
