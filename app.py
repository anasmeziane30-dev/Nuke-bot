import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask
from threading import Thread

# -------------------------------------------------
# 1. خادم Flask (لإبقاء البوت مستيقظاً على Render)
# -------------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is alive on Render!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# -------------------------------------------------
# 2. إعداد بوت ديسكورد
# -------------------------------------------------
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# -------------------------------------------------
# 3. حدث عند تشغيل البوت
# -------------------------------------------------
@bot.event
async def on_ready():
    print(f'✅ البوت متصل كـ {bot.user}')
    print(f'✅ موجود في {len(bot.guilds)} سيرفر')
    await bot.change_presence(activity=discord.Game(name="!nuke | !ping | !test"))

# -------------------------------------------------
# 4. أوامر اختبارية (للتأكد من عمل البوت)
# -------------------------------------------------
@bot.command()
async def ping(ctx):
    """أمر بسيط لاختبار استجابة البوت"""
    await ctx.send("🏓 بونغ! البوت يعمل.")

@bot.command()
async def test(ctx):
    """عرض صلاحيات البوت في القناة الحالية"""
    perms = ctx.channel.permissions_for(ctx.guild.me)
    embed = discord.Embed(title="🔧 صلاحياتي هنا", color=0x00ff00)
    embed.add_field(name="قراءة الرسائل", value="✅" if perms.read_messages else "❌", inline=True)
    embed.add_field(name="إرسال الرسائل", value="✅" if perms.send_messages else "❌", inline=True)
    embed.add_field(name="إدارة القنوات", value="✅" if perms.manage_channels else "❌", inline=True)
    embed.add_field(name="طرد الأعضاء", value="✅" if perms.kick_members else "❌", inline=True)
    embed.add_field(name="حظر الأعضاء", value="✅" if perms.ban_members else "❌", inline=True)
    embed.add_field(name="إدارة الأدوار", value="✅" if perms.manage_roles else "❌", inline=True)
    await ctx.send(embed=embed)

# -------------------------------------------------
# 5. الأمر الرئيسي !nuke (مع تأكيد وحماية)
# -------------------------------------------------
@bot.command()
@commands.has_permissions(administrator=True)
async def nuke(ctx):
    """
    حذف جميع الغرف وطرد جميع الأعضاء (عدا المالك والبوت نفسه)
    يتطلب صلاحية Administrator ويطلب تأكيداً كتابياً
    """

    # أ. طلب تأكيد
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

    # ب. طرد (Ban) جميع الأعضاء باستثناء المالك والبوت
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

    # ج. حذف جميع الغرف (نصية وصوتية)
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

    # د. إنشاء غرفة جديدة لتأكيد التخريب
    try:
        new_channel = await guild.create_text_channel("☢️ تم التخريب")
        await new_channel.send(
            f"✅ **اكتمل التخريب بنجاح!**\n"
            f"تم طرد **{banned_count}** عضواً.\n"
            f"تم حذف **{deleted_count}** غرفة."
        )
    except Exception as e:
        print(f"⚠️ فشل إنشاء غرفة التقرير: {e}")

# -------------------------------------------------
# 6. معالج الأخطاء الخاص بـ !nuke
# -------------------------------------------------
@nuke.error
async def nuke_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("⛔ **خطأ:** تحتاج صلاحية **Administrator** لاستخدام هذا الأمر.")
    else:
        await ctx.send(f"⚠️ حدث خطأ غير متوقع: {error}")

# -------------------------------------------------
# 7. تشغيل البوت (مع إبقاء Flask نشطاً)
# -------------------------------------------------
if __name__ == "__main__":
    keep_alive()  # تشغيل خادم Flask أولاً
    TOKEN = os.environ.get('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ فشل: لم يتم العثور على DISCORD_TOKEN في متغيرات البيئة.")
    else:
        print("🔄 جارٍ تشغيل البوت...")
        bot.run(TOKEN)
