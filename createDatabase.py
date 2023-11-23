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
        CREATE TABLE celestial_class (
        class_id INT PRIMARY KEY AUTO_INCREMENT,
        class_name VARCHAR(50) UNIQUE NOT NULL
            );
    """)
    
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

    # Insert class names
    cursor.execute("INSERT INTO celestial_class (class_name) VALUES ('GALAXY'), ('STAR'), ('QSO');")
    dbconn.commit()

    # Insert data in batches
    def insert_batch(table_name, insert_query, data, batch_size=1000):
        with tqdm(total=len(data), desc=f"Inserting into {table_name}") as pbar:
            for i in range(0, len(data), batch_size):
                batch_data = data[i:i + batch_size]
                cursor.executemany(insert_query, batch_data)
                dbconn.commit()
                pbar.update(len(batch_data))

    # Preparing data for celestial_object
    celestial_object_data = []
    for _, row in df.iterrows():
        class_id_query = f"SELECT class_id FROM celestial_class WHERE class_name = '{row['class']}'"
        cursor.execute(class_id_query)
        class_id = cursor.fetchone()[0]
        celestial_object_data.append((row['obj_ID'], row['alpha'], row['delta'], class_id))

    # Batch insert data into celestial_object
    insert_celestial_object_query = "INSERT INTO celestial_object (obj_ID, alpha, delta, class_id) VALUES (%s, %s, %s, %s)"
    insert_batch("celestial_object", insert_celestial_object_query, celestial_object_data)

    # Preparing data for celestial_photometric_data
    photometric_data = [(row['obj_ID'], row['u'], row['g'], row['r'], row['i'], row['z']) for _, row in df.iterrows()]

    # Batch insert data into celestial_photometric_data
    insert_photometric_query = "INSERT INTO celestial_photometric_data (obj_ID, u, g, r, i, z) VALUES (%s, %s, %s, %s, %s, %s)"
    insert_batch("celestial_photometric_data", insert_photometric_query, photometric_data)

    # Preparing data for celestial_observation_runs
    observation_runs_data = [(row['run_ID'], row['rerun_ID'], row['cam_col'], row['field_ID']) for _, row in df.iterrows()]

    # Batch insert data into celestial_observation_runs
    insert_observation_query = "INSERT INTO celestial_observation_runs (run_ID, rereun_ID, cam_col, field_ID) VALUES (%s, %s, %s, %s)"
    insert_batch("celestial_observation_runs", insert_observation_query, observation_runs_data)

    # Preparing data for celestial_spectroscopic_data
    spectroscopic_data = [(row['spec_obj_ID'], row['obj_ID'], row['plate'], row['MJD'], row['fiber_ID']) for _, row in df.iterrows()]

    # Batch insert data into celestial_spectroscopic_data
    insert_spectroscopic_query = "INSERT INTO celestial_spectroscopic_data (spec_obj_ID, obj_ID, plate, MJD, fiber_ID) VALUES (%s, %s, %s, %s, %s)"
    insert_batch("celestial_spectroscopic_data", insert_spectroscopic_query, spectroscopic_data)


except pymysql.MySQLError as e:
    print("Error in database operation:", e)

finally:
    # Close database connection
    if dbconn:
        dbconn.close()
        print("Database connection closed.")