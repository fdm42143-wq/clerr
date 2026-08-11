import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSIONS_RAW = os.getenv("SESSIONS_STRING", "")

TARGET_BOTS_RAW = os.getenv("TARGET_BOTS", "@EEObot,@hhkra074bot")
TARGET_BOTS = [b.strip() for b in TARGET_BOTS_RAW.split(",") if b.strip()]
SESSIONS = [s.strip() for s in SESSIONS_RAW.split(",") if s.strip()]

async def run_collector(session_string, account_index):
    client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
    
    async with client:
        print(f"🚀 الحساب #{account_index} متصل وجاهز للعمل.")
        
        while True:
            for target_bot in TARGET_BOTS:
                print(f"🔄 [الحساب #{account_index}] الانتقال إلى البوت: {target_bot}")
                
                for _ in range(5):
                    try:
                        # 1. إرسال أمر البدء
                        await client.send_message(target_bot, '/start')
                        await asyncio.sleep(4)
                        
                        messages = await client.get_messages(target_bot, limit=1)
                        if not messages or not messages[0].reply_markup:
                            await asyncio.sleep(6)
                            continue
                        
                        last_msg = messages[0]
                        
                        # 2. البحث والضغط على زر فتح قسم التجميع (قنوات / تيربو)
                        section_clicked = False
                        for row in last_msg.reply_markup.rows:
                            for button in row.buttons:
                                btn_text = button.text.lower()
                                if any(w in btn_text for w in ["قنوات", "تيربو", "تجميع", "نقاط"]):
                                    print(f"📌 [الحساب #{account_index}] الدخول إلى قسم: {button.text}")
                                    await last_msg.click(data=button.data)
                                    await asyncio.sleep(4)
                                    section_clicked = True
                                    break
                            if section_clicked:
                                break
                        
                        # إذا لم يجد زر قسم محدد، نفترض أن الرسالة تعرض القنوات مباشرة
                        target_message = last_msg
                        if section_clicked:
                            new_msg = await client.get_messages(target_bot, limit=1)
                            if new_msg:
                                target_message = new_msg[0]
                        
                        # 3. البحث عن زر الاشتراك/الانضمام للقناة المطلوبة
                        joined = False
                        if target_message.reply_markup:
                            for row in target_message.reply_markup.rows:
                                for button in row.buttons:
                                    text = button.text.lower()
                                    # التحقق مما إذا كان الزر يوجه لقناة أو اشتراك
                                    if any(word in text for word in ["اشتراك", "قناة", "انضمام", "رابط", "http", "t.me"]):
                                        print(f"📌 [الحساب #{account_index}] محاولة الانضمام عبر الزر: {button.text}")
                                        try:
                                            await target_message.click(data=button.data)
                                        except Exception:
                                            pass # تجاهل الخطأ إذا كان الرابط خارجي ومتابعة العملية
                                        
                                        await asyncio.sleep(6)
                                        joined = True
                        
                        if not joined:
                            print(f"⚠️ [الحساب #{account_index}}} لا توجد قنوات حالياً في {target_bot}")
                            await asyncio.sleep(8)
                            break
                        
                        # 4. البحث التلقائي عن زر (تحقق / تأكيد / تم) وضغطه مهما كانت صياغته
                        await asyncio.sleep(4)
                        updated_messages = await client.get_messages(target_bot, limit=1)
                        if updated_messages and updated_messages[0].reply_markup:
                            verified = False
                            up_msg = updated_messages[0]
                            for r in up_msg.reply_markup.rows:
                                for b in r.buttons:
                                    b_text = b.text.lower()
                                    # قائمة شاملة لكل أزرار التأكيد والتحقق الممكنة بمختلف البوتات
                                    if any(kw in b_text for kw in ["تحقق", "تاكيد", "تأكيد", "تم", "التالي", "التأكيد", "✓", "✅"]):
                                        print(f"✅ [الحساب #{account_index}] الضغط على زر التأكيد/التحقق: {b.text}")
                                        await up_msg.click(data=b.data)
                                        await asyncio.sleep(4)
                                        verified = True
                                        break
                                if verified:
                                    break
                        
                        await asyncio.sleep(10)
                        
                    except Exception as e:
                        print(f"❌ خطأ في الحساب #{account_index} مع {target_bot}: {e}")
                        await asyncio.sleep(10)
                        break
                
                await asyncio.sleep(5)
            
            print(f"⏳ [الحساب #{account_index}] استراحة قصيرة بين الجولات لتجنب الحظر...")
            await asyncio.sleep(120)

async def main():
    if not API_ID or not API_HASH or not SESSIONS or not TARGET_BOTS:
        print("⚠️ خطأ: يرجى التأكد من إدخال كافة المتغيرات في Railway.")
        return

    tasks = [run_collector(session, i + 1) for i, session in enumerate(SESSIONS)]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
