# Web Scraper Intuitivo

## Overview

This project is a Streamlit-based web scraping application designed to provide an intuitive visual interface in Portuguese for extracting data from web pages. Its primary purpose is to enable users to easily configure and execute web scraping tasks, including automated and scheduled operations, without needing to write code. The application supports various extraction methods, AI-assisted selector identification, bulk processing, and data export.

## Recent Changes

### Multi-URL AI Extraction (October 30, 2025)
- ✅ **Modo Multi-URL**: Nova funcionalidade na Tab 3 (Extração com IA)
  - **Checkbox para ativar**: Permite processar múltiplas URLs de uma vez
  - **IA identifica uma vez**: IA identifica seletores na página atual
  - **Aplica em todas**: Seletores são aplicados automaticamente em todas as URLs fornecidas
  - **Resultados organizados**: Expanders individuais para cada URL com preview
  - **Download flexível**: 
    - CSV/JSON individual por URL (dados completos)
    - Download combinado de todas as URLs em um único arquivo
  - **Progress bar**: Indicador visual do progresso do processamento
  - **Função auxiliar**: `apply_selectors_to_url()` com separação de preview/dados completos
  - **Casos de uso**: Ideal para quando scraping manual falha ou para processar múltiplas páginas similares

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
