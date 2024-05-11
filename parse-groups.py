import json
import re

# Open the JSON file
with open('6.zdroj-rozvrh.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    print("loaded file", file)

groups = data["groups"]

rows =  []

#### PRO:  6. zdroj dat - groups (nenašlo duplicity)
for group in groups:
    result = {}
    if group["id"]: result["id"] = group["id"] 
    else: result["id"] = None

    if group["name"]: result["name"] = group["name"] 
    else: result["name"] = None

    if result["id"] or result["name"]: rows.append(result)


### Pro 1.zdroj dat a 6. zdroj dat - events
#for group in groups:
#    result = {}
#    if group["groupsIds"]:
#        if group["groupsNames"]:
#            # Zip together IDs and names
#            for group_id, group_name in zip(group["groupsIds"], group["groupsNames"]):
#                # Create a dictionary for each ID-name pair
#                row = {"id": group_id, "name": group_name}
#                rows.append(row)
#        else:
#            # If no names provided, only add IDs
#            for group_id in group["groupsIds"]:
#                row = {"id": group_id, "name": None}
#                rows.append(row)
#    elif group["groupsNames"]:
#        # If no IDs provided, only add names
#        for group_name in group["groupsNames"]:
#            row = {"id": "not-present", "name": group_name}
#            rows.append(row)

#Cross reference (z více zdrojů) - dupliciy jsou
#########################################################################

def check_ids_with_different_names(data):
    id_name_map = {}
    for item in data:
        id_val = item['id']
        name_val = item['name']
        if id_val in id_name_map:
            if id_name_map[id_val] != name_val:
                print(f"ID {id_val} has different names: '{id_name_map[id_val]}' and '{name_val}'")
        else:
            id_name_map[id_val] = name_val

def remove_duplicates(data):
    unique_items = []
    for item in data:
        if item not in unique_items:
            unique_items.append(item)
    return unique_items


parsed = remove_duplicates(rows)
print("########################################## Ids with different name #################################################\n\n")
check_ids_with_different_names(parsed)
print("########################################## Ids with different name #################################################\n\n")

with open('parsed-data6-groups.json', 'w', encoding='utf-8') as f:
    json.dump(parsed, f, ensure_ascii=False, indent=2)

print(parsed[:10])

#print(parsed)
    