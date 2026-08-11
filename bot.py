import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSIONS_RAW = os.getenv("SESSIONS_STRING", "")

# البوتان اللذان حددتهما للعمل بالتناوب
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
                
                for _ in range(6):
                    try:
                        # 1. إرسال أمر البدء للبوت الحالي
                        await client.send_message(target_bot, '/start')
                        await asyncio.sleep(4)
                        
                        messages = await client.get_messages(target_bot, limit=1)
                        if not messages or not messages[0].reply_markup:
                            await asyncio.sleep(5)
                            continue
                        
                        last_msg = messages[0]
                        
                        # 2. الضغط على زر "تجميع النقاط" أو "القنوات" من القائمة الرئيسية
                        menu_clicked = False
                        for row in last_msg.reply_markup.rows:
                            for button in row.buttons:
                                btn_text = button.text.lower()
                                if any(w in btn_text for w in ["تجميع النقاط", "القنوات", "قنوات", "تيربو"]):
                                    print(f"📌 [الحساب #{account_index}] الدخول عبر: {button.text}")
                                    await last_msg.click(data=button.data)
                                    await asyncio.sleep(4)
                                    menu_clicked = True
                                    break
                            if menu_clicked:
                                break
                        
                        current_msg = last_msg
                        if menu_clicked:
                            new_msg = await client.get_messages(target_bot, limit=1)
                            if new_msg:
                                current_msg = new_msg[0]
                        
                        # 3. الضغط على زر فتح القناة أو الاشتراك
                        channel_opened = False
                        if current_msg.reply_markup:
                            for row in current_msg.reply_markup.rows:
                                for button in row.buttons:
                                    text = button.text.lower()
                                    if any(word in text for word in ["افتح", "اشتراك", "انضمام", "قناة", "رابط"]):
                                        print(f"📌 [الحساب #{account_index}] فتح القناة عبر: {button.text}")
                                        try:
                                            await current_msg.click(data=button.data)
                                        except Exception:
                                            pass
                                        await asyncio.sleep(6)
                                        channel_opened = True
                                        break
                                if channel_opened:
                                    break
                        
                        if not channel_opened:
                            print(f"⚠️ [الحساب #{account_index}] لا توجد قنوات متاحة حالياً في {target_bot}")
                            await asyncio.sleep(8)
                            break
                        
                        # 4. الضغط التلقائي على زر التحقق أو التأكيد
                        await asyncio.sleep(4)
                        verify_msg_list = await client.get_messages(target_bot, limit=1)
                        if verify_msg_list and verify_msg_list[0].reply_markup:
                            v_msg = verify_msg_list[0]
                            verified = False
                            for row in v_msg.reply_markup.rows:
                                for button in row.buttons:
                                    b_text = button.text.lower()
                                    if any(kw in b_text for kw in ["تحقق", "تاكيد", "تأكيد", "تم", "✓", "✅"]):
                                        print(f"✅ [الحساب #{account_index}] تم التحقق بنجاح عبر زر: {button.text}")
                                        await v_msg.click(data=button.data)
                                        await asyncio.sleep(4)
                                        verified = True
                                        break
                                if verified:
                                    break
                        
                        await asyncio.sleep(8)
                        
                    except Exception as e:
                        print(f"❌ خطأ في الحساب #{account_index} مع {target_bot}: {e}")
                        await asyncio.sleep(10)
                        break
                
                await asyncio.sleep(5)
            
            print(f"⏳ [الحساب #{account_index}] استراحة أمان بين الجولات...")
            await asyncio.sleep(120)

async def main():
    if not API_ID or not API_HASH or not SESSIONS or not TARGET_BOTS:
        print("⚠️ خطأ: يرجى التحقق من متغيرات Railway.")
        return

    tasks = [run_collector(session, i + 1) for i, session in enumerate(SESSIONS)]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
