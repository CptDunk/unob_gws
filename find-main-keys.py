import re
import json

# Open the JSON file and read its contents
with open('1.zdroj-dat.json', 'r', encoding='utf-8') as file:
    data = file.read()

with open('1.zdroj-dat.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)
    print("loaded file")

# Pattern to match key that contains an array of objects (key and value pairs...). 
pattern = r'("[a-zA-Z_][a-zA-Z0-9_]*"):\s*\[\{'

# Find all occurrences of the pattern in the JSON data
matches = re.findall(pattern, data)

# For all "main" keys
for match in matches:

    #Strip of " " so they can be used in data[match]
    match = match.strip('"')

    print('\n', '-'*30,'\n', match, '\n', '-'*30)

    main_key = json_data[match]
    keys = {}
    for item in main_key:
        for key in item.keys():
            keys[key] = True

    for item in main_key:
        for key in keys.keys():
            if not key in item:
                keys[key] = False

    print('Vše', ':\n')
    print(keys)

    print('---\n','Všude přítomné', ':\n')
    for key, value in keys.items():
        if value:
            print(key, end=' ')
    print()
    print('---\n','Ne vždy přítomné', ':\n')
    for key, value in keys.items():
        if not value:
            print(key, end=' ')
    print()


# writing to a file

### filter what is in the file
## Open the JSON file and read its contents
#with open('1.zdroj-dat.json', 'r', encoding='utf-8') as file:
#    json_data = file.read()
#
## Define the pattern to match
#pattern = r'("[a-zA-Z_][a-zA-Z0-9_]*"):\s*\[\{'
#
## Insert a newline before and afterthe pattern
##modified_json_data = re.sub(pattern, r'\n\1: [{\n', json_data)
#
## Find all occurrences of the pattern in the JSON data
#matches = re.findall(pattern, json_data)
#
### Insert a newline after every '{'
##modified_json_data = json_data.replace(':[{', ':[{\n\n')
#
## Write the modified content to a new file
#with open('modified_file.json', 'w', encoding='utf-8') as new_file:
#    new_file.write(modified_json_data)