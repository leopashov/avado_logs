import json

f = open("./token_lists/zapper.json")
tokens = json.load(f)

for token in tokens["tokens"]:
    print(token)
