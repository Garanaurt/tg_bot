import asyncio
from userbot import userbot_main

async def main():
    await userbot_main(2)

#if __name__ == "__main__":
#    asyncio.run(main())



import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Выполнение SQL-запроса
cursor.execute("UPDATE accounts SET proxy = ? WHERE id = ?", ('45.38.207.214:FfUef6Aa:y3LP7dFy', 1))
conn.commit()

# Закрытие соединения
conn.close()
