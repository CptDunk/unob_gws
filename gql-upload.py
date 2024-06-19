import json
import re
import uuid
import os
from functools import cache

from async_lru import alru_cache
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import asyncio
import aiohttp

class DBWriter:
    def __init__(self, username="john.newbie@world.com", password="john.newbie@world.com"):
        self.username = username
        self.password = password
        self.token = None

    async def getToken(self):
        if self.token:
            return self.token

        keyurl = "http://localhost:33001/oauth/login3"
        async with aiohttp.ClientSession() as session:
            async with session.get(keyurl) as resp:
                keyJson = await resp.json()

            payload = {"key": keyJson["key"], "username": self.username, "password": self.password}
            async with session.post(keyurl, json=payload) as resp:
                tokenJson = await resp.json()
        self.token = tokenJson.get("token", None)
        return self.token

    async def queryGQL(self, query, variables):
        gqlurl = "http://localhost:33001/api/gql"
        token = await self.getToken()
        payload = {"query": query, "variables": variables}
        cookies = {'authorization': token}
        async with aiohttp.ClientSession() as session:
            async with session.post(gqlurl, json=payload, cookies=cookies) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    print(f"failed query \n{query}\n with variables {variables}".replace("'", '"'))
                    print(f"failed resp.status={resp.status}, text={text}")
                    raise Exception(f"Unexpected GQL response", text)
                else:
                    response = await resp.json()
                    return response

    async def queryGQL3(self, query, variables):
        times = 3
        result = None
        for i in range(times):
            try:
                result = await self.queryGQL(query=query, variables=variables)
                if result.get("errors", None) is None:
                    return result
                print(result)
            except Exception as e:
                print(f"Attempt {i+1} failed: {e}")
            await asyncio.sleep(10)

        raise Exception(f"Unable to run query={query} with variables {variables} for {times} times\n{result}".replace("'", '"'))

    @cache
    def GetQuery(self, tableName, queryType):
        assert queryType in ["read", "readp", "create", "update"], f"unknown queryType {queryType}"
        queryfile = f"./gqls/{tableName}/{queryType}.gql"
        with open(queryfile, "r", encoding="utf-8") as fi:
            lines = fi.readlines()
        query = ''.join(lines)
        assert query is not None, f"missing {queryType} query for table {tableName}"
        return query

    @alru_cache(maxsize=1024)
    async def asyncTranslateID(self, outer_id, type_id):
        query = 'query($type_id: ID!, $outer_id: String!){ result: internalId(typeidId: $type_id, outerId: $outer_id) }'
        jsonData = await self.queryGQL3(query=query, variables={"outer_id": outer_id, "type_id": type_id})
        data = jsonData.get("data", {"result": None})
        result = data.get("result", None)
        return result

    @alru_cache()
    async def getAllTypes(self):
        query = self.GetQuery(tableName="externalidtypes", queryType="readp")
        jsonData = await self.queryGQL3(query=query, variables={"limit": 1000})
        data = jsonData.get("data", {"result": None})
        result = data.get("result", None)
        assert result is not None, f"unable to get externalidtypes"
        asdict = {item["name"]: item["id"] for item in result}
        return asdict

    @alru_cache(maxsize=1024)
    async def getTypeId(self, typeName):
        alltypes = await self.getAllTypes()
        result = alltypes.get(typeName, None)
        assert result is not None, f"unable to get id of type {typeName}"
        return result

    async def registerID(self, inner_id, outer_id, type_id):
        mutation = '''
            mutation ($type_id: ID!, $inner_id: ID!, $outer_id: String!) {
                result: externalidInsert(
                    externalid: {innerId: $inner_id, typeidId: $type_id, outerId: $outer_id}
                ) {
                    msg
                    result: externalid {
                        id    
                        }
                    }
                }
        '''
        jsonData = await self.queryGQL3(query=mutation, variables={"inner_id": str(inner_id), "outer_id": outer_id, "type_id": str(type_id)})
        data = jsonData.get("data", {"result": {"msg": "fail"}})
        msg = data["result"]["msg"]
        if msg != "ok":
            print(f'register ID failed ({ {"inner_id": inner_id, "outer_id": outer_id, "type_id": type_id} })\n\tprobably already registered')
        else:
            print(f"registered {outer_id} for {inner_id} ({type_id})")
        return "ok"

    async def Read(self, tableName, variables, outer_id=None, outer_id_type_id=None):
        if outer_id:
            assert outer_id_type_id is not None, f"if outer_id ({outer_id}) defined, outer_id_type_id must be defined also"
            inner_id = await self.asyncTranslateID(outer_id=outer_id, type_id=outer_id_type_id)
            assert inner_id is not None, f"outer_id {outer_id} od type_id {outer_id_type_id} mapping failed on table {tableName}"
            variables = {**variables, "id": inner_id}

        queryRead = self.GetQuery(tableName, "read")
        response = await self.queryGQL3(query=queryRead, variables=variables)
        error = response.get("errors", None)
        assert error is None, f"error {error} during query \n{queryRead}\n with variables {variables}".replace("'", '"')
        data = response.get("data", None)
        assert data is not None, f"got no data during query \n{queryRead}\n with variables {variables}".replace("'", '"')
        result = data.get("result", None)
        return result

    async def Create(self, tableName, variables, outer_id=None, outer_id_type_id=None):
        queryType = "create"
        if outer_id:
            assert outer_id_type_id is not None, f"if outer_id ({outer_id}) defined, outer_id_type_id must be defined also"
            inner_id = await self.asyncTranslateID(outer_id=outer_id, type_id=outer_id_type_id)

            if inner_id:
                print(f"outer_id ({outer_id}) defined ({outer_id_type_id}) \t on table {tableName},\t going update")
                old_data = await self.Read(tableName=tableName, variables={"id": inner_id})
                if old_data is None:
                    print(f"found corrupted data, entity with id {inner_id} in table {tableName} is missing, going to create it")
                    variables = {**variables, "id": inner_id}
                else:
                    variables = {**old_data, **variables, "id": inner_id}
                    queryType = "update"
            else:
                print(f"outer_id ({outer_id}) undefined ({outer_id_type_id}) \t on table {tableName},\t going insert")
                registrationResult = await self.registerID(inner_id=variables["id"], outer_id=outer_id, type_id=outer_id_type_id)
                assert registrationResult == "ok", f"Something is really bad, ID registration failed"

        query = self.GetQuery(tableName, queryType)
        assert query is not None, f"missing {queryType} query for table {tableName}"
        response = await self.queryGQL3(query=query, variables=variables)
        data = response["data"]
        result = data["result"]
        result = result["result"]
        return result
    
async def db_writer_async():
    with open("res/experimental/systemdata_groups.json", "r", encoding="utf-8") as f:
        systemdata = json.load(f)

    groups = systemdata["groups"]
    externalids = systemdata["externalids"]

    db_writer = DBWriter()

    for group in groups:
        group["id"] = group["id"]
        await db_writer.Create(tableName="groups", variables=group)

    for externalid in externalids:
        externalid["id"] = externalid["id"]
        externalid["inner_id"] = externalid["inner_id"]
        externalid["typeid_id"] = externalid["typeid_id"]
        await db_writer.registerID(inner_id=externalid["inner_id"], outer_id=externalid["outer_id"],
                                   type_id=externalid["typeid_id"])
        

if __name__ == '__main__':
    asyncio.run(db_writer_async())   #keyurl = ...