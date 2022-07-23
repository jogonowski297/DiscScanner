import sqlite3
from time import localtime, strftime
from datetime import *
from Scanner import Scanner

con = sqlite3.connect('dane.db')
cur = con.cursor()

if __name__ == "__main__":
    S = Scanner(con, cur)

    config = open('config.txt', 'r', encoding="utf-8")
    main = [s.replace("\n", "").split(",,,") for s in config.readlines()]
    super_folder = main[2]
    super_file = main[4]
    skip_dirs = main[6]
    days = main[8][0]
    disk = main[10][0]


    start = datetime.now().time()
    print('>>> Start:' + str(start))

    named_tuple = localtime()  # get struct_time
    timeDelete = strftime("%d.%m.%y|%H:%M:%S", named_tuple)

    print("Zapisuje do tabeli: ", timeDelete)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS [%s] (
            nr VARCHAR(50) NOT NULL,
            name_ VARCHAR(250) NOT NULL,
            size_ INTEGER NOT NULL,
            extensions VARCHAR(15) NOT NULL,
            file_or_direct VARCHAR(1) NOT NULL,
            too_long VARCHAR(8) ,
            removed VARCHAR(15),
            path_ VARCHAR(1000) NOT NULL
            )""" % timeDelete)

    S.save_to_db(timeDelete, disk, skip_dirs, super_folder, super_file, days)

    con.close()

    koniec = datetime.now().time()
    print('>>> END:' + str(koniec))
    print("Czas: ", datetime.combine(date.today(), koniec) - datetime.combine(date.today(), start))

    print("-----------------------------")

    if (S.error_counter > 0):
        S.show_errors()


