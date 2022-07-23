import datetime
import os
import re
from datetime import *
from time import time
from shutil import rmtree

class Scanner:
    def __init__(self, con, cur):
        self.con = con
        self.cur = cur
        self.error_counter = 0
        self.error_tab = []
        self.path_len = 260

    def save_to_db(self, tabela, disk, skip_dirs, katalogi, pliki, days):
        if (os.path.exists(disk)):
            for dirpath, dirnames, filenames in os.walk(disk):
                dirnames[:] = [d for d in dirnames if self.skip_this(d, skip_dirs) == False]
                print("Aktualna ścieżka: " + dirpath)
                sub_date_dir = datetime.now()

                try:
                    date_create = datetime.fromtimestamp(os.path.getctime(dirpath))
                    sub_date_dir = datetime.now() - date_create
                except:
                    self.error_tab.append(["Nie można odczytać daty katalogu: " + dirpath])
                    print("Nie można odczytać daty katalogu.")
                    self.error_counter += 1

                for _dir in dirnames:
                    data = False

                    try:
                        for kat in katalogi:
                            x = re.compile(kat[1:-1])

                            if (x.search(str(_dir)) != None and sub_date_dir.days >= int(days)):
                                data = (str(dirpath[3:15]), str(_dir), int(self.get_folder_size(dirpath + '/' + _dir)),
                                        "NULL", "D", "FALSE", "TRUE", str(dirpath),)
                                self.delete_folder_or_file(dirpath + "/" + _dir)
                                break

                            if (self.check_len_path(dirpath + "/" + _dir) == False):
                                data = (str(dirpath[3:15]), str(_dir), int(self.get_folder_size(dirpath + '/' + _dir)),
                                        "NULL", "D", "TRUE", "FALSE", str(dirpath),)
                                break
                        if (data):
                            self.commit_to_db(tabela, data)

                    except:
                        self.error_tab.append(["Błąd w katalogach: " + _dir])
                        self.error_counter += 1

                for file in filenames:
                    data = False

                    try:
                        sub_date_file = datetime.now()
                        try:
                            date_create = datetime.fromtimestamp(os.path.getctime(dirpath + "/" + file))
                            sub_date_file = datetime.now() - date_create
                        except:
                            self.error_tab.append(["Nie można odczytać daty pliku: " + file])
                            print("Nie można odczytać daty pliku: ", file)
                            self.error_counter += 1

                        for pli in pliki:
                            x = re.compile(pli[1:-1])
                            removed = False

                            if (x.search(str(file)) != None and sub_date_file.days >= int(days)):
                                data = (str(dirpath[3:15]), str(file), int(os.stat(dirpath + "/" + file).st_size),
                                        str(os.path.splitext(file)[1]), "F", "FALSE", "TRUE", str(dirpath),)
                                self.delete_folder_or_file(dirpath + "/" + file)
                                break

                            if (self.check_len_path(dirpath + "/" + file) == False and removed == False):
                                data = (str(dirpath[3:15]), str(file), int(os.stat(dirpath + "/" + file).st_size),
                                        str(os.path.splitext(file)[1]), "F", "TRUE", "FALSE", str(dirpath),)
                                break

                        if(data):
                            self.commit_to_db(tabela, data)

                    except:
                        self.error_tab.append(["Błąd w plikach: " + dirpath + "/" + file])
                        self.error_counter += 1
        else:
            self.error_tab.append(["Niepoprawna ścieżka. Sprawdz config.txt"])
            self.error_counter += 1
            self.drop_table(tabela)

    def skip_this(self, name, skip):
        for s in skip:
            if (re.compile(s[1:-1]).search(str(name)) != None):
                return True
        return False

    def check_len_path(self, path):
        if (len(path) <= self.path_len):
            return True
        else:
            return False

    def edit_in_db(self, tabela, data):
        insert_stmt = (
                "UPDATE [%s] SET too_long=? AND removed=? WHERE path_=? AND name_=?" % tabela
        )
        self.cur.execute(insert_stmt, data)
        self.con.commit()

    def commit_to_db(self, tabela, data):
        insert_stmt = (
                "INSERT INTO [%s] (nr, name_, size_, extensions, file_or_direct, too_long, removed, path_) VALUES (?, ?, ?, ?, ?, ?, ?, ?)" % tabela
        )
        self.cur.execute(insert_stmt, data)
        self.con.commit()

    def delete_folder_or_file(self,something):
        try:
            print("xxx",something)
            os.remove(something)
        except:
            print("yyy")
            rmtree(something)

    def get_folder_size(self, path):
        size = 0
        for file in os.scandir(path):
            size += os.stat(file).st_size
        return size

    def drop_table(self, tabela):
        insert_stmt = (
                "DROP TABLE [%s]" % tabela
        )
        self.cur.execute(insert_stmt)
        self.con.commit()

    def show_errors(self):
        for i in self.error_tab:
            print(i[0])
        print("Łączna ilość błędów: ", self.error_counter)

    def sleep_hours(self, hours):   # 168 to jeden tydzien
        time.sleep(hours * 3600)

