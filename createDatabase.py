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
    
    # Drop tables if they exist
    cursor.execute("DROP TABLE IF EXISTS celestial_object;")
    cursor.execute("DROP TABLE IF EXISTS celestial_photometric_data;")
    cursor.execute("DROP TABLE IF EXISTS celestial_observation_runs;")
    cursor.execute("DROP TABLE IF EXISTS celestial_spectroscopic_data;")
    cursor.execute("DROP TABLE IF EXISTS celestial_class;")

    dbconn.commit()

    # Create tables
    cursor.execute("""
        CREATE TABLE celestial_object (
            obj_ID BIGINT PRIMARY KEY,
            alpha DECIMAL(17, 12),
            delta DECIMAL(17, 12),
            class_id INT,
            FOREIGN KEY (class_id) REFERENCES celestial_class(class_id)
        );
    """)
    cursor.execute("""
        CREATE TABLE celestial_photometric_data (
            obj_ID BIGINT,
            u DECIMAL(10, 5),
            g DECIMAL(10, 5),
            r DECIMAL(10, 5),
            i DECIMAL(10, 5),
            z DECIMAL(10, 5),
            PRIMARY KEY (obj_ID),
            FOREIGN KEY (obj_ID) REFERENCES celestial_object(obj_ID)
        );
    """)
    cursor.execute("""
        CREATE TABLE celestial_observation_runs (
            run_ID INT PRIMARY KEY,
            rereun_ID INT,
            cam_col INT,
            field_ID INT
        );
    """)
    
    cursor.execute("""
        CREATE TABLE celestial_spectroscopic_data (
            spec_obj_ID VARCHAR(50) PRIMARY KEY,
            obj_ID BIGINT,
            plate INT,
            MJD INT,
            fiber_ID INT,
            FOREIGN KEY (obj_ID) REFERENCES celestial_object(obj_ID)
        );
    """)
    dbconn.commit()

    cursor.execute("""
        CREATE TABLE celestial_class (
        class_id INT PRIMARY KEY AUTO_INCREMENT,
        class_name VARCHAR(50) UNIQUE NOT NULL
            );
    """)
    dbconn.commit()

    # Insert class names
    cursor.execute("INSERT INTO celestial_class (class_name) VALUES ('GALAXY'), ('STAR'), ('QSO');")
    dbconn.commit()

    # Insert data in batches
    def insert_batch(table_name, insert_query, data, batch_size=1000):
        for i in tqdm(range(0, len(data), batch_size), desc=f"Inserting into {table_name}"):
            batch_data = data[i:i + batch_size]
            cursor.executemany(insert_query, batch_data)
            dbconn.commit()

    # Insert data into celestial_object
    for _, row in tqdm(df.iterrows(), desc="Inserting data"):
        class_id_query = f"SELECT class_id FROM celestial_class WHERE class_name = '{row['class']}'"
        cursor.execute(class_id_query)
        class_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO celestial_object (obj_ID, alpha, delta, class_id) VALUES (%s, %s, %s, %s)",
                       (row['obj_ID'], row['alpha'], row['delta'], class_id))

    # Batch insert data into Observation
    observation_data = [(row['obj_ID'], row['u'], row['g'], row['r'], row['i'], row['z'], row['run_ID'], row['rerun_ID'], row['cam_col'], row['field_ID']) for _, row in df.iterrows()]
    insert_observation_query = """INSERT INTO Observation (obj_ID, u, g, r, i, z, run_ID, rerun_ID, cam_col, field_ID)
                                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    insert_batch("Observation", insert_observation_query, observation_data)

    # Batch insert data into Classification
    classification_data = [(row['obj_ID'], row['class'], row['redshift'], row['plate'], row['MJD'], row['fiber_ID'], row['spec_obj_ID']) for _, row in df.iterrows()]
    insert_classification_query = """INSERT INTO Classification (obj_ID, class, redshift, plate, MJD, fiber_ID, spec_obj_ID)
                                     VALUES (%s, %s, %s, %s, %s, %s, %s);"""
    insert_batch("Classification", insert_classification_query, classification_data)

except pymysql.MySQLError as e:
    print("Error in database operation:", e)

finally:
    # Close database connection
    if dbconn:
        dbconn.close()
        print("Database connection closed.")