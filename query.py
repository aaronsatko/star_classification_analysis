import pymysql
import configparser
import logging
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd

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

# Create directory for plots if it doesn't exist
plots_dir = "query_generated_plots"
os.makedirs(plots_dir, exist_ok=True)

# Visualization functions for each query
# Query 1
def plot_avg_stddev_by_class(result):
    classes = [row[0] for row in result]
    averages = { 'U': [row[1] for row in result], 'G': [row[3] for row in result], 'R': [row[5] for row in result], 'I': [row[7] for row in result], 'Z': [row[9] for row in result] }
    stddevs = { 'U': [row[2] for row in result], 'G': [row[4] for row in result], 'R': [row[6] for row in result], 'I': [row[8] for row in result], 'Z': [row[10] for row in result] }
    
    filter_colors = {'U': 'blue', 'G': 'green', 'R': 'red', 'I': 'darkred', 'Z': '#800020'}

    plt.figure(figsize=(12, 6))
    for i, (filter_name, avg_values) in enumerate(averages.items()):
        x_positions = [x + i*0.1 for x in range(len(classes))]  # Offset x positions for each filter
        plt.bar(x_positions, avg_values, width=0.1, yerr=stddevs[filter_name], label=f'{filter_name} Filter', color=filter_colors[filter_name])
    
    plt.xticks(range(len(classes)), classes)
    plt.xlabel('Class')
    plt.ylabel('Average Value')
    plt.title('Average and Stddev of Filters by Class')
    plt.legend()
    
    # save
    plot_filename = os.path.join(plots_dir, 'avg_stddev_by_class.png')
    plt.savefig(plot_filename)
    plt.show()

# Query 2
def plot_highest_redshift(result):
    object_ids = [row[0] for row in result]
    redshifts = [row[-2] for row in result]

    plt.figure(figsize=(10, 6))
    sns.barplot(x=object_ids, y=redshifts)
    plt.xticks(rotation=45)
    plt.xlabel('Object ID')
    plt.ylabel('Redshift')
    plt.title('Top 10 Celestial Objects with Highest Redshift')
    plt.tight_layout()

    plot_filename = os.path.join(plots_dir, 'highest_redshift.png')
    plt.savefig(plot_filename)
    plt.show()
        
# Query 3
def plot_distribution_across_plates(result):
    plates = [row[0] for row in result]
    observation_counts = [row[1] for row in result]

    # Sort the result based on observation counts to ensure top 10 are first
    sorted_results = sorted(zip(plates, observation_counts), key=lambda x: x[1], reverse=True)
    plates, observation_counts = zip(*sorted_results)

    # Split into top 10 and bottom 10 based on sorted observation counts
    top_10_plates = plates[:10]
    bottom_10_plates = plates[-10:]

    df = pd.DataFrame({'Plate': plates, 'Observation Count': observation_counts})

    # Define colors for each bar
    colors = ['green' if plate in top_10_plates else 'red' for plate in df['Plate']]

    plt.figure(figsize=(10, 6))
    sns.barplot(x='Plate', y='Observation Count', data=df, palette=colors, order=df['Plate'])
    plt.xticks(rotation=45)
    plt.xlabel('Plate')
    plt.ylabel('Number of Observations')
    plt.title('Top 10 and Bottom 10 Plates by Observation Count')
    plt.legend([],[], frameon=False)  # Hide the legend
    plt.tight_layout()

    plot_filename = os.path.join(plots_dir, 'plates_distribution.png')
    plt.savefig(plot_filename)
    plt.show()

# Query 4
def plot_avg_redshift_comparison(result):
    classes = [row[0] for row in result]
    avg_redshifts = [row[1] for row in result]

    plt.figure(figsize=(10, 6))
    sns.barplot(x=classes, y=avg_redshifts)
    plt.xlabel('Class')
    plt.ylabel('Average Redshift')
    plt.title('Average Redshift Values Comparison')
    plt.tight_layout()

    plot_filename = os.path.join(plots_dir, 'avg_redshift_comparison.png')
    plt.savefig(plot_filename)
    plt.show()
    
# Query 5
def plot_class_count_and_avg_values(result):
    classes = [row[0] for row in result]
    frequencies = [row[1] for row in result]

    plt.figure(figsize=(10, 6))
    sns.barplot(x=classes, y=frequencies)
    plt.xlabel('Class')
    plt.ylabel('Frequency')
    plt.title('Frequency of Each Class')
    plt.tight_layout()

    plot_filename = os.path.join(plots_dir, 'class_frequency.png')
    plt.savefig(plot_filename)
    plt.show()

# Predefined queries
predefined_queries = {
    1: ("Average and Standard Deviation for Each Filter by Class",
        """SELECT class, AVG(u) AS avg_ultraviolet, STDDEV(u) AS stddev_ultraviolet, 
           AVG(g) AS avg_green, STDDEV(g) AS stddev_green, AVG(r) AS avg_red, 
           STDDEV(r) AS stddev_red, AVG(i) AS avg_near_infrared, 
           STDDEV(i) AS stddev_near_infrared, AVG(z) AS avg_infrared, 
           STDDEV(z) AS stddev_infrared 
           FROM celestial_observations GROUP BY class"""),
    2: ("Celestial Objects with Highest Redshift",
        """SELECT *, plate 
            FROM celestial_observations 
            ORDER BY redshift 
            DESC LIMIT 10"""),
    3: ("Distribution of Observations Across Different Plates",
        """(SELECT plate, COUNT(*) AS observation_count, 'Top 10' AS category
           FROM celestial_observations 
           GROUP BY plate 
           ORDER BY observation_count 
           DESC LIMIT 10)
           UNION ALL
           (Select plate, COUNT(*) AS observation_count, 'Bottom 10' AS category
           FROM celestial_observations
           GROUP BY plate
           ORDER BY observation_count ASC
           LIMIT 10)"""),
    4: ("Average Redshift Values Comparison",
        """SELECT class, AVG(redshift) AS average_redshift, MIN(redshift) AS min_redshift, 
           MAX(redshift) AS max_redshift 
           FROM celestial_observations 
           GROUP BY class"""),
    5: ("Count and Average Values for Each Class",
        """SELECT class, COUNT(*) AS frequency, AVG(u) AS avg_u, AVG(g) AS avg_g, 
           AVG(r) AS avg_r, AVG(i) AS avg_i, AVG(z) AS avg_z 
           FROM celestial_observations 
           GROUP BY class""")
}

def select_query():
    print("Select a predefined query:")
    for key in predefined_queries:
        print(f"{key}: {predefined_queries[key][0]}")
    choice = int(input("Enter the number of the query you want to execute: "))
    print("")
    selected_query = predefined_queries.get(choice, (None, None))[1]
    return choice, selected_query

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

    choice, query = select_query()
    if query:
        cursor.execute(query)
        result = cursor.fetchall()
        format_and_print_result(result)
        if choice == 1:
            plot_avg_stddev_by_class(result)
        elif choice == 2:
            plot_highest_redshift(result)
        elif choice == 3:
            plot_distribution_across_plates(result)
        elif choice == 4:
            plot_avg_redshift_comparison(result)
        elif choice == 5:
            plot_class_count_and_avg_values(result)

except pymysql.MySQLError as e:
    error_message = f"Error connecting to the database: {e}"
    print(error_message)
    logging.error(error_message)

finally:
    if dbconn:
        dbconn.close()
        print("Database connection closed.")