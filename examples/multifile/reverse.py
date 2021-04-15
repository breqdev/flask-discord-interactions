from flask_discord_interactions import DiscordInteractionsBlueprint


bp = DiscordInteractionsBlueprint()


@bp.command()
def reverse(ctx, text: str):
    "Reverse a string"
    return f"*Reverse!* {text[::-1]}"
