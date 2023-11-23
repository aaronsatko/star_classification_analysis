# Star Classification Data Analysis Project

## Overview

This project aims to explore and analyze a dataset of celestial objects and their classifications. Utilizing skills developed over the semester, the project focuses on data importing with PyMySQL, extensive data analysis, and effective data presentation. The goal is to derive meaningful insights from the star classification data and present these findings in an accessible and visually appealing format.

## Project Components

### Data Importing

    Tool Used: PyMySQL
    Description: Data will be imported into a MySQL database using PyMySQL. This process includes establishing a connection to the database, creating tables, and efficiently loading the dataset.

### Data Analysis

    Tools Used: Python (Pandas, NumPy, etc.)
    Description: Data analysis will be performed using Python libraries. This phase involves data cleaning, manipulation, and exploration to uncover patterns and insights in the celestial data.



https://www.kaggle.com/datasets/fedesoriano/stellar-classification-dataset-sdss17


CREATE TABLE CelestialObject (
    obj_ID BIGINT PRIMARY KEY,
    alpha DECIMAL(10, 7),
    delta DECIMAL(10, 7)
);

CREATE TABLE Observation (
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

CREATE TABLE Classification (
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