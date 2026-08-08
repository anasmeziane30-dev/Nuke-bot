import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask
from threading import Thread

# ---------- إعداد خادم Flask (لإبقاء البوت مستيقظاً في Render) ----------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running and alive!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# ---------- إعداد بوت ديسكورد ----------
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# ---------- حدث تشغيل البوت ----------
@bot.event
async def on_ready():
    print(f'✅ البوت متصل كـ {bot.user}')
    await bot.change_presence(activity=discord.Game(name="!nuke | انتظر التأكيد"))

# ---------- أمر التخريب !nuke ----------
@bot.command()
@commands.has_permissions(administrator=True)  # يجب أن يكون للأدمن صلاحية
async def nuke(ctx):
    """
    حذف جميع الغرف وطرد جميع الأعضاء (عدا المالك)
    """

    # 1. طلب تأكيد كتابي لتجنب الضغط بالخطأ
    await ctx.send("💀 **تأكيد التخريب؟** اكتب `confirm` خلال 15 ثانية لتنفيذ الأمر.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'confirm'

    try:
        await bot.wait_for('message', timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("❌ تم إلغاء العملية (انتهى الوقت).")
        return

    # 2. بدء التخريب
    guild = ctx.guild
    await ctx.send(f"☣️ جارٍ تخريب السيرفر `{guild.name}` ...")

    # --- أ. طرد (Ban) جميع الأعضاء (عدا المالك) ---
    await ctx.send(f"🛠️ [1/2] جارٍ طرد {len(guild.members)} عضواً...")
    banned_count = 0
    for member in guild.members:
        # لا تطرد مالك السيرفر، ولا تطرد البوت نفسه
        if member == guild.owner or member == bot.user:
            continue
        try:
            await member.ban(reason="Nuke Command by User")
            banned_count += 1
            await asyncio.sleep(0.5)  # تأخير بسيط لتجنب حدود ديسكورد (Rate Limit)
        except:
            pass

    # --- ب. حذف جميع الغرف (نصية وصوتية) ---
    await ctx.send(f"🗑️ [2/2] جارٍ حذف جميع الغرف...")
    channels = guild.channels
    for channel in channels:
        try:
            await channel.delete()
            await asyncio.sleep(0.3)
        except:
            pass

    # --- ج. إنشاء غرفة جديدة كسجل للتخريب (اختياري) ---
    try:
        new_channel = await guild.create_text_channel("☢️ تم التخريب")
        await new_channel.send(f"✅ **اكتمل التخريب بنجاح!**\nتم طرد **{banned_count}** عضواً وحذف **{len(channels)}** غرفة.")
    except:
        pass  # في حال لم يستطع إنشاء الغرفة

# ---------- معالج الأخطاء (إذا حاول شخص بدون صلاحية استخدام الأمر) ----------
@nuke.error
async def nuke_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("⛔ عذراً، أنت بحاجة إلى صلاحية **Administrator** لاستخدام هذا الأمر.")

# ---------- تشغيل البوت ----------
if __name__ == "__main__":
    keep_alive()  # تشغيل خادم Flask أولاً
    TOKEN = os.environ.get('DISCORD_TOKEN')  # جلب التوكن من متغيرات البيئة في Render
    if TOKEN is None:
        print("❌ خطأ: لم يتم العثور على التوكن! تأكد من إضافة DISCORD_TOKEN في متغيرات البيئة.")
    else:
        bot.run(TOKEN)
