import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask
from threading import Thread

# ---------- خادم Flask (لإبقاء البوت مستيقظاً) ----------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive on Render!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# ---------- إعداد بوت ديسكورد ----------
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ البوت متصل كـ {bot.user}')
    await bot.change_presence(activity=discord.Game(name="!nuke | انتظر التأكيد"))

@bot.command()
@commands.has_permissions(administrator=True)
async def nuke(ctx):
    await ctx.send("💀 **تأكيد التخريب؟** اكتب `confirm` خلال 15 ثانية.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'confirm'

    try:
        await bot.wait_for('message', timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("❌ تم الإلغاء (انتهى الوقت).")
        return

    guild = ctx.guild
    await ctx.send(f"☣️ جارٍ تخريب السيرفر `{guild.name}` ...")

    # طرد الأعضاء
    banned = 0
    for member in guild.members:
        if member == guild.owner or member == bot.user:
            continue
        try:
            await member.ban(reason="Nuke")
            banned += 1
            await asyncio.sleep(0.5)
        except:
            pass

    # حذف الغرف
    channels = guild.channels
    for ch in channels:
        try:
            await ch.delete()
            await asyncio.sleep(0.3)
        except:
            pass

    # غرفة جديدة للتأكيد
    try:
        new_ch = await guild.create_text_channel("☢️ تم التخريب")
        await new_ch.send(f"✅ تم طرد **{banned}** عضواً وحذف **{len(channels)}** غرفة.")
    except:
        pass

@nuke.error
async def nuke_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("⛔ تحتاج صلاحية **Administrator**.")

if __name__ == "__main__":
    keep_alive()
    TOKEN = os.environ.get('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ لم يتم العثور على التوكن! أضف DISCORD_TOKEN في متغيرات البيئة.")
    else:
        bot.run(TOKEN)
