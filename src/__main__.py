import os

from flask import Flask
from flask_discord_interactions import DiscordInteractions, Message, Context
import pymongo
import string
import random
import requests

app = Flask(__name__)
bot = DiscordInteractions(app)


app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]
app.config["DISCORD_BOT_TOKEN"] = os.environ["DISCORD_BOT_TOKEN"]
app.config["MONGO_URL"] = os.environ["MONGO_URL"]
app.config["WEBHOOK_HOSTNAME"] = os.environ["WEBHOOK_HOSTNAME"]
mongo = pymongo.MongoClient(app.config["MONGO_URL"])["Auth"]["Token"]


#@app.route("/github/<token>")
def send_post(token):
    ...

#def send




def _plainly_generate_token():
    asciis = string.ascii_letters + string.digits
    output = ""
    for _ in range(0, 69):
        output += random.choice(asciis)
    return output


def maybe_generate_token(channel_id):
    if mongo.find_one({"_id": channel_id}) is None:
        token = _plainly_generate_token()
        mongo.insert_one({"_id": channel_id, "token": token})
        return token
    return mongo.find_one({"_id": channel_id})["token"]


def regenerate_token(channel_id):
    token = _plainly_generate_token()
    mongo.update_one({"_id": channel_id}, {"$set": {"token": token}})
    return token


@bot.command()
def getlink(ctx):
    """Return a link where you can use to config. Must be executed in the channel the bot should send notification in."""
    if (ctx.author.permissions & 1 << 4) != 1 << 4:
        return "You don't have `Manage Message` permission in this channel."
    token = maybe_generate_token(channel_id=ctx.channel.id)
    return Message(
        content=f"**Don't share this with anyone!** https://{app.config['WEBHOOK_HOSTNAME']}/github/{token}\nIf you shared it to anyone, please re-generate this link with the `/regenerate` command.",
        ephemeral=True,
    )


@bot.command()
def regenerate(ctx: Context):
    """Regenerate the webhook link, if the old link is leaked."""
    if (ctx.author.permissions & 1 << 4) != 1 << 4:
        return "You don't have `Manage Message` permission in this channel."
    token = regenerate_token(channel_id=ctx.channel.id)
    return Message(
        content=f"Your link have been regenerated! Be sure to update the link in the GitHub setting as well!\n**Don't share this with anyone!** https://{app.config['WEBHOOK_HOSTNAME']}/github/{token}\nIf you shared it to anyone, please re-generate this link with the `/regenerate` command.",
        ephemeral=True,
    )



bot.set_route("/bot")


bot.update_commands()


if __name__ == "__main__":
    app.run()
