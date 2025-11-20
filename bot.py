import os
import time
import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Estados da conversa
ESCOLHER_DISCIPLINA = 1

# Variável global para armazenar o bot Selenium
bot_selenium = None
disciplinas_cache = []

# ============================================================================
# CLASSE BOT SELENIUM
# ============================================================================

class PortalBot:
    def __init__(self):
        self.url_login = "https://www.colaboraread.com.br/login/auth"
        self.username = os.getenv('PORTAL_USERNAME')
        self.password = os.getenv('PORTAL_PASSWORD')
        
        # Configurar Chrome para Docker/Render
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # MUDANÇA IMPORTANTE: Não especificar service, deixar Selenium Manager gerenciar
        # O Selenium 4.15+ tem Selenium Manager que baixa ChromeDriver automaticamente
        logger.info("Inicializando Chrome com Selenium Manager...")
        self.driver = webdriver.Chrome(options=chrome_options)
        
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined});'
        })
        
        self.wait = WebDriverWait(self.driver, 10)
        logger.info("Bot Selenium inicializado com sucesso!")
    
    def fazer_login(self):
        try:
            logger.info("Fazendo login...")
            self.driver.get(self.url_login)
            time.sleep(5)
            
            username_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            username_field.send_keys(self.username)
            
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)
            
            time.sleep(7)
            
            if "login" not in self.driver.current_url.lower():
                logger.info("Login realizado!")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro no login: {e}")
            return False
    
    def entrar_curso_agronomia(self):
        """Acessa o curso de Agronomia - VERSÃO CORRIGIDA"""
        try:
            logger.info("="*60)
            logger.info("Tentando acessar curso de Agronomia...")
            logger.info("="*60)
            
            # 1. Aguardar carregamento
            time.sleep(5)
            
            # 2. FECHAR BANNER DE COOKIES (se existir)
            try:
                logger.info("Verificando banner de cookies...")
                cookie_button = self.driver.find_element(By.CSS_SELECTOR, "button.classBtnCookies")
                if cookie_button.is_displayed():
                    logger.info("Fechando banner de cookies...")
                    cookie_button.click()
                    time.sleep(1)
            except Exception as e:
                logger.info(f"Banner de cookies não encontrado ou já fechado: {e}")
            
            # 3. ENCONTRAR O BOTÃO "ENTRAR"
            logger.info("Procurando botão Entrar...")
            entrar_button = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button.btn.btn-primary.entrar"))
            )
            logger.info("✅ Botão encontrado!")
            
            # 4. ROLAR ATÉ O BOTÃO
            logger.info("Rolando até o botão...")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", entrar_button)
            time.sleep(1)
            
            # 5. CLICAR USANDO JAVASCRIPT (ignora elementos na frente)
            logger.info("Clicando no botão (via JavaScript)...")
            self.driver.execute_script("arguments[0].click();", entrar_button)
            time.sleep(3)
            
            # 6. VERIFICAR SE ENTROU
            logger.info(f"✅ Curso acessado! URL: {self.driver.current_url}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao acessar curso: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def listar_disciplinas(self):
        try:
            disciplinas_elements = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "a.atividadeNome[href*='/aluno/timeline/index']")
                )
            )
            
            disciplinas = []
            for elemento in disciplinas_elements:
                nome = elemento.text.strip()
                url = elemento.get_attribute('href')
                if nome and url:
                    disciplinas.append({'nome': nome, 'url': url, 'elemento': elemento})
            
            return disciplinas
        except Exception as e:
            logger.error(f"Erro: {e}")
            return []
    
    def acessar_disciplina(self, disciplina):
        try:
            disciplina['elemento'].click()
            time.sleep(3)
            return True
        except Exception as e:
            logger.error(f"Erro: {e}")
            return False
    
    def configurar_filtros_conteudo_web(self):
        try:
            time.sleep(2)
            marcar_todos = self.driver.find_element(By.ID, "todos")
            if marcar_todos.is_selected():
                marcar_todos.click()
                time.sleep(0.5)
            
            tipos_elements = self.driver.find_elements(
                By.CSS_SELECTOR, "input.filters-tipo[data-filter^='tipo-']"
            )
            
            for elem in tipos_elements:
                label = elem.find_element(By.XPATH, "./parent::label")
                nome = label.text.strip().split('\n')[0].strip()
                
                if "Conteúdo WEB" in nome or "conteúdo web" in nome.lower():
                    if not elem.is_selected():
                        elem.click()
                        time.sleep(0.3)
                    break
            
            time.sleep(1)
            return True
        except Exception as e:
            logger.error(f"Erro filtros: {e}")
            return False
    
    def contar_atividades_cw(self):
        try:
            time.sleep(1)
            atividades = self.driver.find_elements(By.CSS_SELECTOR, "li.atividades[data-show='true']")
            count = 0
            for elem in atividades:
                if elem.value_of_css_property('display') == 'none':
                    continue
                try:
                    titulo = elem.find_element(By.CSS_SELECTOR, ".timeline-title small").text.strip()
                    if titulo.lower().startswith('cw'):
                        count += 1
                except:
                    continue
            return count
        except:
            return 0
    
    def obter_atividade_cw_por_indice(self, indice):
        try:
            time.sleep(1)
            atividades = self.driver.find_elements(By.CSS_SELECTOR, "li.atividades[data-show='true']")
            cw_count = 0
            
            for elem in atividades:
                if elem.value_of_css_property('display') == 'none':
                    continue
                try:
                    titulo = elem.find_element(By.CSS_SELECTOR, ".timeline-title small").text.strip()
                    if titulo.lower().startswith('cw'):
                        if cw_count == indice:
                            return {'titulo': titulo, 'elemento': elem}
                        cw_count += 1
                except:
                    continue
            return None
        except:
            return None
    
    def acessar_atividade(self, atividade):
        try:
            botao = atividade['elemento'].find_element(By.CSS_SELECTOR, "a.btn.btn-primary[title*='Atividade']")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", botao)
            time.sleep(0.5)
            botao.click()
            time.sleep(2)
            return True
        except:
            return False
    
    def processar_todas_secoes(self):
        try:
            time.sleep(1)
            try:
                summary = self.driver.find_element(By.CSS_SELECTOR, "details#detalhe summary")
                details = self.driver.find_element(By.ID, "detalhe")
                if 'open' not in details.get_attribute('outerHTML'):
                    summary.click()
                    time.sleep(1)
            except:
                pass
            
            secoes = self.driver.find_elements(By.CSS_SELECTOR, "details#detalhe a[target='_blank']")
            
            if not secoes:
                logger.info("Nenhuma seção encontrada")
                return True
            
            janela_principal = self.driver.current_window_handle
            
            for idx, secao in enumerate(secoes, 1):
                try:
                    titulo = secao.text.strip()
                    logger.info(f"Processando seção {idx}/{len(secoes)}: {titulo}")
                    
                    secao.click()
                    time.sleep(2)
                    
                    janelas = self.driver.window_handles
                    if len(janelas) > 1:
                        nova_janela = [j for j in janelas if j != janela_principal][0]
                        self.driver.switch_to.window(nova_janela)
                        
                        self.rolar_pagina_automaticamente()
                        
                        self.driver.close()
                        self.driver.switch_to.window(janela_principal)
                        time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Erro na seção {idx}: {e}")
                    try:
                        self.driver.switch_to.window(janela_principal)
                    except:
                        pass
                    continue
            
            return True
        except Exception as e:
            logger.error(f"Erro geral: {e}")
            return False
    
    def rolar_pagina_automaticamente(self):
        try:
            time.sleep(2)
            ultima_altura = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)
                
                nova_altura = self.driver.execute_script("return document.body.scrollHeight")
                
                if nova_altura == ultima_altura:
                    break
                
                ultima_altura = nova_altura
            
            time.sleep(2)
            return True
        except:
            return False
    
    def voltar_para_disciplina(self):
        try:
            if "timeline" in self.driver.current_url:
                return True
            try:
                breadcrumb = self.driver.find_element(By.CSS_SELECTOR, ".breadcrumb li:nth-last-child(2) a")
                breadcrumb.click()
                time.sleep(2)
                return True
            except:
                self.driver.back()
                time.sleep(2)
                return True
        except:
            return False
    
    def fechar(self):
        self.driver.quit()

# ============================================================================
# COMANDOS DO BOT TELEGRAM
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    await update.message.reply_text(
        "🤖 <b>Bot ColaboraRead</b>\n\n"
        "Comandos disponíveis:\n"
        "/iniciar - Iniciar automação\n"
        "/ajuda - Ver ajuda\n"
        "/status - Ver status",
        parse_mode='HTML'
    )

async def iniciar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /iniciar - Inicia o processo"""
    global bot_selenium, disciplinas_cache
    
    await update.message.reply_text("🔧 Inicializando bot...")
    
    try:
        bot_selenium = PortalBot()
        
        await update.message.reply_text("🔐 Fazendo login...")
        if not bot_selenium.fazer_login():
            await update.message.reply_text("❌ Erro no login!")
            return ConversationHandler.END
        
        await update.message.reply_text("✅ Login OK!\n🌾 Acessando Agronomia...")
        if not bot_selenium.entrar_curso_agronomia():
            await update.message.reply_text("❌ Erro ao acessar curso!")
            return ConversationHandler.END
        
        await update.message.reply_text("📚 Listando disciplinas...")
        disciplinas_cache = bot_selenium.listar_disciplinas()
        
        if not disciplinas_cache:
            await update.message.reply_text("❌ Nenhuma disciplina encontrada!")
            return ConversationHandler.END
        
        # Criar teclado com disciplinas
        keyboard = [[str(i+1)] for i in range(len(disciplinas_cache))]
        keyboard.append(["❌ Cancelar"])
        
        disciplinas_text = "\n".join([f"{i+1}. {d['nome']}" for i, d in enumerate(disciplinas_cache)])
        
        await update.message.reply_text(
            f"📚 <b>Escolha uma disciplina:</b>\n\n{disciplinas_text}\n\n"
            "Digite o número da disciplina:",
            parse_mode='HTML',
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        
        return ESCOLHER_DISCIPLINA
        
    except Exception as e:
        logger.error(f"Erro no /iniciar: {e}")
        await update.message.reply_text(f"❌ Erro: {str(e)}")
        return ConversationHandler.END

async def escolher_disciplina(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa escolha da disciplina"""
    global bot_selenium, disciplinas_cache
    
    escolha = update.message.text
    
    if escolha == "❌ Cancelar":
        await update.message.reply_text("❌ Operação cancelada!", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    try:
        indice = int(escolha) - 1
        
        if indice < 0 or indice >= len(disciplinas_cache):
            await update.message.reply_text("❌ Número inválido! Tente novamente.")
            return ESCOLHER_DISCIPLINA
        
        disciplina = disciplinas_cache[indice]
        
        await update.message.reply_text(
            f"🎯 Disciplina escolhida:\n{disciplina['nome']}\n\n⏳ Processando...",
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Processar disciplina
        if not bot_selenium.acessar_disciplina(disciplina):
            await update.message.reply_text("❌ Erro ao acessar disciplina!")
            return ConversationHandler.END
        
        if not bot_selenium.configurar_filtros_conteudo_web():
            await update.message.reply_text("❌ Erro ao configurar filtros!")
            return ConversationHandler.END
        
        total_cw = bot_selenium.contar_atividades_cw()
        
        if total_cw == 0:
            await update.message.reply_text("⚠️ Nenhuma atividade CW encontrada!")
            return ConversationHandler.END
        
        await update.message.reply_text(f"📚 Encontradas {total_cw} atividades CW!\n\n🚀 Iniciando processamento...")
        
        # Processar cada atividade
        for i in range(total_cw):
            percentage = ((i+1) / total_cw) * 100
            await update.message.reply_text(
                f"📊 <b>Progresso: {i+1}/{total_cw} ({percentage:.1f}%)</b>",
                parse_mode='HTML'
            )
            
            atividade = bot_selenium.obter_atividade_cw_por_indice(i)
            if atividade:
                await update.message.reply_text(f"📖 Processando: {atividade['titulo']}")
                
                if bot_selenium.acessar_atividade(atividade):
                    bot_selenium.processar_todas_secoes()
                    bot_selenium.voltar_para_disciplina()
                    bot_selenium.configurar_filtros_conteudo_web()
                    
                    await update.message.reply_text(f"✅ {atividade['titulo']} concluída!")
        
        await update.message.reply_text(f"🎉 <b>Todas as {total_cw} atividades concluídas!</b>", parse_mode='HTML')
        
        bot_selenium.fechar()
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text("❌ Digite apenas números!")
        return ESCOLHER_DISCIPLINA
    except Exception as e:
        logger.error(f"Erro ao processar disciplina: {e}")
        await update.message.reply_text(f"❌ Erro: {str(e)}")
        return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela a operação"""
    await update.message.reply_text("❌ Operação cancelada!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ajuda"""
    await update.message.reply_text(
        "📖 <b>Ajuda - Bot ColaboraRead</b>\n\n"
        "<b>Como usar:</b>\n"
        "1. Digite /iniciar\n"
        "2. Aguarde o login\n"
        "3. Escolha a disciplina\n"
        "4. Aguarde o processamento\n\n"
        "<b>O bot irá:</b>\n"
        "✅ Fazer login automaticamente\n"
        "✅ Listar disciplinas\n"
        "✅ Processar atividades CW\n"
        "✅ Rolar todas as seções\n"
        "✅ Notificar o progresso",
        parse_mode='HTML'
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status"""
    global bot_selenium
    status_text = "✅ Bot online!" if bot_selenium is None else "⚙️ Bot processando..."
    await update.message.reply_text(f"📊 Status: {status_text}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Inicia o bot"""
    token = os.getenv('TELEGRAM_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_TOKEN não encontrado nas variáveis de ambiente!")
        return
    
    application = Application.builder().token(token).build()
    
    # Conversation handler para escolha de disciplina
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('iniciar', iniciar)],
        states={
            ESCOLHER_DISCIPLINA: [MessageHandler(filters.TEXT & ~filters.COMMAND, escolher_disciplina)],
        },
        fallbacks=[CommandHandler('cancelar', cancelar)],
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("ajuda", ajuda))
    application.add_handler(CommandHandler("status", status))
    
    logger.info("🤖 Bot ColaboraRead iniciado com Docker!")
    logger.info("📡 Aguardando comandos do Telegram...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
