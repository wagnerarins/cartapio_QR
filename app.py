import re
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Cardápio Digital", page_icon="🍔", layout="centered"
)


# Converter links do Google Drive para links diretos de imagem
def converter_link_drive(url):
  url = str(url).strip()
  if "drive.google.com" in url:
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", url) or re.search(
        r"id=([a-zA-Z0-9_-]+)", url
    )
    if match:
      file_id = match.group(1)
      return f"https://lh3.googleusercontent.com/d/{file_id}"
  return url


# Carrega a URL do CSV da planilha configurada nos Secrets do Streamlit
try:
  sheet_url = st.secrets["LINK_PLANILHA"]
except:
  sheet_url = "URL_DO_SEU_CSV_PUBLICO_AQUI"


@st.cache_data(ttl=10)
def carregar_dados(url):
  return pd.read_csv(url)


try:
  df = carregar_dados(sheet_url)
except Exception as e:
  st.error("Erro ao carregar a base de dados.")
  st.stop()

# Captura parâmetro de URL (ex: ?cliente=caravaggio)
query_params = st.query_params
cliente_atual = query_params.get("cliente")

if not cliente_atual:
  st.warning(
      "Olá! Por favor, acesse o cardápio lendo o QR Code do estabelecimento."
  )
  st.stop()

# Filtra produtos apenas do cliente atual
df_cliente = df[
    df["Id_Cliente"].astype(str).str.lower() == str(cliente_atual).lower()
]

if df_cliente.empty:
  st.error("Ops! Cardápio não encontrado ou estabelecimento inativo.")
  st.stop()

# Cabeçalho do estabelecimento
nome_loja = df_cliente["Nome"].iloc[0]
st.title(f"🍔 {nome_loja}")
st.markdown("---")

# Agrupa por categoria
categorias = df_cliente["Categoria"].dropna().unique()

for cat in categorias:
  st.header(cat)
  df_cat = df_cliente[df_cliente["Categoria"] == cat]

  for index, linha in df_cat.iterrows():
    st.subheader(str(linha.get("Item", "Produto")))

    descricao = str(linha.get("Descrição", ""))
    if pd.notna(linha.get("Descrição")) and descricao.lower() != "nan":
      st.write(descricao)

    st.markdown(f"**R$ {float(linha.get('Preço', 0)):.2f}**")

    # Tratamento da imagem
    url_bruta = (
        str(linha.get("img", "")).strip()
        if pd.notna(linha.get("img", ""))
        else ""
    )
    url_imagem = converter_link_drive(url_bruta)

    if url_imagem and url_imagem.lower() not in ["0", "nan", ""]:
      try:
        st.image(url_imagem, use_container_width=True)
      except:
        pass

    st.markdown("---")
