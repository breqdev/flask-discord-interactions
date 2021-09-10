# Flask-Discord-Interactions

This is a Flask extension that lets you write Discord Application Commands using a decorator syntax similar to Flask's `@app.route()` or Discord.py's `@bot.command()`.

```
@discord.command()
def ping(ctx):
    "Respond with a friendly 'pong'!"
    return "Pong!"
```

Full documentation is available on [readthedocs](https://flask-discord-interactions.readthedocs.io/).