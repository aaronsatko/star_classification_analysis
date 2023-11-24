# Star Classification Data Analysis Project

## Overview

This project aims to explore and analyze a dataset of celestial objects and their classifications. Utilizing skills developed over the semester, the project focuses on data importing with PyMySQL, extensive data analysis, and effective data presentation. The goal is to derive meaningful insights from the star classification data and present these findings in an accessible and visually appealing format.

## Project Components

### Database Creation

After conducting extensive testing with various database designs for my star classification project, I have concluded that utilizing a single table, named celestial_observations, is the most effective approach. This decision came from a thorough examination of multi-table structures versus a consolidated single-table schema.

A primary advantage of the single-table design is the simplification of the query process. With all relevant data housed in one table, the complexity of constructing and executing queries is significantly reduced. There's no need for elaborate joins or intricate relational mappings that are common with multi-table designs. Since every entry in the database relates to one specific celestial observation, a multi table database would have every table be one-to-one mapped which serves no real purpose in my use case.

Each row in the celestial_observations table represents a distinct observation. This one-to-one correspondence between rows and observations ensures clarity and directness in the relationship of data points, which enhances both the readability and interpretability of the data. It also assists in maintaining a clean and organized dataset where each piece of information is easily accessible.

In addition to structural efficiency, I made a strategic choice to streamline the dataset further by removing columns that were not pertinent to my analysis. This step of pruning unnecessary data fields helps in focusing on relevant data, reducing storage requirements, and improving the performance of data operations.

The single-table design, complemented by a carefully curated dataset, aligns perfectly with the nature of the star classification data. Typically, queries in this domain require a holistic view, where each attribute of an observation is crucial. Therefore, this approach not only simplifies database management but also ensures that the database system is optimized for effective data retrieval and analysis in the star classification project.

### Data Importing

    Tool Used: PyMySQL
    Description: Data will be imported into a MySQL database using PyMySQL. This process includes establishing a connection to the database, creating tables, and efficiently loading the dataset.

### Data Analysis

    Tools Used: Python (Pandas, NumPy, etc.)
    Description: Data analysis will be performed using Python libraries. This phase involves data cleaning, manipulation, and exploration to uncover patterns and insights in the celestial data.



https://www.kaggle.com/datasets/fedesoriano/stellar-classification-dataset-sdss17

