# Web Scraper Intuitivo

## Overview

This project is a Streamlit-based web scraping application designed to provide an intuitive visual interface in Portuguese for extracting data from web pages. Its primary purpose is to enable users to easily configure and execute web scraping tasks, including automated and scheduled operations, without needing to write code. The application supports various extraction methods, AI-assisted selector identification, bulk processing, and data export.

## Recent Changes

### HTML Optimization & Processing Controls (October 30, 2025)
- ✅ **Limpeza Inteligente de HTML**: Sistema de otimização para reduzir custos de API
  - **Função `clean_html_for_ai()`**: Remove elementos desnecessários mantendo conteúdo importante
  - **Remove**:
    - Scripts JavaScript (`<script>`)
    - Estilos CSS (`<style>`, atributos `style`)
    - Comentários HTML
    - Atributos de eventos (onclick, onload, etc.)
    - Tags inúteis (noscript, iframes externos)
    - Tracking/analytics (data-gtm, data-analytics)
  - **Mantém**:
    - Links (href)
    - Imagens (src, alt)
    - GIFs e vídeos do YouTube/Vimeo
    - Estrutura (classes, IDs)
    - Atributos de dados (data-*)
    - Conteúdo de texto completo
  - **Economia**: 50-80% menos tokens nas chamadas de IA
  - **Aplicado em**:
    - `extract_with_ai()` (Identificar Seletores)
    - `extract_data_directly_with_ai()` (Extração Direta)
    - Ambos os modos Multi-URL

- ✅ **Controles de Processamento Multi-URL**: Pausar/Parar durante processamento em massa
  - **Botões de Controle**:
    - **⏸️ Pausar**: Pausa o processamento, permite retomar de onde parou
    - **⏹️ Parar**: Interrompe completamente, salva progresso parcial
    - **▶️ Retomar**: Continua processamento do ponto exato onde pausou
  - **Session State**:
    - `processing_control`: Status ('running', 'paused', 'stopped', 'completed')
    - `processing_results`: Resultados parciais salvos
    - `processing_index`: Índice da última URL processada
  - **Benefícios UX**:
    - Usuário pode parar processamento de 1000 URLs se perceber erro
    - Não perde progresso ao pausar - pode retomar depois
    - Evita desperdício de créditos de API em processamentos incorretos
    - Controle total sobre operações longas

- ✅ **Correção: Método de Extração no Multi-URL**: Proxy agora funciona corretamente
  - **Problema Resolvido**: Multi-URL ignorava seleção "Proxy CORS" e usava sempre Python direto
  - **Solução**: `loading_method` da sidebar agora salvo em `st.session_state.extraction_method`
  - **Resultado**: Age gates (Steam, etc.) contornados automaticamente em Multi-URL
  - **Cookies de Age Gate**: Adicionados diretamente em `fetch_html()` para Steam
    - `wants_mature_content`, `birthtime`, `lastagecheckage`, `mature_content`
  - **Proxy CORS**: Chama corsproxy.io DIRETAMENTE (sem servidor local)
    - Funciona em **Replit** e **Streamlit Cloud**
    - Não depende mais do `proxy_server.py` rodando
    - Compatível com deploy em qualquer plataforma

- ✅ **Explicação da IA Restaurada no Multi-URL**: Mensagens em azul voltaram
  - **Campos `ai_explanation`** adicionados nos resultados Multi-URL:
    - Modo "Identificar Seletores": mostra `explicacao` da IA
    - Modo "Extrair Direto": mostra `resumo` da IA
  - **Exibição**: Box azul com 💡 acima de cada URL processada
  - **Conteúdo**: Explica quantos campos foram encontrados vs solicitados

### State Management Isolation (October 30, 2025)
- ✅ **Isolamento de Estados**: Sistema de limpeza automática para evitar mistura de dados
  - **Problema Resolvido**: Dados de operações anteriores não aparecem mais em novos processamentos
  - **Funções Helper**:
    - `reset_single_extraction()`: Limpa resultados de página única
    - `reset_multi_url_extraction()`: Limpa resultados multi-URL
  - **Limpeza Automática**:
    - Ao ativar multi-URL: limpa resultados de página única (ai_result, ai_direct_result)
    - Ao desativar multi-URL: limpa resultados multi-URL (multi_url_results, loaded_urls)
    - Ao carregar novas URLs: limpa resultados anteriores
  - **Detecção de Mudança**: Compara estado anterior com atual via `previous_multi_url_mode`
  - **Benefícios UX**:
    - Cada modo opera isoladamente sem interferência
    - Workflow mais previsível e intuitivo
    - Sem confusão entre dados de diferentes operações

### AI Direct Data Extraction (October 30, 2025)
- ✅ **Extração Direta com IA**: Novo modo de IA que extrai dados sem identificar seletores
  - **Dois Botões na Tab 3**:
    - **🔍 Identificar Seletores com IA**: Modo original (gera seletores reutilizáveis)
    - **⚡ Extrair Dados Direto com IA**: Modo novo (extração direta, mais rápido)
  - **Vantagens da Extração Direta**:
    - Mais rápido para consultas únicas
    - Mais econômico (menos tokens)
    - Ideal para páginas que mudam frequentemente
    - Não requer aplicar seletores manualmente
  - **Formato de Resposta**:
    - JSON estruturado com campos, valores e status
    - Tabela visual com resultados
    - Downloads em CSV e JSON
  - **Robustez**:
    - Validação de JSON na resposta da IA
    - Fallback para provedores não reconhecidos
    - Tratamento de erros detalhado
  - **Benefícios UX**:
    - Escolhe entre velocidade (direto) ou reutilização (seletores)
    - Interface clara mostrando diferença entre os dois modos
    - Resultados imediatos sem etapas intermediárias

### Enhanced Bulk Scraping with Selective Downloads (October 30, 2025)
- ✅ **Scraping em Massa Aprimorado**: Sistema completo de seleção e filtragem de resultados
  - **Detecção Automática de Problemas**:
    - Identifica URLs com campos vazios, 'nan', 'none' ou erros
    - Métricas visuais: Total URLs, URLs Completas, URLs com Problemas
    - Indicadores visuais (✅/⚠️) em cada URL
  - **Sistema de Filtros**:
    - 📋 Todas as URLs
    - ✅ Apenas URLs Completas
    - ⚠️ Apenas URLs com Problemas
  - **Seleção Individual por URL**:
    - Checkbox em cada URL para marcar/desmarcar
    - Botões "Marcar Todas (Filtradas)" e "Desmarcar Todas"
    - Contador dinâmico de URLs selecionadas
    - Preview expandable de problemas específicos em cada URL
  - **Downloads Seletivos**:
    - CSV/JSON apenas das URLs selecionadas
    - Download individual quando só 1 URL está marcada
    - Nome de arquivo automático baseado no número de URLs
    - Opção separada para baixar TODAS as URLs (não filtrado)
  - **Session State Management**:
    - Resultados salvos em `st.session_state.bulk_results`
    - Seleção resetada automaticamente a cada novo scraping
    - Todas as URLs novas ficam marcadas por padrão
  - **Benefícios UX**:
    - Vê imediatamente quais URLs tiveram problemas
    - Pode baixar só as URLs que funcionaram
    - Não precisa baixar tudo quando só quer algumas URLs
    - Filtros rápidos para encontrar problemas

### Two-Phase Multi-URL Workflow (October 30, 2025)
- ✅ **Workflow em Duas Etapas**: Refatoração completa do Modo Multi-URL para melhor UX
  - **ETAPA 1: Carregar URLs**:
    - Campo de texto para inserir múltiplas URLs (uma por linha)
    - Botão "📥 Carregar URLs" com barra de progresso
    - Tabela visual com status de cada URL carregada (✅/❌)
    - Checkboxes para selecionar quais URLs processar com IA
    - URLs carregadas ficam em memória (session_state) até limpeza manual
  - **ETAPA 2: Processar com IA** (só aparece após carregar URLs):
    - Mostra contador de URLs selecionadas
    - Radio buttons para escolher estratégia:
      - **⚡ Mesmos seletores (rápido)**: IA analisa página atual e aplica em todas
      - **🎯 Seletores individuais (preciso)**: IA analisa cada URL separadamente
    - Botão "🤖 Processar URLs Selecionadas com IA"
    - Barra de progresso durante processamento
  - **Funções Helper Compartilhadas**:
    - `fetch_html(url, extraction_method, timeout)`: Fonte única de verdade para HTTP requests
    - `load_urls(urls, extraction_method, timeout)`: Carrega múltiplas URLs com status
  - **Refatorações Técnicas**:
    - `apply_selectors_to_url()` e `apply_ai_per_url()` agora usam `fetch_html()` internamente
    - Eliminada duplicação de código de requisições HTTP
    - Método de extração (Python/Proxy) respeitado em todas as operações
  - **Benefícios UX**:
    - Usuário vê quais URLs carregaram com sucesso antes de gastar créditos de IA
    - Pode desmarcar URLs com erro antes de processar
    - Workflow mais intuitivo e previsível
    - Menos surpresas e mais controle sobre o processo

### Migration to Streamlit Cloud (October 28, 2025)
- ✅ **Simplified API Key Management**: Removed custom API key management panel
  - **Environment-only**: All API keys now configured via Streamlit Secrets
  - **Removed**: Custom API key management UI (not compatible with Streamlit Cloud)
  - **Configuration**: Set API keys in Streamlit Cloud Settings → Secrets
  - Required secrets:
    - `ADMIN_USERNAME`: Login username
    - `ADMIN_PASSWORD`: Login password
    - `SESSION_SECRET`: Random string for session encryption
    - `GEMINI_API_KEY` (optional): Google Gemini API key
    - `OPENAI_API_KEY` (optional): OpenAI API key
    - `ANTHROPIC_API_KEY` (optional): Anthropic Claude API key
- ✅ **GitHub Integration**: Project synced to https://github.com/Igor-dev1/web-scraper-intuitivo
- ✅ **Platform Migration**: Moved from Replit to Streamlit Community Cloud for free hosting
- ✅ **Updated Documentation**: Removed references to Replit-specific features

## User Preferences

Preferred communication style: Simple, everyday language in Portuguese (Brasil).

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for rapid development and data-focused web applications.
- **Layout**: Wide layout with a sidebar for configuration and a tab-based interface for different functionalities.
- **State Management**: Streamlit's session state persists loaded page data (HTML content, parsed soup object, URL) across interactions.
- **UI Components**: Tabbed navigation, real-time data visualization with pandas DataFrames, and CSV/JSON export buttons.

### Backend Architecture
- **Web Scraping Stack**: `requests` for HTTP requests, `BeautifulSoup` with `lxml` parser for HTML parsing and DOM manipulation.
- **Data Processing**: `pandas` for structured data output and tabular visualization.
- **Session State Pattern**: Maintains `html_content`, `soup`, and `url` for the current scraping context.

### Extraction Methods
The application offers various extraction methods:
- **Estrutura HTML**: HTML structure preview with page statistics, tags, classes, and IDs.
- **Seletor CSS**: Extract elements using CSS selectors.
- **XPath**: Extract elements or attributes using XPath expressions.
- **Tag HTML**: Extract all elements of a specified HTML tag.
- **Classe**: Extract elements by CSS class name.
- **ID**: Extract an element by its ID.
- **Avançado**: Multi-attribute extraction with customizable options.
- **Extração com IA**: AI-powered selector identification based on natural language descriptions, supporting multiple AI providers.
  - **Modo Multi-URL**: Apply AI-identified selectors across multiple URLs in batch, with individual and combined download options.
- **Scraping em Massa**: Batch processing of multiple URLs with the same selectors.
- **Teste Universal**: Test multiple mixed CSS and XPath selectors simultaneously.
- **Scraping Automático**: Automated scraping tasks with scheduling, email notifications, and admin-only access.

### Design Decisions
- **User-Agent Spoofing**: Custom headers to mimic browser behavior and avoid blocking.
- **Error Handling**: HTTP status validation and timeout configuration for robust requests.
- **Parser Choice**: `lxml` chosen for speed and robustness.
- **Localization**: Full Portuguese interface for Brazilian users.
- **Security**: Simple username/password authentication via Streamlit Secrets for restricted access.
- **Simplified API Key Management**: All API keys configured via environment variables (Streamlit Secrets) only.
- **Automated Scraping System**: Intuitive task configuration, flexible scheduling (pre-defined or cron), multi-provider email notifications (SMTP, SendGrid, Resend, Gmail), AI-powered selector identification, CRUD task management, execution history, and persistent data storage (`scraping_tasks.json`, `scraping_history.json`).

## External Dependencies

### Python Libraries
- **streamlit**: Web application framework.
- **requests**: HTTP client.
- **beautifulsoup4**: HTML/XML parsing.
- **lxml**: Faster XML/HTML parser backend.
- **pandas**: Data manipulation.
- **openai**: OpenAI API client for AI assistance.
- **anthropic**: Anthropic API client for AI assistance.
- **google-genai**: Google Gemini API client for AI assistance.

### External Services
- **External websites**: Web pages fetched for scraping.
- **OpenAI API**: For AI-assisted selector identification (requires `OPENAI_API_KEY`).
- **Anthropic API**: For AI-assisted selector identification (requires `ANTHROPIC_API_KEY`).
- **Google Gemini API**: For AI-assisted selector identification (requires `GEMINI_API_KEY`).
- **Email Services**: SMTP, SendGrid, Resend, Gmail for automated task notifications.

### API Key Management
- **Streamlit Secrets**: All API keys and administrative credentials (`ADMIN_USERNAME`, `ADMIN_PASSWORD`, `SESSION_SECRET`) are configured via Streamlit Secrets for security.
- **No Local Storage**: API keys are not stored in local files for compatibility with Streamlit Cloud.

## Deployment

### Streamlit Community Cloud
The application is designed to be deployed on Streamlit Community Cloud:
1. Connect GitHub repository
2. Configure Secrets in Settings
3. Deploy with `app.py` as main file
4. Free hosting with automatic restarts
