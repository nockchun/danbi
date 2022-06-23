import asyncio
import danbi as bi

DB = bi.usePgDBMapper(
    user="rsnet",
    password="rsnet",
    host="postgresql-hl.postgresql",
    port="5432",
    database="rsnet",
    pool_min=5,
    pool_max=10,
    mappers=["res/sqlmap.yaml"],
    namespace="sql-test",
    tag=1.0
)
print(DB.queryRaw("select 1"))
print(DB.query("db.version"))

async def useDB():
    DB = await bi.usePgDBMapperAsync(
        user="rsnet",
        password="rsnet",
        host="postgresql-hl.postgresql",
        port="5432",
        database="rsnet",
        pool_min=5,
        pool_max=10,
        mappers=["res/sqlmap.yaml"],
        namespace="sql-test",
        tag=1.0
    )
    print(await DB.queryRaw("select 1"))
    print(await DB.query("db.version"))

asyncio.get_event_loop().run_until_complete(useDB())
