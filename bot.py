import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timezone
import os
import psutil

# ===================== CONFIG =====================
GUILD_ID = 1351310078849847358
MEMBER_ROLE_ID = 1386784222781505619

ALLOWED_USER_IDS = [771432636563324929, 1329386427460358188]

SYSTEM_LOG_CHANNEL_ID = 1462412675295481971
VERIFY_LOG_CHANNEL_ID = 1462412645150752890
JOIN_LOG_CHANNEL_ID = 1462412615195164908
LEAVE_LOG_CHANNEL_ID = 1462412568747573422
BOT_STATUS_CHANNEL_ID = 1463660427413033093
VOICE_LOG_CHANNEL_ID = 1463842358448623822
TICKET_CATEGORY_ID = 1462421944170446869

TRACKED_VOICE_CHANNELS = [
    1461424134906056846,
    1462421172519178313,
    1439274257585799198,
    1457046754661765245,
    1432491181006127268
]

PROTECTED_IDS = [1351310078887858299, 1386779868532047982]

# ===================== INTENTS =====================
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.reactions = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===================== MEMORY =====================
START_TIME = datetime.now(timezone.utc)
status_message = None
invite_tracker = {}

# ===================== HELPERS =====================
def get_channel(cid):
    return bot.get_channel(cid)

def format_account_age(created_at):
    delta = (datetime.now(timezone.utc) - created_at).days
    return f"{delta // 365}y {(delta % 365) // 30}m {(delta % 365) % 30}d"

def format_uptime():
    delta = datetime.now(timezone.utc) - START_TIME
    h, r = divmod(int(delta.total_seconds()), 3600)
    m, s = divmod(r, 60)
    return f"{h}h {m}m {s}s"

async def send_embed(channel_id, title, color, fields=None, thumbnail=None):
    channel = get_channel(channel_id)
    if not channel:
        return
    embed = discord.Embed(
        title=title,
        color=color,
        timestamp=datetime.now(timezone.utc)
    )
    if fields:
        for n, v, i in fields:
            embed.add_field(name=n, value=v, inline=i)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    await channel.send(embed=embed)

# ===================== STATUS EMBED =====================
async def get_status_embed():
    guild = bot.get_guild(GUILD_ID)
    members = sum(1 for m in guild.members if not m.bot) if guild else 0
    bots = sum(1 for m in guild.members if m.bot) if guild else 0

    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()

    embed = discord.Embed(
        title="🛍️ ꨄ.'s Edit Shop — Bot Status",
        description="✨ Live system & server statistics",
        color=discord.Color.pink(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="👥 Members", value=members, inline=True)
    embed.add_field(name="🤖 Bots", value=bots, inline=True)
    embed.add_field(name="⏱️ Uptime", value=format_uptime(), inline=True)
    embed.add_field(name="⚡ CPU", value=f"{cpu}%", inline=True)
    embed.add_field(
        name="💾 Memory",
        value=f"{mem.percent}% ({mem.used // (1024**2)}MB)",
        inline=True
    )
    embed.set_footer(text="ꨄ.'s Edit Shop • System Monitor")
    return embed

# ===================== VERIFY VIEW =====================
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="✨ Verify",
        style=discord.ButtonStyle.success,
        custom_id="verify_button"
    )
    async def verify(self, interaction: discord.Interaction, _):
        role = interaction.guild.get_role(MEMBER_ROLE_ID)
        if role in interaction.user.roles:
            await interaction.response.send_message(
                "💗 You are already verified!",
                ephemeral=True
            )
            return

        await interaction.user.add_roles(role, reason="Edit Shop Verification")
        await interaction.response.send_message(
            "🎉 Verification complete! Welcome to ꨄ.'s Edit Shop 🛍️",
            ephemeral=True
        )

        await send_embed(
            VERIFY_LOG_CHANNEL_ID,
            "✅ Member Verified",
            discord.Color.green(),
            [
                ("👤 User", f"{interaction.user.mention}\n`{interaction.user.id}`", False),
                ("🕒 Time", f"<t:{int(datetime.now(timezone.utc).timestamp())}:F>", False),
                ("💻 Account Age", format_account_age(interaction.user.created_at), False)
            ],
            interaction.user.display_avatar.url
        )

# ===================== COMMANDS =====================
@bot.tree.command(name="verify", description="Verify to access ꨄ.'s Edit Shop")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def verify(interaction: discord.Interaction):
    embed = discord.Embed(
        title="✨ Verify — ꨄ.'s Edit Shop",
        description=(
            "🛍️ Welcome to **ꨄ.'s Edit Shop**!\n\n"
            "Click the button below to verify and unlock all channels 💕\n"
            "🔓 Verification is required to chat & order."
        ),
        color=discord.Color.pink()
    )
    await interaction.response.send_message(embed=embed, view=VerifyView())

@bot.tree.command(name="rules", description="View server rules")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def rules(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 ꨄ.'s Edit Shop — Rules",
        description=(
            "🌸 **Please follow all rules below** 🌸\n\n"
            "1️⃣ Be respectful — no drama or hate\n"
            "2️⃣ No spamming or flooding\n"
            "3️⃣ No NSFW or disturbing content\n"
            "4️⃣ No advertising or self-promo\n\n"
            "🛍️ **Shop Rules**\n"
            "5️⃣ Do not rush edits\n"
            "6️⃣ Be clear with your order details\n"
            "7️⃣ No refunds once started\n\n"
            "⚠️ Breaking rules may result in warnings, mutes, or bans."
        ),
        color=discord.Color.blurple()
    )
    await interaction.response.send_message(embed=embed)

# ===================== EVENTS (UNCHANGED LOGIC) =====================
@bot.event
async def on_ready():
    bot.add_view(VerifyView())
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))

    guild = bot.get_guild(GUILD_ID)
    if guild:
        for inv in await guild.invites():
            invite_tracker[inv.code] = inv.uses

    update_status.start()
    print(f"🟢 Logged in as {bot.user}")

# ===================== STATUS LOOP =====================
@tasks.loop(seconds=10)
async def update_status():
    global status_message
    channel = get_channel(BOT_STATUS_CHANNEL_ID)
    if not channel:
        return

    embed = await get_status_embed()
    if status_message is None:
        status_message = await channel.send(embed=embed)
    else:
        await status_message.edit(embed=embed)

# ===================== RUN =====================
bot.run(os.getenv("TOKEN"))
