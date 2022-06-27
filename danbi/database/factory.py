from danbi import Jinja2Mapper
from danbi.database import ConnMngPsqlAsync, DBPsqlAsync
from danbi.database import ConnMngPsql, DBPsql, IDB

def usePgDBMapper(user: str, password: str, host: str, port: int, database: str, pool_min: int, pool_max: int, mappers: list, namespace: str, tag, base_package: str = None) -> IDB:
    psql = ConnMngPsql(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    ).connect(minconn=pool_min, maxconn=pool_max)
    mapper = Jinja2Mapper(mappers, namespace, tag, base_package)
    db = DBPsql(psql, mapper)

    return db

async def usePgDBMapperAsync(user: str, password: str, host: str, port: int, database: str, pool_min: int, pool_max: int, mappers: list, namespace: str, tag, base_package: str = None) -> IDB:
    psql = await ConnMngPsqlAsync(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    ).connect(min_size=pool_min, max_size=pool_max)
    mapper = Jinja2Mapper(mappers,namespace, tag, base_package)
    db = DBPsqlAsync(psql, mapper)

    return db

