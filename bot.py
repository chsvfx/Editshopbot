import os
import psutil
from datetime import datetime, timezone

import discord
from discord.ext import commands, tasks

# ===================== CONFIG =====================
GUILD_ID = 1351310078849847358
MEMBER_ROLE_ID = 1386784222781505619

VERIFY_LOG_CHANNEL_ID = 1462412645150752890
JOIN_LOG_CHANNEL_ID = 1462412615195164908
LEAVE_LOG_CHANNEL_ID = 1462412568747573422
BOT_STATUS_CHANNEL_ID = 1463660427413033093

# ===================== INTENTS =====================
intents = discord.Intents.none()
intents.guilds = True
intents.members = True
intents.messages = True

bot = commands.Bot(intents=intents)

START_TIME = datetime.now(timezone.utc)
status_message = None

# ===================== HELPERS =====================
def uptime():
    delta = datetime.now(timezone.utc) - START_TIME
    h, r = divmod(int(delta.total_seconds()), 3600)
    m, s = divmod(r, 60)
    return f"{h}h {m}m {s}s"

async def send_embed(channel_id, title, color, fields=None):
    channel = bot.get_channel(channel_id)
    if not channel:
        return

    embed = discord.Embed(
        title=title,
        color=color,
        timestamp=datetime.now(timezone.utc)
    )

    if fields:
        for n, v in fields:
            embed.add_field(name=n, value=v, inline=False)

    await channel.send(embed=embed)

# ===================== VERIFY VIEW =====================
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✨ Verify", style=discord.ButtonStyle.success)
    async def verify(self, button, interaction):
        role = interaction.guild.get_role(MEMBER_ROLE_ID)

        if role in interaction.user.roles:
            await interaction.response.send_message(
                "✅ You are already verified.",
                ephemeral=True
            )
            return

        await interaction.user.add_roles(role, reason="Verification")
        await interaction.response.send_message(
            "🎉 Verified! Welcome to ꨄ.'s Edit Shop 🛍️",
            ephemeral=True
        )

        await send_embed(
            VERIFY_LOG_CHANNEL_ID,
            "✅ Member Verified",
            discord.Color.green(),
            [
                ("User", f"{interaction.user} ({interaction.user.id})"),
                ("Time", f"<t:{int(datetime.now(timezone.utc).timestamp())}:F>")
            ]
        )

# ===================== SLASH COMMANDS =====================
@bot.slash_command(name="verify", description="Verify yourself")
async def verify(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        title="✨ Verify — ꨄ.'s Edit Shop",
        description="Click the button below to verify and unlock the server 💕",
        color=discord.Color.pink()
    )
    await ctx.respond(embed=embed, view=VerifyView())

@bot.slash_command(name="rules", description="View server rules")
async def rules(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        title="📜 Server Rules",
        description=(
            "🌸 Be respectful\n"
            "🚫 No spam / ads\n"
            "🛍️ Do not rush edits\n"
            "❌ No refunds once started\n\n"
            "Breaking rules = punishment."
        ),
        color=discord.Color.blurple()
    )
    await ctx.respond(embed=embed)

# ===================== EVENTS =====================
@bot.event
async def on_ready():
    print(f"🟢 Logged in as {bot.user}")
    update_status.start()

@bot.event
async def on_member_join(member):
    await send_embed(
        JOIN_LOG_CHANNEL_ID,
        "🟢 Member Joined",
        discord.Color.green(),
        [
            ("User", f"{member} ({member.id})"),
            ("Account Created", f"<t:{int(member.created_at.timestamp())}:F>")
        ]
    )

@bot.event
async def on_member_remove(member):
    await send_embed(
        LEAVE_LOG_CHANNEL_ID,
        "🔴 Member Left",
        discord.Color.red(),
        [
            ("User", f"{member} ({member.id})")
        ]
    )

# ===================== STATUS LOOP =====================
@tasks.loop(seconds=15)
async def update_status():
    global status_message
    channel = bot.get_channel(BOT_STATUS_CHANNEL_ID)
    if not channel:
        return

    mem = psutil.virtual_memory()

    embed = discord.Embed(
        title="🛍️ ꨄ.'s Edit Shop — Bot Status",
        color=discord.Color.pink(),
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="⏱️ Uptime", value=uptime(), inline=True)
    embed.add_field(name="💾 Memory", value=f"{mem.percent}%", inline=True)

    if status_message is None:
        status_message = await channel.send(embed=embed)
    else:
        await status_message.edit(embed=embed)

# ===================== RUN =====================
bot.run(os.getenv("TOKEN"))
