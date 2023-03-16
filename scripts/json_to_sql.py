import json
import sqlite3
from os import listdir
import os


def init_connection():
    """create connection to sql db"""
    con = sqlite3.connect("./token_lists/tokens.db")
    # create cursor to execute database commands
    cur = con.cursor()
    return cur


def load_json(filename):
    f = open("./token_lists/%s.json" % filename)
    return json.load(f)


def write(json):
    """create connection to sql db"""
    con = sqlite3.connect("./token_lists/tokens.db")
    # create cursor to execute database commands
    cur = con.cursor()
    count = 0
    print("json[tokens] type: ", type(json["tokens"]))
    for token in json["tokens"]:
        print(token)
        print("trying to write: ")
        print((token["address"]))
        print((token["name"]))
        print((token["symbol"]))
        print((token["decimals"]))
        print((token["chainId"]))
        print("<<<<<<<<<<>>>>>>>>>>>")

        #  db.execute("INSERT INTO registrants (name, sport) VALUES(?, ?)", name, sport)
        cur.execute(
            "INSERT OR IGNORE INTO token(address, name, symbol, decimals, chain_id) VALUES (?, ?, ?, ?, ?);",
            (
                token["address"],
                token["name"],
                token["symbol"],
                token["decimals"],
                token["chainId"],
            ),
        )
    # COMMIT DATA TO TABLE OTHERWISE WON'T BE WRITTEN
    con.commit()
    con.close()
    return


def get_json_filenames(path):
    filenames = []
    for file in listdir(path):
        # print(file)
        (filename, file_extension) = os.path.splitext(file)
        # print(filename, file_extension)
        if file_extension == ".json":
            filenames.append(filename)
    return filenames


def main():
    ADDRESS_LIST = []
    # cur = init_connection()
    for filename in get_json_filenames("./token_lists"):
        loaded = load_json(filename)
        write(loaded)


# cur.execute("CREATE TABLE transactions(tx_id INTEGER PRIMARY KEY, address TEXT)")

if __name__ == "__main__":
    main()
