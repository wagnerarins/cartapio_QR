import pandas as pd
import streamlit as st

st.set_page_config(page_title="Cardápio Digital", page_icon="🍔", layout="centered")

# Pega o link da planilha configurado nos secrets do Streamlit
try:
    sheet_url = st.secrets["LINK_PLANILHA"]
except:
    # Se der erro, coloque sua URL do CSV direto aqui entre as aspas
    sheet_url = "URL_DO_SEU_CSV_AQUI"

@st.cache_data(ttl=10) # Atualiza o cache a cada 10 segundos
def carregar_dados(url):
    return pd.read_csv(url)

try:
    df = carregar_dados(sheet_url)
except Exception as e:
    st.error("Erro ao carregar a base de dados.")
    st.stop()

# Captura qual é o cliente pelo link (ex: site.app/?cliente=Caravaggio)
query_params = st.query_params
cliente_atual = query_params.get("cliente")

if not cliente_atual:
    st.warning("Olá! Por favor, acesse o cardápio lendo o QR Code do estabelecimento.")
    st.stop()

# Filtra a planilha inteira para mostrar SÓ as linhas desse cliente
# O .str.lower() garante que "Caravaggio" e "caravaggio" funcionem igual
df_cliente = df[df['Id_Cliente'].astype(str).str.lower() == str(cliente_atual).lower()]

if df_cliente.empty:
    st.error("Ops! Cardápio não encontrado ou estabelecimento inativo.")
    st.stop()

# Monta o Cabeçalho com o nome do estabelecimento (Pega da coluna 'Nome')
nome_loja = df_cliente["Nome"].iloc[0]
st.title(f"🍔 {nome_loja}")
st.markdown("---")

# Separa os produtos por Categoria (ex: Aperitivos, Bebidas, etc)
categorias = df_cliente['Categoria'].dropna().unique()

for cat in categorias:
    st.header(cat)
    # Filtra os itens apenas daquela categoria
    df_cat = df_cliente[df_cliente['Categoria'] == cat]
    
    for index, linha in df_cat.iterrows():
        st.subheader(str(linha.get("Item", "Produto")))
        
        # Mostra a descrição apenas se ela existir
        descricao = str(linha.get("Descrição", ""))
        if pd.notna(linha.get("Descrição")) and descricao.lower() != "nan":
             st.write(descricao)
             
        # Formata o preço
        st.markdown(f"**R$ {float(linha.get('Preço', 0)):.2f}**")

        # Tratamento da imagem
        url_imagem = str(linha.get("img", "")).strip() if pd.notna(linha.get("img", "")) else ""
        if url_imagem and url_imagem.lower() not in ["0", "nan", ""]:
            try:
                st.image(url_imagem, use_container_width=True)
            except:
                pass

        st.markdown("---")
