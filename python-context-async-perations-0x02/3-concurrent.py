import asyncio
from aiosqlite import connect
import aiosqlite



connection = (
    host = 'localhost',
    database = 'users',
    password = 'testpassword',
    port = 3306,
    user = 'root'
)

async def async_fetch_users():
    async with connect(connection) as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT * FROM users")
        users = await cursor.fetchall()
        await cursor.close()
        return users
    
async def async_fetch_older_users():
    async with connect(connection) as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT * FROM users WHERE age > 40")
        older_users = await cursor.fetchall()
        await cursor.close()
        return older_users
    
async def fetch_concurrently():
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    print("All Users:", all_users)
    print("Users Older Than 40:", older_users)

# Run the async function
asyncio.run(fetch_concurrently())