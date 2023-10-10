import datetime

"""Constants and setup"""
# What time the bot sends a user daily messages
# 7:30 AM PST by default
TIME = datetime.time(hour=14, minute=30, tzinfo=datetime.timezone.utc)
# Text API settings
MOTIVATION_PROMPT = f"Generate a completely unique philosopical daily motivational quote that is perfect to start the day with, but with a humourous and quirky twist, using {datetime.datetime.now()} as a random seed"
# Personality is the prefix of all prompts sent to the text api
PERSONALITY = "Take on the personality of a funny, intelligent, and curious person when replying to this message: "
COMMAND_PREFIX = '/'
DEFAULT_LOCATION = "Irvine"
LOGGING = True