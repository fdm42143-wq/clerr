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
        
        # 1. التفعيل الأولي (أول مرة فقط عند تشغيل البوت لكل بوت)
        for target_bot in TARGET_BOTS:
            try:
                print(f"⭐ [الحساب #{account_index}] إرسال التفعيل الأولي (ستار) لـ {target_bot}")
                await client.send_message(target_bot, '/start')
                await asyncio.sleep(4)
                await client.send_message(target_bot, 'ستار')
                await asyncio.sleep(5)
            except Exception as e:
                print(f"⚠️ تنبيه في التفعيل الأولي لـ {target_bot}: {e}")

        # 2. حلقة التجميع المستمرة بالخطوات الصحيحة
        while True:
            for target_bot in TARGET_BOTS:
                print(f"🔄 [الحساب #{account_index}] بدء التجميع في البوت: {target_bot}")
                
                for _ in range(5):
                    try:
                        # أ) إرسال /start
                        await client.send_message(target_bot, '/start')
                        await asyncio.sleep(4)
                        
                        messages = await client.get_messages(target_bot, limit=1)
                        if not messages or not messages[0].reply_markup:
                            await asyncio.sleep(5)
                            continue
                        
                        last_msg = messages[0]
                        
                        # ب) الضغط على زر "تجميع النقاط"
                        points_clicked = False
                        for row in last_msg.reply_markup.rows:
                            for button in row.buttons:
                                if "تجميع النقاط" in button.text:
                                    print(f"📌 [الحساب #{account_index}] الضغط على: {button.text}")
                                    await last_msg.click(data=button.data)
                                    await asyncio.sleep(4)
                                    points_clicked = True
                                    break
                            if points_clicked:
                                break
                        
                        if not points_clicked:
                            await asyncio.sleep(5)
                            continue
                        
                        # ج) الدخول إلى قسم "قنوات"
                        menu_msg_list = await client.get_messages(target_bot, limit=1)
                        if not menu_msg_list or not menu_msg_list[0].reply_markup:
                            await asyncio.sleep(5)
                            continue
                        
                        menu_msg = menu_msg_list[0]
                        channels_clicked = False
                        for row in menu_msg.reply_markup.rows:
                            for button in row.buttons:
                                if "قنوات" in button.text:
                                    print(f"📌 [الحساب #{account_index}] الدخول إلى قسم: {button.text}")
                                    await menu_msg.click(data=button.data)
                                    await asyncio.sleep(4)
                                    channels_clicked = True
                                    break
                            if channels_clicked:
                                break
                        
                        if not channels_clicked:
                            print(f⚠️ [الحساب #{account_index}] زر القنوات غير موجود حالياً.")
                            await asyncio.sleep(6)
                            break
                        
                        # د) فتح القناة والاشتراك فيها
                        chan_msg_list = await client.get_messages(target_bot, limit=1)
                        if not chan_msg_list or not chan_msg_list[0].reply_markup:
                            print(f"⚠️ [الحساب #{account_index}] لا توجد قنوات متاحة للتجميع حالياً.")
                            await asyncio.sleep(8)
                            break
                        
                        chan_msg = chan_msg_list[0]
                        opened = False
                        for row in chan_msg.reply_markup.rows:
                            for button in row.buttons:
                                if any(w in button.text for w in ["فتح", "القناة", "اشتراك"]):
                                    print(f"📌 [الحساب #{account_index}] النقر على: {button.text}")
                                    try:
                                        await chan_msg.click(data=button.data)
                                    except Exception:
                                        pass
                                    await asyncio.sleep(6)
                                    opened = True
                                    break
                            if opened:
                                break
                        
                        if not opened:
                            break
                        
                        # هـ) الضغط على زر "تحقق" أو "تأكيد" لاحتساب النقاط
                        await asyncio.sleep(4)
                        verify_msg_list = await client.get_messages(target_bot, limit=1)
                        if verify_msg_list and verify_msg_list[0].reply_markup:
                            v_msg = verify_msg_list[0]
                            verified = False
                            for row in v_msg.reply_markup.rows:
                                for button in row.buttons:
                                    b_text = button.text.lower()
                                    if any(kw in b_text for kw in ["تحقق", "تاكيد", "تأكيد", "تم", "✓", "✅"]):
                                        print(f"✅ [الحساب #{account_index}] تم الضغط على زر التحقق: {button.text}")
                                        await v_msg.click(data=button.data)
                                        await asyncio.sleep(4)
                                        verified = True
                                        break
                                if verified:
                                    break
                        
                        await asyncio.sleep(8)
                        
                    except Exception as e:
                        print(f"❌ خطأ في الحساب #{account_index}: {e}")
                        await asyncio.sleep(10)
                        break
                
                await asyncio.sleep(5)
            
            print(f"⏳ [الحساب #{account_index}] استراحة أمان مؤقتة...")
            await asyncio.sleep(120)

async def main():
    if not API_ID or not API_HASH or not SESSIONS or not TARGET_BOTS:
        print("⚠️ خطأ: يرجى التأكد من ضبط المتغيرات في Railway.")
        return

    tasks = [run_collector(session, i + 1) for i, session in enumerate(SESSIONS)]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
