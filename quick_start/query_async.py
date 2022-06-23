import asyncio
from datetime import datetime
from danbi import Jinja2Mapper
from danbi.database import ConnMngPsqlAsync, DBPsqlAsync

async def main():
    psql = await ConnMngPsqlAsync(
        user="rsnet",
        password="rsnet",
        host="postgresql-hl.postgresql",
        port="5432",
        database="rsnet"
    ).connect(min_size=2, max_size=10)
    mapper = Jinja2Mapper(["res/sqlmap.yaml"], "sql-test", 1.0)
    db = DBPsqlAsync(psql, mapper)

    # Create Table
    await db.execute("book.create")

    # Insert Data
    print("----------------------------- Insert Data ------------------------------")
    values = (1, 'Layla Nowiztki', '789-1-46-268414-1', 'How to become a professional programmer', datetime.strptime("January 25 2011", "%B %d %Y"))
    assert await db.execute("book.insert.async", values) is None, "can't insert."

    # Insert Bulk
    values = [
        (2, 'Layla Nowiztki', '789-1-46-268414-1', 'How to become a professional programmer', datetime.strptime("January 25 2011", "%B %d %Y")),
        (3, 'Layla Nowiztki', '789-1-46-268414-1', 'How to become a professional programmer', datetime.strptime("January 25 2011", "%B %d %Y")),
        (4, 'Layla Nowiztki', '789-1-46-268414-1', 'How to become a professional programmer', datetime.strptime("January 25 2011", "%B %d %Y")),
        (5, 'Layla Nowiztki', '789-1-46-268414-1', 'How to become a professional programmer', datetime.strptime("January 25 2011", "%B %d %Y")),
    ]
    assert await db.executeMany("book.insert.async", values) is None, "can't insert."
    print("done", "\n")

    # Select Data
    print("----------------------------- Select Data ------------------------------")
    print(await db.queryRaw("SELECT version();"), "\n")
    print(await db.query("book.select", {"id": 3}), "\n")
    print(await db.queryPandas("book.select", dtype={"author": str}), "\n")

    # Delete Data
    print("----------------------------- Delete Data ------------------------------")
    print(await db.execute("book.delete.async", (2,)), "\n")
    print(await db.queryPandas("book.select"), "\n")

    # Close DB
    await psql.close()

asyncio.get_event_loop().run_until_complete(main())