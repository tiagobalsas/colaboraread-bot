import os
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv

load_dotenv()


class PortalBot:
    """Bot para automação do portal ColaboraRead"""
    
    def __init__(self, headless=False):
        """
        Inicializa o bot
        
        Args:
            headless (bool): Se True, executa sem abrir janela do navegador
        """
        self.url_login = "https://www.colaboraread.com.br/login/auth"
        self.username = os.getenv('PORTAL_USERNAME')
        self.password = os.getenv('PORTAL_PASSWORD')
        
        # Configurar sistema de logs
        self._configurar_logs()
        
        # Validar credenciais
        if not self.username or not self.password:
            raise ValueError(
                "Credenciais não encontradas! Configure as variáveis de ambiente:\n"
                "PORTAL_USERNAME e PORTAL_PASSWORD"
            )
        
        # Configurar opções do Edge
        edge_options = Options()
        if headless:
            edge_options.add_argument('--headless')
        edge_options.add_argument('--no-sandbox')
        edge_options.add_argument('--disable-dev-shm-usage')
        
        # Inicializar driver
        self.driver = webdriver.Edge(options=edge_options)
        self.wait = WebDriverWait(self.driver, 10)  # Reduzido de 15 para 10 segundos
        
        # NOVO: Rastreamento de progresso (Baby Step 2)
        self.disciplina_atual = None
        self.atividade_atual_index = 0
        self.total_atividades = 0
        
        self.logger.info("Bot inicializado com sucesso!")
        print("✓ Bot inicializado com sucesso!")
    
    def _configurar_logs(self):
        """Configura o sistema de logging"""
        # Criar pasta de logs se não existir
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Nome do arquivo com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"logs/bot_portal_{timestamp}.log"
        
        # Configurar logging
        self.logger = logging.getLogger('PortalBot')
        self.logger.setLevel(logging.INFO)
        
        # Formato dos logs
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Handler para arquivo
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.log_filename = log_filename
    
    def verificar_sessao_valida(self):
        """Verifica se a sessão ainda é válida e tenta recuperar se necessário"""
        try:
            current_url = self.driver.current_url
            # Se está na página de login, a sessão expirou
            if "login" in current_url.lower():
                self.logger.warning("Sessão expirada - detectado redirecionamento para login")
                return False
            self.logger.info(f"Sessão válida - URL atual: {current_url}")
            return True
        except Exception as e:
            self.logger.error(f"Sessão invalidada: {e}")
            return False

    def recuperar_sessao(self):
        """Tenta recuperar a sessão e retomar de onde parou"""
        try:
            self.logger.info("Tentando recuperar sessão...")
            print("\n🔄 Tentando recuperar sessão...")
            
            # Fechar driver atual se ainda existir
            try:
                self.driver.quit()
            except:
                pass
            
            # Reinicializar driver
            edge_options = Options()
            edge_options.add_argument('--no-sandbox')
            edge_options.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Edge(options=edge_options)
            self.wait = WebDriverWait(self.driver, 10)
            
            # Refazer login
            if self.fazer_login():
                # Tentar voltar para o curso
                if self.entrar_curso_agronomia():
                    self.logger.info("Sessão recuperada com sucesso!")
                    print("✅ Sessão recuperada com sucesso!")
                    
                    # NOVO: Informar sobre progresso se tivermos
                    if self.disciplina_atual:
                        print(f"📊 Último progresso: {self.disciplina_atual} - Atividade {self.atividade_atual_index + 1}/{self.total_atividades}")
                        print("💡 Dica: Reinicie o bot para recomeçar da disciplina")
                    
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro ao recuperar sessão: {e}")
            return False

    def salvar_progresso(self):
        """Salva o progresso atual para recuperação em caso de falha"""
        progresso = {
            'disciplina': self.disciplina_atual,
            'atividade_index': self.atividade_atual_index,
            'total_atividades': self.total_atividades,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.logger.info(f"Progresso salvo: {progresso}")
        print(f"📊 Progresso salvo: Atividade {self.atividade_atual_index + 1}/{self.total_atividades}")
        return progresso
    
    def salvar_html_pagina(self, nome_arquivo=None):
        """Salva o HTML da página atual para debug"""
        if nome_arquivo is None:
            timestamp = datetime.now().strftime("%H%M%S")
            nome_arquivo = f"debug_page_{timestamp}.html"
        
        html_content = self.driver.page_source
        with open(f"logs/{nome_arquivo}", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        self.logger.info(f"HTML salvo em: logs/{nome_arquivo}")
        return nome_arquivo
    
    def fazer_login(self):
        """Realiza o login no portal"""
        try:
            self.logger.info(f"Acessando {self.url_login}")
            print(f"\n→ Acessando {self.url_login}")
            self.driver.get(self.url_login)
            
            # Aguardar e preencher campo de usuário
            self.logger.info("Preenchendo credenciais...")
            print("→ Preenchendo credenciais...")
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.clear()
            username_field.send_keys(self.username)
            
            # Preencher campo de senha
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Clicar no botão de login
            self.logger.info("Efetuando login...")
            print("→ Efetuando login...")
            login_button = self.driver.find_element(
                By.CSS_SELECTOR, 
                "button.btn.btn-primary.btn-lg.btn-block"
            )
            login_button.click()
            
            # Aguardar redirecionamento (reduzido de 3s para 2s)
            time.sleep(2)
            
            # Verificar se o login foi bem-sucedido
            if "login" not in self.driver.current_url.lower():
                self.logger.info("Login realizado com sucesso!")
                print("✓ Login realizado com sucesso!")
                return True
            else:
                self.logger.error("Falha no login - verifique as credenciais")
                print("✗ Falha no login - verifique as credenciais")
                return False
                
        except TimeoutException:
            self.logger.error("Timeout: Página demorou muito para carregar")
            print("✗ Timeout: Página demorou muito para carregar")
            return False
        except NoSuchElementException as e:
            self.logger.error(f"Elemento não encontrado: {e}")
            print(f"✗ Elemento não encontrado: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erro inesperado no login: {e}")
            print(f"✗ Erro inesperado: {e}")
            return False
    
    def obter_titulo_pagina(self):
        """Retorna o título da página atual"""
        return self.driver.title
    
    def tirar_screenshot(self, nome_arquivo="screenshot.png"):
        """Salva um screenshot da página atual"""
        self.driver.save_screenshot(nome_arquivo)
        self.logger.info(f"Screenshot salvo: {nome_arquivo}")
        print(f"✓ Screenshot salvo: {nome_arquivo}")
    
    def entrar_curso_agronomia(self):
        """Acessa o curso de Agronomia - Bacharelado"""
        try:
            self.logger.info("Procurando curso de Agronomia...")
            print("\n→ Procurando curso de Agronomia...")
            
            # Aguardar o botão "Entrar" aparecer
            entrar_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary.entrar"))
            )
            
            self.logger.info("Clicando em 'Entrar' no curso de Agronomia...")
            print("→ Clicando em 'Entrar' no curso de Agronomia...")
            entrar_button.click()
            
            # Aguardar carregamento (reduzido de 3s para 2s)
            time.sleep(2)
            
            self.logger.info(f"Curso acessado! URL atual: {self.driver.current_url}")
            print(f"✓ Curso acessado! URL atual: {self.driver.current_url}")
            return True
            
        except TimeoutException:
            self.logger.error("Timeout: Botão 'Entrar' não encontrado")
            print("✗ Timeout: Botão 'Entrar' não encontrado")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao acessar curso: {e}")
            print(f"✗ Erro ao acessar curso: {e}")
            return False
    
    def listar_disciplinas(self):
        """Lista todas as disciplinas disponíveis e retorna uma lista com seus dados"""
        try:
            self.logger.info("Buscando disciplinas disponíveis...")
            print("\n→ Buscando disciplinas disponíveis...")
            
            # Aguardar as disciplinas carregarem
            disciplinas_elements = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "a.atividadeNome[href*='/aluno/timeline/index']")
                )
            )
            
            disciplinas = []
            
            for elemento in disciplinas_elements:
                nome = elemento.text.strip()
                url = elemento.get_attribute('href')
                
                # Filtrar "Atividades interdisciplinares" se necessário
                if nome and url:
                    disciplinas.append({
                        'nome': nome,
                        'url': url,
                        'elemento': elemento
                    })
            
            self.logger.info(f"Encontradas {len(disciplinas)} disciplinas")
            return disciplinas
            
        except TimeoutException:
            self.logger.error("Timeout: Disciplinas não encontradas")
            print("✗ Timeout: Disciplinas não encontradas")
            return []
        except Exception as e:
            self.logger.error(f"Erro ao listar disciplinas: {e}")
            print(f"✗ Erro ao listar disciplinas: {e}")
            return []
    
    def escolher_disciplina(self, disciplinas):
        """Mostra menu para o usuário escolher uma disciplina"""
        if not disciplinas:
            self.logger.error("Nenhuma disciplina encontrada!")
            print("✗ Nenhuma disciplina encontrada!")
            return None
        
        print("\n" + "="*60)
        print("DISCIPLINAS DISPONÍVEIS:")
        print("="*60)
        
        for i, disc in enumerate(disciplinas, 1):
            print(f"{i}. {disc['nome']}")
        
        print("="*60)
        
        while True:
            try:
                escolha = input(f"\nDigite o número da disciplina (1-{len(disciplinas)}) ou 0 para sair: ")
                escolha = int(escolha)
                
                if escolha == 0:
                    self.logger.info("Operação cancelada pelo usuário")
                    print("✗ Operação cancelada pelo usuário")
                    return None
                
                if 1 <= escolha <= len(disciplinas):
                    disciplina_escolhida = disciplinas[escolha - 1]
                    self.logger.info(f"Disciplina escolhida: {disciplina_escolhida['nome']}")
                    return disciplina_escolhida
                else:
                    print(f"✗ Número inválido! Digite um número entre 1 e {len(disciplinas)}")
                    
            except ValueError:
                print("✗ Por favor, digite apenas números!")
            except KeyboardInterrupt:
                self.logger.info("Operação cancelada pelo usuário (KeyboardInterrupt)")
                print("\n✗ Operação cancelada pelo usuário")
                return None
    
    def acessar_disciplina(self, disciplina):
        """Acessa a disciplina escolhida"""
        try:
            self.logger.info(f"Acessando disciplina: {disciplina['nome']}")
            print(f"\n→ Acessando disciplina: {disciplina['nome']}")
            
            disciplina['elemento'].click()
            
            # Aguardar carregamento (reduzido de 3s para 2s)
            time.sleep(2)
            
            self.logger.info(f"Disciplina acessada! URL: {self.driver.current_url}")
            print(f"✓ Disciplina acessada! URL: {self.driver.current_url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao acessar disciplina: {e}")
            print(f"✗ Erro ao acessar disciplina: {e}")
            return False
    
    def configurar_filtros_conteudo_web(self):
        """Configura os filtros para mostrar apenas Conteúdo WEB"""
        try:
            self.logger.info("Configurando filtros para 'Conteúdo WEB'...")
            print("\n→ Configurando filtros para 'Conteúdo WEB'...")
            
            # Aguardar os filtros carregarem (reduzido de 2s para 1s)
            time.sleep(1)
            
            # 1. DESMARCAR TODOS primeiro
            self.logger.info("Desmarcando todos os tipos de atividade...")
            print("→ Desmarcando todos os tipos de atividade...")
            marcar_todos = self.driver.find_element(By.ID, "todos")
            
            if marcar_todos.is_selected():
                marcar_todos.click()
                time.sleep(0.5)  # Reduzido de 1s para 0.5s
            
            # 2. MARCAR apenas "Conteúdo WEB"
            self.logger.info("Marcando apenas 'Conteúdo WEB'...")
            print("→ Marcando apenas 'Conteúdo WEB'...")
            tipos_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "input.filters-tipo[data-filter^='tipo-']"
            )
            
            for elem in tipos_elements:
                label = elem.find_element(By.XPATH, "./parent::label")
                nome = label.text.strip().split('\n')[0].strip()
                
                if "Conteúdo WEB" in nome or "conteúdo web" in nome.lower():
                    if not elem.is_selected():
                        elem.click()
                        self.logger.info(f"Filtro marcado: {nome}")
                        print(f"  ✓ {nome}")
                        time.sleep(0.3)  # Reduzido de 0.5s para 0.3s
                    break
            
            self.logger.info("Filtros configurados com sucesso")
            print("✓ Filtros configurados!")
            time.sleep(1)  # Reduzido de 2s para 1s (aguardar atualização da página)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao configurar filtros: {e}")
            print(f"✗ Erro ao configurar filtros: {e}")
            return False
    
    def contar_atividades_cw(self):
        """Conta quantas atividades CW existem no total"""
        try:
            time.sleep(1)  # Reduzido de 2s para 1s
            atividades_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "li.atividades[data-show='true']"
            )
            
            count = 0
            for elem in atividades_elements:
                if elem.value_of_css_property('display') == 'none':
                    continue
                try:
                    titulo_elem = elem.find_element(By.CSS_SELECTOR, ".timeline-title small")
                    titulo = titulo_elem.text.strip()
                    if titulo.lower().startswith('cw'):
                        count += 1
                except:
                    continue
            
            self.logger.info(f"Total de atividades CW encontradas: {count}")
            return count
        except Exception as e:
            self.logger.error(f"Erro ao contar atividades CW: {e}")
            return 0

    def obter_atividade_cw_por_indice(self, indice):
        """
        Obtém a atividade CW pelo índice (0=CW1, 1=CW2, 2=CW3, 3=CW4)
        
        Args:
            indice (int): Índice da atividade (0, 1, 2, 3...)
        
        Returns:
            dict: {'titulo': str, 'elemento': WebElement} ou None
        """
        try:
            time.sleep(1)  # Reduzido de 2s para 1s
            
            # Buscar todas as atividades visíveis
            atividades_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "li.atividades[data-show='true']"
            )
            
            self.logger.info(f"Buscando atividade CW índice {indice}. Total de elementos: {len(atividades_elements)}")
            
            cw_count = 0
            
            for elem in atividades_elements:
                # Verificar se está visível
                if elem.value_of_css_property('display') == 'none':
                    continue
                
                try:
                    titulo_elem = elem.find_element(By.CSS_SELECTOR, ".timeline-title small")
                    titulo = titulo_elem.text.strip()
                    
                    # Se é uma atividade CW
                    if titulo.lower().startswith('cw'):
                        self.logger.info(f"Encontrada atividade CW #{cw_count}: {titulo}")
                        
                        # Se é o índice que queremos
                        if cw_count == indice:
                            self.logger.info(f"Retornando atividade índice {indice}: {titulo}")
                            return {
                                'titulo': titulo,
                                'elemento': elem
                            }
                        cw_count += 1
                except Exception as e:
                    self.logger.warning(f"Erro ao processar elemento: {e}")
                    continue
            
            self.logger.warning(f"Atividade CW índice {indice} não encontrada. Total CWs encontrados: {cw_count}")
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao obter atividade por índice: {e}")
            print(f"✗ Erro ao obter atividade por índice: {e}")
            return None
    
    def acessar_atividade(self, atividade):
        """Acessa a atividade escolhida clicando no botão apropriado"""
        try:
            self.logger.info(f"Acessando atividade: {atividade['titulo']}")
            print(f"\n→ Acessando atividade: {atividade['titulo']}")
            
            # Buscar o botão "Atividade"
            botao = atividade['elemento'].find_element(
                By.CSS_SELECTOR, 
                "a.btn.btn-primary[title*='Atividade']"
            )
            
            # Rolar até o botão
            self.driver.execute_script("arguments[0].scrollIntoView(true);", botao)
            time.sleep(0.5)  # Reduzido de 1s para 0.5s
            
            # Clicar no botão
            botao.click()
            
            # Aguardar carregamento (reduzido de 3s para 2s)
            time.sleep(2)
            
            self.logger.info("Atividade acessada com sucesso")
            print(f"✓ Atividade acessada!")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao acessar atividade: {e}")
            print(f"✗ Erro ao acessar atividade: {e}")
            return False

    def obter_todas_secoes_material_externo(self):
        """
        Obtém TODAS as seções do material externo
        
        Returns:
            list: Lista de dicionários com {'nome': str, 'elemento': WebElement}
        """
        try:
            self.logger.info("Buscando todas as seções do material externo...")
            
            # Aguardar carregar (reduzido de 2s para 1s)
            time.sleep(1)
            
            # Expandir details se necessário
            try:
                summary = self.driver.find_element(By.CSS_SELECTOR, "details#detalhe summary")
                # Verificar se já está expandido (tem o atributo 'open')
                details_element = self.driver.find_element(By.ID, "detalhe")
                if 'open' not in details_element.get_attribute('outerHTML'):
                    summary.click()
                    time.sleep(0.5)
                    self.logger.info("Material externo expandido")
            except:
                self.logger.info("Material externo já expandido ou não encontrado")
                pass
            
            # Buscar TODOS os links das seções
            secoes_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "details#detalhe a[target='_blank']"
            )
            
            secoes = []
            
            for elemento in secoes_elements:
                nome = elemento.text.strip()
                if nome:
                    secoes.append({
                        'nome': nome,
                        'elemento': elemento
                    })
            
            self.logger.info(f"Encontradas {len(secoes)} seções: {[s['nome'] for s in secoes]}")
            return secoes
            
        except Exception as e:
            self.logger.error(f"Erro ao obter seções do material externo: {e}")
            return []

    def processar_todas_secoes_material_externo(self):
        """
        Processa TODAS as seções do material externo sequencialmente
        VERSÃO SEGURA: Mantém a guia principal sempre aberta
        
        Returns:
            bool: True se todas as seções foram processadas, False se houve erro
        """
        try:
            # Obter todas as seções
            secoes = self.obter_todas_secoes_material_externo()
            
            if not secoes:
                self.logger.warning("Nenhuma seção encontrada no material externo")
                print("⚠ Nenhuma seção encontrada no material externo")
                return False
            
            total_secoes = len(secoes)
            self.logger.info(f"Iniciando processamento de {total_secoes} seções")
            print(f"\n📚 Encontradas {total_secoes} seções no material externo")
            
            # Guardar a guia principal (disciplina) - CRÍTICO
            guia_principal = self.driver.current_window_handle
            self.logger.info(f"Guia principal salva: {guia_principal}")
            
            # Processar cada seção
            for i, secao in enumerate(secoes, 1):
                print(f"\n📖 Processando seção {i}/{total_secoes}: {secao['nome']}")
                self.logger.info(f"Processando seção {i}/{total_secoes}: {secao['nome']}")
                
                try:
                    # ✅ ESTRATÉGIA SEGURA: Abrir em nova guia sem sair da atual
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", secao['elemento'])
                    time.sleep(0.5)
                    
                    # ✅ IMPORTANTE: não use window.open(href) aqui, pois isso NÃO dispara o onclick do link.
                    # No Colabora, o onclick geralmente chama saveProgressoEngajamento(...),
                    # que é o que registra a leitura/conclusão. Então clicamos no <a> e esperamos a nova guia.
                    handles_antes = set(self.driver.window_handles)
                    self.driver.execute_script("arguments[0].click();", secao['elemento'])
                    
                    # Aguardar abrir nova guia
                    nova_guia = None
                    for _ in range(40):  # ~10s
                        handles_agora = set(self.driver.window_handles)
                        diff = list(handles_agora - handles_antes)
                        if diff:
                            nova_guia = diff[0]
                            break
                        time.sleep(0.25)
                    
                    if not nova_guia:
                        self.logger.error("Nova guia não foi aberta!")
                        print("✗ Nova guia não foi aberta!")
                        continue
                    
                    self.driver.switch_to.window(nova_guia)
                    self.logger.info(f"Nova guia acessada para: {secao['nome']}")
                    
                    # Aguardar carregamento
                    self.logger.info("Aguardando carregamento da seção...")
                    time.sleep(3)
                    
                    # Verificar iframe
                    try:
                        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                        if iframes:
                            self.logger.info(f"Encontrados {len(iframes)} iframes. Mudando para o primeiro...")
                            self.driver.switch_to.frame(iframes[0])
                            time.sleep(1)
                    except Exception as e:
                        self.logger.info(f"Nenhum iframe encontrado ou erro: {e}")
                    
                    # Rolar até o final
                    self.rolar_pagina_automaticamente(intervalo=1)
                    
                    # ✅ FECHAR APENAS A GUIA DA SEÇÃO (mantém principal)
                    self.driver.close()
                    self.logger.info(f"Guia da seção {i} fechada")
                    
                    # ✅ VOLTAR PARA GUIA PRINCIPAL IMEDIATAMENTE
                    self.driver.switch_to.window(guia_principal)
                    self.logger.info(f"Voltou para guia principal após seção {i}")
                    
                    self.logger.info(f"Seção {i} concluída: {secao['nome']}")
                    print(f"✓ Seção {i} concluída: {secao['nome']}")
                    
                    # Pequena pausa entre seções para estabilidade
                    time.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Erro ao processar seção {i}: {e}")
                    print(f"✗ Erro ao processar seção {i}: {e}")
                    
                    # ✅ RECUPERAÇÃO: Tentar voltar para guia principal mesmo com erro
                    try:
                        self.driver.switch_to.window(guia_principal)
                        self.logger.info("Recuperação: Voltou para guia principal após erro")
                    except Exception as recovery_error:
                        self.logger.error(f"Erro na recuperação: {recovery_error}")
                    
                    return False
            
            self.logger.info(f"Todas as {total_secoes} seções foram processadas com sucesso")
            print(f"✅ Todas as {total_secoes} seções foram processadas!")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro geral ao processar seções: {e}")
            print(f"✗ Erro ao processar seções: {e}")
            
            # Tentar voltar para guia principal em caso de erro geral
            try:
                self.driver.switch_to.window(guia_principal)
            except:
                pass
            return False
    
    def rolar_pagina_automaticamente(self, intervalo=1):
        """Rola a página automaticamente até o final"""
        try:
            self.logger.info(f"Iniciando rolagem automática (intervalo: {intervalo}s)")
            print(f"\n→ Iniciando rolagem automática...")
            
            rolagens = 0
            pixels_por_rolagem = 500
            
            while True:
                altura_total = self.driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);")
                altura_janela = self.driver.execute_script("return window.innerHeight;")
                
                # Rolar
                self.driver.execute_script(f"window.scrollBy(0, {pixels_por_rolagem}); window.dispatchEvent(new Event('scroll'));")
                time.sleep(intervalo)
                
                posicao = self.driver.execute_script("return window.pageYOffset;")
                rolagens += 1
                
                progresso = int(((posicao + altura_janela) / altura_total) * 100) if altura_total > 0 else 100
                self.logger.info(f"Rolagem #{rolagens} - Progresso: {progresso}%")
                print(f"  ✓ Rolagem #{rolagens} - {progresso}%")
                
                # Verificar se chegou ao final (viewport encostou no fim)
                if (posicao + altura_janela) >= (altura_total - 2):
                    # Força scroll no "bottom" real e espera um pouco para o portal contabilizar
                    self.driver.execute_script(
                        "window.scrollTo(0, Math.max(document.body.scrollHeight, document.documentElement.scrollHeight));"
                        "window.dispatchEvent(new Event('scroll')); document.dispatchEvent(new Event('scroll'));"
                    )
                    time.sleep(max(intervalo, 1.0))

                    # Recalcula progresso final (garante 100% quando bateu no fim)
                    altura_total2 = self.driver.execute_script(
                        "return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);"
                    )
                    altura_janela2 = self.driver.execute_script("return window.innerHeight;")
                    posicao2 = self.driver.execute_script("return window.pageYOffset;")
                    progresso2 = int(((posicao2 + altura_janela2) / altura_total2) * 100) if altura_total2 > 0 else 100
                    if progresso2 < 100 and (posicao2 + altura_janela2) >= (altura_total2 - 1):
                        progresso2 = 100

                    self.logger.info(
                        f"Fim da página alcançado. Total de rolagens: {rolagens} | Progresso final: {progresso2}%"
                    )
                    print(f"✓ Fim da página! Total: {rolagens} rolagens | Progresso final: {progresso2}%")

                    # Linger no fim
                    time.sleep(2)
                    break
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro durante rolagem: {e}")
            print(f"✗ Erro durante rolagem: {e}")
            return False
    
    def voltar_para_disciplina(self):
        """Volta para a página da disciplina de forma segura"""
        try:
            self.logger.info("Voltando para disciplina...")
            print("\n→ Voltando para disciplina...")
            
            # ✅ VERIFICAR SESSÃO ANTES DE QUALQUER OPERAÇÃO
            if not self.verificar_sessao_valida():
                self.logger.error("Sessão invalidada ao tentar voltar para disciplina")
                return False
            
            # Verificar URL atual para debug
            current_url = self.driver.current_url
            self.logger.info(f"URL atual antes de voltar: {current_url}")
            
            # Se já estamos na timeline, não precisa fazer nada
            if "timeline" in current_url:
                self.logger.info("Já está na timeline da disciplina")
                print("✓ Já está na timeline da disciplina")
                return True
            
            # Tentar voltar via breadcrumb
            try:
                breadcrumb = self.driver.find_element(By.CSS_SELECTOR, ".breadcrumb li:nth-last-child(2) a")
                breadcrumb.click()
                self.logger.info("Retornou para a timeline da disciplina via breadcrumb")
                print("✓ Retornou para a timeline da disciplina")
                time.sleep(2)
                return True
            except Exception as e:
                self.logger.info(f"Breadcrumb não encontrado: {e}")
            
            # Tentar voltar via botão voltar do navegador
            try:
                self.driver.back()
                self.logger.info("Voltou via navegador back()")
                time.sleep(2)
                
                # Verificar se voltou para timeline
                if "timeline" in self.driver.current_url:
                    self.logger.info("Voltou com sucesso para timeline")
                    print("✓ Voltou para timeline via navegador")
                    return True
            except Exception as e:
                self.logger.error(f"Erro ao voltar via navegador: {e}")
            
            self.logger.warning("Não foi possível voltar para timeline, mas continuando...")
            print("⚠ Não foi possível voltar para timeline, continuando...")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao voltar para disciplina: {e}")
            print(f"✗ Erro ao voltar: {e}")
            return False
    
    def fechar(self):
        """Fecha o navegador"""
        self.logger.info("Encerrando bot...")
        print("\n→ Encerrando bot...")
        
        # Salvar log final
        self.logger.info("=== BOT ENCERRADO ===")
        
        self.driver.quit()
        print("✓ Bot encerrado!")
        print(f"📄 Log salvo em: {self.log_filename}")


def main():
    """Função principal"""
    bot = None
    
    try:
        # Inicializar bot
        bot = PortalBot(headless=False)
        
        # Fazer login
        if bot.fazer_login():
            # Entrar no curso
            if bot.entrar_curso_agronomia():
                # Listar disciplinas
                disciplinas = bot.listar_disciplinas()
                
                if disciplinas:
                    # ÚNICA INTERAÇÃO: Usuário escolhe a disciplina
                    disciplina_escolhida = bot.escolher_disciplina(disciplinas)
                    
                    if disciplina_escolhida:
                        # Acessar a disciplina
                        if bot.acessar_disciplina(disciplina_escolhida):
                            
                            # Configurar filtros para Conteúdo WEB
                            if bot.configurar_filtros_conteudo_web():
                                
                                # SALVAR HTML PARA DEBUG
                                bot.salvar_html_pagina("debug_antes_processamento.html")
                                
                                # Contar quantas atividades CW existem
                                total_cw = bot.contar_atividades_cw()
                                
                                if total_cw > 0:
                                    print(f"\n{'='*60}")
                                    print(f"✓ Encontradas {total_cw} atividades CW")
                                    print(f"{'='*60}\n")
                                    
                                    # NOVO: Inicializar rastreamento de progresso (Baby Step 2)
                                    bot.total_atividades = total_cw
                                    bot.disciplina_atual = disciplina_escolhida['nome']
                                    
                                    # PROCESSAR CADA ATIVIDADE CW POR ÍNDICE
                                    for i in range(total_cw):  # 0, 1, 2, 3 (índices)
                                        print(f"\n{'='*60}")
                                        print(f"PROCESSANDO {i+1}/{total_cw}")
                                        print(f"{'='*60}")
                                        
                                        # NOVO: Atualizar progresso atual
                                        bot.atividade_atual_index = i
                                        bot.salvar_progresso()
                                        
                                        # ✅ VERIFICAR SESSÃO ANTES DE CADA OPERAÇÃO
                                        if not bot.verificar_sessao_valida():
                                            print("✗ Sessão perdida! Tentando recuperar...")
                                            if bot.recuperar_sessao():
                                                print("✅ Sessão recuperada! Continuando processamento...")
                                                # Por enquanto apenas continuamos - próximo baby step tratará de voltar para a disciplina
                                            else:
                                                print("✗ Falha ao recuperar sessão! Reinicie o bot.")
                                                break
                                        
                                        # Buscar atividade por índice específico
                                        atividade = bot.obter_atividade_cw_por_indice(i)
                                        
                                        if atividade:
                                            print(f"→ Atividade encontrada: {atividade['titulo']}")
                                            
                                            # Acessar atividade
                                            if bot.acessar_atividade(atividade):
                                                
                                                # ✅ VERIFICAR SESSÃO ANTES DE PROCESSAR SEÇÕES
                                                if not bot.verificar_sessao_valida():
                                                    print("✗ Sessão perdida antes de processar seções!")
                                                    break
                                                
                                                # Processar TODAS as seções do material externo
                                                print(f"\n🔍 Verificando seções do material externo...")
                                                if bot.processar_todas_secoes_material_externo():
                                                    print(f"✓ Todas as seções de {atividade['titulo']} concluídas!")
                                                else:
                                                    print(f"⚠ Algum problema ao processar seções de {atividade['titulo']}")
                                                
                                                # ✅ VERIFICAR SESSÃO ANTES DE VOLTAR
                                                if not bot.verificar_sessao_valida():
                                                    print("✗ Sessão perdida após processar seções!")
                                                    break
                                                
                                                # Voltar para a disciplina
                                                if not bot.voltar_para_disciplina():
                                                    print("✗ Erro ao voltar para disciplina! Sessão pode ter expirado.")
                                                    break
                                                
                                                # ✅ VERIFICAR SESSÃO ANTES DE RECONFIGURAR
                                                if not bot.verificar_sessao_valida():
                                                    print("✗ Sessão perdida ao voltar!")
                                                    break
                                                
                                                # Reconfigurar filtros
                                                if not bot.configurar_filtros_conteudo_web():
                                                    print("✗ Erro ao reconfigurar filtros!")
                                                    break
                                            
                                            # NOVO: Salvar progresso após cada atividade concluída
                                            bot.salvar_progresso()
                                            print(f"\n✓ {atividade['titulo']} concluída!")
                                        else:
                                            print(f"✗ Não foi possível encontrar a atividade CW #{i+1}")
                                            break  # Parar se não encontrar atividade esperada
                                    
                                    print(f"\n{'='*60}")
                                    print(f"✅ TODAS AS {total_cw} ATIVIDADES CW FORAM PROCESSADAS!")
                                    print(f"{'='*60}\n")
                                    
                                else:
                                    print("\n✗ Nenhuma atividade CW encontrada")
                else:
                    print("\n✗ Não foi possível listar as disciplinas")
    
    except KeyboardInterrupt:
        print("\n\n⚠ Interrompido pelo usuário")
        if bot:
            bot.logger.info("Bot interrompido pelo usuário")
    
    except Exception as e:
        print(f"\n✗ Erro: {e}")
        if bot:
            bot.logger.error(f"Erro não tratado: {e}")
    
    finally:
        if bot:
            print(f"\n📄 Log completo salvo em: {bot.log_filename}")
            input("\n⏸ Pressione ENTER para fechar o navegador...")
            bot.fechar()


if __name__ == "__main__":
    main()
