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

# ---------- إعداد البوت (تعطيل الأمر help الافتراضي) ----------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# ---------- حدث التشغيل ----------
@bot.event
async def on_ready():
    print(f'✅ البوت متصل كـ {bot.user}')
    print(f'✅ موجود في {len(bot.guilds)} سيرفر')
    await bot.change_presence(activity=discord.Game(name="!help | !nuke"))

# ---------- حدث استقبال الرسائل (للتشخيص) ----------
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    print(f'📩 رسالة من {message.author}: {message.content}')
    await bot.process_commands(message)

# ---------- أمر help المخصص ----------
@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📋 قائمة الأوامر",
        description="البوت جاهز للتخريب (بإذنك)",
        color=0xff0000
    )
    embed.add_field(name="!ping", value="اختبار استجابة البوت", inline=False)
    embed.add_field(name="!test", value="عرض صلاحيات البوت في القناة", inline=False)
    embed.add_field(name="!nuke", value="تخريب السيرفر (يتطلب صلاحية Administrator)", inline=False)
    await ctx.send(embed=embed)

# ---------- أمر ping ----------
@bot.command()
async def ping(ctx):
    await ctx.send('🏓 Pong! البوت يعمل.')

# ---------- أمر test ----------
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

# ---------- الأمر الرئيسي !nuke (نسخة كاملة) ----------
@bot.command()
@commands.has_permissions(administrator=True)
async def nuke(ctx):
    """
    حذف جميع الغرف وطرد جميع الأعضاء (عدا المالك والبوت)
    يتطلب صلاحية Administrator ويطلب تأكيداً كتابياً
    """

    # 1. طلب تأكيد
    await ctx.send("💀 **تأكيد التخريب؟** اكتب `confirm` خلال 15 ثانية لتنفيذ الأمر.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'confirm'

    try:
        await bot.wait_for('message', timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("❌ تم إلغاء العملية (انتهى الوقت).")
        return

    guild = ctx.guild
    await ctx.send(f"☣️ بدء تخريب السيرفر `{guild.name}` ...")

    # 2. طرد (Ban) جميع الأعضاء باستثناء المالك والبوت
    await ctx.send(f"🛠️ [1/2] جارٍ طرد الأعضاء...")
    banned_count = 0
    for member in guild.members:
        if member == guild.owner or member == bot.user:
            continue
        try:
            await member.ban(reason="Nuke Command")
            banned_count += 1
            await asyncio.sleep(0.5)  # تجنب تجاوز حدود ديسكورد
        except Exception as e:
            print(f"⚠️ فشل طرد {member}: {e}")

    # 3. حذف جميع الغرف (نصية وصوتية)
    await ctx.send(f"🗑️ [2/2] جارٍ حذف جميع الغرف...")
    channels = guild.channels
    deleted_count = 0
    for channel in channels:
        try:
            await channel.delete()
            deleted_count += 1
            await asyncio.sleep(0.3)
        except Exception as e:
            print(f"⚠️ فشل حذف {channel}: {e}")

    # 4. إنشاء غرفة جديدة لتأكيد التخريب
    try:
        new_channel = await guild.create_text_channel("☢️ تم التخريب")
        await new_channel.send(
            f"✅ **اكتمل التخريب بنجاح!**\n"
            f"تم طرد **{banned_count}** عضواً.\n"
            f"تم حذف **{deleted_count}** غرفة."
        )
    except Exception as e:
        print(f"⚠️ فشل إنشاء غرفة التقرير: {e}")

# ---------- معالج الأخطاء (إذا لم يكن لديه صلاحية) ----------
@nuke.error
async def nuke_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("⛔ **خطأ:** تحتاج صلاحية **Administrator** لاستخدام هذا الأمر.")
    else:
        await ctx.send(f"⚠️ حدث خطأ غير متوقع: {error}")

# ---------- تشغيل البوت في Thread منفصل ----------
def run_bot():
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        print('❌ لم يتم العثور على DISCORD_TOKEN!')
        return
    bot.run(token)

# تشغيل Thread البوت فوراً (لأن gunicorn لا ينفذ if __name__)
bot_thread = Thread(target=run_bot, daemon=True)
bot_thread.start()

# ---------- تشغيل Flask (إذا كان الملف هو الرئيسي) ----------
if __name__ == "__main__":
    run_flask()
