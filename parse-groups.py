import json
import re

# Open the JSON file
with open('1.zdroj-dat.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    print("loaded file", file)

groups = data["types"]

rows =  []

for group in groups:
    result = {}
    if group["groupsIds"]: result["id"] = group["groupsIds"] 
    else: result["id"] = None

    if group["groupsNames"]: result["name"] = group["groupsNames"] 
    else: result["name"] = None

    if result["id"] or result["name"]: rows.append(result)
    # Todo: filter lists to be single pairs

#TODO
##DELETE THE SAME ids

print(rows[:10])

print(rows)
    