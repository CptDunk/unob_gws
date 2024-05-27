import re
import json
groupDict = {}
groupDict['groups'] = []
# Open the JSON file and read its contents
with open('res/1.zdroj-dat.json', 'r', encoding='utf-8') as file:
    data = file.read()

with open('res/1.zdroj-dat.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)
    print("loaded file")

    tempDict = {}
    for key in json_data["types"]:
        #get difference in length of 'groupsIds' and 'groupsNames'
        difLen = abs(len(key["groupsIds"]) - len(key["groupsNames"]))
        #if the difference is greater that 0, that means there are more IDs than names, meaning
        #that there are false IDs present(in this case "0")
        if difLen > 0:
            # print("ids:", len(key["groupsIds"]), "names:", len(key["groupsNames"]))
            for ind, type in enumerate(key["groupsIds"]):
                # print(ind, type)
                # do nothing until you go over false IDs
                if ind >= difLen:
                    # use dictionary to get rid of duplicate values
                    tempDict[type] = key["groupsNames"][ind - difLen]
                else:
                    pass
    # save the dictionary to the groupDict in proper format
    for key in tempDict:
        appDict = {'id': key, 'name': tempDict[key]}
        groupDict['groups'].append(appDict)

with open('res/GroupTypes.json', 'w', encoding='utf-8') as data:
    print(len(groupDict['groups']))
    json.dump(groupDict, data, indent= 4, ensure_ascii=False)
