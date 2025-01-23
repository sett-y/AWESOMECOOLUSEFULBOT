import sqlite3

# helper commands for working with the sqlite database
# this is mainly to reduce codebase size and encourage code reuse

async def return_guild_emoji(guildID, defaultEmoji=None):
    table_name = f"guild_{guildID}"

    con = sqlite3.connect("files/configs.db")
    cur = con.cursor()
    query = f'''
    SELECT emoji FROM {table_name}
    '''
    guildEmoji = cur.execute(query).fetchall()
    con.close()

    if guildEmoji[0][0]:
        return guildEmoji[0][0]
    else:
        print("using default emoji")
        return defaultEmoji

async def delete_guild_emoji(guildID):
    table_name = f"guild_{guildID}"

    guild_emoji = await return_guild_emoji(guildID)

    con = sqlite3.connect("files/configs.db")
    cur = con.cursor()
    query = f'''
    DELETE FROM {table_name}
    WHERE emoji = ?
    '''
    cur.execute(query,(guild_emoji,))

    con.commit()
    con.close()

