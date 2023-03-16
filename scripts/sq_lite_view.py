import sqlite3
import pandas as pd


class Query:
    def __init__(self, path):
        self.con = sqlite3.connect(path)
        self.cur = self.con.cursor()

    def printQueryResult(self, query):
        self.cur.execute(query)
        result = self.cur.fetchall()
        print(result)
        # self.con.close()

    def queryToDataframe(self, query):
        df = pd.read_sql_query(query, self.con)

        # Verify that result of SQL query is stored in the dataframe
        return df

    def closeConnection(self):
        self.con.close


def main():

    q = Query("/home/leo/Eth_Dev/avado_queries_no_flask/token_lists/tokens.db")
    q.printQueryResult("SELECT * FROM token WHERE name LIKE '%bitcoin%'")
    print(q.queryToDataframe("SELECT * FROM token"))
    q.closeConnection()


if __name__ == "__main__":
    main()
