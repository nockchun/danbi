import danbi as di

# Create db-work environments with query-mapper.
psql = di.ConnMngPsql(
    user="rsnet",
    password="rsnet",
    host="postgresql-hl.postgresql",
    port="5432",
    database="rsnet"
).connect(minconn=1, maxconn=2)
mapper = di.Jinja2Mapper(["res/sqlmap.yaml"], "sql-test", 1.0)
db = di.DBPsql(psql, mapper)

# Create Table
db.execute("book.create")

# Insert Data
print("----------------------------- Insert Data ------------------------------")
values = (1, 'Layla Nowiztki', '789-1-46-268414-1', 'How to become a professional programmer', 'January 25 2011')
print("insert amount : ", db.execute("book.insert", values))

# Insert Bulk
values = [
    (2, 'Layla Nowiztki', '789-1-46-268414-1', 'How to become a professional programmer', 'January 25 2011'),
    (3, 'Layla Nowiztki', '789-1-46-268414-1', 'How to become a professional programmer', 'January 25 2011'),
    (4, 'Layla Nowiztki', '789-1-46-268414-1', 'How to become a professional programmer', 'January 25 2011'),
    (5, 'Layla Nowiztki', '789-1-46-268414-1', 'How to become a professional programmer', 'January 25 2011'),
]
print("insert amount : ", db.executeMany("book.insert", values), "\n")

# Select Data
print("----------------------------- Select Data ------------------------------")
print(db.queryRaw("SELECT version();"), "\n")
print(db.query("book.select", {"id": 3}), "\n")
print(db.queryPandas("book.select", dtype={"author": str}), "\n")

# Delete Data
print("----------------------------- Delete Data ------------------------------")
print(db.execute("book.delete", (2,)), "\n")
print(db.queryPandas("book.select"), "\n")

# Close DB
psql.close()
