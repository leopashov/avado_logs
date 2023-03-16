import requests


def main():
    URL = "https://tokens.coingecko.com/uniswap/all.json"
    response = requests.get(URL)

    path = "./token_lists/cgecko.json"
    open(path, "wb").write(response.content)
    print("done - coingecko tokens written to ./token_lists/cgecko.json")


if __name__ == "__main__":
    main()
