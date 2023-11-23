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
    cursor.execute("DROP TABLE IF EXISTS celestial_spectroscopic_data;")
    cursor.execute("DROP TABLE IF EXISTS celestial_photometric_data;")
    cursor.execute("DROP TABLE IF EXISTS celestial_observation_runs;")
    cursor.execute("DROP TABLE IF EXISTS celestial_object;")
    cursor.execute("DROP TABLE IF EXISTS celestial_class;")


    dbconn.commit()

    # Create tables
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS celestial_class (
        class_id INT PRIMARY KEY AUTO_INCREMENT,
        class_name VARCHAR(50) UNIQUE NOT NULL
            );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS celestial_object (
            id INT PRIMARY KEY AUTO_INCREMENT,
            obj_ID BIGINT,
            alpha DECIMAL(17, 12),
            delta DECIMAL(17, 12),
            class_id INT,
            FOREIGN KEY (class_id) REFERENCES celestial_class(class_id)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS celestial_photometric_data (
            id INT PRIMARY KEY AUTO_INCREMENT,
            u DECIMAL(10, 5),
            g DECIMAL(10, 5),
            r DECIMAL(10, 5),
            i DECIMAL(10, 5),
            z DECIMAL(10, 5),
            FOREIGN KEY (id) REFERENCES celestial_object(id)
        );
    """)
    '''
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS celestial_observation_runs (
            run_ID INT PRIMARY KEY,
            rerun_ID INT,
            cam_col INT,
            field_ID INT
        );
    """)
    '''
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS celestial_spectroscopic_data (
            id INT PRIMARY KEY AUTO_INCREMENT,
            spec_obj_ID VARCHAR(50),
            plate INT,
            MJD INT,
            fiber_ID INT,
            FOREIGN KEY (id) REFERENCES celestial_object(id)
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

    # Insert unique class names into celestial_class
    class_names = df['class'].unique()
    class_data = [(name,) for name in class_names]
    insert_class_query = "INSERT INTO celestial_class (class_name) VALUES (%s);"
    insert_batch("celestial_class", insert_class_query, class_data)

    # Map class names to class_ids
    cursor.execute("SELECT class_id, class_name FROM celestial_class;")
    class_map = {name: id for id, name in cursor.fetchall()}

    # Insert data into celestial_object
    celestial_data = [(row['obj_ID'], row['alpha'], row['delta'], class_map[row['class']]) for _, row in df.iterrows()]
    insert_celestial_query = """INSERT INTO celestial_object (obj_ID, alpha, delta, class_id)
                                VALUES (%s, %s, %s, %s);"""
    insert_batch("celestial_object", insert_celestial_query, celestial_data)

    # Insert data into celestial_photometric_data
    cursor.execute("SELECT obj_ID, id FROM celestial_object;")
    obj_id_to_id = {obj_id: id for obj_id, id in cursor.fetchall()}

    photometric_data = [(row['u'], row['g'], row['r'], row['i'], row['z'], obj_id_to_id[row['obj_ID']]) for _, row in df.iterrows()]
    insert_photometric_query = """INSERT INTO celestial_photometric_data (u, g, r, i, z)
                                VALUES (%s, %s, %s, %s, %s);"""
    insert_batch("celestial_photometric_data", insert_photometric_query, photometric_data)
    '''
    # Insert data into celestial_observation_runs
    observation_run_data = [(row['run_ID'], row['rerun_ID'], row['cam_col'], row['field_ID']) for _, row in df.iterrows()]
    insert_observation_run_query = """INSERT INTO celestial_observation_runs (run_ID, rerun_ID, cam_col, field_ID)
                                    VALUES (%s, %s, %s, %s)
                                    ON DUPLICATE KEY UPDATE rerun_ID=VALUES(rerun_ID), cam_col=VALUES(cam_col), field_ID=VALUES(field_ID);"""
    insert_batch("celestial_observation_runs", insert_observation_run_query, observation_run_data)
    '''
    # Insert data into celestial_spectroscopic_data
    cursor.execute("SELECT obj_ID, id FROM celestial_object;")
    obj_id_to_id = {obj_id: id for obj_id, id in cursor.fetchall()}

    spectroscopic_data = [(row['spec_obj_ID'], row['plate'], row['MJD'], row['fiber_ID'], obj_id_to_id[row['obj_ID']]) for _, row in df.iterrows()]
    insert_spectroscopic_query = """INSERT INTO celestial_spectroscopic_data (spec_obj_ID, plate, MJD, fiber_ID)
                                    VALUES (%s, %s, %s, %s);"""
    insert_batch("celestial_spectroscopic_data", insert_spectroscopic_query, spectroscopic_data)
    
except pymysql.MySQLError as e:
    print("Error in database operation:", e)

finally:
    # Close database connection
    if dbconn:
        dbconn.close()
        print("Database connection closed.")