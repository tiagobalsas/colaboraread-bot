# 🤖 Bot ColaboraRead - Documentação Completa

## 📋 Índice
1. [Sobre o Projeto](#sobre-o-projeto)
2. [Finalidade](#finalidade)
3. [Tecnologias Utilizadas](#tecnologias-utilizadas)
4. [Como Foi Desenvolvido](#como-foi-desenvolvido)
5. [Funcionalidades Implementadas](#funcionalidades-implementadas)
6. [Arquitetura do Sistema](#arquitetura-do-sistema)
7. [Configuração e Deploy](#configuração-e-deploy)
8. [Como Usar](#como-usar)
9. [Possíveis Erros e Soluções](#possíveis-erros-e-soluções)
10. [Melhorias Futuras](#melhorias-futuras)
11. [Limitações Conhecidas](#limitações-conhecidas)

---

## 📖 Sobre o Projeto

O **Bot ColaboraRead** é um assistente automatizado desenvolvido para processar atividades de Conteúdo WEB (CW) do portal ColaboraRead de forma automática, economizando tempo e esforço manual do usuário.

### Contexto
O portal ColaboraRead é uma plataforma educacional que exige que os alunos visualizem todo o conteúdo das atividades CW, o que envolve:
- Abrir cada atividade
- Acessar múltiplas seções/unidades
- Rolar cada página até o final
- Fazer isso para todas as disciplinas

Este processo manual é repetitivo e demorado. O bot automatiza completamente esse fluxo.

---

## 🎯 Finalidade

### Objetivo Principal
Automatizar o processamento de atividades CW (Conteúdo WEB) no portal ColaboraRead, rolando automaticamente todas as seções de cada atividade.

### Benefícios
- ✅ Economia de tempo (4 atividades em ~5 minutos vs ~20-30 minutos manual)
- ✅ Automatização completa do processo
- ✅ Interface amigável via Telegram
- ✅ Notificações em tempo real do progresso
- ✅ Disponível 24/7 na nuvem

---

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.11** - Linguagem principal
- **Selenium 4.15.2** - Automação web (controle do navegador)
- **ChromeDriver** - Driver para controlar o Google Chrome
- **python-telegram-bot 21.9** - Interface com Telegram
- **psutil** - Monitoramento de recursos do sistema

### Infraestrutura
- **Railway.app** - Hospedagem do bot (8GB RAM)
- **GitHub** - Controle de versão e CI/CD
- **Telegram Bot API** - Interface de usuário

### Navegador
- **Google Chrome (Headless)** - Execução sem interface gráfica

---

## 🔨 Como Foi Desenvolvido

### Fase 1: Prototipação e Testes Locais
1. Análise do portal ColaboraRead
2. Identificação dos elementos HTML (seletores CSS)
3. Desenvolvimento da lógica de automação com Selenium
4. Testes locais do fluxo completo

### Fase 2: Integração com Telegram
1. Criação do bot no Telegram (via BotFather)
2. Implementação dos comandos (/iniciar, /status, /ajuda)
3. Sistema de conversação para escolha de disciplinas
4. Notificações de progresso em tempo real

### Fase 3: Deploy e Otimizações
1. **Tentativa 1: Render.com (512MB)** ❌
   - Problema: Memória insuficiente
   - Chrome consumia mais de 512MB
   - Processo era encerrado pelo sistema

2. **Tentativa 2: Otimizações Extremas no Render** ❌
   - Desabilitação de imagens
   - Limite de memória JavaScript
   - Reinício do Chrome entre atividades
   - Ainda insuficiente para 512MB

3. **Solução Final: Railway.app (8GB)** ✅
   - Memória suficiente para processar todas as atividades
   - Deploy automático via GitHub
   - Estabilidade garantida

### Fase 4: Testes e Refinamentos
1. Testes com múltiplas disciplinas
2. Validação do processamento de seções
3. Tratamento de erros e edge cases
4. Melhorias de logging para debug

---

## ✨ Funcionalidades Implementadas

### 1. Autenticação Automática
- Login automático no portal ColaboraRead
- Credenciais armazenadas com segurança em variáveis de ambiente
- Tratamento de erros de autenticação

### 2. Navegação Inteligente
- Acesso automático ao curso de Agronomia
- Detecção e fechamento de banners/popups
- Navegação por breadcrumbs

### 3. Listagem de Disciplinas
- Busca automática de todas as disciplinas disponíveis
- Interface de seleção via Telegram
- Validação de entrada do usuário

### 4. Processamento de Atividades CW
- Identificação automática de atividades CW
- Filtragem por tipo de conteúdo (Conteúdo WEB)
- Contagem total de atividades


### 4.1 Processamento de Atividades TA (Teleaula) **(NOVO)** 🎥
- Filtragem por tipo de conteúdo (**Teleaula**)
- Listagem automática de TA1..TAn na timeline
- Acesso a cada Teleaula e processamento de todos os vídeos (“Vídeo - 1..N”)
- Reprodução automática via cliques no player (**Play** + **Forward 10s** repetidamente)  
  > Estratégia “humana” e estável (sem dependência de API JS do player)
- **Skip inteligente**: se a Teleaula já estiver com **`100%`** no card (ex.: `<small>100%</small>`), o bot **pula** e vai para a próxima
- Retorno seguro para a timeline + reaplicação do filtro Teleaula entre TAs

### 5. Processamento de Seções
- Abertura de cada seção em nova aba
- Rolagem automática até o fim da página
- Detecção de carregamento dinâmico (lazy loading)
- Timeout de segurança (máximo 20 rolagens por seção)

### 6. Notificações em Tempo Real
- Progresso percentual (ex: 2/4 - 50%)
- Status de cada atividade
- Confirmação de conclusão
- Mensagens de erro quando aplicável

### 7. Gerenciamento de Recursos
- Limpeza de cache após cada atividade
- Fechamento correto do navegador
- Liberação de memória

### 8. Interface de Comandos
```
/start   - Apresentação do bot
/iniciar - Iniciar processamento de atividades
/status  - Verificar se bot está online
/ajuda   - Exibir ajuda
/cancelar - Cancelar operação em andamento
```

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                         USUÁRIO                              │
│                      (Telegram App)                          │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    │ Comandos via Telegram
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    BOT TELEGRAM                              │
│  - Recebe comandos                                           │
│  - Gerencia conversação                                      │
│  - Envia notificações                                        │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    │ Chama métodos
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                   CLASSE PortalBot                           │
│  - fazer_login()                                             │
│  - entrar_curso_agronomia()                                  │
│  - listar_disciplinas()                                      │
│  - acessar_disciplina()                                      │
│  - configurar_filtros_conteudo_web()                         │
│  - contar_atividades_cw()                                    │
│  - obter_atividade_cw_por_indice()                           │
│  - acessar_atividade()                                       │
│  - processar_todas_secoes()                                  │
│  - rolar_pagina_automaticamente()                            │
│  - voltar_para_disciplina()                                  │
│  - limpar_cache()                                            │
│  - fechar()                                                  │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    │ Controla
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                SELENIUM + CHROMEDRIVER                       │
│  - Controla o navegador Chrome                               │
│  - Executa JavaScript                                        │
│  - Interage com elementos HTML                               │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    │ Acessa
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              PORTAL COLABORAREAD                             │
│  www.colaboraread.com.br                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Configuração e Deploy

### Pré-requisitos
- Conta no GitHub
- Conta no Railway.app
- Bot do Telegram criado (via @BotFather)
- Credenciais do portal ColaboraRead

### Variáveis de Ambiente

### Execução Local (Windows/macOS/Linux) **(NOVO)**
> Recomendado para testar mudanças antes do deploy.

1. **Criar e ativar ambiente virtual**
   - Windows (PowerShell):
     ```bash
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - macOS/Linux:
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```

2. **Instalar dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar `.env`**
   - Copie `env.example` para `.env` e preencha:
     - `PORTAL_USERNAME`
     - `PORTAL_PASSWORD`
     - `TELEGRAM_TOKEN` (se for usar o modo Telegram)

4. **Executar**
   ```bash
   python bot.py
   ```

5. **Escolha do modo (CW vs TA)**
   - Ao acessar a disciplina, o bot pergunta:
     - `1) Conteúdo WEB (CW)`
     - `2) Teleaula (TA)`

6. **Headless (sem abrir janela)**
   - No código, altere a inicialização para `PortalBot(headless=True)` (ex.: em `main()`).
   - Útil para rodar em servidor / Railway.


```env
PORTAL_USERNAME=seu_cpf
PORTAL_PASSWORD=sua_senha
TELEGRAM_TOKEN=seu_token_do_telegram
```

### Estrutura de Arquivos
```
colaboraread-bot/
├── bot.py                 # Código principal
├── requirements.txt       # Dependências Python
├── README.md             # Documentação resumida
└── .gitignore            # Arquivos ignorados pelo Git
```

### Deploy no Railway

1. **Criar conta no Railway**
   - Acesse: https://railway.app
   - Login com GitHub

2. **Criar novo projeto**
   - New Project → Deploy from GitHub repo
   - Selecione o repositório

3. **Configurar variáveis**
   - Vá em "Variables"
   - Adicione as 3 variáveis de ambiente

4. **Deploy automático**
   - Railway detecta Python automaticamente
   - Instala dependências do requirements.txt
   - Inicia o bot.py

### Deploy Automático
- Todo push na branch `main` → Deploy automático
- Não precisa configuração adicional
- Logs disponíveis em tempo real

---

## 📱 Como Usar

### Passo a Passo

1. **Iniciar conversa com o bot**
   ```
   /start
   ```

2. **Iniciar processamento**
   ```
   /iniciar
   ```

3. **Aguardar login automático**
   - Bot faz login no portal
   - Acessa o curso de Agronomia

4. **Escolher disciplina**
   - Bot lista todas as disciplinas
   - Digite o número da disciplina desejada
   - Exemplo: `5` (para Ecologia Agrícola)

5. **Aguardar processamento**
   - Bot mostra progresso em tempo real:
     ```
     📊 Progresso: 1/4 (25.0%)
     📖 Cw1 - Ecologia Agrícola
     ✅ Cw1 - Ecologia Agrícola concluída!
     
     📊 Progresso: 2/4 (50.0%)
     📖 Cw2 - Ecologia Agrícola
     ✅ Cw2 - Ecologia Agrícola concluída!
     
     📊 Progresso: 3/4 (75.0%)
     ...
     
     🎉 Todas as 4 atividades concluídas!
     ```

6. **Verificar no portal**
   - Acesse o portal ColaboraRead
   - Verifique se as atividades foram marcadas como visualizadas

### Cancelar Operação
```
/cancelar
```

### Ver Status
```
/status
```

---

## ⚠️ Possíveis Erros e Soluções

### 1. Erro: "❌ Erro no login!"

**Causa:** Credenciais incorretas ou portal fora do ar

**Solução:**
1. Verifique se as variáveis de ambiente estão corretas
2. Teste fazer login manual no portal
3. Aguarde alguns minutos se o portal estiver instável

---

### 2. Erro: "❌ Nenhuma disciplina encontrada!"

**Causa:** Problemas ao carregar a página do curso

**Solução:**
1. Tente novamente após alguns minutos
2. Verifique se o curso de Agronomia está ativo na sua conta
3. Verifique os logs do Railway para mais detalhes

---

### 3. Erro: "⚠️ Nenhuma atividade CW encontrada!"

**Causa:** 
- Disciplina não tem atividades CW
- Filtros não foram aplicados corretamente

**Solução:**
1. Verifique no portal se a disciplina realmente tem atividades CW
2. Tente outra disciplina
3. Aguarde alguns minutos e tente novamente

---

### 4. Bot processa muito rápido (suspeita de não processar)

**Causa:** 
- Seções não estão sendo encontradas
- Seletores CSS mudaram no portal

**Sintomas:**
- 4 atividades em menos de 2 minutos
- Mensagens como "Nenhuma seção encontrada"

**Solução:**
1. Verifique os logs do Railway
2. Procure por mensagens: "📚 Total: X seção(ões)"
3. Se sempre mostrar "0 seções", o seletor CSS precisa ser atualizado
4. Entre em contato para atualização do código

---

### 5. Erro: "timeout: Timed out receiving message from renderer"

**Causa:** Chrome demorou muito para responder

**Impacto:** Geralmente não afeta o resultado (a atividade é concluída)

**Solução:** 
- Ignorar (é um aviso, não erro crítico)
- Se acontecer frequentemente, reportar para análise

---

### 6. Erro: "Conflict: terminated by other getUpdates request"

**Causa:** Duas instâncias do bot rodando ao mesmo tempo

**Solução:**
1. Pare o bot no Render (se ainda estiver rodando lá)
2. Mantenha apenas uma instância (Railway)
3. Reinicie o bot no Railway se necessário

---

### 7. Erro: "Memory limit exceeded"

**Causa:** Bot ultrapassou a memória disponível

**Status:** ✅ Resolvido ao migrar para Railway (8GB)

**Solução:**
- Se ocorrer no Railway: reportar (não deveria acontecer)
- Railway tem 8GB, suficiente para processar todas as atividades

---

### 8. Bot não responde no Telegram

**Possíveis causas:**
1. Bot está offline no Railway
2. Token do Telegram incorreto
3. Problema de conectividade

**Solução:**
1. Verifique se o serviço está "Active" no Railway
2. Veja os logs: deve ter "🤖 Bot iniciado!"
3. Verifique a variável TELEGRAM_TOKEN
4. Reinicie o serviço no Railway

---

### 9. Erro: "no such element: Unable to locate element"

**Causa:** Elemento HTML não foi encontrado na página

**Possíveis razões:**
- Portal mudou a estrutura HTML
- Página não carregou completamente
- Seletor CSS desatualizado

**Solução:**
1. Tente novamente após alguns segundos
2. Se persistir, reportar para atualização do código
3. Verificar se não é problema de conexão

---

## 🚀 Melhorias Futuras

### 1. Relatório Detalhado
- Número de seções processadas por atividade
- Tempo total de processamento
- Log exportável

### 2. Processamento Seletivo
- Escolher qual atividade CW processar (ex: apenas Cw1)
- Processar múltiplas disciplinas em sequência
- Modo "resumo" (apenas contar atividades)

### 3. Agendamento Automático
- Processar automaticamente novas atividades
- Notificações quando novas atividades estiverem disponíveis
- Execução em horários programados

### 4. Dashboard Web
- Visualizar histórico de processamento
- Estatísticas de uso
- Configurações via interface web

### 5. Suporte a Múltiplos Usuários
- Cada usuário com suas próprias credenciais
- Fila de processamento
- Autenticação segura

### 6. Monitoramento Avançado
- Alertas de falhas
- Métricas de performance
- Análise de logs automatizada

### 7. Modo de Validação
- Screenshots das páginas processadas
- Verificação se conteúdo foi realmente visualizado
- Relatório com evidências

---

## 🔒 Limitações Conhecidas

### 1. Dependência do Portal
- Se o portal ColaboraRead mudar a estrutura HTML, o bot pode parar de funcionar
- Requer atualização manual dos seletores CSS

### 2. Processamento Sequencial
- Processa uma disciplina por vez
- Não é possível processar múltiplas disciplinas simultaneamente

### 3. Sem Validação de Conteúdo
- Bot não verifica se o conteúdo foi realmente lido
- Apenas simula a visualização (rolagem de página)

### 4. Curso Específico
- Atualmente funciona apenas para o curso de Agronomia
- Requer adaptação para outros cursos

### 5. Tipo de Atividade
- Processa atividades do tipo **Conteúdo WEB (CW)** e **Teleaula (TA)**
- Outros tipos de atividades não são suportados

### 6. Tempo de Processamento
- Depende da velocidade de carregamento do portal
- Em média: 2-3 minutos por atividade
- Pode variar conforme conexão e carga do servidor

### 7. Custo de Hospedagem
- Railway oferece $5 grátis (trial)
- Após esgotar: ~$5-10/mês dependendo do uso
- Alternativa: hospedar localmente (grátis)

---

## 📊 Estatísticas do Projeto

### Desenvolvimento
- **Tempo total:** ~4 horas
- **Linhas de código:** ~600 linhas
- **Iterações de deploy:** 3 (Render → Render otimizado → Railway)
- **Plataformas testadas:** 2 (Render, Railway)

### Tecnologias
- **Linguagem:** Python 3.11
- **Bibliotecas principais:** 4 (Selenium, python-telegram-bot, requests, psutil)
- **Comandos do bot:** 5 (/start, /iniciar, /status, /ajuda, /cancelar)

### Performance
- **Tempo por atividade:** ~1-2 minutos
- **Memória utilizada:** ~300-400MB
- **Taxa de sucesso:** ~95% (estimado)

---

## 📞 Suporte e Manutenção

### Quando Reportar Problemas

Reporte se:
- ❌ Bot não consegue fazer login (após verificar credenciais)
- ❌ Erro "no such element" persistente
- ❌ Bot processa mas portal não marca como visualizado
- ❌ Bot fica offline constantemente
- ❌ Erros não documentados neste guia

### Informações para Reportar

Ao reportar um problema, inclua:
1. Comando utilizado
2. Mensagem de erro (screenshot ou texto)
3. Disciplina que estava processando
4. Logs do Railway (se possível)
5. Horário aproximado do erro

---

## 🎓 Conclusão

O Bot ColaboraRead é uma solução funcional e eficiente para automatizar o processamento de atividades CW no portal ColaboraRead. 

### Status Atual: ✅ **FUNCIONANDO**

**Pronto para uso:**
- ✅ Login automático
- ✅ Listagem de disciplinas
- ✅ Processamento de atividades CW
- ✅ Interface via Telegram
- ✅ Hospedado no Railway (8GB)
- ✅ Deploy automático configurado

**Próximos passos:**
- 🧪 Validação em produção com novas atividades
- 🔧 Ajustes finos conforme necessário
- 🚀 Implementação de melhorias futuras

---

## 📝 Changelog

### v1.1 (2026-02-14) - Teleaula (TA) + Menu CW/TA
- ✅ Suporte a **Teleaula (TA)** com reprodução via **Play + Forward 10s**
- ✅ Skip automático de Teleaulas já em **100%**
- ✅ Menu de execução **CW ou TA** mantendo CW intacto

### v1.0 (2025-01-20) - Release Inicial
- ✅ Sistema de autenticação
- ✅ Interface com Telegram
- ✅ Processamento de atividades CW
- ✅ Deploy no Railway
- ✅ Documentação completa

---

## 📄 Licença

Este projeto foi desenvolvido para uso pessoal/educacional.

**Aviso Legal:** Este bot foi criado para fins de automação pessoal. O uso é de responsabilidade do usuário. Certifique-se de estar em conformidade com os termos de uso do portal ColaboraRead.

---

**Desenvolvido com ❤️ em Python**

*Última atualização: Fevereiro 2026*
