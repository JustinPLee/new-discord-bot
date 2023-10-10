import discord

from datetime import datetime

from bot.user import User

class Forecast:

    # used for creating friendly advice
    advice = {
        'highest_temperature': {
            '90': "PLEASE DON'T WEAR A JACKET!",
            '85': "Moderately hot day. Watch out..",
            '80': "Nice SoCal sun.",
            '75': "Maybe don't wear shorts?",
            '70': "PLEASE WEAR A JACKET!"
        },
        'wind': {
            '30': "Be careful, it will be extremely windy today!",
            '25': "Be careful, it will be very windy today!",
            "15": "Nice breeze incoming!"
        },
        'rain': {
            '50': "Prepare for rain!",
            '0': "Yet another sunny day."
        }
    }

    @classmethod
    def generate(cls, data: {}) -> discord.Embed:
        """
        Returns a forecast embed.

        Parameters
        ----------
        data: `dict`\n
            location:``str`\n
            highest_temperature:`int`
                Highest temperature in farenheit.\n
            rain:`int`
                Percent chance of rain.\n
            wind:`int`
                Max wind speeds in MPH.
            summary:`str`
                Description of weather.\n
            source:`str`
                Name of api source.
        """
        if not data:
            return discord.Embed(
                title=f"Error retrieving forecast data.",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )

        embed = discord.Embed(
            title=f"Forecast for {data['location']}!",
            color=discord.Color.random(),
            description="",
            timestamp=datetime.now()
        )
        # generate friendly advice
        advice = ""
        for category in cls.advice:
            for limit, msg in cls.advice[category].items():
                if data[category] >= int(limit):
                    advice += msg + ' '
                    break

        embed.add_field(name=":thermometer: Highest Temperature", value=f"{data['highest_temperature']}°F")
        embed.add_field(name=":cloud_with_rain: Chance of rain", value=f"{data['rain']}%", inline=False)
        embed.add_field(name=":triangular_flag_on_post: Max Wind Speed", value=f"{data['wind']} mph", inline=False)
        embed.add_field(name=":thinking: Feels like...", value=f"{data['summary']}!", inline=False)
        embed.add_field(name=":smirk_cat: Friendly Advice!", value=advice)

        if data['icon'] != "Unknown":
            embed.set_thumbnail(url=f"https:{data['icon']}")

        embed.set_footer(text=f"Data provided by {data['source']}")

        return embed

class Reminders:

    @staticmethod
    def generate(user: User, reminders: list[str]) -> discord.Embed:
        """
        Returns a reminders embed.

        Parameters
        ----------
        user: `User`\n
        reminders: `list[str]`
        """

        embed = discord.Embed(
            title=f"{user.display_name}'s Reminders",
            color=discord.Color.random(),
            description="",
            timestamp=datetime.now()
        )
        # TODO: use emojis instead of numbers
        index = 1
        for reminder in reminders:
            embed.add_field(name=f"{index}. )", value=reminder, inline=False)
            index += 1

        if len(reminders) == 0:
            embed.add_field(name="", value=":partying_face: Yay! You have no reminders! :partying_face:")

        embed.set_thumbnail(url=user.display_avatar)

        return embed
        

class Motivation:

    @staticmethod
    def generate(data: {}) -> discord.Embed:
        """
        Returns a motivation embed.

        Parameters
        ----------
        data: `dict`\n
            result:`str`
                Reply of text bot
            source:`str`
                Name of api source
        """
        if not data:
            return discord.Embed(
                title=f"Error retrieving motivation data.",
                color=discord.Color.red(),
                timestamp=datetime.now(),
            )

        embed = discord.Embed(
            title=f":fire:Daily Motivational Quote!",
            color=discord.Color.random(),
            description="",
            timestamp=datetime.now()
        )

        embed.add_field(name="", value= data['result'])
        embed.set_footer(text=f"Generated by {data['source']}")

        return embed

class DailyCat:

    @staticmethod
    def generate(data: {}) -> discord.Embed:
        """
        Returns a cat embed.

        Parameters
        ----------
        data: `dict`\n
            url:`str`\n
            source:`str`
                Name of api source
        """

        embed = discord.Embed(
            title="Daily Update!",
            color=discord.Color.random(),
        )

        embed.set_image(url=data['url'])
        embed.set_footer(text=f"Supplied by {data['source']}")
    
        return embed