import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

# قراءة المتغيرات من الاستضافة
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
TARGET_BOT = os.getenv("TARGET_BOT", "@funding_bot")
SESSIONS_RAW = os.getenv("SESSIONS_STRING", "")

# تقسيم الجلسات بناءً على الفاصلة
SESSIONS = [s.strip() for s in SESSIONS_RAW.split(",") if s.strip()]

async def run_collector(session_string, account_index):
    # تهيئة العميل لكل حساب
    client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
    
    async with client:
        print(f"🚀 الحساب #{account_index} متصل وجاهز للعمل.")
        while True:
            try:
                # إرسال /start
                await client.send_message(TARGET_BOT, '/start')
                await asyncio.sleep(6)
                
                # جلب الرسالة الأخيرة
                messages = await client.get_messages(TARGET_BOT, limit=1)
                if not messages:
                    await asyncio.sleep(60)
                    continue
                
                last_msg = messages[0]
                
                # محاولة النقر على أزرار "الاشتراك" أو "التجميع"
                if last_msg.reply_markup:
                    for row in last_msg.reply_markup.rows:
                        for button in row.buttons:
                            text = button.text.lower()
                            if any(word in text for word in ["اشتراك", "قناة", "انضمام", "تجميع"]):
                                print(f"📌 [الحساب {account_index}] انضمام إلى: {button.text}")
                                await last_msg.click(data=button.data)
                                await asyncio.sleep(5)
                                
                                # محاولة النقر على زر "تحقق" بعد الانضمام
                                updated = await client.get_messages(TARGET_BOT, limit=1)
                                if updated and updated[0].reply_markup:
                                    for r in updated[0].reply_markup.rows:
                                        for b in r.buttons:
                                            if any(w in b.text.lower() for w in ["تحقق", "تأكيد", "تم"]):
                                                print(f"✅ [الحساب {account_index}] تم التحقق بنجاح.")
                                                await updated[0].click(data=b.data)
                                                await asyncio.sleep(3)
                
                # وقت راحة بين الجولات لكل حساب
                await asyncio.sleep(120)
                
            except Exception as e:
                print(f"❌ خطأ في الحساب {account_index}: {e}")
                await asyncio.sleep(60)

async def main():
    if not API_ID or not API_HASH:
        print("⚠️ خطأ: تأكد من ضبط API_ID و API_HASH في المتغيرات.")
        return
    if not SESSIONS:
        print("⚠️ خطأ: لا توجد جلسات (SESSIONS_STRING) مضافة.")
        return

    print(f"✅ تم بدء تشغيل {len(SESSIONS)} حساب.")
    tasks = [run_collector(session, i + 1) for i, session in enumerate(SESSIONS)]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
