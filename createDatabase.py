import pandas as pd
import configparser
import pymysql
from tqdm import tqdm

# Read CSV file
CSVfile = 'star_classification.csv'
df = pd.read_csv(CSVfile)

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

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CelestialObject (
            obj_ID BIGINT PRIMARY KEY,
            alpha DECIMAL(10, 7),
            delta DECIMAL(10, 7)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Observation (
            observation_ID INT AUTO_INCREMENT PRIMARY KEY,
            obj_ID BIGINT,
            u DECIMAL(5, 2),
            g DECIMAL(5, 2),
            r DECIMAL(5, 2),
            i DECIMAL(5, 2),
            z DECIMAL(5, 2),
            run_ID INT,
            rerun_ID INT,
            cam_col INT,
            field_ID INT,
            FOREIGN KEY (obj_ID) REFERENCES CelestialObject(obj_ID)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Classification (
            classification_ID INT AUTO_INCREMENT PRIMARY KEY,
            obj_ID BIGINT,
            class VARCHAR(50),
            redshift DECIMAL(8, 7),
            plate INT,
            MJD INT,
            fiber_ID INT,
            spec_obj_ID BIGINT,
            FOREIGN KEY (obj_ID) REFERENCES CelestialObject(obj_ID)
            );
        """)
    dbconn.commit()

    # Insert data into CelestialObject
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Inserting CelestialObject"):
        insert_celestial = """INSERT INTO CelestialObject (obj_ID, alpha, delta)
                              VALUES (%s, %s, %s)
                              ON DUPLICATE KEY UPDATE alpha = VALUES(alpha), delta = VALUES(delta);"""
        cursor.execute(insert_celestial, (row['obj_ID'], row['alpha'], row['delta']))

    # Insert data into Observation
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Inserting Observation"):
        insert_observation = """INSERT INTO Observation (obj_ID, u, g, r, i, z, run_ID, rerun_ID, cam_col, field_ID)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
        cursor.execute(insert_observation, (row['obj_ID'], row['u'], row['g'], row['r'], row['i'], row['z'], row['run_ID'], row['rerun_ID'], row['cam_col'], row['field_ID']))

    # Insert data into Classification
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Inserting Classification"):
        insert_classification = """INSERT INTO Classification (obj_ID, class, redshift, plate, MJD, fiber_ID, spec_obj_ID)
                                   VALUES (%s, %s, %s, %s, %s, %s, %s);"""
        cursor.execute(insert_classification, (row['obj_ID'], row['class'], row['redshift'], row['plate'], row['MJD'], row['fiber_ID'], row['spec_obj_ID']))

    dbconn.commit()

except pymysql.MySQLError as e:
    print("Error in database operation:", e)

finally:
    # Close database connection
    if dbconn:
        dbconn.close()
        print("Database connection closed.")