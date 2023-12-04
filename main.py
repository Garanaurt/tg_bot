import asyncio
from aiogram import Bot, Dispatcher
from handlers import hd_admin, add_del_group, add_del_user, change_group_settings, user_settings
from userbot import run_bots
from sqlite3 import OperationalError


TOKEN = "697934mzE"


#start bot
async def main():
    try:
        #part of admin
        bot = Bot(token=TOKEN)
        dp = Dispatcher()
        dp.include_routers(hd_admin.router)
        dp.include_routers(add_del_user.router)
        dp.include_routers(add_del_group.router)
        dp.include_routers(change_group_settings.router)
        dp.include_routers(user_settings.router)
        await bot.delete_webhook(drop_pending_updates=True)

        tasks = [
            asyncio.create_task(dp.start_polling(bot)),
            asyncio.create_task(run_bots()),
        ]


        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        print("Таск был отменен.")
        pass
    except OperationalError:
        print("sqlite.")
        pass


if __name__ == "__main__":
    asyncio.run(main())
