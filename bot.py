import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSIONS_RAW = os.getenv("SESSIONS_STRING", "")

# جلب عدة بوتات تمويل مفصولة بفواصل (مثلاً: @bot1,@bot2,@bot3)
TARGET_BOTS_RAW = os.getenv("TARGET_BOTS", "@funding_bot1,@funding_bot2")
TARGET_BOTS = [b.strip() for b in TARGET_BOTS_RAW.split(",") if b.strip()]

SESSIONS = [s.strip() for s in SESSIONS_RAW.split(",") if s.strip()]

async def run_collector(session_string, account_index):
    client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
    
    async with client:
        print(f"🚀 الحساب #{account_index} متصل وجاهز للعمل بأمان.")
        
        while True:
            # المرور على كل بوت تمويل واحد تلو الآخر
            for target_bot in TARGET_BOTS:
                print(f"🔄 [الحساب #{account_index}] الانتقال إلى البوت: {target_bot}")
                
                # محاولة التجميع من هذا البوت لفترة أو حتى تنتهي قنواته
                empty_rounds = 0
                for _ in range(5):  .
                    try:
                        await client.send_message(target_bot, '/start')
                        await asyncio.sleep(6)
                        
                        messages = await client.get_messages(target_bot, limit=1)
                        if not messages:
                            empty_rounds += 1
                            await asyncio.sleep(10)
                            continue
                        
                        last_msg = messages[0]
                        action_taken = False
                        
                        if last_msg.reply_markup:
                            for row in last_msg.reply_markup.rows:
                                for button in row.buttons:
                                    text = button.text.lower()
                                    if any(word in text for word in ["اشتراك", "قناة", "انضمام", "تجميع"]):
                                        print(f"📌 [الحساب #{account_index}] انضمام عبر {target_bot} إلى: {button.text}")
                                        await last_msg.click(data=button.data)
                                        # فاصل زمني أمان لحماية الحساب من الحظر
                                        await asyncio.sleep(8)
                                        action_taken = True
                                        
                                        # محاولة الضغط على زر التحقق
                                        updated = await client.get_messages(target_bot, limit=1)
                                        if updated and updated[0].reply_markup:
                                            for r in updated[0].reply_markup.rows:
                                                for b in r.buttons:
                                                    if any(w in b.text.lower() for w in ["تحقق", "تأكيد", "تم"]):
                                                        print(f"✅ [الحساب #{account_index}] تم التحقق بنجاح.")
                                                        await updated[0].click(data=b.data)
                                                        await asyncio.sleep(4)
                        
                        if not action_taken:
                            print(f"⚠️ [الحساب #{account_index}] لا توجد قنوات جديدة في {target_bot}، الانتقال للبوت التالي...")
                            empty_rounds += 1
                            break
                        
                        # استراحة قصيرة بين كل عملية تجميع وأخرى لحماية الحساب
                        await asyncio.sleep(15)
                        
                    except Exception as e:
                        print(f"❌ خطأ في الحساب #{account_index} مع {target_bot}: {e}")
                        await asyncio.sleep(20)
                        break
                
                # استراحة بين الانتقال من بوت لآخر
                await asyncio.sleep(10)
            
            print(f"⏳ [الحساب #{account_index}] انتهت جولة كل البوتات، استراحة أمان طويلة قبل إعادة الكرّة...")
            await asyncio.sleep(300) # استراحة 5 دقائق لتجنب أي حظر مزعج

async def main():
    if not API_ID or not API_HASH or not SESSIONS or not TARGET_BOTS:
        print("⚠️ خطأ: يرجى التأكد من إدخال كافة المتغيرات بشكل صحيح.")
        return

    print(f"✅ بدء التشغيل بـ {len(SESSIONS)} حساب و {len(TARGET_BOTS)} بوتات تمويل بالتناوب.")
    tasks = [run_collector(session, i + 1) for i, session in enumerate(SESSIONS)]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
