import pymysql
import configparser
import logging

# Set up logging
logging.basicConfig(filename='database_errors.log', level=logging.ERROR, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Get credentials to connect to the database
config = configparser.ConfigParser()
with open('credentials.txt') as f:
    config.read_file(f)
dbhost = config['csc']['dbhost']
dbuser = config['csc']['dbuser']
dbpw = config['csc']['dbpw']
dbschema = config['csc']['dbschema']

# Predefined queries
predefined_queries = {
    1: ("Average and Standard Deviation for Each Filter by Class",
        """SELECT class, AVG(u) AS avg_ultraviolet, STDDEV(u) AS stddev_ultraviolet, 
           AVG(g) AS avg_green, STDDEV(g) AS stddev_green, AVG(r) AS avg_red, 
           STDDEV(r) AS stddev_red, AVG(i) AS avg_near_infrared, 
           STDDEV(i) AS stddev_near_infrared, AVG(z) AS avg_infrared, 
           STDDEV(z) AS stddev_infrared FROM celestial_observations GROUP BY class"""),
    2: ("Celestial Objects with Highest Redshift",
        """SELECT *, plate FROM celestial_observations ORDER BY redshift DESC LIMIT 10"""),
    3: ("Distribution of Observations Across Different Plates",
        """SELECT plate, COUNT(*) AS observation_count, AVG(redshift) AS avg_redshift 
           FROM celestial_observations GROUP BY plate ORDER BY observation_count DESC"""),
    4: ("Average Redshift Values Comparison",
        """SELECT class, AVG(redshift) AS average_redshift, MIN(redshift) AS min_redshift, 
           MAX(redshift) AS max_redshift FROM celestial_observations GROUP BY class"""),
    5: ("Count and Average Values for Each Class",
        """SELECT class, COUNT(*) AS frequency, AVG(u) AS avg_u, AVG(g) AS avg_g, 
           AVG(r) AS avg_r, AVG(i) AS avg_i, AVG(z) AS avg_z 
           FROM celestial_observations GROUP BY class""")
}

def select_query():
    print("Select a predefined query:")
    for key in predefined_queries:
        print(f"{key}: {predefined_queries[key][0]}")
    choice = int(input("Enter the number of the query you want to execute: "))
    print("")
    return predefined_queries.get(choice, (None, None))[1]

def format_and_print_result(result):
    for row in result:
        formatted_row = ' | '.join(str(x).ljust(15) for x in row)
        print(formatted_row)

dbconn = None
try:
    dbconn = pymysql.connect(host=dbhost, user=dbuser, passwd=dbpw, db=dbschema, 
                             use_unicode=True, charset='utf8mb4', autocommit=True)
    print("Database connection successful.")
    cursor = dbconn.cursor()

    query = select_query()
    if query:
        cursor.execute(query)
        result = cursor.fetchall()
        format_and_print_result(result)
    else:
        print("Invalid query selection.")

except pymysql.MySQLError as e:
    error_message = f"Error connecting to the database: {e}"
    print(error_message)
    logging.error(error_message)

finally:
    if dbconn:
        dbconn.close()
        print("Database connection closed.")