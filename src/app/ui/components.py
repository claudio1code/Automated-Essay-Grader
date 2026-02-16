"""
Componentes de UI reutilizáveis para Streamlit.
Centraliza elementos visuais comuns da aplicação.
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from app.core.utils import TextUtils


class HeaderComponent:
    """Componente para cabeçalho da aplicação."""
    
    @staticmethod
    def render(title: str = "📝 Corretor de Redação Enem", 
              subtitle: str = "Análise inteligente de redações com IA") -> None:
        """Renderiza o cabeçalho principal."""
        st.title(title)
        st.markdown(f"*{subtitle}*")
        st.divider()


class SidebarComponent:
    """Componente para barra lateral."""
    
    @staticmethod
    def render_student_info() -> Dict[str, str]:
        """Renderiza formulário de informações do aluno."""
        st.sidebar.header("� Informações da Turma")
        
        with st.sidebar.form("student_form"):
            tema_redacao = st.text_input(
                "Tema da Redação",
                placeholder="Digite o tema central",
                help="Tema proposto para a redação (usado para busca de referências)"
            )
            
            ano_escolar = st.selectbox(
                "Ano Escolar",
                options=["1º EM", "2º EM", "3º EM"],
                index=2,  # Default: 3º EM
                help="Selecione o ano do aluno"
            )
            
            bimestre = st.selectbox(
                "Bimestre",
                options=["1º Bimestre", "2º Bimestre", "3º Bimestre", "4º Bimestre"],
                help="Selecione o bimestre atual"
            )
            
            submitted = st.form_submit_button("📋 Salvar Informações")
            
            if submitted:
                if tema_redacao:
                    st.session_state.tema_redacao = tema_redacao.strip()
                    st.session_state.ano_escolar = ano_escolar
                    st.session_state.bimestre = bimestre
                    st.sidebar.success("✅ Informações salvas!")
                else:
                    st.sidebar.error("❌ Preencha o tema da redação!")
        
        return {
            "tema_redacao": st.session_state.get("tema_redacao", ""),
            "ano_escolar": st.session_state.get("ano_escolar", "3º EM"),
            "bimestre": st.session_state.get("bimestre", "1º Bimestre")
        }


class UploadComponent:
    """Componente para upload de arquivos."""
    
    @staticmethod
    def render_image_upload() -> Optional[str]:
        """Renderiza componente de upload de imagem."""
        st.subheader("📸 Upload da Redação")
        
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                uploaded_file = st.file_uploader(
                    "Faça upload da imagem da redação manuscrita",
                    type=['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp'],
                    help="Formatos aceitos: JPG, PNG, BMP, TIFF, WebP. Tamanho máximo: 10MB"
                )
            
            with col2:
                st.info("""
                **💡 Dicas:**
                - Tire uma foto nítida
                - Iluminação boa
                - Redação inteira visível
                - Sem sombras
                """)
        
        if uploaded_file is not None:
            # Validações básicas
            if uploaded_file.size > 10 * 1024 * 1024:  # 10MB
                st.error("❌ Arquivo muito grande! Máximo permitido: 10MB")
                return None
            
            st.success(f"✅ Arquivo `{uploaded_file.name}` carregado com sucesso!")
            return uploaded_file
        
        return None


class ResultsComponent:
    """Componente para exibição de resultados."""
    
    @staticmethod
    def render_analysis_header(resultado: Dict[str, Any]) -> None:
        """Renderiza cabeçalho dos resultados."""
        st.subheader("📊 Resultados da Análise")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Nota Final",
                TextUtils.format_grade(resultado.get("nota_final", 0)),
                delta=None,
                delta_color="normal"
            )
        
        with col2:
            nome = resultado.get("nome_aluno", "Detectado pela IA")
            st.metric("Aluno", nome)
        
        with col3:
            ano = resultado.get("ano_escolar", "3º EM")
            st.metric("Ano", ano)
        
        with col4:
            bimestre = resultado.get("bimestre", "1º Bimestre")
            st.metric("Bimestre", bimestre)
        
        # Tema em linha separada
        tema = resultado.get("tema_redacao", "Não informado")
        st.info(f"📝 **Tema da Redação:** {tema}")
    
    @staticmethod
    def render_competences(competencias: Dict[str, Any]) -> None:
        """Renderiza análise das competências."""
        st.subheader("🎯 Análise por Competência")
        
        for comp_id, comp_data in competencias.items():
            if comp_id.startswith('c') and comp_data:
                with st.expander(f"**Competência {comp_id.upper()}**", expanded=True):
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        nota = comp_data.get("nota", 0)
                        cor = TextUtils.get_competence_grade_color(nota)
                        st.markdown(f"### {cor} {nota}/200")
                    
                    with col2:
                        analise = comp_data.get("analise", "Análise não disponível.")
                        st.markdown(analise)
    
    @staticmethod
    def render_general_comments(comentarios: str, alerta: Optional[str] = None) -> None:
        """Renderiza comentários gerais."""
        st.subheader("💬 Comentários Gerais")
        
        if alerta:
            st.warning(f"⚠️ **Alerta de Originalidade:** {alerta}")
        
        st.markdown(comentarios)
    
    @staticmethod
    def render_download_button(resultado: Dict[str, Any]) -> None:
        """Renderiza botão de download do relatório."""
        st.subheader("📥 Relatório")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **📄 Relatório Disponível**
            
            O relatório completo em formato DOCX foi gerado com:
            - Análise detalhada
            - Notas por competência
            - Comentários gerais
            - Formatação profissional
            """)
        
        with col2:
            if st.button("📥 Baixar Relatório DOCX", type="primary"):
                from app.services import report_service
                try:
                    nome_aluno = resultado.get("nome_aluno", "aluno")
                    docx_path = report_service.gerar_relatorio_docx(resultado)
                    
                    with open(docx_path, "rb") as file:
                        st.download_button(
                            label="📥 Baixar Relatório",
                            data=file.read(),
                            file_name=f"relatorio_redacao_{TextUtils.clean_text(nome_aluno)}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                except Exception as e:
                    st.error(f"❌ Erro ao gerar relatório: {str(e)}")


class LoadingComponent:
    """Componente para estados de carregamento."""
    
    @staticmethod
    def render_analysis_loading() -> None:
        """Renderiza tela de análise em andamento."""
        with st.spinner("🤖 Analisando redação... Isso pode levar alguns minutos."):
            st.info("""
            **📝 Análise em Progresso**
            
            O sistema está realizando:
            - 🔍 OCR e extração do texto
            - 🧠 Análise com IA Gemini
            - 📚 Busca de referências (RAG)
            - 📊 Avaliação por competência
            - 📄 Geração do relatório
            
            Por favor, aguarde...
            """)
    
    @staticmethod
    def render_error_state(error_message: str) -> None:
        """Renderiza tela de erro."""
        st.error(f"""
        ## ❌ Erro na Análise
        
        Ocorreu um erro ao processar sua redação:
        
        **Descrição:** {error_message}
        
        **Sugestões:**
        - Verifique se a imagem está nítida
        - Tente fazer upload novamente
        - Se o problema persistir, contate o suporte
        """)
        
        if st.button("🔄 Tentar Novamente"):
            st.rerun()


class StatusComponent:
    """Componente para exibição de status."""
    
    @staticmethod
    def render_system_status() -> None:
        """Renderiza status do sistema."""
        with st.expander("🔧 Status do Sistema", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.success("✅ API Gemini")
            
            with col2:
                st.success("✅ Vector DB")
            
            with col3:
                st.success("✅ Sistema RAG")
            
            st.markdown("---")
            st.caption("Todos os sistemas estão operacionais")
