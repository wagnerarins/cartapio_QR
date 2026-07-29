import streamlit as st
import pandas as pd
import re

# Configuração visual do aplicativo
st.set_page_config(page_title="Cardápio Digital", layout="centered")

# Busca o link da planilha com segurança no cofre do Streamlit
try:
    LINK_PLANILHA = st.secrets["LINK_PLANILHA"]
except KeyError:
    st.error("Erro de configuração: adicione 'LINK_PLANILHA' nos Secrets do Streamlit.")
    st.stop()

# Função que converte links do Google Drive para links diretos de imagem
def converter_link_drive(url):
    if pd.isna(url) or not isinstance(url, str):
        return None
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if match:
        file_id = match.group(1)
        return f"https://lh3.googleusercontent.com/d/{file_id}"
    return url

@st.cache_data(ttl=30)  # Atualiza as informações a cada 30 segundos
def carregar_dados():
    return pd.read_csv(LINK_PLANILHA)

try:
    df = carregar_dados()

    # Título principal baseado na primeira linha do estabelecimento
    nome_estabelecimento = df['Estabelecimento'].iloc[0] if not df.empty else "Cardápio Digital"
    st.title(f"🍔 {nome_estabelecimento}")
    st.markdown("---")

    # Renderiza a lista de produtos
    for index, linha in df.iterrows():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(linha['Produto'])
            if pd.notna(linha['Descrição']):
                st.write(linha['Descrição'])
            st.write(f"**R$ {float(linha['Preço']):.2f}**")
        
        with col2:
            img_url = converter_link_drive(linha['link/img'])
            if img_url:
                st.image(img_url, use_container_width=True)
                
        st.markdown("---")

except Exception as e:
    st.error("Carregando cardápio... Verifique se a planilha está acessível.")
