import discord
from discord.ext import commands, tasks

import datetime

from api.weather_api import WeatherApi
from api.palm_api import PalmApi
from api.cat_api import CatApi

from bot.embeds import Reminders, Forecast, Motivation, DailyCat
from bot.manager import Manager

from bot.user import User

from logs.log import log

from secret import COMMAND_PREFIX


"""Constants and setup"""
# What time the bot sends a user daily messages
# 7:30 AM PST by default
TIME = datetime.time(hour=14, minute=30, tzinfo=datetime.timezone.utc)
# Text API settings
MOTIVATION_PROMPT = f"Generate a completely unique philosopical daily motivational quote that is perfect to start the day with, but with a humourous and quirky twist, using {datetime.datetime.now()} as a random seed"
# Personality is the prefix of all prompts sent to the text api
PERSONALITY = "Take on the personality of a funny, intelligent, and curious person when replying to this message: "

intents = discord.Intents.default()
# for rights to send DMs
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)
COMMANDS = [
    ['sign-up', ''],
    ['opt-out', ''],
    ['forecast', '[location: `str`]'],
    ['add-reminder', 'reminder: `str` [reminder2: `str`] [reminder3: `str`]'],
    ['remove-reminder', '[index: `int`] [remove_all: `bool`]'],
    ['view-reminders', ''],
    ['motivation', ''],
    ['help-commands', ''],
    ['@BOT', 'msg: `str`']
]

manager = Manager(
    apis={
        'weather': WeatherApi,
        'text': PalmApi,
        'cat': CatApi
    },
    embeds={
        'reminders': Reminders,
        'forecast':  Forecast,
        'motivation': Motivation,
        'cat': DailyCat
    }
)

@bot.event
async def on_ready():
    log("Mr. Weather is up and up!", append_before="----------------------------------\n")

    if bot.is_ws_ratelimited:
        log("Uh oh, bot is being rate-limited.")

    daily_msg.start()
    await bot.tree.sync()

@tasks.loop(time=TIME)
async def daily_msg():
    channels = [await bot.fetch_user(user_id) for user_id in manager.get_signed_up()]
    for channel in channels:
        await channel.send(
            embeds=[
                manager.embed(
                    name='cat',
                    data=manager.api_call(name='cat')
                ),
                manager.embed(
                    name='reminders',
                    user=manager.get_user(user_id=channel.id),
                    reminders=manager.get_reminders(user_id=channel.id)
                ),
                manager.embed(
                    name='forecast',
                    data=manager.api_call(name='weather', location=manager.get_user(channel.id).location)
                ),
                manager.embed(
                    name='motivation',
                    data=manager.api_call(
                        name='text',
                        prompt=MOTIVATION_PROMPT
                    ),
                )
            ]
        )

@bot.tree.command(name="forecast")
async def forecast(
    interaction: discord.Interaction,
    location: str="",
    set_default: bool=False
) -> None:
    """Get today's forecast for any location."""

    if not manager.exists_user(interaction.user.id):
        manager.add_user(User(
            id=interaction.user.id,
            display_name=interaction.user.display_name,
            display_avatar=interaction.user.display_avatar.url
        ))

    if location == "":
        await interaction.response.send_message(
            embed=manager.embed(
                name='forecast',
                data=manager.api_call(name='weather', location=manager.get_user(interaction.user.id).location)
            )
         )
    elif location != "" and manager.location_exists('weather', location):
        if set_default:
            manager.update_location(interaction.user.id, location)
        await interaction.response.send_message(
            embed=manager.embed(
                name='forecast',
                data=manager.api_call(name='weather', location=location)
            )
         )
    else:
         await interaction.response.send_message(f"Error: {location} was not recognized.", ephemeral=True)

@bot.tree.command(name="sign-up")
async def signup(
    interaction: discord.Interaction,
    confirmation: bool
) -> None:
    """Signup for a daily DM at 8:00AM with daily forecast and reminders."""
    if not confirmation:
        await interaction.response.send_message("Info: request canceled.", ephemeral=True)
        return None
    # add user info and restart the task loop
    if not manager.exists_user(interaction.user.id):
        manager.add_user(User(
            id=interaction.user.id,
            display_name=interaction.user.display_name,
            display_avatar=interaction.user.display_avatar.url,
            is_signed_up=True
        ))
        await interaction.response.send_message("Success: signed up!", ephemeral=True)
    else:
        manager.update_signup(interaction.user.id, True)
        await interaction.response.send_message("Success: signed up!", ephemeral=True)

@bot.tree.command(name="opt-out")
async def optout(
    interaction: discord.Interaction,
    confirmation: bool
):
    """Opt-out of receiving daily messages from Mr. Weather."""
    if not confirmation:
        await interaction.response.send_message("Info: request canceled.", ephemeral=True)
        return None

    if not manager.exists_user(interaction.user.id):
        manager.add_user(User(
            id=interaction.user.id,
            display_name=interaction.user.display_name,
            display_avatar=interaction.user.display_avatar.url
        ))
    manager.update_signup(interaction.user.id, False)
    await interaction.response.send_message("Success: opted out!", ephemeral=True)

'''
Reminder Details
Unique for each user
'''
@bot.tree.command(name="add-reminders")
@discord.app_commands.describe(
    reminder1="Your reminder!",
    reminder2="Your second reminder!",
    reminder3="Your third reminder!"
)
async def add_reminders(
    interaction:discord.Interaction,
    reminder1: str,
    reminder2: str="",
    reminder3: str=""
) -> None:
    """Add a reminder."""
    if not manager.exists_user(interaction.user.id):
        manager.add_user(User(
            id=interaction.user.id,
            display_name=interaction.user.display_name,
            display_avatar=interaction.user.display_avatar.url
        ))

    reminders = [reminder1, reminder2, reminder3]
    for reminder in reminders:
        manager.add_reminder(interaction.user.id, reminder)

    await interaction.response.send_message("Success: added reminders!", ephemeral=True)

@bot.tree.command(name="view-reminders")
async def view_reminders(
    interaction: discord.Interaction,
    confirmation: bool
) -> None:
    """View your reminders."""
    if not confirmation:
        await interaction.response.send_message("Info: request canceled.", ephemeral=True)
        return None

    if not manager.exists_user(interaction.user.id):
        manager.add_user(User(
            id=interaction.user.id,
            display_name=interaction.user.display_name,
            display_avatar=interaction.user.display_avatar.url
        ))

    await interaction.response.send_message(
        embed=manager.embed(
            name='reminders',
            user=manager.get_user(interaction.user.id),
            reminders=manager.get_reminders(interaction.user.id)
        )
    )

@bot.tree.command(name="remove-reminders")
@discord.app_commands.describe(
    index="Index of reminder to remove"
)
async def remove_reminders(
    interaction: discord.Interaction,
    index: int
) -> None:
    """Remove one of your reminders."""
    if not manager.exists_user(interaction.user.id):
        manager.add_user(User(
            id=interaction.user.id,
            display_name=interaction.user.display_name,
            display_avatar=interaction.user.display_avatar.url
        ))
        await interaction.response.send_message("Error: you have no reminders.")
        return None

    try:
        manager.remove_reminder(interaction.user.id, index-1)
    except IndexError:
        # user entered invalid index
        await interaction.response.send_message("Error: invalid index.", ephemeral=True)
    else:
        # successfully removed reminder at index
        await interaction.response.send_message("Success: reminder removed!", ephemeral=True)

@bot.tree.command(name="motivation")
async def motivation(
    interaction: discord.Interaction,
    confirmation: bool
) -> None:
    """Get motivated!"""
    if not confirmation:
        await interaction.response.send_message("Info: request canceled.", ephemeral=True)
        return None

    await interaction.response.send_message(
        embed=manager.embed(
            name='motivation',
            data=manager.api_call(
                name='text',
                prompt=MOTIVATION_PROMPT
            ),
        )
    )

@bot.tree.command(name="help-commands")
async def help_commands(
    interaction: discord.Interaction,
    confirmation: bool
) -> None:
    """View commands."""
    if not confirmation:
        await interaction.response.send_message("Info: request canceled.", ephemeral=True)
        return None

    embed = discord.Embed(
        title="Commands",
        color=discord.Color.random(),
        timestamp=datetime.datetime.now()
    )

    icon = discord.File("assets/bot_icon.jpg", filename="bot_icon.jpg")
    embed.set_image(url="attachment://bot_icon.jpg")

    for pair in COMMANDS:
        name, params = pair
        embed.add_field(name=name, value=params, inline=False)

    await interaction.response.send_message(embed=embed, file=icon)

@bot.event
async def on_message(message: str):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        data = manager.api_call(
            name='text',
            prompt=f"{PERSONALITY} {message.content}"
        )
        if not data:
            await message.channel.send("Error.")

        await message.channel.send(data['result'])