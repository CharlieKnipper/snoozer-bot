# Charlie Knipper
# Snoozer Bot for Discord
# Last updated --> 1/9/23

import os
import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks

import datetime

# Create a Bot instance to connect to discord
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# Set the intents required for the bot's operation
intents = discord.Intents().default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
intents.messages = True
intents.members = True

# Instantiate the bot
bot = commands.Bot(command_prefix='s', intents=intents)
bot_channel = None

# Dict of users and snooze time
snoozers = {}
offset = 1.0
server_output = False

#---------------------Bot Events---------------------#

@bot.event
async def on_ready():
    # Connect to the guild designated by the environment
    guild = discord.utils.get(bot.guilds, name=GUILD)
    if server_output:
        print(f'{bot.user} is connected to guild \'{guild.name}\' (id={guild.id})\n')

    # Set status to the help command
    await bot.change_presence(activity=discord.Game('snoozehelp'))

    # Begin disconnect_user process to auto-run every minute
    disconnect_user.start()

@tasks.loop(minutes=offset)
async def disconnect_user():
    # Disconnect a user at the set time
    global bot_channel
    # snoozed = []

    n = datetime.datetime.now()
    if server_output:
        print('Checking for snoozers...\n')
    for member, time in snoozers.items():
        if time.hour==n.hour and time.minute==n.minute:
            if server_output:
                print(f'Disconnecting {member}.\n')
            if bot_channel != None:
                await bot_channel.send(f'Disconnecting {member.name}... Goodnight!\n')
            await member.edit(voice_channel=None, reason='Snooze')
            # snoozed.append(member)

    # for member in snoozed:
        # snoozers.pop(member)

@bot.command(name='nooze')
async def time_set(context):
    # Update the calling user's snoozers entry with the time provided
    global bot_channel
    
    try:
        s = str(context.message.content)[7:12].split(':')
        t = datetime.time(int(s[0]), int(s[1]), 0, 0)
        snoozers.update({context.author: t})
        if server_output:
            print(f'Registered snoozer {context.author} for {s[0]}:{s[1]}.\n')
    
        if bot_channel == None:
            bot_channel = context.channel
        await context.send(f'Snoozer, {context.author.name}, will be snoozing at {s[0]}:{s[1]} from now on.')
    except:
        await context.send(f'Please provide a valid snoozing time (i.e. snooze 23:30).')
    
@bot.command(name='topsnooze')
async def remove_entry(context):
    # Remove the snoozer entry for the calling user
    if snoozers.get(context.author) != None:
        snoozers.pop(context.author)
        await context.send(f'Snoozer, {context.author.name}, will no longer be snoozing.')
    else:
        await context.send(f'Snoozer, {context.author.name}, is not registered to snooze.')

@bot.command(name='howsnooze')
async def show_entries(context):
    # Show all snoozer entries currently waiting
    if len(snoozers) < 1:
        await context.send(f'There are no snoozers currently registered.')
    else:
        m = '---------------------------------------------\nSnoozer:\t\t\t\t\t\t\t\tRegistered Time:\n'
        for member, time in snoozers.items():
            m = m + f'{member.name}\t\t\t\t{time}\n'
        m = m + '---------------------------------------------'
        await context.send(m)

@bot.command(name='noozehelp')
async def help(context):
    # List all commands and uses
    m = 'snoozehelp:\t\tList all commands supported by the bot.\n'
    m = m + 'snooze:\t\t\t\tRegisters the calling user for a given time (i.e. \'snooze hh:mm\', 24 hr format, cst).\n'
    m = m + 'stopsnooze:\t\tCancels the snooze registered for the calling user.\n'
    m = m + 'showsnooze:\t\tLists all currently registered snoozers and the corresponding snooze times.'

    await context.send(m)

#---------------------Bot Events---------------------#

bot.run(TOKEN)