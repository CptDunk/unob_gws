import datetime
import json
import uuid


# uuid(UUID(str)) should be enough on its own, but from some comments on Stackoverflow it is said that it can
# return false negative even when it passes the function, hence the try-except block
def is_valid_uuid(_uid):
    try:
        uuid.UUID(str(_uid))
        return True
    except ValueError:
        return False


def source1_extraction():
    """ Extracting data from 1st source(study plan),
        source is not reachable right now, so the data is stored in a file"""
    group_dict = {'groups': []}
    with open('res/1.zdroj-dat.json', 'r', encoding='utf-8') as file:
        json_data = json.load(file)
        print("loaded file")

        temp_dict = {}
        for key in json_data["types"]:
            # get difference in length of 'groupsIds' and 'groupsNames'
            dif_len = abs(len(key["groupsIds"]) - len(key["groupsNames"]))
            # if the difference is greater that 0, that means there are more IDs than names, meaning
            # that there are false IDs present(in this case "0")
            if dif_len > 0:
                # print("ids:", len(key["groupsIds"]), "names:", len(key["groupsNames"]))
                for ind, _type in enumerate(key["groupsIds"]):
                    # print(ind, _type)
                    # do nothing until you go over false IDs
                    if ind >= dif_len:
                        # use dictionary to get rid of duplicate values
                        temp_dict[_type] = key["groupsNames"][ind - dif_len]
                    else:
                        pass
        # save the dictionary to the group_dict in proper format
        for key in temp_dict:
            app_dict = {'id': key, 'name': temp_dict[key]}
            group_dict['groups'].append(app_dict)
        save_as_json("GroupTypes", group_dict)
    # with open('res/GroupTypes.json', 'w', encoding='utf-8') as data:
    #     # print(f"Groups saved.\nNumber of groups: {len(group_dict['groups'])}")
    #     json.dump(group_dict, data, indent= 4, ensure_ascii=False)


def merge_function(rozvrh, ap, dymado, ext_ids, new_dict):
    """
        function that merges all sources into systemdata.json
        """
    # create a list of values of key "name" from rozvrh
    rozvrh_names = [group["name"] for group in rozvrh["groups"]]

    # reformat data from MojeAP to fit new format
    for fakulta in ap["MojeAP"]:
        for group_ap in ap["MojeAP"][fakulta]:
            # if the name is in the list, remove it from the list
            if group_ap["name"] in rozvrh_names:
                rozvrh_names.remove(group_ap["name"])
                _rozvrh = [_rozvrh for _rozvrh in rozvrh["groups"] if _rozvrh["name"] == group_ap["name"]]
                # use the implementation of func_append_dict to add the entry to the dictionary and externalids
                new_dict = func_append_dict(_rozvrh[0], new_dict, ext_ids, outer=group_ap["id"], source=1)
            else:
                new_dict = func_append_dict(group_ap, new_dict, ext_ids, outer=group_ap["id"], source=1)
    # reformat data from Study plan to fit new format as well
    for group in rozvrh["groups"]:
        if group["name"] in rozvrh_names:
            rozvrh_names.remove(group["name"])
            new_dict = func_append_dict(group, new_dict, ext_ids, source=0)
        else:
            pass
    # and lastly, reformat data from dymado
    # just in case some IDs are matching, we will check with the IDs and names of dymado with list of new_dict's items

    new_dict_id = [group["id"] for group in new_dict["groups"]]
    new_dict_name = [group["name"] for group in new_dict["groups"]]

    for group_dymado in dymado["dymado"]["value"]:
        if group_dymado["SHORT"] not in new_dict_name or group_dymado["UIC"].strip('0') not in new_dict_id:
            pass

            new_dict = func_append_dict(group_dymado, new_dict, ext_ids, source=2)
        else:
            print("Group already exists in the dictionary.", group_dymado["UIC"])

    # save_as_json("res/experimental/NewGroups", new_dict)
    # save_as_json("res/experimental/NewExtIDS", ext_ids)
    # save_as_json("res/experimental/systemdata",)


def func_append_dict(rozvrh, _dict, ext_ids, outer=0, source=0):
    # all of these groups are under faculty and all are study programs, hence the hardcoded values, for now
    #TODO
    # study group is id of st group from dummy systemdata(i presume its student group) - group_type_id
    group_type_id = "cd49e157-610c-11ed-9312-001a7dda7110"
    # master id is what the group "falls" under, in this case a group called faculty
    #TODO
    # here we might use the distribution of groups in MojeAP source and assign their ids matching specific faculty
    master_id = "2d9dced0-a4a2-11ed-b9df-0242ac120003"

    lastchange = str(datetime.datetime.now())
    ext_id = str(uuid.uuid4())
    inner_id = ""
    name = ""
    #TODO
    # default for now, might change(outer_id)
    outer_id = outer

    # now include switch to determine whethere it is study group or other dpts. since dynamo is now integrated too
    match source:
        case 0:
            inner_id = rozvrh["id"] if is_valid_uuid(rozvrh["id"]) else str(uuid.uuid4())
            name = rozvrh["name"]
        case 1:
            inner_id = rozvrh["id"] if is_valid_uuid(rozvrh["id"]) else str(uuid.uuid4())
            name = rozvrh["name"]
        case 2:

            inner_id = str(uuid.uuid4())
            outer_id = rozvrh["UIC"].strip('0')
            name = rozvrh["SHORT"]
            for grouptype in ext_ids["grouptypes"]:
                if grouptype["ex_type"] == rozvrh["TYPE"]:
                    group_type_id = grouptype["id"]
                    break
                else:
                    group_type_id = f"NaN - {rozvrh['TYPE']}"

        #TODO
        # - How do i manage these types, are they even relevant, i cant seem to find any similarity
        # only dymado has specified type(others are study groups[MojeAP and studyplan])
        # - take parent UICs, then match them with existing and get their id(in externalids)
                master_id = rozvrh["PARENT_UIC"].replace(" ", "").split(",")

    typeid_id = ext_ids["externalidtypes"][source]["id"]
    ext_ids["externalids"].append({"id": ext_id, "inner_id": inner_id, "outer_id": outer_id, "typeid_id": typeid_id})

    _dict["groups"].append(dict({"id": inner_id, "name": name, "lastchange": lastchange, "valid": True,
                                 "grouptype_id": group_type_id, "mastergroup_id": master_id}))

    return _dict


def save_as_json(name, _dict):
    with open(f"{name}.json", "w", encoding="utf-8") as file:
        json.dump(_dict, file, indent=4, ensure_ascii=False)
# merge data sources(study plan, MojeAP(groups), Dymado)


def merge_data():

    with (open("res/GroupTypes.json", "r", encoding="utf-8") as groups_rozvrh,
          open("res/MojeAP_groups_rev1.0.json", "r", encoding="utf-8") as groups_mojeAP,
          open("pagecache/dymado/dymado.json", "r", encoding="utf-8") as groups_dymado,
          open("res/externalIDs.json", "r", encoding="utf-8") as externalIds):

        data_rozvrh = json.load(groups_rozvrh)
        data_moje_ap = json.load(groups_mojeAP)
        data_dymado = json.load(groups_dymado)
        ext_ids = json.load(externalIds)

        new_dict = {"groups": []}

        # temp_dict = [[], []]  # store unmatched groups

        merge_function(data_rozvrh, data_moje_ap, data_dymado, ext_ids, new_dict)
        ext_ids["groups"] = new_dict["groups"]
        systemdata = sort_dymado(ext_ids)
        save_as_json("res/experimental/systemdata", systemdata)


def sort_dymado(systemdata):
    for group in systemdata["groups"]:
        if not is_valid_uuid(group["mastergroup_id"]):
            temp = []
            for value in group["mastergroup_id"]:
                for dym in systemdata["externalids"]:
                    if dym["outer_id"] == value.strip("0"):
                        temp.append(str(dym["inner_id"]))
                else:
                    # no respective id
                    pass
            else:
                group["mastergroup_id"] = temp if not None else "nan"
                temp.clear()
        else:
            pass
    return systemdata


if __name__ == "__main__":
    merge_data()
