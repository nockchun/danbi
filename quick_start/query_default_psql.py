from danbi import Jinja2Mapper
from danbi.database import psql, setPsql

# Create db-work environments with query-mapper.
setPsql(
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

# Create Table
psql.execute("book.create")

# Insert Data
print("----------------------------- Insert Data ------------------------------")
values = (1, 'Layla Nowiztki', '789-1-46-268414-1', 'How to become a professional programmer', 'January 25 2011')
print("insert amount : ", psql.execute("book.insert", values))

# Insert Bulk
values = [
    (2, 'Layla Nowiztki', '789-1-46-268414-1', 'How to become a professional programmer', 'January 25 2011'),
    (3, 'Layla Nowiztki', '789-1-46-268414-1', 'How to become a professional programmer', 'January 25 2011'),
    (4, 'Layla Nowiztki', '789-1-46-268414-1', 'How to become a professional programmer', 'January 25 2011'),
    (5, 'Layla Nowiztki', '789-1-46-268414-1', 'How to become a professional programmer', 'January 25 2011'),
]
print("insert amount : ", psql.executeMany("book.insert", values), "\n")

# Select Data
print("----------------------------- Select Data ------------------------------")
print(psql.queryRaw("SELECT version();"), "\n")
print(psql.query("book.select", {"id": 3}), "\n")
print(psql.queryPandas("book.select", dtype={"author": str}), "\n")

# Delete Data
print("----------------------------- Delete Data ------------------------------")
print(psql.execute("book.delete", (2,)), "\n")
print(psql.queryPandas("book.select"), "\n")

# Close DB
psql.getManager().close()
