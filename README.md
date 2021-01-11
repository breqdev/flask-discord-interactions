# Flask-Discord-Interactions

This is a Flask extension that lets you write Discord Slash Commands using a decorator syntax similar to Flask's `@app.route()` or Discord.py's `@bot.command()`.

```
@discord.command()
def ping(ctx):
    "Respond with a friendly 'pong'!"
    return "Pong!"
```

*You might want to skim the [Discord docs](https://discord.com/developers/docs/interactions/slash-commands) on slash commands if you aren't familiar with them. This library handles authenticating with the `applications.commmands.update` scope, making the HTTP requests to register slash commands, receiving and validating incoming interactions, responding to `PING` with `PONG`, creating an object representing the context, and calling the functions that you defined with `@discord.command()`.*

## Bot Setup

### Step 1: Create an application in the [Discord Developer Portal](https://discord.com/developers/applications)
The name and avatar you set here will be the name and avatar of your bot. **You do not need to create a "Bot user"** like you would with a traditional Discord bot.

### Step 2: Authorize the application to create slash commands in one of your servers

In the Developer Portal, go to the OAuth2 tab, click the "applications.commands" checkbox, and copy the URL.

(You don't need the "bot" scope--that one is for traditional WebSocket-based Discord bots.)

![](docs/images/oauth.png)

Go to this URL, and you'll be prompted to select a server and click "Authorize". Select the testing server you want to add your bot to. (You can always go back and add more servers later.)

![](docs/images/authorization.png)

### Step 3: Set your environment variables

The library requires your client ID, public key (to authenticate incoming requests), and client secret (to register new commands). You can find all three in the "General Information" section of the Developer Portal. Store them in the `DISCORD_CLIENT_ID`, `DISCORD_PUBLIC_KEY`, and `DISCORD_CLIENT_SECRET` environment variables.

If you're new to environment variables, Twilio has a nice [guide](https://www.twilio.com/blog/2017/01/how-to-set-environment-variables.html). For deploying on Heroku/Dokku/etc, refer to their documentation on how to set environment variables.

```
export DISCORD_CLIENT_ID=795079214377730068
export DISCORD_PUBLIC_KEY=4ed566bf47318ee9482be3e11669d715520350b9f68672f339eee2f31a6822e1
export DISCORD_CLIENT_SECRET=[your secret here]
```

The example also uses the environment variable `TESTING_GUILD` to store the ID of the server you want to add commands to. Discord has an [article](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-) about how to find the server ID using developer mode.

```
export TESTING_GUILD=197777408198180864
```

### Step 4: Run the program

You should be able to run the example without any errors now. It should register slash commands in your server. However, these slash commands will not work yet.

### Step 5: Expose your server to the Internet

In order for Discord to reach your bot, it has to be reachable on the public Internet. This step will depend on how you are running your code.

#### Testing
For testing on your local machine, you will need to proxy traffic from a public address to your computer. Services like [ngrok](https://ngrok.com/) can do this for you. Follow the guide to sign up and install, then use the command `./ngrok http 5000` to create a tunnel (assuming your Flask app is running on port 5000). The terminal should display a public URL (something like `https://92832de0.ngrok.io`). Make sure you use the HTTPS one, as Discord will not send interactions over HTTP. Leave ngrok running in the background while you run your bot.

#### Deployment
If you are using something like [Heroku](https://devcenter.heroku.com/articles/getting-started-with-python) or [Dokku](http://dokku.viewdocs.io/dokku/), your public URL should be visible when you deploy the app, something like `https://serene-caverns-82714.herokuapp.com/`. If you are deploying directly to a cloud VPS with a public IP address, the steps are outlined in this [DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04) tutorial (it should be similar for most providers). You could also deploy to a local machine and use a service like [No-IP](https://www.noip.com/support/knowledgebase/getting-started-with-no-ip-com/) to expose it to the Internet.

### Step 6: Tell Discord where to send interactions
You need to provide Discord with your public URL so they can send you interactions. This setting is located in the "General Information" section of the Developer Portal.

*Note that the example uses the /interactions endpoint to receive interactions.*

![](docs/images/endpoint.png)

Click the "Save Changes" box at the bottom. Note that if your bot is not configured properly, the Developer Portal will not allow you to save the URL.

## Usage

Look in the examples directory for more detailed examples.

```
import os

from flask import Flask
from flask_discord_interactions import DiscordInteractions


app = Flask(__name__)
discord = DiscordInteractions(app)


app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]


@discord.command()
def ping(ctx):
    "Respond with a friendly 'pong'!"
    return "Pong!"


discord.set_route("/interactions")


discord.update_slash_commands(guild_id=os.environ["TESTING_GUILD"])


if __name__ == '__main__':
    app.run()
```

## How is this different from `discord-py-slash-command`?

`Discord.py` and `discord-py-slash-command` use a bot user and a websocket to connect to Discord, just like a regular Discord bot. It's a nice way to add support for slash commands to an existing Discord bot, or if you need to use a bot user to manage channels, reactions, etc.

However, for simple bots, using webhooks instead of websockets can let your bot scale better and use less resources. You can deploy a webhook-based bot behind a load balancer and scale it up or down as needed without needing to worry about sharding or dividing up guilds between the app processes.

## Versioning
Since this library is new, and Discord Slash Commands are in beta, the API of this library might not be particularly stable. I strongly suggest you pin this library to a specific version when you deploy, and test your code after updates.

## Contributing

This is a project I made for my own personal use with some of my bots. I'm happy to provide support for others who want to use it if I have the time. I'm probably not going to develop new features on my own, unless I need them for something I'm working on, so if you want to see something new, the best way to make it happen is a pull request!
