# index.py
import discord
import os
from discord.ext import commands

TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

PREFIX = '!'
bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())

TICKET_CHANNEL_ID = 1246630234913247342
SUPPORT_ROLE_ID = 1357999371966349533

TICKET_CATEGORIES = {
    "vehicle": {
        "name": "Vehicle Orders",
        "emoji_id": 1358002486899642440,
        "category_id": 1355398688822001694,
        "message": "Hello! Thanks for ordering! What vehicle goodies are you after today? Let me know if you want a **Livery** or some awesome **ELS**!",
        "open_count": 0
    },
    "discord": {
        "name": "Discord Orders",
        "emoji_id": 1358002874574967015,
        "category_id": 1357997919957028914,
        "message": "Hey! So you need some Discord help? Tell me what you're looking for! Is it a **Custom Bot**, a full **Server Setup**, or maybe help with **Channels, Roles, and Permissions**?",
        "open_count": 0
    },
    "clothing": {
        "name": "Clothing Orders",
        "emoji_id": 1358002571540959345,
        "category_id": 1358003614328557708,
        "message": "Hi there! Ready for some new threads? Tell me if you're after **Shirts**, **Pants**, or a cool **Full Set**!",
        "open_count": 0
    },
    "graphics": {
        "name": "Graphic Orders",
        "emoji_id": 1358002515320377466,
        "category_id": 1358003871443587314,
        "message": "Hello! Looking for some awesome graphics? Let me know if you need **Logos**, **Banners**, or some cool **GFX**!",
        "open_count": 0
    }
}

TICKET_EMBED_MESSAGE_ID = None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await send_ticket_embed()

async def update_ticket_counts():
    global TICKET_EMBED_MESSAGE_ID
    channel = bot.get_channel(TICKET_CHANNEL_ID)
    if not channel:
        print(f"Error: Ticket channel not found with ID {TICKET_CHANNEL_ID}")
        return

    embed = discord.Embed(title="Pick what you need by reacting with the right emoji!", color=0x00ff00)
    description = ""
    for category_key, data in TICKET_CATEGORIES.items():
        emoji = bot.get_emoji(data["emoji_id"])
        if emoji:
            description += f"{emoji} **{data['name']} |** ({data['open_count']} Open)\n"
            if category_key == "vehicle":
                description += "- Liveries\n- ELS\n"
            elif category_key == "discord":
                description += "- Custom Bots\n- Server Setups\n- Channel / Roles / Perms\n"
            elif category_key == "clothing":
                description += "- Shirts\n- Pants\n- Full Sets\n"
            elif category_key == "graphics":
                description += "- Logos\n- Banners\n- GFX\n"
        else:
            print(f"Error: Emoji not found with ID {data['emoji_id']} for {data['name']}")
            return
    embed.description = description

    if TICKET_EMBED_MESSAGE_ID:
        try:
            message = await channel.fetch_message(TICKET_EMBED_MESSAGE_ID)
            await message.edit(embed=embed)
        except discord.NotFound:
            print("Error: Ticket embed message not found. Resending...")
            await send_ticket_embed()
    else:
        await send_ticket_embed()

async def send_ticket_embed():
    global TICKET_EMBED_MESSAGE_ID
    channel = bot.get_channel(TICKET_CHANNEL_ID)
    if not channel:
        print(f"Error: Ticket channel not found with ID {TICKET_CHANNEL_ID}")
        return

    embed = discord.Embed(title="Pick what you need by reacting with the right emoji!", color=0x00ff00)
    description = ""
    for category_key, data in TICKET_CATEGORIES.items():
        emoji = bot.get_emoji(data["emoji_id"])
        if emoji:
            description += f"{emoji} **{data['name']} |** ({data['open_count']} Open)\n"
            if category_key == "vehicle":
                description += "- Liveries\n- ELS\n"
            elif category_key == "discord":
                description += "- Custom Bots\n- Server Setups\n- Channel / Roles / Perms\n"
            elif category_key == "clothing":
                description += "- Shirts\n- Pants\n- Full Sets\n"
            elif category_key == "graphics":
                description += "- Logos\n- Banners\n- GFX\n"
        else:
            print(f"Error: Emoji not found with ID {data['emoji_id']} for {data['name']}")
            return
    embed.description = description

    message = await channel.send(embed=embed)
    TICKET_EMBED_MESSAGE_ID = message.id
    for category_key in TICKET_CATEGORIES:
        emoji = bot.get_emoji(TICKET_CATEGORIES[category_key]["emoji_id"])
        if emoji:
            await message.add_reaction(emoji)

@bot.command()
async def orderhereembed(ctx):
    """Sends the ticket order embed to the ticket channel."""
    await send_ticket_embed()
    await ctx.send("The order embed has been sent!", delete_after=5)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    channel = bot.get_channel(payload.channel_id)
    if channel.id != TICKET_CHANNEL_ID:
        return

    message = await channel.fetch_message(payload.message_id)
    if not message.embeds:
        return

    emoji = payload.emoji

    for category_key, data in TICKET_CATEGORIES.items():
        if data["emoji_id"] == emoji.id:
            guild = bot.get_guild(payload.guild_id)
            if guild is None:
                return
            member = guild.get_member(payload.user_id)
            if member is None:
                return

            ticket_category = guild.get_channel(data["category_id"])
            if not ticket_category:
                print(f"Error: Ticket category not found with ID {data['category_id']} for {data['name']}")
                return

            support_role = guild.get_role(SUPPORT_ROLE_ID)
            if not support_role:
                print("Error: Support role not found.")
                return

            ticket_name = f'{category_key}-ticket-{member.name.lower().replace(" ", "-")}'

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                support_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
                bot.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }

            ticket_channel = await ticket_category.create_text_channel(ticket_name, overwrites=overwrites)
            await ticket_channel.send(f"Hey <@{member.id}>! Welcome to your **{data['name']}** ticket!\n\n{data['message']}")
            await ticket_channel.send(f"Members with the <@&{SUPPORT_ROLE_ID}> role can now help you!")
            await member.send(f"Your **{data['name']}** ticket has been created: <#{ticket_channel.id}>")

            TICKET_CATEGORIES[category_key]["open_count"] += 1
            await update_ticket_counts()

            await message.remove_reaction(emoji, member)
            return

@bot.command()
async def close(ctx, *, reason="No reason provided"):
    """Closes the current ticket."""
    channel_name = ctx.channel.name
    for category_key in TICKET_CATEGORIES:
        if channel_name.startswith(f'{category_key}-ticket-'):
            support_role = ctx.guild.get_role(SUPPORT_ROLE_ID)
            if support_role in ctx.author.roles or ctx.author == ctx.guild.owner:
                await ctx.channel.send(f"This ticket is now being closed by <@{ctx.author.id}>. Reason: {reason}")
                await ctx.channel.delete()
                TICKET_CATEGORIES[category_key]["open_count"] -= 1
                await update_ticket_counts()
            else:
                await ctx.send("You don't have permission to close this ticket.")
            return
    await ctx.send("This command can only be used in a ticket channel.")

bot.run(TOKEN)
