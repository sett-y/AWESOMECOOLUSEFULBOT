# helper commands for working with the sqlite database
# this is mainly to reduce codebase size and encourage code reuse

async def return_guild_emoji(guildID, cur, defaultEmoji=None):
    table_name = f"guild_{guildID}"

    query = f'''
    SELECT emoji FROM {table_name}
    '''
    try:
        guildEmoji = cur.execute(query).fetchall()
    except:# Exception as e:
        #print(e)
        return defaultEmoji

    if guildEmoji:
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

async def check_column(table_name, column_name, cur):
    query = f'''
    SELECT COUNT(*) AS column_exists
    FROM pragma_table_info('{table_name}')
    WHERE name='{column_name}'
    '''
    col = cur.execute(query).fetchall()
    print(col)
    print(col[0][0])
    return col

# updates column, creates if doesnt exist
async def update_column(table_name, column_name, column_val, cur, con):
    print(f"updating column {column_name}")

    # check if table exists
    query = f'''
    SELECT name FROM sqlite_master
    WHERE type='table' AND name='{table_name}'
    '''
    tabCheck = cur.execute(query).fetchall()
    if not tabCheck:
        print("creating new table")
        tabQuery = f'''
        CREATE TABLE {table_name} ({column_name} TEXT)
        '''
        cur.execute(tabQuery)
        valQuery = f'''
        INSERT INTO {table_name} ({column_name})
        VALUES ('{column_val}')
        '''
        cur.execute(valQuery)

    query = f'''
    SELECT COUNT(*) AS column_exists
    FROM pragma_table_info('{table_name}')
    WHERE name='{column_name}'
    '''
    colCheck = cur.execute(query).fetchone()[0]
    
    if colCheck == 0:
        # add
        print("creating new column")
        colQuery = f'''
        ALTER TABLE {table_name}
        ADD COLUMN {column_name} TEXT
        '''
        cur.execute(colQuery)
    
    # update
    print("updating column")
    query = f'''
    UPDATE {table_name}
    SET {column_name} = '{column_val}'
    '''
    cur.execute(query)  
    print(f"{column_name} updated")
    con.commit()

async def delete_column(table_name, column_name, cur, con):
    print(f"deleting column {column_name}")
    query = f'''
    ALTER TABLE {table_name}
    DROP COLUMN {column_name}
    '''
    cur.execute(query)
    con.commit()

async def select_column(table_name, column_name, cur):
    print(f"selecting column {column_name}")
    query = f'''
    SELECT {column_name} FROM {table_name}
    '''
    column = cur.execute(query).fetchall()
    print(f"column value: {column}")
    if column:
        return column[0][0]
    else:
        print("column not found")