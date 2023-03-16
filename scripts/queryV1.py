import web3
import sqlite3
from ens import ENS
import pandas as pd
import time


class DataCollect:
    def __init__(self):
        self.w3 = self.init_connection()
        self.txs = {
            "tx hash": [],
            "block number": [],
            "token contract address": [],
            "token symbol": [],
            "from address": [],
            "from address ENS": [],
            "to address": [],
            "to address ENS": [],
            "erc-20 value transferred": [],
        }
        self.df = pd.DataFrame(
            columns=[
                "tx hash",
                "block number",
                "token contract address",
                "token symbol",
                "from address",
                "from address ENS",
                "to address",
                "to address ENS",
                "erc-20 value transferred",
            ]
        )
        self.con = sqlite3.connect("./token_lists/tokens.db")
        self.cur = self.con.cursor()
        # cur.execute("CREATE TABLE transactions(tx_id INTEGER PRIMARY KEY, address TEXT)")
        self.ns = ENS.fromWeb3(self.w3)

    def block_selector(self, scan_depth):
        # request the latest block number
        ending_blocknumber = self.w3.eth.blockNumber

        # latest block number minus 100 blocks
        starting_blocknumber = ending_blocknumber - scan_depth
        return (starting_blocknumber, ending_blocknumber)

    def getTransactions(self, start, end, address):
        """This function takes three inputs, a starting block number, ending block number
        and an Ethereum address. Put "" for address to access all block data. The function loops over the transactions in each block and
        checks if the address in the to field matches the one we set in the blockchain_address.
        Additionally, it will write the found transactions to a pickle file for quickly serializing and de-serializing
        a Python object."""
        if end == 0:
            end = self.w3.eth.block_number
        print(
            f"Started filtering through block number {start} to {end} for transactions involving the address - {address}..."
        )
        for x in range(start, end):
            block = self.w3.eth.getBlock(x, True)
            for transaction in block.transactions:
                print(transaction)
                # if len(address) > 2:
                #     if transaction["to"] == address or transaction["from"] == address:
                #         with open("transactions.pkl", "wb") as f:
                #             hashStr = transaction["hash"].hex()
                #             tx_dictionary[hashStr] = transaction
                #             pickle.dump(tx_dictionary, f)
                #         f.close()
        print(
            f"Finished searching blocks {start} through {end} and found {len(self.tx_dictionary)} transactions"
        )

    def block_selector(self, scan_depth):
        # request the latest block number
        ending_blocknumber = self.w3.eth.blockNumber

        # latest block number minus 'scan depth' blocks
        starting_blocknumber = ending_blocknumber - scan_depth
        return (starting_blocknumber, ending_blocknumber)

    def value_corrector(self, value):
        """Some contract calls do a number of operations, and are not simple swaps
        e.g sync or swap. These come with large data fields (e.g 258 characters representing
        4 numbers. This function splits those characters into batches of 64 chars
        (with a '0x' at the start)"""
        output = []
        # remove '0x' from front
        value = value[2::]
        # if data field larger than simple transfer

        while len(value) > 64:

            output.append(value[0:64])
            value = value[64::]

        output.append(value)
        # print(f"value corrector output: ", output)
        return output

    def address_to_token(self, address):
        self.con = sqlite3.connect("./token_lists/tokens.db")
        self.cur = self.con.cursor()
        search = list(
            self.cur.execute("SELECT symbol FROM token WHERE address = (?)", (address,))
        )
        self.con.close()
        try:
            search = search[0][0]
            # print("search = ", search)
            return (search, True)
        except:
            # print("address not in db")
            return (0, False)

    def account_to_ENS(self, address):
        ## ENS info:
        ens_name = self.ns.name(address)
        # print("ENS NAME: ", ens_name)
        return ens_name

        # https://web3py.readthedocs.io/en/stable/ens_overview.html
        # ns = ENS.fromWeb3(w3)
        # domain = ns.name('address')

    def blocks_to_database(self, depth):
        (start_block, end_block) = self.block_selector(depth)
        number = 0
        for x in range(start_block, end_block):
            block = self.w3.eth.getBlock(x, True)
            print(f"getting txs from block: ", x, "of: ", end_block)
            for transaction in block.transactions:
                tx_hash_hex = transaction["hash"].hex()
                tx_receipt = self.w3.eth.get_transaction_receipt(transaction["hash"])
                for log in tx_receipt["logs"]:
                    number += 1
                    values = self.value_corrector(log["data"])
                    if len(values) == 1:
                        try:
                            value_transferred = int(values[0], 16)
                        except:
                            continue
                        token = self.address_to_token(log["address"])
                        if token[1]:
                            # print(f"tx hash: ", tx_hash_hex)
                            # print(f"")
                            # print(
                            #     f"erc-20 value transferred (dec): ",
                            #     (value_transferred),  # * (10 ** (-18)),
                            # )
                            # print(f"erc-20 value transferred (hex): ", values)
                            # print(
                            #     f"address that emitted log (ie. token contract): ",
                            #     log["address"],
                            # )
                            # print(token[0])
                            # print(
                            #     f"from address: ",
                            #     tx_receipt["from"],
                            #     "ENS: ",
                            #     self.account_to_ENS(tx_receipt["from"]),
                            # )
                            # print(
                            #     f"to address: ",
                            #     tx_receipt["to"],
                            #     "ENS: ",
                            #     self.account_to_ENS(tx_receipt["from"]),
                            # )

                            # self.txs["tx hash"].append(tx_hash_hex)
                            # self.txs["block number"].append(x)
                            # self.txs["token contract address"].append(log["address"])
                            # self.txs["token symbol"].append(token[0])
                            # self.txs["from address"].append(tx_receipt["from"])
                            # self.txs["from address ENS"].append(
                            #     self.account_to_ENS(tx_receipt["from"])
                            # )
                            # self.txs["to address"].append(tx_receipt["to"])
                            # self.txs["to address ENS"].append(
                            #     self.account_to_ENS(tx_receipt["to"])
                            # )
                            # self.txs["erc-20 value transferred"].append(
                            #     value_transferred
                            # )

                            # CREATE TABLE txs (number INT PRIMARY KEY, tx_hash TEXT, block_number INT, token_contract_address TEXT, token_symbol TEXT, from_address TEXT, from_address_ENS TEXT, to_address TEXT, to_address_ENS TEXT);
                            # self.con = sqlite3.connect(
                            #     "/home/leo/Eth_Dev/avado_queries_no_flask/scripts/transactions.db"
                            # )
                            # self.cur = self.con.cursor()
                            # self.cur.execute(
                            #     "INSERT INTO txs(number, tx_hash, block_number, token_contract_address, token_symbol, from_address, from_address_ENS, to_address, to_address_ENS, value_transferred) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                            #     (
                            #         number,
                            #         str(tx_hash_hex),
                            #         x,
                            #         str(log["address"]),
                            #         str(token[0]),
                            #         str(tx_receipt["from"]),
                            #         str(self.account_to_ENS(tx_receipt["from"])),
                            #         str(tx_receipt["to"]),
                            #         str(self.account_to_ENS(tx_receipt["to"])),
                            #         str(value_transferred),
                            #     ),
                            # ),
                            # self.con.commit()
                            # self.con.close()

                            entry = pd.DataFrame.from_dict(
                                {
                                    "tx hash": [tx_hash_hex],
                                    "block number": [x],
                                    "token contract address": [log["address"]],
                                    "token symbol": [token[0]],
                                    "from address": [tx_receipt["from"]],
                                    "from address ENS": [
                                        self.account_to_ENS(tx_receipt["from"])
                                    ],
                                    "to address": [tx_receipt["to"]],
                                    "to address ENS": [
                                        self.account_to_ENS(tx_receipt["to"])
                                    ],
                                    "erc-20 value transferred": [
                                        str(value_transferred)
                                    ],
                                }
                            )

                            self.df = pd.concat([self.df, entry], ignore_index=True)
        self.con = sqlite3.connect("./scripts/transactions.db")
        self.df.to_sql("txsDF", self.con, if_exists="replace")
        # self.df = pd.DataFrame(data=self.txs)

    def init_connection(self):
        avado_url = "http://ethchain-geth.my.ava.do:8545"
        w3 = web3.Web3(web3.Web3.HTTPProvider(avado_url))
        print(f"connection active? ", w3.isConnected())
        return w3


def main():
    dc = DataCollect()
    dc.blocks_to_database(130)
    # print(dc.df)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
