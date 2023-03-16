from brownie import network, config
import web3
import sqlite3
from ens import ENS


def init_connection():
    avado_url = "http://ethchain-geth.my.ava.do:8545"
    w3 = web3.Web3(web3.Web3.HTTPProvider(avado_url))
    print(f"connection active? ", w3.isConnected())
    return w3


def block_selector(scan_depth, w3):
    # request the latest block number
    ending_blocknumber = w3.eth.blockNumber

    # latest block number minus 100 blocks
    starting_blocknumber = ending_blocknumber - scan_depth
    return (starting_blocknumber, ending_blocknumber)


# create an empty dictionary we will add transaction data to
tx_dictionary = {}


def getTransactions(start, end, address, w3):
    """This function takes three inputs, a starting block number, ending block number
    and an Ethereum address. Put "" for address to access all block data. The function loops over the transactions in each block and
    checks if the address in the to field matches the one we set in the blockchain_address.
    Additionally, it will write the found transactions to a pickle file for quickly serializing and de-serializing
    a Python object."""
    print(
        f"Started filtering through block number {start} to {end} for transactions involving the address - {address}..."
    )
    for x in range(start, end):
        block = w3.eth.getBlock(x, True)
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
        f"Finished searching blocks {start} through {end} and found {len(tx_dictionary)} transactions"
    )


def value_corrector(value):
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


def account_to_ENS(address, ns):
    ## ENS info:
    ens_name = ns.name(address)
    # print("ENS NAME: ", ens_name)
    return ens_name

    # https://web3py.readthedocs.io/en/stable/ens_overview.html
    # ns = ENS.fromWeb3(w3)
    # domain = ns.name('address')


def address_to_token(address, cur):
    search = list(
        cur.execute("SELECT symbol FROM token WHERE address = (?)", (address,))
    )
    try:
        search = search[0][0]
        # print("search = ", search)
        return (search, True)
    except:
        # print("address not in db")
        return (0, False)


def main():
    # Create web3 connection
    w3 = init_connection()
    # connect to sql database
    con = sqlite3.connect("./token_lists/tokens.db")
    # create cursor to execute database commands
    cur = con.cursor()
    # cur.execute("CREATE TABLE transactions(tx_id INTEGER PRIMARY KEY, address TEXT)")
    # create ens object using web3 connection
    ns = ENS.fromWeb3(w3)
    for x in range(block_selector(1, w3)[0], block_selector(1, w3)[1]):
        block = w3.eth.getBlock(x, True)
        # print all transactions from last block. prints a list of dictionaries
        # print(block.transactions[0])  # [0]["blockHash"].hex())
        for transaction in block.transactions:
            eth_value = web3.Web3.fromWei(transaction["value"], "ether")
            print(f"eth value: ", eth_value)
            tx_hash = transaction["hash"]
            tx_hash_hex = transaction["hash"].hex()
            # print(f"tx hash: ", tx_hash_hex)
            tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
            print(f"transaction hash: ", tx_hash_hex)
            count = 0
            for log in tx_receipt["logs"]:
                # print(f"log number: ", count)

                for value in value_corrector(log["data"]):
                    if len(value) > 1:
                        print(
                            f"erc-20 value transferred (dec): ",
                            (int(value, 16)),  # * (10 ** (-18)),
                        )
                        print(f"erc-20 value transferred (hex): ", value)
                        pass
                    else:
                        pass
                print(
                    f"address that emitted log (ie. token contract): ",
                    log["address"],
                )
                print(address_to_token(log["address"], cur))
                print(
                    f"from address: ",
                    tx_receipt["from"],
                    "ENS: ",
                    account_to_ENS(tx_receipt["from"], ns),
                )
                print(
                    f"to address: ",
                    tx_receipt["to"],
                    "ENS: ",
                    account_to_ENS(tx_receipt["from"], ns),
                )

                count += 1
        # tx receipt ["logs"]["data"] gives value of erc20

        # check get transaction reciept

    # print(dir(w3.eth))
    # print(w3.geth.admin.node_info())
    # Close sql connection
    # con.close()


if __name__ == "__main__":
    main()
