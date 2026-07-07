# Connects to MySQL database, loads geographic and language data form the table 
# school_lang_geo, and generates an interactive choropleth map showing the percentage 
# of students taught in foreign languages across countries using Plotly.

# %%
import mysql.connector
import sqlalchemy
from sqlalchemy import create_engine, text
from mysql.connector import Error
from getpass import getpass
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
from shapely.ops import unary_union
from matplotlib.patches import Patch
import json
from shapely.geometry import mapping
import plotly.graph_objects as go
from pathlib import Path
import webbrowser
import plotly.express as px
from IPython.display import IFrame, display
from shapely import wkt
from shapely.geometry import Polygon, MultiPolygon

# %%
user = "brutalist"
password = getpass("MySQL password: ")
database = "my_database_2"

engine = create_engine(f"mysql+pymysql://{user}:{password}@localhost/{database}")

try:
    with engine.connect() as conn:
        # Wrap query in text() function
        result = conn.execute(text("SELECT '✅ Connection successful' AS status"))
        print(result.scalar())  # Fetch the first column of first row
except Exception as e:
    print(f"❌ Connection failed: {e}")

# %%
query = "SELECT * FROM school_lang_geo"

# %%
df = pd.read_sql(query, engine)

# %%
df = df[df['name'] != 'Antarctica']

# %%
# edit to fix scattered map
def fix_geometry(geom):
    """Fix invalid geometries without removing structure"""
    if geom is None or geom.is_empty:
        return geom
    
    # Only fix if invalid
    if not geom.is_valid:
        geom = geom.buffer(0)
    
    return geom

# %%
# Convert df to GeoDataFrame and fix geometries BEFORE creating plot dataframes
df['geometry'] = df['geometry_wkt'].apply(wkt.loads)
df['geometry'] = df['geometry'].apply(fix_geometry)
df = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")

# %%
# Fix Crimea geography

# Load admin boundaries for Crimea adjustment
admin1 = gpd.read_file(
    "https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_1_states_provinces.zip"
)

mask = admin1['name_en'].str.contains('Crimea', case=False, na=False)
crimea_raw = admin1.loc[mask, 'geometry'].union_all()

crimea = (
    gpd.GeoSeries([crimea_raw], crs=admin1.crs)
       .to_crs(df.crs)
       .iloc[0]
       .buffer(0)
)

# Remove Crimea from Russia's geometry
df.loc[df['name']=='Russia', 'geometry'] = (
    df.loc[df['name']=='Russia', 'geometry']
          .apply(lambda g: g.difference(crimea).buffer(0))
)

# Add Crimea to Ukraine's geometry
df.loc[df['name']=='Ukraine', 'geometry'] = (
    df.loc[df['name']=='Ukraine', 'geometry']
          .apply(lambda g: g.union(crimea))
)

# Clean up Russia's geometry (remove small artifacts)
russia_parts = df.loc[df['name']=='Russia', 'geometry'].explode(index_parts=False)
min_area = 0.10
large_parts = [part for part in russia_parts if part.area > min_area]
clean_russia = unary_union(large_parts)
df.loc[df['name']=='Russia', 'geometry'] = clean_russia

# %%
# Fix Baikonur - merge with Kazakhstan
if 'Baikonur' in df['name'].values:
    # Get Baikonur's geometry
    baikonur_geom = df.loc[df['name']=='Baikonur', 'geometry'].union_all()
    
    # Add Baikonur to Kazakhstan's geometry
    df.loc[df['name']=='Kazakhstan', 'geometry'] = (
        df.loc[df['name']=='Kazakhstan', 'geometry']
              .apply(lambda g: g.union(baikonur_geom))
    )
    
    # Remove Baikonur as a separate entity
    df = df[df['name'] != 'Baikonur']
    
    print("✅ Baikonur merged with Kazakhstan")
else:
    print("ℹ️ Baikonur not found in data")

# %%
# Prepare data for all levels (keep geometry fixes intact)
# Get unique countries with their fixed geometries
world_df = df[["name", "geometry"]].drop_duplicates("name").copy()
world = gpd.GeoDataFrame(world_df, geometry="geometry", crs="EPSG:4326")

print(f"Total countries before filtering: {len(world)}")

# %%
# Load disputed areas to fix Somalia/Somaliland
disputed = gpd.read_file(
    "https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_0_disputed_areas.zip"
)

# Merge Somalia and Somaliland geometries for unified display
somalia = world.loc[world['name']=='Somalia', 'geometry']
somaliland = disputed.loc[disputed['NAME']=='Somaliland', 'geometry']

if len(somalia) > 0 and len(somaliland) > 0:
    somaliland = somaliland.to_crs(world.crs)
    full_somalia = unary_union(list(somalia) + list(somaliland))
    world.loc[world['name']=='Somalia', 'geometry'] = full_somalia
    
    # Remove Somaliland as a separate entity (already merged above)
    world = world[world['name'] != 'Somaliland']

# %%
# SIMPLIFY GEOMETRIES - drastically reduce complexity for performance
# Tolerance of 0.1 degrees is fine for world maps
print("Simplifying geometries...")
world['geometry'] = world['geometry'].simplify(tolerance=0.05, preserve_topology=True)

# Remove very small islands/territories (below 0.01 square degrees ~ tiny islands)
print("Filtering out tiny islands...")
world = world[world.geometry.area > 0.01].copy()

print(f"Countries after filtering: {len(world)}")

# Keep in WGS84 (EPSG:4326) - Plotly will handle the projection
# Do NOT project to Equal Earth here - let Plotly do it
print("Keeping geometries in WGS84 for Plotly...")

# Create GeoJSON AFTER all filtering and modifications
world_geojson = json.loads(world.to_json())
print(f"\nBase layer has {len(world_geojson['features'])} geometries")

# %%
# Prepare efficient data structure for each education level
levels = {
    'early grades': 'Early Grades',
    'end of prim': 'End of Primary',
    'lower sec': 'Lower Secondary'
}

# For each level, create a lookup of country -> value (not full geometries)
level_data = {}
for level_key, level_label in levels.items():
    # Filter data for this level
    level_df = df[df["level"].eq(level_key)].copy()
    
    # Create dictionary: country -> (value, year)
    data_dict = {}
    for _, row in level_df.iterrows():
        data_dict[row['name']] = {
            'value': row['taught_in_foreign'],
            'year': int(row['year']) if pd.notna(row['year']) else None
        }
    
    level_data[level_key] = data_dict
    print(f"{level_label}: {len(data_dict)} countries with data")

# %%
# Create interactive Plotly map with dropdown menu (optimized)
fig = go.Figure()

# DIAGNOSTIC VERSION - replace your loop temporarily
for idx, (level_key, level_label) in enumerate(levels.items()):
    data_dict = level_data[level_key]
    
    z_values = []
    hover_text = []
    customdata = []
    
    for i, feature in enumerate(world_geojson['features']):
        country_name = feature['properties']['name']
        
        if country_name in data_dict:
            value = data_dict[country_name]['value']
            year = data_dict[country_name]['year']
            
            if pd.notna(value):
                z_values.append(value)
                pct = f"{value:.1f}%"
                year_str = str(year) if year else "N/A"
                hover_text.append(f"<b>{country_name}</b><br>Foreign Language: {pct}<br>Year: {year_str}")
            else:
                z_values.append(-0.001)
                hover_text.append(f"<b>{country_name}</b><br>No data")
        else:
            z_values.append(0.0001)
            hover_text.append(f"<b>{country_name}</b><br>No data")
    
    # Add choropleth for this level
    fig.add_trace(go.Choropleth(
        geojson=world_geojson,
        locations=[f['properties']['name'] for f in world_geojson['features']],
        featureidkey="properties.name",
        z=z_values,
        customdata=customdata,
        colorscale=[
            [0.00000, '#B5AFA8'],  # no data (sentinel at zmin)
            [0.00099, '#B5AFA8'],  # keep grey flat
            [0.00100, '#FFF0A0'],  # jump to real scale at 0
            [0.25, '#F5C842'],   # saffron yellow
            [0.5,  '#D4880D'],   # burnt amber
            [0.75, '#8B5A2B'],   # warm chestnut
            [1,    '#5C3317'],   # dark tobacco — was espresso, now this is your ceiling
        ],
        zmin=-0.001,
        zmax=100,
        marker_line_color='white',
        marker_line_width=0.5,
        hovertemplate='%{hovertext}<extra></extra>',
        hovertext=hover_text,
        colorbar=dict(
            orientation="h",
            thickness=12,
            len=0.55,
            x=0.5,
            xanchor="center",
            y=-0.01,
            yanchor="top",
            tickmode="array",
            tickvals=[0, 20, 40, 60, 80, 100],
            ticktext=["0", "20", "40", "60", "80", "100"],
            title=dict(text="")  # move title to annotation (left side)
        ),
        visible=(idx == 0),  # Only first level visible initially
        name=level_label,
        # Style countries without data as light grey
        zauto=False,
        marker=dict(
            line=dict(color='white', width=0.5),
        )
    ))

# Create dropdown menu buttons
buttons = []
for idx, (level_key, level_label) in enumerate(levels.items()):
    visibility = [False] * len(levels)
    visibility[idx] = True
    
    buttons.append(dict(
        label=f"<b>{level_label}<b>",
        method="update",
        args=[{"visible": visibility}],
    ))

# Update layout
fig.update_geos(
    projection_type="equal earth",
    showcoastlines=False,
    showland=False,
    showcountries=False,
    fitbounds="locations",
    bgcolor='#F5F0E8',
    showframe=False,
    lataxis=dict(range=[-55, 65]),
    lonaxis=dict(range=[-145, 165])
)

fig.update_layout(
    title=dict(
        text="Percentage of Students Taught in Foreign Language",
        x=0.5,
        xanchor='center',
        y=0.975,
        yanchor='top',
        font=dict(size=18)
    ),
    updatemenus=[
        dict(
            buttons=buttons,
            direction="down",
            showactive=True,
            x=0.02,
            xanchor="left",
            y=0.99,
            yanchor="top",
            bgcolor="#EDEAE5",
            bordercolor="#666666",
            borderwidth=1,
            font=dict(size=13),
            pad=dict(t=20, b=5, l=10, r=10),  # Padding inside the dropdown
        )
    ],
    annotations=[
        dict(
            text="<b>% of Students<br>Taught in Foreign<br>Language</b>",
            x=0.22, y=-0.04, xref="paper", yref="paper",
            showarrow=False, xanchor="right", yanchor="middle",
            font=dict(size=12, color="black")
        ),
        dict(
            text="<b>No Data</b>",
            x=0.8, y=-0.04, xref="paper", yref="paper",
            showarrow=False, xanchor="left", yanchor="middle",
            bgcolor="#B5AFA8", bordercolor="grey", borderwidth=1, borderpad=4,
            font=dict(size=11, color="black")
        )
    ],
    height=800,
    margin=dict(l=0, r=0, t=40, b=70),
    paper_bgcolor='#EDE3D3',
    hoverlabel=dict(
    bgcolor="#F0F0F0",
    font=dict(
        size=14,
        family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif",
        color="black",
        )
    ),
)

open_full_page_button_script = """
<style>
  #open-fullpage-btn{
    position: fixed;
    top: 12px;
    right: 30px;
    z-index: 9999;
    box-sizing: border-box;
    padding: 8px 10px;
    font: 14px/1.2 Arial, sans-serif;
    background: rgba(255,255,255,0.85);
    border: 1px solid rgba(0,0,0,0.25);
    border-radius: 6px;
    cursor: pointer;
  }
  #open-fullpage-btn:hover{
    background: rgba(255,255,255,0.98);
  }
</style>

<button id=\"open-fullpage-btn\" type=\"button\" title=\"Open in a new tab\">
  Open full page ↗
</button>

<script>
(function () {
  const btn = document.getElementById('open-fullpage-btn');
  if (!btn) return;

  const embedded = (window.self !== window.top);
  if (!embedded) {
    btn.style.display = 'none';
    return;
  }

  btn.addEventListener('click', function () {
    window.open(window.location.href, '_blank', 'noopener');
  });
})();
</script>
<script>
(function () {
  function isEmbedded() {
    try { return window.self !== window.top; } catch(e) { return true; }
  }

  function applyResponsiveHeight() {
    var gd = document.querySelector('.js-plotly-plot');
    if (!gd) return;

    var h = isEmbedded() ? 600 : 800;   // embed vs full page
    Plotly.relayout(gd, {height: h}).then(function () {
      document.body.style.overflow = isEmbedded() ? 'hidden' : 'auto';
    });  
  }

  window.addEventListener('load', applyResponsiveHeight);
  window.addEventListener('resize', applyResponsiveHeight);
})();
</script>
"""

plot_html = fig.to_html(full_html=True, include_plotlyjs='cdn', config={'displayModeBar': False, 'responsive': True})
html = plot_html.replace("</body>", open_full_page_button_script + "</body>")

output_path = Path("school_lang_map_final.html")
output_path.write_text(html, encoding="utf-8")
webbrowser.open(output_path.resolve().as_uri())

fig.show()