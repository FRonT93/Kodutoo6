import streamlit as st
import requests
import pandas as pd
from io import StringIO
import json
import geopandas as gpd
import matplotlib.pyplot as plt

st.title("Loomulik iive Eesti maakondades")

STATISTIKAAMETI_API_URL = "https://andmed.stat.ee/api/v1/et/stat/RV032"

JSON_PAYLOAD_STR = """ {
"query": [
    {
      "code": "Aasta",
      "selection": {
        "filter": "item",
        "values": [
          "2014",
          "2015",
          "2016",
          "2017",
          "2018",
          "2019",
          "2020",
          "2021",
          "2022",
          "2023"
        ]
      }
    },
    {
      "code": "Maakond",
      "selection": {
        "filter": "item",
        "values": [
          "39",
          "44",
          "49",
          "51",
          "57",
          "59",
          "65",
          "67",
          "70",
          "74",
          "78",
          "82",
          "84",
          "86",
          "37"
        ]
      }
    },
    {
      "code": "Sugu",
      "selection": {
        "filter": "item",
        "values": [
          "2",
          "3"
        ]
      }
    }
  ],
  "response": {
    "format": "csv"
  }
}
"""

geojson = "maakonnad.geojson"

def import_data():
    headers = {"Content-Type": "application/json"}
    parsed_payload = json.loads(JSON_PAYLOAD_STR)

    response = requests.post(
        STATISTIKAAMETI_API_URL,
        json=parsed_payload,
        headers=headers
    )

    if response.status_code == 200:
        text = response.content.decode("utf-8-sig")
        df = pd.read_csv(StringIO(text))
        return df
    else:
        st.error(f"Viga andmete laadimisel: {response.status_code}")
        st.write(response.text)
        return pd.DataFrame()

def import_geojson():
    gdf = gpd.read_file(geojson)
    return gdf

df = import_data()
gdf = import_geojson()

st.write("Andmete eelvaade:")
st.write(df.head())

aastad = sorted(df["Aasta"].unique())
valitud_aasta = st.sidebar.selectbox("Vali aasta", aastad)

df_aasta = df[df["Aasta"] == valitud_aasta]

# Kui sama maakonna kohta on mitu rida, liidame väärtused kokku
df_aasta["Loomulik iive"] = df_aasta["Mehed Loomulik iive"] + df_aasta["Naised Loomulik iive"]
df_aasta = df_aasta.groupby("Maakond", as_index=False)["Loomulik iive"].sum()
# Ühendame kaardiandmed ja Statistikaameti andmed
kaart = gdf.merge(df_aasta, on="Maakond", how="left")

fig, ax = plt.subplots(1, 1, figsize=(12, 8))

kaart.plot(
    column="Loomulik iive",
    ax=ax,
    legend=True,
    cmap="viridis",
    legend_kwds={"label": "Loomulik iive"}
)

ax.set_title(f"Loomulik iive maakonniti aastal {valitud_aasta}")
ax.axis("off")

st.pyplot(fig)
