import web3
import sqlite3
from ens import ENS


class DataCollect:
    def __init__(self):
        self.w3 = self.init_connection()
        self.tx_dictionary = {}
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

    def blocks_to_database(self, depth):
        (start_block, end_block) = self.block_selector(depth)
        for x in range(start_block, end_block):
            block = self.w3.eth.getBlock(x, True)
            for transaction in block.transactions:
                tx_hash_hex = transaction["hash"].hex()
                tx_receipt = self.w3.eth.get_transaction_receipt(transaction["hash"])
                for log in tx_receipt["logs"]:
                    for value in self.value_corrector(log["data"]):
                        if len(value) > 1:
                            print(
                                f"erc-20 value transferred (dec): ",
                                (int(value, 16)),  # * (10 ** (-18)),
                            )
                            print(f"erc-20 value transferred (hex): ", value)

    def init_connection(self):
        avado_url = "http://ethchain-geth.my.ava.do:8545"
        w3 = web3.Web3(web3.Web3.HTTPProvider(avado_url))
        print(f"connection active? ", w3.isConnected())
        return w3


def main():
    dc = DataCollect()
    dc.blocks_to_database(1)


if __name__ == "__main__":
    main()
