import pymysql
import configparser

# Get credentials to connect to database

config = configparser.ConfigParser()
config.read_file(open('credentials.txt'))
dbhost = config['csc']['dbhost']
dbuser = config['csc']['dbuser']
dbpw = config['csc']['dbpw']

# Choose schema 

dbschema = 'asatko'

# 1. Open database connection

dbconn = pymysql.connect(host=dbhost,
                         user=dbuser,
                         passwd=dbpw,
                         db=dbschema,
                         use_unicode=True,
                         charset='utf8mb4',
                         autocommit=True)
cursor = dbconn.cursor()

# 2. Set up query as a string

query = str(input("Enter your query here: "))
