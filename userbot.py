from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch, UserStatusRecently, UserStatusOnline
from telethon.errors.rpcerrorlist import FloodWaitError, ForbiddenError, ChatWriteForbiddenError, BadRequestError, SlowModeWaitError
import asyncio
from database.db import db
import time

class UserBot:
    def __init__(self, api_id, api_hash, session_name, user_id, proxy):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client = None
        self.user_id = user_id
        self.proxy = proxy



    async def start_client(self):
        try:
            proxy_items = self.proxy.split(':')
            if len(proxy_items) == 4:
                proxy = ('socks5', proxy_items[0], int(proxy_items[3]), proxy_items[1], proxy_items[2])
                self.client = TelegramClient(self.session_name, self.api_id, self.api_hash, proxy=proxy)
            else:
                self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
            #user_data = db.db_get_user_info(self.user_id)
            try:
                await self.client.connect() #start(user_data[5], code_callback=11,)
            except OSError:
                print(f"Error during client initialization: {e}")
                db.db_set_user_stop(self.user_id)
                return False
            me = await self.client.get_me()
            print(f'Вошли в аккаунт: {me.first_name} {me.last_name} (@{me.username})')
            return True
        except Exception as e:
            print(f"Error during client initialization: {e}")
            db.db_set_user_stop(self.user_id)
            return False

    async def send_sms_to_chats(self, groups, message, sleep_time, online, recently, user_id, count):
        cnt = 0
        messa = message
        spam_count = 0
        for group in groups:
            user_running = db.db_get_user_info(user_id)[10]
            if user_running:
                online_users, recently_users = await self.get_online_and_recent_users(group)
                add_text = ''
                if online:
                    for user in online_users:
                        add_text += f'@{user.username} '
                if recently:
                    for user in recently_users:
                        add_text += f'@{user.username} '
                try:
                    messag = await self.client.send_message(entity=group, message=add_text + messa.text + " .i")
                    try:
                        await self.client.edit_message(entity=group, message=messag, text=messa.text)
                    except Exception:
                        await self.client.edit_message(entity=group, message=messag, text=messa.text)
                    cnt += 1
                except FloodWaitError:
                    await self.send_msg_to_spambot()
                    spam_count += 1
                except Exception as e:
                    print("ошибка", e)
                time.sleep(sleep_time)
            else:
                self.client.disconnect()
            if cnt % 5 == 0:
                user_cnt = db.db_get_user_info(user_id)[11]
                db.db_update_count(user_id, int(user_cnt) + cnt)
                cnt = 0
            


    async def disconnect(self):
        await self.client.disconnect()



    async def get_chat_list(self):
        user_groups_id = []
        dialogs = await self.client.get_dialogs()
        groups = [dialog for dialog in dialogs if dialog.is_group]
        for group in groups:
            print(f'name: {group.title}, ID: {group.id}')
            user_groups_id.append(group.id)
        return user_groups_id
    
    
    async def get_saved_messages(self):
        try:
            saved_messages = await self.client.get_messages('me')
            #for message in saved_messages:
                #print(f'Message ID: {message.id}, Text: {message.message}')
            return saved_messages
        
        except Exception as e:
            print(f"Error: {e}")


    async def send_msg_to_spambot(self):
        print('spambot')
        spam_bot_username = 'SpamBot'
        try:
            await self.client.send_message(spam_bot_username, '/start')
        except FloodWaitError as e:
            print(f'Слишком часто обращаюсь в спамбот, нужно подождать {e.seconds} секунд')
            await asyncio.sleep(e.seconds)



    async def get_online_and_recent_users(self, group_entity):
        online_users = []
        recent_users = []
        offset = 0
        while True:
            recent_participants = await self.client(GetParticipantsRequest(group_entity, ChannelParticipantsSearch(''), offset=offset, limit=200, hash=0))
            if not recent_participants.users:
                break
            for user in recent_participants.users:
                if isinstance(user.status, UserStatusRecently):
                    recent_users.append(user)
                elif isinstance(user.status, UserStatusOnline):
                    online_users.append(user)
            offset += len(recent_participants.users)

        return online_users, recent_users
    

    async def update_statistics_periodically(self, interval_hours=24):
        while True:
            await self.update_statistics()
            await asyncio.sleep(interval_hours * 3600)


    async def update_statistics(self):
        user_groups_id = []
        dialogs = await self.client.get_dialogs()
        for dialog in dialogs:
            print(dialog)
        groups = [dialog for dialog in dialogs if dialog.is_group]
        for group in groups:
            print(f'name: {group.title}, ID: {group.id}')
            user_groups_id.append(group.id)
        groups_string = ':'.join(map(str, user_groups_id))
        user_data = db.db_get_user_info(self.user_id)
        if user_data[6] is None:   
            db.db_set_user_dialogs(groups_string, self.user_id)
        else:
            db.db_set_user_dialogs_old(user_data[6], self.user_id)
            db.db_set_user_dialogs(groups_string, self.user_id)


async def userbot_main(user_id):
    user = db.db_get_user_info(user_id)
    bot = UserBot(user[2], user[3], user[5], user[0], user[4])
    started = await bot.start_client()
    if not started:
        return
    asyncio.create_task(bot.update_statistics_periodically())
    while user[10]:
        user_info = db.db_get_user_info(user_id)
        group_info = db.db_get_group_info(user_info[1])
        sleep_time = group_info[2]
        online = group_info[4]
        recently = group_info[5]
        messages = await bot.get_saved_messages()
        groups = await bot.get_chat_list()
        await bot.send_sms_to_chats(groups, messages[-1], sleep_time, online, recently, user_id, int(user[11]))
        await asyncio.sleep(group_info[3])
    else:
        db.db_update_count(user_id, 0)
        bot.disconnect()



async def run_bots():
    print('oookey leets gooo')
    bots_data = []
    users_data = db.db_get_all_users()
    for user in users_data:
        db.db_set_user_start(user[0])
        bots_data.append({'user_id': user[0]})


    tasks = [userbot_main(bot['user_id']) for bot in bots_data]

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(run_bots())
