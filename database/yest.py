from db import DbSpamer


with DbSpamer() as db:

    users = db.db_get_all_users()
    print(users)