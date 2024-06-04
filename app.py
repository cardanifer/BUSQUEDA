import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

def get_academic_articles(keyword, num_results=10, year_range=None):
    base_url = "https://scholar.google.com/scholar"
    params = {"q": keyword, "hl": "en"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }

    response = requests.get(base_url, params=params, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    articles = []

    for entry in soup.select(".gs_ri")[:num_results]:
        title_tag = entry.select_one(".gs_rt a")
        title = title_tag.text if title_tag else "N/A"
        link = title_tag['href'] if title_tag else "N/A"

        author_year_tag = entry.select_one(".gs_a")
        author_year = author_year_tag.text if author_year_tag else "N/A"
        author = author_year.split(" - ")[0]

        # Extraer el año correctamente
        year = "N/A"
        for part in author_year.split(" - ")[1:]:
            if part.strip().isdigit():
                year = part.strip()
                break

        # Filtrar por rango de años
        if year_range:
            if not year.isdigit() or int(year) < year_range[0] or int(year) > year_range[1]:
                continue

        articles.append({"Author": author, "Title": title, "Link": link, "Year": year})

    return pd.DataFrame(articles)

st.title("Búsqueda de Artículos Académicos")
keyword = st.text_input("Ingrese la palabra clave para buscar artículos académicos:")

st.sidebar.title("Filtros de Búsqueda")
start_year = st.sidebar.number_input("Año de inicio:", min_value=2000, max_value=2024, step=1, value=2000)
end_year = st.sidebar.number_input("Año de fin:", min_value=2000, max_value=2024, step=1, value=2024)

if st.button("Buscar"):
    if keyword:
        with st.spinner("Buscando artículos..."):
            try:
                num_results = 10
                year_range = (start_year, end_year) if start_year <= end_year else None
                df = get_academic_articles(keyword, num_results, year_range=year_range)
                file_name = "articulos_academicos.xlsx"
                df.to_excel(file_name, index=False)
                st.success("Búsqueda completada!")
                st.dataframe(df)

                with open(file_name, "rb") as file:
                    btn = st.download_button(
                        label="Descargar archivo Excel",
                        data=file,
                        file_name=file_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"Ha ocurrido un error: {e}")
    else:
        st.warning("Debe ingresar una palabra clave")
