import sqlite3

# helper commands for working with the sqlite database
# this is mainly to reduce codebase size and encourage code reuse

async def return_guild_emoji(guildID, cur, defaultEmoji=None):
    table_name = f"guild_{guildID}"

    query = f'''
    SELECT emoji FROM {table_name}
    '''
    try:
        guildEmoji = cur.execute(query).fetchall()
    except Exception as e:
        print(e)

    if guildEmoji[0][0]:
        return guildEmoji[0][0]
    else:
        print("using default emoji")
        return defaultEmoji

async def delete_guild_emoji(guildID, cur, con):
    table_name = f"guild_{guildID}"

    guild_emoji = await return_guild_emoji(guildID)

    query = f'''
    DELETE FROM {table_name}
    WHERE emoji = ?
    '''
    cur.execute(query,(guild_emoji,))
    con.commit()

async def update_column(table_name, column_name, column_val, cur, con):
    print(f"updating column {column_name}")
    query = f'''
    UPDATE {table_name}
    SET {column_name} = ?
    '''
    column = cur.execute(query, (column_val,))
    
    if not column:
        print("column does not exist, creating new column")
        query = f'''
        ALTER TABLE {table_name}
        ADD {column_name} TEXT
        '''
        cur.execute(query)

        query = f'''
        UPDATE {table_name}
        SET {column_name} = ?
        '''
        cur.execute(query, (column_val,))

    con.commit()