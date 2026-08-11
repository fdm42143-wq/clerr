import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
SESSIONS_RAW = os.getenv("SESSIONS_STRING", "")

TARGET_BOTS_RAW = os.getenv("TARGET_BOTS", "@EEObot,@hhkra074bot")
TARGET_BOTS = [b.strip() for b in TARGET_BOTS_RAW.split(",") if b.strip()]
SESSIONS = [s.strip() for s in SESSIONS_RAW.split(",") if s.strip()]

async def run_collector(session_string, account_index):
    client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
    
    async with client:
        print(f"Account #{account_index} is connected and ready.")
        
        # 1. التفعيل الأولي (أول مرة فقط لكل بوت)
        for target_bot in TARGET_BOTS:
            try:
                print(f"Initial activation (Star) for {target_bot}")
                await client.send_message(target_bot, '/start')
                await asyncio.sleep(4)
                await client.send_message(target_bot, 'ستار')
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Initial activation notice for {target_bot}: {e}")

        # 2. حلقة التجميع المستمرة
        while True:
            for target_bot in TARGET_BOTS:
                print(f"Starting collection loop in: {target_bot}")
                
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
                                    print(f"Clicking points button: {button.text}")
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
                                    print(f"Entering channels section: {button.text}")
                                    await menu_msg.click(data=button.data)
                                    await asyncio.sleep(4)
                                    channels_clicked = True
                                    break
                            if channels_clicked:
                                break
                        
                        if not channels_clicked:
                            print("Channels button not found currently.")
                            await asyncio.sleep(6)
                            break
                        
                        # د) استخراج رابط القناة والانضمام إليها فعلياً
                        chan_msg_list = await client.get_messages(target_bot, limit=1)
                        if not chan_msg_list or not chan_msg_list[0].reply_markup:
                            print("No channels available for collection right now.")
                            await asyncio.sleep(8)
                            break
                        
                        chan_msg = chan_msg_list[0]
                        channel_entity = None
                        
                        for row in chan_msg.reply_markup.rows:
                            for button in row.buttons:
                                if any(w in button.text for w in ["فتح", "القناة", "اشتراك"]):
                                    # محاولة استخراج يوزر أو رابط القناة من الأزرار
                                    if hasattr(button, 'url') and button.url:
                                        channel_entity = button.url
                                    break
                            if channel_entity:
                                break
                        
                        # إذا لم يوجد رابط مباشر في الزر، نستخرج الرابط من نص الرسالة
                        if not channel_entity and chan_msg.text:
                            import re
                            urls = re.findall(r'(https://t\.me/\+[\w-]+|https://t\.me/[\w_]+|@[\w_]+)', chan_msg.text)
                            if urls:
                                channel_entity = urls[0]

                        # النقر على زر فتح القناة افتراضياً
                        try:
                            await chan_msg.click(0)
                        except Exception:
                            pass
                        await asyncio.sleep(4)

                        # الانضمام الفعلي للقناة
                        if channel_entity:
                            try:
                                print(f"Joining channel: {channel_entity}")
                                await client(JoinChannelRequest(channel_entity))
                                await asyncio.sleep(3)
                            except Exception as join_err:
                                print(f"Notice during join: {join_err}")

                        # هـ) العودة للبوت والضغط على "تحقق" (لـ EEObot) أو "تأكيد" (لـ hhkra074bot)
                        await asyncio.sleep(4)
                        verify_msg_list = await client.get_messages(target_bot, limit=1)
                        if verify_msg_list and verify_msg_list[0].reply_markup:
                            v_msg = verify_msg_list[0]
                            verified = False
                            for row in v_msg.reply_markup.rows:
                                for button in row.buttons:
                                    b_text = button.text.lower()
                                    if target_bot == "@EEObot" and any(kw in b_text for kw in ["تحقق", "✓", "✅"]):
                                        print(f"Verified via: {button.text}")
                                        await v_msg.click(data=button.data)
                                        verified = True
                                        break
                                    elif target_bot == "@hhkra074bot" and any(kw in b_text for kw in ["تاكيد", "تأكيد"]):
                                        print(f"Confirmed via: {button.text}")
                                        await v_msg.click(data=button.data)
                                        verified = True
                                        break
                                if verified:
                                    break
                        
                        # و) الانتقال للمهمة التالية عبر زر "التالي ▶️" إن وجد
                        await asyncio.sleep(4)
                        next_msg_list = await client.get_messages(target_bot, limit=1)
                        if next_msg_list and next_msg_list[0].reply_markup:
                            n_msg = next_msg_list[0]
                            for row in n_msg.reply_markup.rows:
                                for button in n_msg.reply_markup.rows: # للتأكد من تفحص الأزرار
                                    pass
                                for button in row.buttons:
                                    if "التالي" in button.text or "▶️" in button.text:
                                        print(f"Moving to next task: {button.text}")
                                        await n_msg.click(data=button.data)
                                        break
                        
                        await asyncio.sleep(8)
                        
                    except Exception as e:
                        print(f"Error occurred: {e}")
                        await asyncio.sleep(10)
                        break
                
                await asyncio.sleep(5)
            
            print("Taking a security rest between rounds...")
            await asyncio.sleep(120)

async def main():
    if not API_ID or not API_HASH or not SESSIONS or not TARGET_BOTS:
        print("Error: Check environment variables in Railway.")
        return

    tasks = [run_collector(session, i + 1) for i, session in enumerate(SESSIONS)]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
