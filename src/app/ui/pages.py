"""
Páginas principais da aplicação Streamlit.
Organiza as diferentes telas e funcionalidades.
"""

import streamlit as st
import tempfile
import os
from typing import Optional, Dict, Any

from .components import (
    HeaderComponent, SidebarComponent, UploadComponent, 
    ResultsComponent, LoadingComponent, StatusComponent
)
from app.services import ai_service, report_service
from app.core.validators import FileValidator, TextValidator, ValidationException
from app.core.exceptions import IAException, ReportException
from app.core.utils import FileUtils, ImageUtils


class IndividualCorrectionPage:
    """Página para correção individual de redações."""
    
    def __init__(self):
        self.prompt_mestre = None
        self._initialize_services()
    
    def _initialize_services(self) -> None:
        """Inicializa serviços da aplicação."""
        try:
            ai_service.configurar_ia()
            
            if "prompt_mestre" not in st.session_state:
                st.session_state["prompt_mestre"] = ai_service.carregar_prompt()
            
            self.prompt_mestre = st.session_state["prompt_mestre"]
            
        except Exception as e:
            st.error(f"❌ Erro na inicialização: {str(e)}")
            st.stop()
    
    def render(self) -> None:
        """Renderiza a página principal."""
        HeaderComponent.render()
        
        # Barra lateral
        student_info = SidebarComponent.render_student_info()
        
        # Status do sistema
        StatusComponent.render_system_status()
        
        # Upload da imagem
        uploaded_file = UploadComponent.render_image_upload()
        
        # Processamento
        if uploaded_file and student_info["tema_redacao"]:
            self._process_essay(uploaded_file, student_info)
        elif uploaded_file:
            st.warning("⚠️ Preencha o tema da redação na barra lateral para continuar.")
    
    def _process_essay(self, uploaded_file, student_info: Dict[str, str]) -> None:
        """Processa a redação enviada."""
        try:
            # Validações
            TextValidator.validate_theme(student_info["tema_redacao"])
            
            # Salva arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_path = tmp_file.name
            
            try:
                # Valida e otimiza imagem
                FileValidator.validate_image_file(temp_path)
                FileValidator.validate_file_size(temp_path, max_size_mb=10)
                
                optimized_path = ImageUtils.validate_and_optimize_image(temp_path)
                
                # Análise
                LoadingComponent.render_analysis_loading()
                
                resultado = ai_service.analisar_redacao(
                    optimized_path, 
                    self.prompt_mestre,
                    student_info["tema_redacao"]
                )
                
                if resultado:
                    # Adiciona informações da turma (nome será detectado pela IA)
                    resultado["tema_redacao"] = student_info["tema_redacao"]
                    resultado["ano_escolar"] = student_info["ano_escolar"]
                    resultado["bimestre"] = student_info["bimestre"]
                    
                    # Exibe resultados
                    self._display_results(resultado)
                else:
                    st.error("❌ Não foi possível analisar a redação. Tente novamente.")
                
            finally:
                # Limpeza
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                if 'optimized_path' in locals() and os.path.exists(optimized_path):
                    os.unlink(optimized_path)
        
        except ValidationException as e:
            st.error(f"❌ Validação: {str(e)}")
        except IAException as e:
            st.error(f"❌ Erro na análise: {str(e)}")
        except Exception as e:
            LoadingComponent.render_error_state(str(e))
    
    def _display_results(self, resultado: Dict[str, Any]) -> None:
        """Exibe os resultados da análise."""
        # Cabeçalho dos resultados
        ResultsComponent.render_analysis_header(resultado)
        
        # Análise por competência
        competencias = resultado.get("analise_competencias", {})
        ResultsComponent.render_competences(competencias)
        
        # Comentários gerais
        comentarios = resultado.get("comentarios_gerais", "")
        alerta = resultado.get("alerta_originalidade")
        ResultsComponent.render_general_comments(comentarios, alerta)
        
        # Download do relatório
        ResultsComponent.render_download_button(resultado)


class BatchCorrectionPage:
    """Página para correção em lote."""
    
    def render(self) -> None:
        """Renderiza página de correção em lote."""
        st.header("📁 Correção em Lote")
        
        tab1, tab2 = st.tabs(["📁 Google Drive", "💻 Arquivos Locais"])
        
        with tab1:
            self._render_drive_correction()
        
        with tab2:
            self._render_local_correction()
    
    def _render_drive_correction(self) -> None:
        """Renderiza correção via Google Drive."""
        st.subheader("📁 Correção via Google Drive")
        
        with st.form("drive_form"):
            st.info("""
            **📋 Instruções:**
            1. Cole as URLs das pastas do Google Drive
            2. Configure as informações da turma
            3. Clique em iniciar para processar todas as redações
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                input_folder = st.text_input(
                    "📥 Pasta de Entrada",
                    placeholder="https://drive.google.com/drive/folders/ID_DA_PASTA",
                    help="Pasta onde estão as imagens das redações"
                )
            
            with col2:
                output_folder = st.text_input(
                    "📤 Pasta de Saída",
                    placeholder="https://drive.google.com/drive/folders/ID_DA_PASTA", 
                    help="Pasta onde os relatórios serão salvos"
                )
            
            # Informações da turma
            st.markdown("---")
            st.markdown("**📓 Informações da Turma:**")
            
            col3, col4 = st.columns(2)
            with col3:
                tema_lote = st.text_input(
                    "Tema da Redação",
                    placeholder="Digite o tema central",
                    help="Tema aplicado a todas as redações"
                )
            
            with col4:
                ano_escolar = st.selectbox(
                    "Ano Escolar",
                    options=["1º EM", "2º EM", "3º EM"],
                    index=2
                )
            
            bimestre = st.selectbox(
                "Bimestre",
                options=["1º Bimestre", "2º Bimestre", "3º Bimestre", "4º Bimestre"],
                index=0
            )
            
            submitted = st.form_submit_button("🚀 Iniciar Correção em Lote")
            
            if submitted and input_folder and output_folder and tema_lote:
                batch_info = {
                    "input_folder": input_folder,
                    "output_folder": output_folder,
                    "tema": tema_lote,
                    "ano": ano_escolar,
                    "bimestre": bimestre
                }
                self._process_drive_correction(batch_info)
            elif submitted:
                st.error("❌ Preencha todos os campos obrigatórios!")
    
    def _render_local_correction(self) -> None:
        """Renderiza correção de arquivos locais."""
        st.subheader("💻 Correção de Arquivos Locais")
        
        st.info("""
        **📋 Instruções:**
        1. Clique no botão para selecionar a pasta
        2. Escolha a pasta com as imagens
        3. Configure as informações da turma
        4. Inicie o processamento
        """)
        
        if st.button("📂 Selecionar Pasta Local"):
            # Implementar seleção de pasta local
            st.warning("⚠️ Funcionalidade em desenvolvimento")
    
    def _process_drive_correction(self, batch_info: Dict[str, str]) -> None:
        """Processa correção via Google Drive."""
        try:
            from app.services.drive_service import GoogleDriveService
            from app.core.validators import DriveValidator
            from app.core.utils import TextUtils
            
            # Validar URLs
            input_id = DriveValidator.validate_folder_id(batch_info["input_folder"])
            output_id = DriveValidator.validate_folder_id(batch_info["output_folder"])
            
            # Inicializar serviço
            drive_service = GoogleDriveService()
            
            # Criar container para progresso
            progress_container = st.container()
            
            with progress_container:
                st.subheader("🔄 Processando Correção em Lote")
                
                # Barra de progresso
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Etapa 1: Listar arquivos
                status_text.text("📋 Listando arquivos na pasta de entrada...")
                files = drive_service.list_files(input_id, image_extensions=['.jpg', '.jpeg', '.png', '.bmp'])
                
                if not files:
                    st.error("❌ Nenhum arquivo de imagem encontrado na pasta de entrada!")
                    return
                
                total_files = len(files)
                st.info(f"📁 Encontrados {total_files} arquivos para processar")
                
                # Etapa 2: Processar cada arquivo
                results = []
                for i, file_info in enumerate(files):
                    progress_bar.progress((i + 1) / (total_files + 1))
                    status_text.text(f"📝 Processando arquivo {i+1}/{total_files}: {file_info['name']}")
                    
                    try:
                        # Download do arquivo
                        file_content = drive_service.download_file(file_info['id'])
                        
                        # Salvar temporariamente
                        import tempfile
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                            tmp_file.write(file_content)
                            temp_path = tmp_file.name
                        
                        # Analisar redação
                        resultado = ai_service.analisar_redacao(
                            temp_path,
                            self.prompt_mestre,
                            batch_info["tema"]
                        )
                        
                        if resultado:
                            # Adicionar informações do lote
                            resultado["tema_redacao"] = batch_info["tema"]
                            resultado["ano_escolar"] = batch_info["ano"]
                            resultado["bimestre"] = batch_info["bimestre"]
                            
                            # Gerar relatório
                            docx_path = report_service.gerar_relatorio_docx(resultado)
                            
                            # Upload para pasta de saída
                            with open(docx_path, "rb") as docx_file:
                                output_name = f"relatorio_{TextUtils.clean_text(resultado.get('nome_aluno', 'aluno'))}.docx"
                                drive_service.upload_file(
                                    output_id,
                                    output_name,
                                    docx_file.read(),
                                    mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                )
                            
                            results.append({
                                "file": file_info['name'],
                                "status": "✅ Sucesso",
                                "output": output_name
                            })
                        else:
                            results.append({
                                "file": file_info['name'],
                                "status": "❌ Falha na análise",
                                "output": None
                            })
                        
                        # Limpar arquivo temporário
                        import os
                        os.unlink(temp_path)
                        
                    except Exception as e:
                        logger.error(f"Erro ao processar arquivo {file_info['name']}: {str(e)}")
                        results.append({
                            "file": file_info['name'],
                            "status": f"❌ Erro: {str(e)}",
                            "output": None
                        })
                
                # Etapa 3: Resultados finais
                progress_bar.progress(1.0)
                status_text.text("✅ Processamento concluído!")
                
                st.success(f"🎉 Correção em lote concluída! {len([r for r in results if 'Sucesso' in r['status']])} arquivos processados com sucesso.")
                
                # Tabela de resultados
                st.subheader("📊 Resultados do Processamento")
                results_df = []
                for result in results:
                    results_df.append({
                        "Arquivo": result["file"],
                        "Status": result["status"],
                        "Relatório Gerado": result["output"] if result["output"] else "❌"
                    })
                
                st.dataframe(results_df, use_container_width=True)
                
        except Exception as e:
            logger.error(f"Erro na correção em lote: {str(e)}")
            st.error(f"❌ Erro na correção em lote: {str(e)}")
            
            if "credentials" in str(e).lower():
                st.error("🔑 **Problema de autenticação:** Verifique se as credenciais do Google Drive estão configuradas corretamente.")
            elif "access" in str(e).lower() or "permission" in str(e).lower():
                st.error("🔒 **Problema de permissão:** Verifique se as pastas estão compartilhadas com a conta de serviço.")


class HistoryPage:
    """Página para histórico de correções."""
    
    def render(self) -> None:
        """Renderiza página de histórico."""
        st.header("📚 Histórico de Correções")
        
        st.info("""
        **📋 Funcionalidades:**
        - Visualizar correções anteriores
        - Comparar evolução do aluno
        - Baixar relatórios antigos
        - Estatísticas de desempenho
        
        ⚠️ Funcionalidade em desenvolvimento
        """)


class SettingsPage:
    """Página de configurações."""
    
    def render(self) -> None:
        """Renderiza página de configurações."""
        st.header("⚙️ Configurações")
        
        tab1, tab2, tab3 = st.tabs(["🤖 IA", "📚 Referências", "🔧 Sistema"])
        
        with tab1:
            self._render_ai_settings()
        
        with tab2:
            self._render_reference_settings()
        
        with tab3:
            self._render_system_settings()
    
    def _render_ai_settings(self) -> None:
        """Renderiza configurações da IA."""
        st.subheader("🤖 Configurações da IA")
        
        st.info("""
        **Modelos Atuais:**
        - Geração: Gemini 2.5 Flash
        - Embedding: Gemini Embedding 001
        - Temperatura: 0.2 (para consistência)
        
        ⚠️ As configurações são definidas no arquivo `.env`
        """)
    
    def _render_reference_settings(self) -> None:
        """Renderiza configurações de referências."""
        st.subheader("📚 Sistema de Referências (RAG)")
        
        st.info("""
        **Referências Carregadas:**
        - Competências ENEM
        - Exemplos de redações
        - Critérios de avaliação
        
        ⚠️ Adicione mais documentos em `assets/referencias/`
        """)
    
    def _render_system_settings(self) -> None:
        """Renderiza configurações do sistema."""
        st.subheader("🔧 Configurações do Sistema")
        
        st.info("""
        **Status:**
        - ✅ Docker Container
        - ✅ API Gemini
        - ✅ Vector Database
        - ✅ Sistema de Arquivos
        
        ⚠️ Logs disponíveis via `make-docker logs`
        """)
