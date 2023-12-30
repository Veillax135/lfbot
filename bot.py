import datetime
from time import sleep
import random
import os
import json
import re

import discord
from discord.ext import commands, tasks
from discord.utils import get
from discord.ui import Button

intents = discord.Intents.default()  # Create a default set of intents
intents.typing = False  # Disable typing events to reduce unnecessary traffic (optional)
intents.presences = False  # Disable presence events (optional)
intents.message_content = True  # Enable message content intent
command_prefix = '?'
bot = commands.AutoShardedBot(command_prefix=command_prefix,
                              intents=intents,
                              help_command=None,
                              shard_count=3)
bot.start_time = datetime.datetime.now(datetime.UTC)

owner_id = 758058288024911962
weights = [
    4, 9, 6, 8, 30, 3, 25, 2, 2, 7, 7, 2, 2, 9, 4, 22, 5, 4, 31, 3, 18, 1, 8,
    10, 3, 8, 6, 6, 6, 20, 3, 3, 14, 29, 4, 3, 6, 3, 17, 2, 24, 7, 32, 1, 28,
    10, 4, 21, 19, 5, 6, 7, 2, 12, 5, 16, 27, 26, 1, 4, 5, 3, 1, 5, 5, 3, 9,
    23, 7, 11, 5, 13, 4, 15, 4, 3, 8
]

with open('config.json', 'r') as f:
    global config
    config = json.load(f)


def calculate_rank(count):
    thresholds = [1, 5, 8]  # initial thresholds for rank 1 and 2
    rank = 1
    while count >= thresholds[-1]:
        rank += 1
        thresholds.append(thresholds[-1] + rank / 2)  # add next threshold
    if count > 2 and count < 6:
        rank = 2
    if count > 5 and count < 9:
        rank = 3
    return rank


class NotOwner(commands.CheckFailure):
    ...


def is_owner():

    async def predicate(ctx):
        if ctx.author.id != ctx.guild.owner_id:
            raise NotOwner("User does not have required permissions")
        return True

    return commands.check(predicate)


def deEmojify(text):
    regrex_pattern = re.compile(
        pattern="["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+",
        flags=re.UNICODE)
    return regrex_pattern.sub(r'', text)


@bot.command(name='help', aliases=['commands', 'cmds', '?'])
async def commands(ctx, index=None):
    bot_commands = config["bot_commands"]
    # List all available commands with descriptions
    await ctx.channel.purge(limit=1)
    embed = discord.Embed(title="Bot Commands", color=discord.Colour(0x5539cc))

    if index:
        command_name = index
        if command_name in bot_commands:
            embed.add_field(name=f"**Command: {command_name}**",
                            value=f"Description: {bot_commands[command_name]}")
            embed.add_field(name='Usage',
                            value=config['usage'][index],
                            inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(
                f"Command '{command_name}' not found. Use `{command_prefix}help` to see the list of available commands."
            )
    else:
        for k, v in bot_commands.items():
            embed.add_field(name=k, value=v, inline=False)

        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text="Bot designed by Veillax")
        await ctx.send(embed=embed)


# Debug
@bot.command(name='debug')
async def debug_cmd(ctx):
    if ctx.author.id == owner_id:
        current_time = datetime.datetime.now(datetime.UTC)
        uptime = current_time - bot.start_time

        # Get the number of servers the bot is in
        server_count = len(bot.guilds)

        # Calculate bot latency
        latency = round(bot.latency * 1000)  # Convert to milliseconds

        # Create an embed to display debug information
        embed = discord.Embed(title="Bot Debug Information", color=0x5539cc)
        embed.add_field(name="Bot Uptime", value=str(uptime), inline=False)
        embed.add_field(name="Number of Servers",
                        value=str(server_count),
                        inline=False)
        embed.add_field(name="Bot Latency", value=f"{latency}ms", inline=False)

        await ctx.send(embed=embed)


# Ping Command
@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)  # Convert to milliseconds
    embed = discord.Embed(title="Pong!",
                          description=f"Latency: {latency}ms",
                          color=2067276)
    embed.timestamp = datetime.datetime.now()
    embed.set_footer(text="Bot designed by Veillax")
    await ctx.send(embed=embed)


# Purge
@bot.command(name='purge',
             aliases=[
                 'clear', 'msg.purge', 'channel.purge', 'msg.del', 'msg.clear',
                 'channel.clear'
             ])
async def purge_cmd(ctx, limit):
    limit = int(limit)
    if ctx.message.author.id in [
            998956850886230148, 758058288024911962, 995161417902719136
    ]:
        await ctx.channel.purge(limit=limit)
        await ctx.send(f'Cleared {str(limit)} messages.')
        sleep(1)
        await ctx.channel.purge(limit=1)


# Bounty Commands
@bot.group()
async def bounty(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Invalid subcommand.")
        sleep(2)
        await ctx.channel.purge(limit=1)


@bounty.command(name="update")
async def bounty_update(ctx, bounty_key, value):
    if ctx.message.author.id in [
            998956850886230148, 758058288024911962, 995161417902719136
    ]:
        bounties = config["bounties"]
        await ctx.channel.purge(limit=len(bounties) + 2)
        # Check if the bounty exists
        if str(bounty_key) not in config['bounties']:
            await ctx.send(f"Bounty {bounty_key} does not exist.")
            return
        reward = config["bounties"][bounty_key]["reward"]
        words = reward.split()
        words[0] = str(value)
        config["bounties"][bounty_key]["reward"] = " ".join(words)
        await ctx.send(
            "Bounties are a new way to earn valuables."
            "\nTo join the Bounty Hunter's Core, you must complete a bounty, however, you will not get any rewards from it, the reward will be your admission to the Bounty Hunter's Core"
            "\nFrom then, you must show proof of bounty completion to be rewarded. Proof must be a screenshot of the death message of the target."
            "\nBelow is a list of the currently active bounties")
        for bounty_id, bounty in bounties.items():
            target = bounty["target"]
            reward = bounty["reward"]
            embed = discord.Embed(title=f"📜 Bounty {bounty_id} 📜",
                                  color=0x7300ff)
            embed.add_field(name=f"Target: {target}", value="", inline=False)
            embed.add_field(name=f"Reward: {reward}", value="", inline=False)
            embed.set_footer(text="Bounties")
            await ctx.send(embed=embed)
        # Save the updated data to config.json
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)


@bounty.command(name='delete')
async def bounty_delete(ctx, bounty_key: int):
    if ctx.message.author.id in [
            998956850886230148, 758058288024911962, 995161417902719136
    ]:
        bounties = config["bounties"]
        await ctx.channel.purge(limit=len(bounties) + 2)
        # Check if the bounty exists
        if str(bounty_key) not in config['bounties']:
            await ctx.send(f"Bounty {bounty_key} does not exist.")
            return

        # Remove the bounty
        del config['bounties'][str(bounty_key)]

        # Update the keys
        config['bounties'] = {
            str(i + 1): v
            for i, v in enumerate(config['bounties'].values())
        }

        # Update the bounty_id
        config['bounty_id'] = len(config['bounties']) + 1

        # Save the updated data to config.json
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)

        await ctx.send(
            f"Successfully removed bounty {bounty_key} and updated the keys.")
        bounties = config["bounties"]
        await ctx.channel.purge(limit=len(bounties) + 2)
        await ctx.send(
            "Bounties are a new way to earn valuables."
            "\nTo join the Bounty Hunter's Core, you must complete a bounty, however, you will not get any rewards from it, the reward will be your admission to the Bounty Hunter's Core"
            "\nFrom then, you must show proof of bounty completion to be rewarded. Proof must be a screenshot of the death message of the target."
            "\nBelow is a list of the currently active bounties")
        for bounty_id, bounty in bounties.items():
            target = bounty["target"]
            reward = bounty["reward"]
            embed = discord.Embed(title=f"📜 Bounty {bounty_id} 📜",
                                  color=0x7300ff)
            embed.add_field(name=f"Target: {target}", value="", inline=False)
            embed.add_field(name=f"Reward: {reward}", value="", inline=False)
            embed.set_footer(text="Bounties")
            await ctx.send(embed=embed)


@bounty.command(name="create")
async def bounty_create(ctx):
    if ctx.message.author.id in [
            998956850886230148, 758058288024911962, 995161417902719136
    ]:
        global bounty_id  # access the global bounty_id variable
        bounties = config["bounties"]
        await ctx.channel.purge(limit=len(bounties) + 2)
        targets = [
            "Arcadia_2011", "2Pups", "Tuffinator", "_whynot", "OofThe4th",
            "BlobOCherryPie", "Crash", "wolfgirl", "cinderchili", "LiamRay10",
            "Kylo_Criptic", "Malaspy", "Mope", "Pink", "SterlingSilver"
        ]
        rewards = ["diamonds", "gold", "Sharpness", "Protection"]

        target = targets[random.choice(0, len(targets)) - 1]
        reward = rewards[random.randint(0, len(rewards)) - 1]
        if reward == "Protection":
            tier = random.randint(1, 3)
            reward = "1 " + reward
            reward += " 1 " if tier == 1 else " 2 " if tier == 2 else " 3 "
            reward += "Book"
        elif reward == "Sharpness":
            tier = random.randint(1, 3)
            reward = "1 " + reward
            reward += " 1 " if tier == 1 else " 2 " if tier == 2 else " 3 "
            reward += "Book"
        else:
            reward = str(random.choice(values)) + " " + reward

        # Add the bounty details to the bounties dictionary
        config["bounties"][config["bounty_id"]] = {
            "target": target,
            "reward": reward
        }
        config["bounty_id"] += 1

        # Save the bounties dictionary to config.json
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)

        embed = discord.Embed(title="📜 New Bounty 📜", color=0x7300ff)
        embed.add_field(name=f"Target: {target}", value="", inline=False)
        embed.add_field(name=f"Reward: {reward}", value="", inline=False)
        embed.set_footer(text="Bounties")
        await ctx.send(embed=embed)


@bounty.command(name="complete")
async def bounty_complete(ctx, member: discord.Member):
    if ctx.message.author.id in [
            998956850886230148, 758058288024911962, 995161417902719136
    ]:
        await ctx.channel.purge(limit=1)
        count = 1
        config["hunters"][member.name]["count"] += count
        config["hunters"][
            member.name]["rank"] = 1 if count == 0 else calculate_rank(
                config["hunters"][member.name]["count"])
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)
            bounies = "bounties" if count >= 2 else "bounty"
        await ctx.send(
            f"{member.global_name} successfully completed {count} {bounies}")


@bot.group()
async def bounties(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Invalid subcommand.")
        sleep(2)
        await ctx.channel.purge(limit=1)


import discord
from discord.ext import commands

# ...


@bounties.command(name="view")
async def list_bounties(ctx):
    if ctx.message.author.id in [
            998956850886230148, 758058288024911962, 995161417902719136
    ]:
        bounties = config["bounties"]
        await ctx.channel.purge(limit=len(bounties) + 2)
        message = (
            "Bounties are a new way to earn valuables.\n"
            "To join the Bounty Hunter's Core, you must complete a bounty, however, you will not get any rewards from it, the reward will be your admission to the Bounty Hunter's Core.\n"
            "From then, you must show proof of bounty completion to be rewarded. Proof must be a screenshot of the death message of the target.\n"
            "Below is a list of the currently active bounties:")
        embed = discord.Embed(title="Bounties",
                              description=message,
                              color=0x7300ff)
        for bounty_id, bounty in bounties.items():
            target = bounty["target"]
            reward = bounty["reward"]
            embed.add_field(name=f"Bounty {bounty_id}",
                            value=f"Target: {target}\nReward: {reward}",
                            inline=False)

        embed.set_footer(text="Bounty Hunter's Core")
        embed.set_thumbnail(url="https://i.imgur.com/8fQyZ5v.png")
        embed.set_author(name="Bounty Hunter's Core",
                         icon_url="https://i.imgur.com/8fQyZ5v.png")

        # Creating a button to refresh
        button = discord.ui.Button(style=discord.ButtonStyle.secondary,
                                   label="Refresh",
                                   emoji="♻️",
                                   disabled=False)

        # Adding the button to the component
        view = discord.ui.View()
        view.add_item(button)

        # Send the initial embed
        message = await ctx.send(embed=embed, view=view)

        # Wait for button interaction
        try:
            button_ctx = await view.wait()
            await button_ctx.defer(edit_origin=True)

            # Perform bounty update when the button is clicked
            for bounty_id, bounty in bounties.items():
                target = bounty["target"]
                reward = bounty["reward"]
                embed = discord.Embed(title=f"📜 Bounty {bounty_id} 📜",
                                      color=0x7300ff)
                embed.add_field(name=f"Target: {target}",
                                value="",
                                inline=False)
                embed.add_field(name=f"Reward: {reward}",
                                value="",
                                inline=False)
                embed.set_footer(text="Bounties")
                await button_ctx.send(embed=embed)

            # Save the updated data to config.json
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)

        except asyncio.TimeoutError:
            await ctx.send("Button interaction timed out.")


@bounties.command(name="update_all")
async def update_all_bounties(ctx):
    if ctx.message.author.id in [
            998956850886230148, 758058288024911962, 995161417902719136
    ]:
        bounties = config["bounties"]
        await ctx.channel.purge(limit=len(bounties) + 2)

        # Update all bounties with values from the config
        for bounty_id, bounty in bounties.items():
            target = bounty["target"]
            reward = bounty["reward"]
            embed = discord.Embed(title=f"📜 Bounty {bounty_id} 📜",
                                  color=0x7300ff)
            embed.add_field(name=f"Target: {target}", value="", inline=False)
            embed.add_field(name=f"Reward: {reward}", value="", inline=False)
            embed.set_footer(text="Bounties")
            await ctx.send(embed=embed)

        # Save the updated data to config.json
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)


@bounties.command(name="remove")
async def hunter_remove(ctx, member: discord.Member, count: int):
    if ctx.message.author.id in [
            998956850886230148, 758058288024911962, 995161417902719136
    ]:
        await ctx.channel.purge(limit=1)
        config["hunters"][member.name]["count"] -= count
        config["hunters"][
            member.name]["rank"] = 1 if count == 0 else calculate_rank(
                config["hunters"][member.name]["count"])
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)


@bot.group()
async def hunters(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Invalid subcommand.")
        sleep(2)
        await ctx.channel.purge(limit=1)


@hunters.command(name="list")
async def hunter_list(ctx, member: discord.Member = None):
    if member is None:
        hunters = config["hunters"]
        for hunter_key, hunter_value in hunters.items():
            count = hunter_value["count"]
            rank = calculate_rank(hunter_value["count"])
            avatar = hunter_value["avatar"]
            name = hunter_value["name"]
            embed = discord.Embed(title="Hunter Stats", color=0x7300ff)
            embed.add_field(name=f"Bounties Completed: {count}",
                            value="",
                            inline=False)
            embed.add_field(name=f"Bounties Rank: {rank}",
                            value="",
                            inline=False)
            embed.set_author(name=name, icon_url=avatar)
            embed.set_footer(text="Bounties")
            await ctx.send(embed=embed)
    else:
        count = config["hunters"][member.name]["count"]
        rank = calculate_rank(config["hunters"][member.name]["count"])
        avatar = config["hunters"][member.name]["avatar"]
        embed = discord.Embed(title="Hunter Stats", color=0x7300ff)
        embed.add_field(name=f"Bounties Completed: {count}",
                        value="",
                        inline=False)
        embed.add_field(name=f"Bounties Rank: {rank}", value="", inline=False)
        embed.set_author(name=member.global_name, icon_url=avatar)
        embed.set_footer(text="Bounties")
        await ctx.send(embed=embed)


@hunters.command(name="add")
async def hunters_add(ctx, member: discord.Member):
    await ctx.channel.purge(limit=1)
    if ctx.message.author.id in [
            998956850886230148, 758058288024911962, 995161417902719136
    ]:
        if member.name not in config["hunters"]:
            avatar = member.display_avatar.url
            await ctx.send(
                f"Added {member.global_name if member.global_name is not None else member.name} as a Bounty Hunter"
            )
            config["hunters"][member.name] = {
                "name": member.global_name,
                "count": 1,
                "rank": 0,
                "avatar": avatar
            }
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            role = get(member.guild.roles, id=1170851733824614571)
            await member.add_roles(role)
        else:
            await ctx.send(
                f"{member.global_name} is already listed as a Bounty Hunter")
        await member.create_dm()
        await member.dm_channel.typing()
        sleep(4)
        await member.dm_channel.send(
            """Welcome to the heart of the Bounty Hunter's Core within the enchanting "+~.Llama Fun.~+" guild!

        Here's a glimpse of your potential exploits:

        Accept Bounties: In the Bounty Hunter's Core, every member is eligible to accept bounties and embrace the challenge.

        Fulfilling Bounties: Your mission, should you choose to accept it, involves eliminating the designated target. Provide irrefutable proof of your conquest to a Core High Official.

        Gather Rewards: Once your proof is validated, claim your well-deserved rewards. Send a message to a Core High Official, and the spoils of your triumphant endeavor shall be yours.

        While these are the primary tenets, there might be additional adventures awaiting you. Your journey has just begun! Thank you for choosing to stand among our esteemed ranks, and remember: Capture By Design, Kill By Necessity, this is the way of the hunter. Good luck out there."""
        )


@hunters.command(name="remove")
async def hunters_remove(ctx, member: discord.Member):
    await ctx.channel.purge(limit=1)
    if ctx.message.author.id in [
            998956850886230148, 758058288024911962, 995161417902719136
    ]:
        if member.name in config["hunters"]:
            await ctx.send(
                f"Removed {member.global_name if member.global_name is not None else member.name} as a Bounty Hunter"
            )
            del config["hunters"][member.name]
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            role = get(member.guild.roles, id=1170851733824614571)
            await member.remove_roles(role)
        else:
            await ctx.send(f"{member.global_name} is not a Bounty Hunter")


# Bot ping about command
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    bounties = len(config["bounties"])
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name=f"{bounties} bounties"))


@bot.event
async def on_command(ctx):
    bounties = len(config["bounties"])
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name=f"{bounties} bounties"))


@bot.event
async def on_disconnect():
    print("Bot disconnected. Attempting to reconnect...")
    while not bot.is_ready():
        try:
            await bot.connect(reconnect=True)
        except Exception as e:
            print(
                f"Failed to reconnect due to {e.__class__.__name__}: {e}. Retrying in 5 seconds..."
            )
            sleep(5)


# Run the bot
TOKEN = os.getenv('TOKEN')
bot.run(TOKEN)
