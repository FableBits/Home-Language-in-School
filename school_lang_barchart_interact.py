# Connects to MySQL database, loads learning assessments performance data form the table 
# wide_simple, and generates an interactive barchart showing the performance of students 
# in different subjects and levels, based on whether they speak the school language at 
# home or not, using Plotly.


# %%
import mysql.connector
import sqlalchemy
from sqlalchemy import create_engine, text
from mysql.connector import Error
from getpass import getpass
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from pathlib import Path
import webbrowser
import ipywidgets as widgets
from IPython.display import display, clear_output

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
query = "SELECT * FROM wide_simple"

# %%
df = pd.read_sql(query, engine)

# %%
# Make a working copy
plot_df = df.copy()

# --- 1) Standardize column names (optional but safer) ---
plot_df.columns = [c.strip() for c in plot_df.columns]

# --- 2) Clean key filter columns ---
filter_cols = ["level"]

for col in filter_cols:
    if col in plot_df.columns:
        # convert to string only where not null, trim spaces
        plot_df[col] = plot_df[col].astype("string").str.strip()

        # turn empty strings into NA
        plot_df[col] = plot_df[col].replace("", pd.NA)

# --- 3) Normalize language values to Yes / No only
plot_df["language"] = (
    plot_df["language"]
    .str.lower()
    .replace({
        "yes": "Yes",
        "no": "No"
    })
)

# Keep only rows where language is Yes/No
plot_df = plot_df[plot_df["language"].isin(["Yes", "No"])].copy()

# --- 4) Ensure score columns are numeric ---
score_cols = [
    "mlevel1_m","mlevel2_m","mlevel3_m","mlevel4_m",
    "rlevel1_m","rlevel2_m","rlevel3_m","rlevel4_m",
    "slevel1_m","slevel2_m","slevel3_m","slevel4_m"
]

for c in score_cols:
    if c in plot_df.columns:
        plot_df[c] = pd.to_numeric(plot_df[c], errors="coerce")

print("✅ Step 1 done")
print("Rows:", len(plot_df))
print("Language values:", plot_df["language"].dropna().unique())
print("Level values:", plot_df["level"].dropna().unique())

# %%
def apply_filters(
    data,
    level_selected                  # required (no "All")
):
    dff = data.copy()

    # Required filter
    dff = dff[dff["level"] == level_selected]

    return dff

# %%
test_df = apply_filters(
    plot_df,
    level_selected="early grades"
)

print("Filtered rows:", len(test_df))
print("Language split:")
print(test_df["language"].value_counts(dropna=False))

# %%
# Columns we need for the chart
metric_cols = [
    "rlevel1", "rlevel2", "rlevel3", "rlevel4",
    "mlevel1", "mlevel2", "mlevel3", "mlevel4",
    "slevel1", "slevel2", "slevel3", "slevel4",
]

# 1) Mean by language (Yes/No)
means_wide = (
    test_df
    .groupby("language", dropna=False)[metric_cols]
    .mean()
    .reset_index()
)

# 2) Wide -> long
plot_long = means_wide.melt(
    id_vars="language",
    value_vars=metric_cols,
    var_name="metric",
    value_name="avg_score"
)

# 3) Parse subject + achievement level from metric names
plot_long["subject_code"] = plot_long["metric"].str[0]         # r, m, s
plot_long["ach_level_num"] = plot_long["metric"].str.extract(r"[rms]level(\d)").astype(int)

# 4) Human-readable labels
subject_map = {"r": "Reading", "m": "Mathematics", "s": "Science"}
ach_map = {
    1: "Level 1 (Low proficiency)",
    2: "Level 2 (Minimium proficiency)",
    3: "Level 3 (Medium proficiency)",
    4: "Level 4 (High proficiency)",
}

plot_long["subject"] = plot_long["subject_code"].map(subject_map)
plot_long["achievement_level"] = plot_long["ach_level_num"].map(ach_map)

# 5) Keep a stable plotting order
plot_long["subject"] = pd.Categorical(
    plot_long["subject"],
    categories=["Reading", "Mathematics", "Science"],
    ordered=True
)
plot_long["ach_level_num"] = pd.Categorical(
    plot_long["ach_level_num"],
    categories=[1, 2, 3, 4],
    ordered=True
)

# Optional rounding for display
plot_long["avg_score"] = plot_long["avg_score"].round(2)

print("✅ Step 3 done")
print(plot_long.head(4))

# %%
plot_long.groupby(["subject", "achievement_level", "language"], observed=True)["avg_score"].first()

# %%
# Create plot fig
# -----------------------------
# Helper: build plot_long from filtered df
# -----------------------------
def build_plot_long(dff):
    metric_cols = [
        "rlevel1", "rlevel2", "rlevel3", "rlevel4",
        "mlevel1", "mlevel2", "mlevel3", "mlevel4",
        "slevel1", "slevel2", "slevel3", "slevel4",
    ]

    means_wide = (
        dff.groupby("language", dropna=False)[metric_cols]
        .mean()
        .reset_index()
    )

    pl = means_wide.melt(
        id_vars="language",
        value_vars=metric_cols,
        var_name="metric",
        value_name="avg_score"
    )

    # Parse subject + level from avg_rlevel1 style
    pl["subject_code"] = pl["metric"].str.extract(r"([rms])level", expand=False)
    pl["ach_level_num"] = pl["metric"].str.extract(r"level(\d)", expand=False).astype(int)

    subject_map = {"r": "Reading", "m": "Mathematics", "s": "Science"}
    ach_map = {
        1: "Level 1 (Low proficiency)",
        2: "Level 2 (Minimum proficiency)",
        3: "Level 3 (Medium proficiency)",
        4: "Level 4 (High proficiency)",
    }

    pl["subject"] = pl["subject_code"].map(subject_map)
    pl["achievement_level"] = pl["ach_level_num"].map(ach_map)

    pl["subject"] = pd.Categorical(
        pl["subject"],
        categories=["Reading", "Mathematics", "Science"],
        ordered=True
    )
    pl["ach_level_num"] = pd.Categorical(
        pl["ach_level_num"],
        categories=[1, 2, 3, 4],
        ordered=True
    )

    pl["avg_score"] = pl["avg_score"].round(2)
    return pl


# -----------------------------
# Helper: add 6 traces (3 subjects x 2 language) for one education level
# -----------------------------
def add_level_traces(fig, pl, visible=False):
    subjects = ["Reading", "Mathematics", "Science"]
    level_labels = {
        1: "Low Proficiency",
        2: "Minimum Proficiency",
        3: "Medium Proficiency",
        4: "High Proficiency"
    }
    color_map = {"Yes": "#D4880D", "No": "#5C3317"}

    for row_i, subj in enumerate(subjects, start=1):
        sub = pl[pl["subject"] == subj].copy()
        x_vals = [level_labels[k] for k in [1, 2, 3, 4]]

        for lang in ["Yes", "No"]:
            d = sub[sub["language"] == lang].sort_values("ach_level_num")

            fig.add_trace(
                go.Bar(
                    x=x_vals,
                    y=d["avg_score"],
                    name=lang,
                    marker_color=color_map[lang],
                    legendgroup=lang,
                    showlegend=(row_i == 1),  # one legend block only
                    visible=visible,
                    hovertemplate=(
                        f"Speaks School Language At Home: <b>{lang}</b><br>"
                        "Average Performance: <b>%{y:.2f}%</b><br>"
                        "<extra></extra>"
                    ),
                ),
                row=row_i, col=1
            )


# -----------------------------
# Build figure with one trace-set per 'level' value
# -----------------------------
level_values = ["early grades", "end of primary", "end of lower secondary"]

fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=False,
    vertical_spacing=0.10,
    subplot_titles=["Reading", "Mathematics", "Science"]
)

# Add traces block-by-block for each education level
for i, lvl in enumerate(level_values):
    dff_lvl = apply_filters(plot_df, level_selected=lvl)
    pl_lvl = build_plot_long(dff_lvl)
    add_level_traces(fig, pl_lvl, visible=(i == 0))  # first level visible

# -----------------------------
# Dropdown: toggle visibility per level block
# Each level contributes exactly 6 traces (3 subjects x 2 languages)
# -----------------------------
# Replace traces_per_level / total_traces
traces_per_level = 6
total_traces = len(level_values) * traces_per_level

level_label_map = {
    "early grades": "Early Grades",
    "end of primary": "End of Primary",
    "end of lower secondary": "Lower Secondary",
}

buttons = []
for i, lvl in enumerate(level_values):
    vis = [False] * total_traces
    start = i * traces_per_level
    end = start + traces_per_level
    for j in range(start, end):
        vis[j] = True

    buttons.append(
        dict(
            label=f"<b>{level_label_map[lvl]}<b>",
            method="update",
            args=[
                {"visible": vis},
                {"title": {
                    "text":f"Learning Achievements by Language Familiarity",
                    "x":0.5,
                    "xanchor": "center",
                    "y": 0.98,
                    "font": {"size": 18}
                }}
            ]
        )
    )

fig.update_layout(
    barmode="group",
    height=950,
    template="plotly_white",
    plot_bgcolor = "#F5F0E8",
    paper_bgcolor = "#EDE3D3",
    title=dict(
        text=f"Learning Achievements by Language Familiarity",
        x=0.5,
        y=0.98,
        font=dict(size=18)
    ),
    legend=dict(
        title="Speaks School Language At Home",
        orientation="h",
        x=0.5,
        y=1.12,
        xanchor="center",
        font=dict(size=14)
    ),
    updatemenus=[
        dict(
            buttons=buttons,
            direction="down",
            x=0, xanchor="left",
            y=1.08, yanchor="top",
            showactive=True,
            bgcolor="#EDEAE5",
            bordercolor="#666666",
            borderwidth=1,
            font=dict(size=13),
            pad=dict(t=20, b=5, l=10, r=10),
        )
    ],
    margin=dict(l=70, r=30, t=150, b=60),
    hoverlabel=dict(
    bgcolor="#F0F0F0",
    font=dict(
        size=14,
        family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif",
        color="black",
    )
),
)

for r in [1, 2, 3]:
    fig.update_yaxes(range=[0, 100], row=r, col=1)

fig.update_yaxes(title_text="Average Learning Assessment Performance (%)", row=2, col=1)

fig.update_xaxes(title_text="Achievement Level", row=3, col=1)

# --- Save to HTML with JavaScript for Pointer Cursor and Full-page Button ---
output_file = "school_lang_bars_final.html"

html_string = fig.to_html(
    include_plotlyjs="cdn",
    full_html=True,
    config={"displayModeBar": False, "scrollZoom": False},
)

html_enhancements = """
<style>
  #open-fullpage-btn {
    position: fixed;
    top: 12px;
    right: 12px;
    z-index: 9999;
    padding: 8px 10px;
    font: 14px/1.2 Arial, sans-serif;
    background: rgba(255,255,255,0.85);
    border: 1px solid rgba(0,0,0,0.25);
    border-radius: 6px;
    cursor: pointer;
  }

  #open-fullpage-btn:hover {
    background: rgba(255,255,255,0.98);
  }
</style>

<button id="open-fullpage-btn" type="button" title="Open in a new tab">
  Open full page ↗
</button>

<script>
window.addEventListener('load', function () {
    const plotDiv = document.querySelector('.plotly-graph-div');
    const btn = document.getElementById('open-fullpage-btn');
    
    if (!plotDiv) return;

    function setOverlayCursor(value) {
        plotDiv.querySelectorAll('.draglayer rect, .draglayer path').forEach(function (el) {
            el.style.cursor = value;
        });
    }

    setOverlayCursor('default');

    plotDiv.on('plotly_hover', function () {
        setOverlayCursor('pointer');
    });

    plotDiv.on('plotly_unhover', function () {
        setOverlayCursor('default');
    });

    plotDiv.on('plotly_afterplot', function () {
        setOverlayCursor('default');
    });

    if (btn) {
        const embedded = (window.self !== window.top);

        if (!embedded) {
            btn.style.display = 'none';
        } else {
            btn.addEventListener('click', function () {
                window.open(window.location.href, '_blank', 'noopener');
            });
        }
    }
});
</script>
"""

html_string = html_string.replace('</body>', html_enhancements + '</body>')

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_string)

webbrowser.open(output_file)

print(f"Saved to: {output_file}")

fig.show()