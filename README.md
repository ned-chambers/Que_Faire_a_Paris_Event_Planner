# 📊 *Que Faire à Paris?* - Interactive outing planner dashboard

## 📖 About the Project
*Que Faire à Paris?* is an interactive dashboard designed to help users explore and plan their outings in Paris.

This tool combines a map of events, trend analyses, and interactive features to personalise the user experience.

Our goal is to simplify cultural exploration in Paris by providing an accessible and visually engaging platform. Discover current events, analyse trends, and plan your outings at a glance.

---

## 🗺️ How to Use
- **Interactive Map**: Explore events near you or in a specific arrondissement.
- **Dynamic Filters**: Refine your searches by date, category, price, accessibility, or audience.
- **Direct Links**: Click on an event to access additional details or make reservations.

---

## 🛠️ Technology Stack & ETL Pipeline
The project leverages a robust ETL (Extract, Transform, Load) pipeline, culminating in an interactive Tableau dashboard:

1. **Extract**: Event data is sourced daily from the [Paris Open Data platform](https://opendata.paris.fr/explore/dataset/que-faire-a-paris-/).
2. **Transform**: Data is cleaned and standardised using Python, applying operations such as:
   - Normalising column names and formats
   - Handling missing data
   - Enhancing accessibility information
   - Splitting and validating geolocation data
3. **Load**: The cleaned data is loaded into a **PostgreSQL database**, hosted on **Koyeb**.
4. **Visualise**: The transformed data powers a **Tableau** dashboard, enabling dynamic exploration.

The ETL process is orchestrated using **Apache Airflow** within a **Docker container**. For details on each step, refer to the `dag_que_faire_a_paris.py` script.

---

## 🏗️ Developed By
This project was created by **Ned Chambers** and **Jean-Baptiste Allombert** as part of their final project in the *Data Analyst Lead* program at **Jedha Bootcamp** in February 2025.

---

## 📊 Data Source
The event data in this dashboard is provided by the Open Data platform of the City of Paris:  
[https://opendata.paris.fr/explore/dataset/que-faire-a-paris-/](https://opendata.paris.fr/explore/dataset/que-faire-a-paris-/)

Data is updated daily to ensure accuracy and freshness.

---

## ❤️ Thank You!
We hope this dashboard enriches your Parisian experience and inspires you to discover all the amazing events the City of Light has to offer.

---

## ✉️ Feedback
We would love to hear your suggestions or comments to improve this dashboard. Feel free to contact us at:  
📧 **ned.chambers@gmail.com**
