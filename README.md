# 🤖 Bot ColaboraRead - Automação de Atividades

Bot Telegram para automatizar atividades do portal ColaboraRead usando Selenium.

## 🚀 Funcionalidades

- ✅ Login automático no portal
- ✅ Listagem de disciplinas
- ✅ Escolha de disciplina via Telegram
- ✅ Processamento automático de atividades CW
- ✅ Notificações em tempo real
- ✅ Controle total pelo celular

## 📱 Comandos do Bot

- `/start` - Iniciar bot
- `/iniciar` - Começar automação
- `/ajuda` - Ver ajuda
- `/status` - Ver status do bot
- `/cancelar` - Cancelar operação

## ⚙️ Configuração no Render

### 1. Fork este repositório

### 2. Criar Web Service no Render
- Vá para [render.com](https://render.com)
- Clique em "New +" → "Web Service"
- Conecte seu repositório GitHub
- Configure:
  - **Name**: colaboraread-bot
  - **Environment**: Python 3
  - **Build Command**: `./setup_chrome.sh && pip install -r requirements.txt`
  - **Start Command**: `python bot.py`

### 3. Adicionar variáveis de ambiente
No Render, adicione estas variáveis em "Environment":
```
PORTAL_USERNAME=seu_usuario
PORTAL_PASSWORD=sua_senha
TELEGRAM_TOKEN=seu_token_telegram
TELEGRAM_CHAT_ID=seu_chat_id
```

### 4. Deploy
Clique em "Deploy" e aguarde 5-10 minutos.

## 🔧 Desenvolvimento Local
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Edite o .env com suas credenciais

# Executar
python bot.py
```

## 📝 Notas

- ⚠️ Não commit o arquivo `.env` (já está no .gitignore)
- ✅ Use variáveis de ambiente no Render
- 🔒 Mantenha suas credenciais seguras

## 🛠️ Stack

- Python 3.11+
- Selenium WebDriver
- python-telegram-bot
- Chrome/ChromeDriver

## 📄 Licença

MIT License

## 👤 Autor

Seu Nome
