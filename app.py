import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# ---------- خادم Flask ----------
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

@bot.event
async def on_ready():
    print(f'✅ البوت متصل كـ {bot.user}')
    print(f'✅ موجود في {len(bot.guilds)} سيرفر')
    await bot.change_presence(activity=discord.Game(name="!ping | !nuke"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    print(f'📩 رسالة من {message.author}: {message.content}')
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send('🏓 Pong! البوت يعمل.')

@bot.command()
async def test(ctx):
    await ctx.send('✅ البوت يعمل بنجاح!')

@bot.command()
@commands.has_permissions(administrator=True)
async def nuke(ctx):
    await ctx.send('💀 جارٍ تنفيذ التخريب... (نسخة تجريبية)')

# ---------- تشغيل البوت في Thread منفصل ----------
def run_bot():
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        print('❌ لم يتم العثور على DISCORD_TOKEN!')
        return
    bot.run(token)

# **هنا التعديل**: تشغيل Thread البوت مباشرة (خارج if __name__)
bot_thread = Thread(target=run_bot, daemon=True)
bot_thread.start()

# ---------- تشغيل Flask (إذا كان الملف هو الرئيسي) ----------
if __name__ == "__main__":
    run_flask()
