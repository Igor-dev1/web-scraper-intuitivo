# Web Scraper Intuitivo

## Overview

This is a comprehensive web scraping application built with Streamlit that allows users to extract data from web pages through an intuitive visual interface in Portuguese. The application provides multiple extraction methods (CSS selectors, XPath, HTML tags, classes, IDs, and advanced multi-attribute extraction) with HTML structure preview and data export capabilities.

## Recent Changes (October 27, 2025)

### Automated Scraping System (October 27, 2025)
- ✅ **🤖 Scraping Automático**: Full-featured automated scraping system with scheduling and email notifications
  - **Intuitive Task Configuration**: Create scraping tasks via web interface (no code needed)
    - Name task, set source URL (product launch pages), target site for search
    - Choose search method: Hybrid (Python + AI), Python only, or AI only
    - Define custom fields to extract (Title, Price, Availability, Link, Image, etc.)
  - **Flexible Scheduling**: Configure execution frequency
    - Pre-defined options: Daily, Weekly, Monthly
    - Custom cron expressions for advanced scheduling
  - **Multi-Provider Email Notifications**: Choose your preferred email service
    - **SMTP Customizado**: Full control with your own SMTP server (Gmail, Outlook, etc.)
      - Configure server, port, username, password directly in UI
      - Works with any SMTP-compatible service
    - **SendGrid Integration**: Professional transactional email service (100 emails/day free)
    - **Resend Integration**: Modern email API with simple setup
    - **Gmail Integration**: Use your Google account directly
  - **AI-Powered Extraction**: Automatic selector identification using configured AI providers
    - Supports Gemini, OpenAI, and Anthropic APIs
    - Intelligent field extraction based on natural language descriptions
    - Automatic fallback between providers if one fails
  - **Task Management**: Full CRUD operations via UI
    - View all configured tasks with details
    - Execute tasks manually on-demand (▶️ button)
    - Delete tasks when no longer needed
    - Real-time execution feedback with product preview
  - **Execution History**: Track all scraping runs
    - Success/failure status with timestamps
    - Product counts and error messages
    - Last 5 executions displayed in sidebar
  - **Data Storage**: Persistent task configuration and history
    - Tasks saved in `scraping_tasks.json`
    - Execution history in `scraping_history.json`
    - Both files excluded from git via `.gitignore`
  - **Admin-Only Access**: Restricted to master admin (igor.as0703@gmail.com)
  - **Ready for Automation**: Can be integrated with Replit's Scheduled Deployments for true cron-like automation

### Security & Authentication (October 28, 2025)
- ✅ **Simplified Login/Password Authentication**: Ultra-simple authentication system
  - **Login screen** with username and password before accessing the app
  - **Credentials configured via Replit Secrets**:
    - `ADMIN_USERNAME`: "Igonald.admin.dev"
    - `ADMIN_PASSWORD`: "Dev@2025#App!scrape"
  - **Logout button** in sidebar (🚪 Sair)
  - **Session state** maintains login during the session
  - **Note**: Removed Replit Auth integration completely due to incompatibility
    - Replit Auth doesn't work with Streamlit's WebSocket-based server
    - Simple username/password provides functional authentication
  - Single admin user with full access to all features
  - All scraping automation features available after login

### Code Optimization (October 27, 2025)
- ✅ **Added 5th tab for automation**: Expanded to 5 tabs with new automated scraping features
  - Tabs: Estrutura HTML, Extração com IA, Scraping em Massa, Validador de Seletores, **Scraping Automático**
  - Clean, modular code structure with dedicated functions for scraping automation
  - ~1760 lines with comprehensive automation features

### HTML Upload & Bulk Processing (October 27, 2025)
- ✅ **Multiple HTML file upload support**: Process multiple HTML files simultaneously in Scraping em Massa
  - Upload several saved HTML files at once (from Ctrl+S or Ctrl+U → Save)
  - Apply AI-identified selectors to all uploaded files
  - Perfect for JavaScript-heavy sites (Steam, Amazon) where Python requests can't execute JS
  - Results show source filename for easy identification

### Improved Visualization (October 27, 2025)
- ✅ **Enhanced HTML rendering**: Fixed overlapping issues in "Visualização Melhorada"
  - Proper CSS spacing with `display: block` and `clear: both`
  - Correct margins for h1-h6, paragraphs, and images
  - Images display inline with text when appropriate (using keyword detection)
  - HD image quality: prioritizes data-src/data-screenshot over src for better resolution

### MVP Completion
- ✅ Added HTML structure preview tab showing page statistics, available tags, classes, and IDs
- ✅ Implemented XPath extraction support alongside CSS selectors
- ✅ All 7 extraction methods fully functional and tested
- ✅ Complete Portuguese interface with intuitive design
- ✅ CSV and JSON download functionality for all extraction methods

### Advanced Features Added
- ✅ **Extração com IA**: AI-assisted extraction using OpenAI (ChatGPT/gpt-5), Anthropic (Claude Sonnet 4), or Google (Gemini 2.5)
  - Natural language description of what to extract
  - Automatic identification of CSS/XPath selectors by AI
  - Support for multiple AI providers with flexible API key management
  - Detailed explanations and examples for suggested selectors
  - **NEW**: Checkbox selection for multiple selectors
  - **NEW**: Single button to copy all selected selectors at once
  - **NEW**: Results persist across page refreshes
  - **FIXED**: Anthropic API JSON parsing error resolved
- ✅ **Scraping em Massa**: Bulk scraping of multiple URLs simultaneously
  - Process multiple URLs with same selectors in one operation
  - Support for all extraction methods (CSS, XPath, Tag, Class)
  - Progress tracking with visual feedback
  - Consolidated results with URL identification
  - Single CSV/JSON download for all extracted data

### Bug Fixes (October 27, 2025)
- ✅ Fixed Anthropic Claude API JSON parsing error by properly concatenating response content blocks
- ✅ Removed copy buttons that caused UI collapse when clicked
- ✅ Improved UX: AI results now persist in session state, allowing users to interact with checkboxes without losing results
- ✅ Added "Limpar" button to clear AI results and start fresh queries

### Major UX Improvements (October 27, 2025)
- ✅ **Auto-extraction in AI tab**: AI now automatically extracts data using ALL identified selectors - no manual copying needed!
  - Shows consolidated results table immediately after AI identifies selectors
  - Direct CSV/JSON download from AI tab
  - Selector details preserved in collapsible expander for reference
  - **Clean copy button**: Copy ONLY the selector strings (no comments, no descriptions) - one selector per line
- ✅ **AI selectors in bulk scraping**: Use AI-identified selectors to process multiple similar pages
  - Checkbox to "Use AI selectors" in Scraping em Massa tab (defaults to checked when AI selectors available)
  - Automatically applies ALL AI selectors to every URL
  - One-click extraction of multiple fields from multiple pages
- ✅ **Universal Selector Testing (NEW Tab)**: Test multiple mixed selectors at once
  - Accepts CSS and XPath selectors mixed together (one per line)
  - Auto-detects selector type: XPath (`//`, `/`, `./`, `::`, etc.) vs CSS
  - Tests all selectors simultaneously
  - Shows results: selector, type, count, first value
  - CSV/JSON download available

## User Preferences

Preferred communication style: Simple, everyday language in Portuguese (Brasil).

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - chosen for rapid development of data-focused web applications with minimal frontend code
- **Layout**: Wide layout configuration for better data visualization and workspace
- **State Management**: Streamlit's session state pattern is used to persist loaded page data (HTML content, parsed soup object, and URL) across user interactions
- **UI Components**: 
  - Sidebar-based configuration panel for URL input and page loading controls
  - Tab-based interface with 7 extraction methods
  - Real-time data visualization with pandas DataFrames
  - Download buttons for CSV and JSON export

### Backend Architecture
- **Web Scraping Stack**:
  - **requests**: HTTP library for fetching web page content with custom headers to mimic browser behavior
  - **BeautifulSoup (lxml parser)**: Primary HTML parsing library for CSS selector-based DOM manipulation and data extraction
  - **lxml**: High-performance XML/HTML parser used for XPath support and as the parsing backend
- **Data Processing**: pandas for structured data output and tabular visualization
- **Session State Pattern**: Maintains three key states:
  1. `html_content`: Raw HTML text from the fetched page
  2. `soup`: Parsed BeautifulSoup object for DOM traversal
  3. `url`: Current URL being scraped

### Extraction Methods
1. **Estrutura HTML**: Displays page statistics, all available tags, CSS classes, and IDs with HTML preview
2. **Seletor CSS**: Extract elements using CSS selectors (e.g., `div.produto`, `#header > p`)
3. **XPath**: Extract elements or attributes using XPath expressions (e.g., `//h1`, `//a/@href`)
4. **Tag HTML**: Extract all elements of a specific HTML tag
5. **Classe**: Extract elements by CSS class name
6. **ID**: Extract specific element by ID
7. **Avançado**: Multi-attribute extraction with customizable options
8. **Extração com IA**: AI-powered selector identification based on natural language descriptions
9. **Scraping em Massa**: Batch processing of multiple URLs with identical selectors
10. **Teste Universal**: Test multiple mixed selectors (CSS and XPath) simultaneously on the loaded page
11. **Scraping Automático**: Configure automated scraping tasks with scheduling and email notifications (admin only)

### Design Decisions
- **User-Agent Spoofing**: Custom headers mimic a real browser to avoid being blocked by websites that detect scrapers
- **Error Handling**: HTTP status validation with `raise_for_status()` to catch failed requests
- **Timeout Configuration**: 10-second timeout prevents hanging on unresponsive websites
- **Parser Choice**: lxml parser selected for speed and robustness over html.parser
- **XPath Implementation**: Handles both element nodes and attribute nodes correctly, displaying results in appropriate columns
- **Portuguese Interface**: All UI text, messages, and examples in Portuguese for Brazilian users

## External Dependencies

### Python Libraries
- **streamlit**: Web application framework for the user interface
- **requests**: HTTP client for fetching web pages
- **beautifulsoup4**: HTML/XML parsing and DOM manipulation
- **lxml**: XML/HTML parser backend (faster than default html.parser)
- **pandas**: Data manipulation and structured output
- **replit**: Replit Auth integration for secure authentication
- **openai**: OpenAI API client for GPT-5 model (AI-assisted extraction)
- **anthropic**: Anthropic API client for Claude Sonnet 4 (AI-assisted extraction)
- **google-genai**: Google Gemini API client for Gemini 2.5 (AI-assisted extraction)

### External Services
- **External websites**: Accessed via user-provided URLs with custom User-Agent headers
- **OpenAI API** (optional): For AI-assisted selector identification - requires OPENAI_API_KEY
- **Anthropic API** (optional): For AI-assisted selector identification - requires ANTHROPIC_API_KEY
- **Google Gemini API** (optional): For AI-assisted selector identification - requires GEMINI_API_KEY

### API Key Management (Hybrid System)
- **Hybrid approach**: Prioritizes Replit Secrets, allows custom keys via interface
- **Replit Secrets** (most secure): Managed via Tools → Secrets panel
- **Custom Keys** (convenient): Admin can add/remove via "🔑 Gerenciar API Keys" in sidebar
  - Add key: Name + Value → Save
  - Remove key: Click 🗑️ button
  - Keys masked in display (e.g., `sk-...xyz`)
  - Stored in `api_keys.json` (excluded from git via `.gitignore`)
- **Priority system**: Replit Secrets override custom keys with same name
- **UI indication**: Shows source (Replit Secrets 🔒 or Custom 🔑)
- **Security**: Only admin master can view/manage API keys
- Users can choose between different AI providers based on preference and availability

### Authentication & Security
- **Replit Auth**: Built-in authentication restricts app access to authorized users only
- **Access Control**: Email-based allowlist with persistent JSON file storage (`authorized_emails.json`)
- **Admin Panel**: Master admin can manage user access via web interface (no code editing needed)
  - Add users: Enter email → Click "Adicionar Acesso"
  - Remove users: Click 🗑️ button next to user email
  - View all users: List shows admin (👑) and regular users (✉️)
  - Protection: Master admin email cannot be removed for security
- **Master Admin**: igor.as0703@gmail.com (hardcoded in `ADMIN_EMAIL` constant)
- **Login Methods**: Users can authenticate via Google, GitHub, X, Apple, or Email
- **Session Management**: Handled automatically by Replit Auth infrastructure
- **Development & Production**: Auth works seamlessly in both environments (.replit.dev and .replit.app)