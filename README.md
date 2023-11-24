# Star Classification Data Analysis Project

## Overview

This project aims to explore and analyze a dataset of celestial objects and their classifications. The focus is on data importing with PyMySQL, extensive data analysis, and effective data presentation. The goal is to derive meaningful insights from the star classification data and present these findings in an accessible and visually appealing format.

The data used in this project was sourced from Kaggle: Stellar Classification Dataset - SDSS17
https://www.kaggle.com/datasets/fedesoriano/stellar-classification-dataset-sdss17

## Dependencies

The project relies on several external Python libraries:

    pandas: For reading and manipulating data in a DataFrame format.
    configparser: To manage database configurations.
    PyMySQL: For establishing a connection with the MySQL database and executing SQL statements.
    tqdm: To provide a progress meter during data insertion.

## Project Components

### Database Creation

Utilizing a single table, named celestial_observations, was identified as the most effective approach for the star classification project. This decision was based on a comparison of multi-table structures versus a single-table schema.

Key advantages:

    Simplified query process without the need for complex joins or relational mappings.
    Direct correspondence between each row and a celestial observation, enhancing data clarity and organization.
    Removal of non-essential columns to focus on relevant data, reducing storage requirements and improving data operation performance.

The single-table design is well-suited for queries requiring a holistic view of each celestial observation.

### Data Importing

The data was imported into a MySQL database using Python. The process included:

    Reading 'star_classification.csv' into a pandas DataFrame.
    Selecting essential columns: 'obj_ID', 'alpha', 'delta', 'u', 'g', 'r', 'i', 'z', 'spec_obj_ID', 'class', 'redshift', 'plate', and 'MJD'.
    Employing a batch insertion method with PyMySQL's executemany method.
    Using tqdm for progress visualization during the data insertion.

### Data Analysis

    Tools Used: Python (Pandas, NumPy, etc.)
    Description: Data analysis will be performed using Python libraries for data cleaning, manipulation, and exploration to uncover patterns and insights in the celestial data.

## Interesting Queries

### Computes the average values for the ultraviolet, green, red, near-infrared, and infrared filters for each class of celestial object.

SELECT class, AVG(u) AS avg_ultraviolet, AVG(g) AS avg_green, AVG(r) AS avg_red, AVG(i) AS avg_near_infrared, AVG(z) AS avg_infrared
FROM celestial_observations
GROUP BY class;


### Identify the celestial objects with the highest redshift values to find the farthest or oldest objects.

SELECT *
FROM celestial_observations
ORDER BY redshift DESC
LIMIT 10;


### Analyze the distribution of observations across different plates.

SELECT plate, COUNT(*) AS observation_count
FROM celestial_observations
GROUP BY plate;


### Compare the average redshift values between galaxies, stars, and quasars.

SELECT class, AVG(redshift) AS average_redshift
FROM celestial_observations
GROUP BY class;


### Count how many of each class of object (galaxy, star, quasar) are in the dataset.

SELECT class, COUNT(*) AS frequency
FROM celestial_observations
GROUP BY class;


### Explore any apparent correlation between redshift and the measurements in different filters.

SELECT redshift, AVG(u) AS avg_u, AVG(g) AS avg_g, AVG(r) AS avg_r, AVG(i) AS avg_i, AVG(z) AS avg_z
FROM celestial_observations
GROUP BY redshift;
