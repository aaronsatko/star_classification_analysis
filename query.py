import pymysql
import configparser

# Get credentials to connect to the database
config = configparser.ConfigParser()
with open('credentials.txt') as f:
    config.read_file(f)
dbhost = config['csc']['dbhost']
dbuser = config['csc']['dbuser']
dbpw = config['csc']['dbpw']

# Choose schema
dbschema = 'world'

dbconn = None
try:
    # Open database connection
    dbconn = pymysql.connect(host=dbhost,
                             user=dbuser,
                             passwd=dbpw,
                             db=dbschema,
                             use_unicode=True,
                             charset='utf8mb4',
                             autocommit=True)

    # Print connection confirmation
    print("Database connection successful.")
    cursor = dbconn.cursor()

    # Set up and execute query
    #query = str(input("Enter your query here: "))
    query = "SELECT Code, CountryName FROM Country;"
    cursor.execute(query)

    # Fetch and process results
    result = cursor.fetchall()
    # process result
    for row in result:
        print("Country Code:", row[0], end=' -> ')
        print("Country Name:", row[1])


except pymysql.MySQLError as e:
    print(f"Error connecting to the database: {e}")
    
finally:
    # Close database connection
    if dbconn:
        dbconn.close()
        print("Database connection closed.")