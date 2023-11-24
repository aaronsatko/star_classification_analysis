import pandas as pd
import configparser
import pymysql
from tqdm import tqdm

# Read CSV file
CSVfile = 'star_classification.csv'
df = pd.read_csv(CSVfile)
columns_to_keep = ['obj_ID', 'alpha', 'delta', 'u', 'g', 'r', 'i', 'z', 'spec_obj_ID', 'class', 'redshift', 'plate', 'MJD']
df = df[columns_to_keep]

# Read db configuration
config = configparser.ConfigParser()
with open('credentials.txt') as f:
    config.read_file(f)
dbhost = config['csc']['dbhost']
dbuser = config['csc']['dbuser']
dbpw = config['csc']['dbpw']
dbschema = config['csc']['dbschema']

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

    print("Database connection successful.")
    cursor = dbconn.cursor()

    # Drop tables if they exist

    dbconn.commit()

    cursor.execute("DROP TABLE IF EXISTS celestial_observations")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS celestial_observations (
            observation_id INT AUTO_INCREMENT PRIMARY KEY,
            obj_ID BIGINT,
            alpha DOUBLE,
            delta DOUBLE,
            u DOUBLE,
            g DOUBLE,
            r DOUBLE,
            i DOUBLE,
            z DOUBLE,
            spec_obj_ID BIGINT UNSIGNED,
            class VARCHAR(10),
            redshift DOUBLE,
            plate INT,
            MJD INT
        );
    """)
    

    dbconn.commit()

    # Insert class names
    '''
    cursor.execute("INSERT INTO celestial_class (class_name) VALUES ('GALAXY'), ('STAR'), ('QSO');")
    dbconn.commit()
    '''
    
    def insert_batch(table_name, insert_query, data, batch_size=1000):
        for i in tqdm(range(0, len(data), batch_size), desc=f"Inserting into {table_name}"):
            batch_data = data[i:i + batch_size]
            cursor.executemany(insert_query, batch_data)
            dbconn.commit()

    data_tuples = list(df.itertuples(index=False, name=None))

    # Define the insert query
    insert_query = """
    INSERT INTO celestial_observations (obj_ID, alpha, delta, u, g, r, i, z, spec_obj_ID, class, redshift, plate, MJD)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    insert_batch('celestial_observations', insert_query, data_tuples)
    
except pymysql.MySQLError as e:
    print("Error in database operation:", e)

finally:
    # Close database connection
    if dbconn:
        dbconn.close()
        print("Database connection closed.")