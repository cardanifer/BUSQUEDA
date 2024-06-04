import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

def get_academic_articles(keyword, num_results=10):
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
        year = "N/A"
        for part in author_year.split(" - ")[1:]:
            if part.strip().isdigit():
                year = part.strip()
                break

        articles.append({"Author": author, "Title": title, "Link": link, "Year": year})

    return pd.DataFrame(articles).sort_values(by='Year', ascending=False)

st.title("Búsqueda de Artículos Académicos")
keyword = st.text_input("Ingrese la palabra clave para buscar artículos académicos:")

if st.button("Buscar"):
    if keyword:
        with st.spinner("Buscando artículos..."):
            try:
                num_results = 10
                df = get_academic_articles(keyword, num_results)
                file_name = "articulos_academicos.xlsx"
                df.to_excel(file_name, index=False)
                st.success("Búsqueda completada!")

                for i, row in df.iterrows():
                    st.markdown(f"**{row['Title']}**")
                    st.markdown(f"Autor: {row['Author']}")
                    st.markdown(f"Enlace: [{row['Link']}]({row['Link']})")
                    st.markdown("---")

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
