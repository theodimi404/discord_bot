import os
import random
from dotenv import load_dotenv
import discord
from discord.ext import commands
import requests
import bs4
import re
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')  # Takes your Discord TOKEN from the .env file

bot = commands.Bot(command_prefix="!")  # The prefix before each command


@bot.event  # Informs if the bot is connected in the server
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


# Call these functions so the bot will join and leave respectively the
# voice chat. I want to include in the future commands, so it can play
# songs from youtube.
@bot.command(name='summon')  # The bot joins the voice chat
async def join_voice(ctx):
    channel = ctx.message.author.voice.channel
    await channel.connect()
    response = bot.voice_clients[0].guild
    await ctx.message.channel.send(response)


@bot.command(name='unsummon')  # The bot leaves the voice chat
async def leave_voice(ctx):
    for x in bot.voice_clients:
        if x.user.id == 701024962072543282:
            await ctx.message.channel.send("Bot has left the voice chat")
            await x.disconnect()


@bot.event  # The bot reacts on messages with a random emoji if a user reacts to it
async def on_reaction_add(reaction, user):
    if user.name == bot.user.name:
        return
    elif len(reaction.message.reactions) > 1:
        return

    random_emojis = [
        '😁', '😈', '🥱',
        '😱', '👌', '☣️',
        '😞', '🙏', '🗽',
        '😴', '💨', '😤',
        '🤩', '💣', '🤥',
        '💪', '❤️', '💀',
        '🖕🏻', '✝️', '😜',
        '🤣', '💯', '😱',
        '😥', '💤', '🤯',
        '💩', '🔞', '🤤',
    ]
    response = random.choice(random_emojis)
    await reaction.message.add_reaction(response)


@bot.event  # Functions which are derived through messages in the text server
async def on_message(message):
    # creates teams for a certain game. Change the variable to customize the command
    game = 'tichu'
    if message.content == 'omades' + game:
        active_users = []
        for i in range(len(message.guild.members)):  # Excludes the bot and the offline users
            if message.guild.members[i].bot is False and message.guild.members[i].status == discord.Status('online'):
                active_users.append(message.guild.members[i].name)

        random.shuffle(active_users)

        first_team = active_users[:len(active_users) // 2]
        second_team = active_users[len(active_users) // 2:]
        await message.channel.send("The first team is: \n")
        await message.channel.send(first_team)
        await message.channel.send("The second team is: \n")
        await message.channel.send(second_team)

    # The following block creates teams for a game, but excludes certain online users who don't play
    # a certain game. You have to edit the .env file with their IDs and add them here
    """
    if message.content == 'omades aoe':
        active_users = []
        for i in range(len(message.guild.members)):
            if message.guild.members[i].bot == False and message.guild.members[i].status == discord.Status('online') and \
                    message.guild.members[i].id != int(USER1_WHO_DONT_PLAY) and message.guild.members[i].id != int(USER2_WHO_DONT_PLAY):
                active_users.append(message.guild.members[i].name)

        random.shuffle(active_users)

        first_team = active_users[:len(active_users) // 2]
        second_team = active_users[len(active_users) // 2:]
        await message.channel.send("The first team is: \n")
        await message.channel.send(first_team)
        await message.channel.send("The second team is: \n")
        await message.channel.send(second_team)
    """
    # If a user writes a certain word, the bot responds so it will hype the rest of the users to play
    # a certain game. In this example, it uploads an image for the game AGE OF EMPIRES 3
    if message.content == 'aoe':
        await message.channel.send(file=discord.File('aoe.jpg'))

    # A response if someone greets in the chat
    if message.author == bot.user:
        return
    if message.content == 'Hi' or message.content == 'hi' or message.content == 'HI':
        response = "Hi! " + message.author.name + "  :)" + "\n you created your account at " + str(
            message.author.created_at)
        await message.channel.send(response)

    # A response with the horse emoji if someone sends a message that contains the word aoe
    if re.search(r'\baoe\b',message.content).group(0) == 'aoe':
        await message.channel.send('🐎')

    # Three functions that work with 3 key words. map, weather, imdb.
    # map + one address will return the given address in google maps
    # weather + one greek city will return the weather forecast for the given city
    # imdb + one genre will return a random movie with this genre
    indicator = message.content.split()

    # MAP
    if indicator[0] == 'map':
        indicator.remove('map')
        address = ' '.join(indicator)
        response = 'https://www.google.com/maps/place/' + address
        await message.channel.send(response)

    # WEATHER
    if indicator[0] == "weather":
        def get_weather(city):
            url = f'http://www.skaikairos.gr/main/{city}/position'

            res = requests.get(url)
            if res.status_code != requests.codes.ok:
                return '404'

            soup = bs4.BeautifulSoup(res.text, 'html.parser')
            kairos = soup.find("div", {"id": "forecast-upper-seven"})
            data = list(kairos.stripped_strings)

            if data:
                return f"""\
        Η πρόγνωση του καιρού είναι:
        {data[2]}
        {data[3]}{data[4]}
        {data[5]} {data[6]} Μποφόρ
        ------
        {data[7]}
        {data[8]}
        {data[9]}{data[10]}
        {data[11]} {data[12]} Μποφόρ
        ------
        {data[13]}
        {data[14]}
        {data[15]}{data[16]}
        {data[17]} {data[18]} Μποφόρ
        ------
        {data[19]}
        {data[20]}
        {data[21]}{data[22]}
        {data[23]} {data[24]} Μποφόρ
        (Data from skaikairos.gr)"""
            else:
                return '404'
        city = ' '.join(indicator[1:])
        response = get_weather(city)
        await message.channel.send(response)

    # IMDB
    if indicator[0] == "imdb":
        genre = ' '.join(indicator[1:])
        url = f'https://www.imdb.com/search/title/?title_type=movie&genres={genre}&explore=title_type,genres&ref_=adv_explore_rhs'

        res = requests.get(url)
        if res.status_code != requests.codes.ok:
            return ''
        soup = bs4.BeautifulSoup(res.text, 'html.parser')

        data = []
        for ana in soup.findAll('a'):
            if ana.parent.name == 'h3':
                data.append('https://www.imdb.com' + ana["href"])
        await message.channel.send(random.choice(data))


# Function that transforms the bot into a snitch. When a user deletes a message, the bot resend it
@bot.event
async def on_message_delete(message):
    response = "O " + str(message.author.name) + " deleted this message:\n" + str(message.content)
    await message.channel.send(response)


# Welcomes a new member in the user
@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )


bot.run(TOKEN)
