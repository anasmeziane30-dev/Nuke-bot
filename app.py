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
intents.message_content = True   # مهم جداً
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ البوت متصل كـ {bot.user}')
    print(f'✅ موجود في {len(bot.guilds)} سيرفر')
    await bot.change_presence(activity=discord.Game(name="!nuke | !ping"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    print(f'📩 رسالة من {message.author}: {message.content}')
    await bot.process_commands(message)

# ---------- أمر اختبار ----------
@bot.command()
async def ping(ctx):
    await ctx.send('🏓 Pong! البوت يعمل.')

# ---------- أمر nuke (نسخة مبسطة) ----------
@bot.command()
@commands.has_permissions(administrator=True)
async def nuke(ctx):
    await ctx.send('💀 جارٍ تنفيذ التخريب... (نسخة تجريبية)')
    # سيتم إضافة الكود الكامل لاحقاً

# ---------- تشغيل البوت في خلفية (Thread) ----------
def run_bot():
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        print('❌ لم يتم العثور على DISCORD_TOKEN!')
        return
    bot.run(token)

# ---------- عند تشغيل الملف ----------
if __name__ == "__main__":
    # 1. تشغيل البوت في Thread منفصل
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # 2. تشغيل خادم Flask (الذي سيديره gunicorn)
    run_flask()
