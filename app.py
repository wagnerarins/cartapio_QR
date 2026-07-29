import streamlit as st
import pandas as pd
import re

# Configurações da página
st.set_page_config(page_title="Cardápio Digital", layout="centered")

# Link formatado em CSV da sua planilha DB_cardapio_QR
LINK_PLANILHA = "https://docs.google.com/spreadsheets/d/1tqUZ_jP7qw7TsEs6gjB5m_l_fgmpExaZhnYnAUuEXug/export?format=csv"

# Converte o link de visualização do Google Drive em link direto de imagem
def converter_link_drive(url):
    if pd.isna(url) or not isinstance(url, str):
        return None
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if match:
        file_id = match.group(1)
        return f"https://lh3.googleusercontent.com/d/{file_id}"
    return url

@st.cache_data(ttl=30)  # Atualiza os dados a cada 30 segundos
def carregar_dados():
    return pd.read_csv(LINK_PLANILHA)

try:
    df = carregar_dados()

    # Define o título do estabelecimento
    nome_estabelecimento = df['Estabelecimento'].iloc[0] if not df.empty else "Cardápio Digital"
    st.title(f"🍔 {nome_estabelecimento}")
    st.markdown("---")

    # Renderiza os produtos
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
    st.error("Carregando cardápio... Se persistir, verifique a planilha.")
