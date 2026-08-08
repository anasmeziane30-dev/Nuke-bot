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
    return "✅ Bot is alive on Render!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# ---------- إعداد البوت ----------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ---------- حدث تشغيل البوت ----------
@bot.event
async def on_ready():
    print(f'✅ البوت متصل كـ {bot.user}')
    print(f'✅ موجود في {len(bot.guilds)} سيرفر')
    await bot.change_presence(activity=discord.Game(name="!ping | !nuke"))

# ---------- حدث استقبال الرسائل (للتشخيص) ----------
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    print(f"📩 رسالة من {message.author}: {message.content}")
    await bot.process_commands(message)

# ---------- الأمر: ping ----------
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 بونغ! البوت يعمل.")

# ---------- الأمر: test ----------
@bot.command()
async def test(ctx):
    perms = ctx.channel.permissions_for(ctx.guild.me)
    msg = (
        "🔧 **صلاحياتي هنا:**\n"
        f"• قراءة الرسائل: {'✅' if perms.read_messages else '❌'}\n"
        f"• إرسال الرسائل: {'✅' if perms.send_messages else '❌'}\n"
        f"• إدارة القنوات: {'✅' if perms.manage_channels else '❌'}\n"
        f"• طرد الأعضاء: {'✅' if perms.kick_members else '❌'}\n"
        f"• حظر الأعضاء: {'✅' if perms.ban_members else '❌'}"
    )
    await ctx.send(msg)

# ---------- الأمر: nuke (نسخة مبسطة للاختبار) ----------
@bot.command()
async def nuke(ctx):
    await ctx.send("⚡ تم استقبال أمر nuke! سيتم تنفيذ التخريب...")
    # سيتم إضافة الكود الكامل لاحقاً بعد التأكد من عمل البوت

# ---------- تشغيل البوت في خلفية (Thread) ----------
def run_bot():
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        print("❌ لم يتم العثور على DISCORD_TOKEN!")
        return
    bot.run(token)

# ---------- عند تشغيل الملف ----------
if __name__ == "__main__":
    # تشغيل البوت في thread منفصل
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True  # ينتهي تلقائياً عند إغلاق البرنامج
    bot_thread.start()
    
    # تشغيل خادم Flask (الذي سيديره gunicorn)
    run_flask()
