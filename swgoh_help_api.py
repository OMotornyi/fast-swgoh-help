"""Fully asyncio API wrapper for swgoh.help that automatically handles rate linits"""
import asyncio
import aiohttp
import json
import sys
from os import path
from datetime import datetime, timedelta
import time
from aiohttp.web_exceptions import HTTPError
#from utils2 import aiohttp_post


class HelpAPI:
    SWGOH_HELP = 'https://api.swgoh.help'
    RATE = 1.5
    MAX_TOKENS = 5

    def __init__(self):
        self.session = aiohttp.ClientSession()
        if path.isfile("../CONFIGURE.json"):
            with open("../CONFIGURE.json") as json_file:
                self.config = json.load(json_file)
        else:
            print("File does not exist")
        self.tokens = self.MAX_TOKENS
        self.updated_at = time.monotonic()
        self.response_count = 0


    async def ai_get_access_token(self):
        if 'access_token' in self.config['swgoh.help']:
            expire = self.config['swgoh.help']['access_token_expire']
            if expire > datetime.now() + timedelta(seconds=60):
                return self.config['swgoh.help']['access_token']

        headers = {
            'method': 'post',
            'content-type': 'application/x-www-form-urlencoded',
        }

        data = {
            'username': self.config['swgoh.help']['username'],
            'password': self.config['swgoh.help']['password'],
            'grant_type': 'password',
            'client_id': 'abc',
            'client_secret': '123',
        }

        auth_url = '%s/auth/signin' % self.SWGOH_HELP
        # async with self.session:
        response, error = await self.aiohttp_post(auth_url, headers=headers, data=data)
        if error:
            raise Exception(f'Authentication failed to swgohhelp API: {error}')
        data = await response.json()
        if 'access_token' not in data:
            raise Exception(f'Authentication failed: Server returned `{data}`')

        self.config['swgoh.help']['access_token'] = data['access_token']
        self.config['swgoh.help']['access_token_expire'] = datetime.now() + timedelta(seconds=data['expires_in'])

        return self.config['swgoh.help']['access_token']

    async def get_headers(self):
        token = await self.ai_get_access_token()
        return {
            'method': 'post',
            'content-type': 'application/json',
            'authorization': f'Bearer {token}',
        }

    async def call_api(self, project, url):
        headers =await self.get_headers()
        #async with self.session:
        response, error = await self.aiohttp_post(url, headers=headers, json=project)
        if error:
            raise Exception(f'http_post({url}) failed: {error}')

        try:
            data = await response.json()

        except Exception as err:
            print("Failed to decode JSON:\n%s\n---" % response.content)
            raise err

        if 'error' in data and 'error_description' in data:
            raise Exception(data['error_description'])

        return data

    async def api_swgoh_guilds(self, project):
        return await self.call_api( project, f'{self.SWGOH_HELP}/swgoh/guilds')

    async def fetch_guilds(self, project):

        if type(project) is list:
            project = {'allycodes': project}

        ally_codes = project['allycodes']
        guilds = await self.api_swgoh_guilds( project)
        #print(guilds)
        return guilds

    async def api_swgoh_players(self, project):

        result = []
        expected_players = len(project['allycodes'])

        new_proj = dict(project)
        new_proj['allycodes'] = list(project['allycodes'])

        while len(result) < expected_players:

            returned = await self.call_api(new_proj, '%s/swgoh/players' % self.SWGOH_HELP)
            for player in returned:
                result.append(player)
                new_proj['allycodes'].remove(player['allyCode'])

        return result

    async def fetch_players(self, project):

        if type(project) is list:
            project = {'allycodes': project}

        players = await self.api_swgoh_players(project)

        result = {}
        for player in players:

            if 'roster' in player:
                player['roster'] = self.get_units_dict(player['roster'], 'defId')

            ally_code = player['allyCode']
            result[ally_code] = player
        print(result[ally_code]['name'])
        return result

    async def aiohttp_post(self, url, *args, **kwargs):
        print(f"Tokens:{self.tokens} updated at: {self.updated_at}")
        await self.wait_for_token()
        print(f"Tokens:{self.tokens} updated at: {self.updated_at}")
        try:
            async with self.session.post(url, *args, **kwargs) as response:
                if response.status not in [200, 404]:
                    response.raise_for_status()
                data = await response.json()

        except HTTPError as http_err:
            return (None, 'HTTP error occured: %s' % http_err)

        except Exception as err:
            return (None, 'Other error occured: %s' % err)

        else:
            self.response_count += 1
            print(self.response_count)
            return response, False

    async def wait_for_token(self):
        while self.tokens <= 1:
            self.add_new_tokens()
            await asyncio.sleep(1)
        self.tokens -= 1

    def add_new_tokens(self):
        now = time.monotonic()
        time_since_update = now - self.updated_at
        new_tokens = time_since_update * self.RATE
        if self.tokens + new_tokens >= 1:
            self.tokens = min(self.tokens + new_tokens, self.MAX_TOKENS)
            self.updated_at = now

    def get_units_dict(self, units, base_id_key):

        d = {}

        for unit in units:
            base_id = str(unit[base_id_key])
            d[base_id] = unit

        return d
