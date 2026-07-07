# Home Language in School

An analysis of UNESCO's Institiute of Statistics (UIS) and World Inequality Database on Education (WIDE) data, exploring the relationship between students' home language and their academic performance and distribution across countries.

## What This Project Does

This project processes UNESCO education data through SQL and Python to produce two interactive visualisations:

- **Choropleth Map** — shows the geographic distribution of students who speak a different language at home than the one used in school, across countries worldwide.
- **Bar Chart** — compares learning assessment performance between students who speak the school language at home and those who don't, highlighting the gap across countries.

## Files

| File | Description |
|------|-------------|
| `school_lang_map.sql` | SQL script that prepares and structures the geographic data used for the choropleth map |
| `school_lang_bars.sql` | SQL script that processes UNESCO's `wide_2026.csv` assessment data for the bar chart |
| `school_lang_map_interact.py` | Python script that connects to a MySQL database and renders the interactive choropleth map using Plotly |
| `school_lang_barchart_interact.py` | Python script that connects to a MySQL database and renders the interactive barchart using Plotly |

## D

[UNESCO Institiute of Statistics (UIS)](https://databrowser.uis.unesco.org/)
[UNESCO World Inequality Database on Education (WIDE)](https://www.education-inequalities.org/)

## Requirements

- Python 3.x
- MySQL database with the relevant tables loaded
- Python packages: `pandas`, `geopandas`, `plotly`, `sqlalchemy`, `shapely`, `matplotlib`

## Usage

1. Load the SQL scripts into your MySQL database to prepare the data tables.
2. Run `school_lang_map_interact.py` and enter your MySQL password when prompted.
3. The interactive map will open in your browser.