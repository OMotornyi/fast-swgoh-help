import asyncio
import swgohhelp
from swgoh_help_api import HelpAPI

#969192911 669323375 928429534 139328937
async def main():

    tasks = []
    # tasks.append(asyncio.create_task(swgohhelp.fetch_guilds(swgohhelp.CONFIG, [969192911])))
    # tasks.append(asyncio.create_task(swgohhelp.fetch_guilds(swgohhelp.CONFIG, [669323375])))
    # tasks.append(asyncio.create_task(swgohhelp.fetch_guilds(swgohhelp.CONFIG, [928428534])))
    # tasks.append(asyncio.create_task(swgohhelp.fetch_guilds(swgohhelp.CONFIG, [139328937])))
    # for task in tasks:
    #     await task
    # p1 = asyncio.create_task(swgohhelp.fetch_guilds(swgohhelp.CONFIG, [969192911]))
    # p2 = asyncio.create_task(swgohhelp.fetch_guilds(swgohhelp.CONFIG, [669323375]))
    # p3 = asyncio.create_task(swgohhelp.fetch_guilds(swgohhelp.CONFIG, [928428534]))
    # p4 = asyncio.create_task(swgohhelp.fetch_guilds(swgohhelp.CONFIG, [139328937]))
    #await asyncio.gather(*tasks)
    #return token
    swgoh_api = HelpAPI()
    print(swgoh_api.config)
    print(swgoh_api.session)
    #await swgoh_api.ai_get_access_token()
    guild = await swgoh_api.fetch_guilds([928428534])
    #print(guild)
    codes = [x['allyCode'] for x in guild[0]['roster']]
    for code in codes[:]:
        print(code)
        tasks.append(swgoh_api.fetch_players([code]))
    guild_players = await asyncio.gather(*tasks, return_exceptions=False)
    tasks = []
    for code in codes:
        print(code)
        tasks.append(swgoh_api.fetch_players([code]))
    guild_players = await asyncio.gather(*tasks, return_exceptions=False)
    tasks = []
    for code in codes:
        print(code)
        tasks.append(swgoh_api.fetch_players([code]))
    guild_players = await asyncio.gather(*tasks,return_exceptions=False)
    print(len(guild_players))
    #for gp in guild_players:
    #    print(gp)
    #guild = await swgoh_api.fetch_guilds([928428534])

    #print(guild)
    print(swgoh_api.config)
    print(swgoh_api.session)
    await swgoh_api.session.close()
    return guild

if __name__ == '__main__':
    guild = asyncio.run(main())

    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()