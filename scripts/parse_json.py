import json


def main():
    f = open("./token_lists/zapper.json")
    tokens = json.load(f)

    for token in tokens["tokens"]:
        print(token)


if __name__ == "__main__":
    main()
