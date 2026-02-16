"""
Aplicação principal do Corretor de Redação AI.
Interface Streamlit refatorada e profissional.
"""

import streamlit as st
from app.ui.pages import (
    IndividualCorrectionPage, 
    BatchCorrectionPage, 
    HistoryPage, 
    SettingsPage
)
from app.core.logger import get_logger

# Configuração da página (DEVE ser o primeiro comando Streamlit)
st.set_page_config(
    layout="wide", 
    page_title="Corretor de Redação Enem", 
    page_icon="📝",
    initial_sidebar_state="expanded"
)

logger = get_logger(__name__)


def main():
    """Função principal da aplicação."""
    try:
        # Menu de navegação
        st.sidebar.title("📝 Corretor de Redação")
        st.sidebar.markdown("---")
        
        page_names = {
            "📝 Correção Individual": IndividualCorrectionPage,
            "📁 Correção em Lote": BatchCorrectionPage,
            "📚 Histórico": HistoryPage,
            "⚙️ Configurações": SettingsPage
        }
        
        selected_page = st.sidebar.selectbox(
            "Selecione uma página:",
            list(page_names.keys()),
            index=0
        )
        
        # Renderiza página selecionada
        page_class = page_names[selected_page]
        page_instance = page_class()
        page_instance.render()
        
        # Rodapé
        st.sidebar.markdown("---")
        st.sidebar.markdown(
            """
            **🤖 Corretor de Redação AI**
            
            Versão 2.0 | Powered by Gemini
            
            ---
            *Desenvolvido com ❤️ para educação*
            """
        )
        
    except Exception as e:
        logger.error(f"Erro na aplicação principal: {str(e)}")
        st.error(f"""
        ## ❌ Erro Crítico
        
        Ocorreu um erro inesperado na aplicação:
        
        **Erro:** {str(e)}
        
        **Soluções:**
        1. Recarregue a página
        2. Verifique os logs do sistema
        3. Contate o suporte técnico
        
        Se o problema persistir, execute:
        ```bash
        make-docker logs
        ```
        """)
        
        if st.button("🔄 Recarregar Página"):
            st.rerun()


if __name__ == "__main__":
    main()
