# Web Scraper Intuitivo

## Overview

This project is a Streamlit-based web scraping application designed to provide an intuitive visual interface in Portuguese for extracting data from web pages. Its primary purpose is to enable users to easily configure and execute web scraping tasks, including automated and scheduled operations, without needing to write code. The application supports various extraction methods, AI-assisted selector identification, bulk processing, and data export in formats like CSV, JSON, and stylized HTML. The application aims to offer a user-friendly experience with advanced features for both single-page and multi-URL scraping, focusing on efficiency, cost-effectiveness, and robust data handling.

## User Preferences

Preferred communication style: Simple, everyday language in Portuguese (Brasil).

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for rapid development and data-focused web applications.
- **Layout**: Wide layout with a sidebar for configuration and a tab-based interface for different functionalities, all localized in Portuguese.
- **State Management**: Streamlit's session state persists loaded page data (HTML content, parsed soup object, URL) across interactions, with automatic isolation and cleanup between different operational modes (single-page vs. multi-URL).
- **UI Components**: Tabbed navigation, real-time data visualization with pandas DataFrames, and CSV/JSON/HTML export buttons. Enhanced multi-URL processing includes interactive controls for pausing/stopping and selective downloads based on checkboxes and filters.

### Backend Architecture
- **Web Scraping Stack**: `requests` for HTTP requests, `BeautifulSoup` with `lxml` parser for HTML parsing and DOM manipulation. Intelligent HTML cleaning is applied before AI processing to optimize token usage.
- **Data Processing**: `pandas` for structured data output and tabular visualization.
- **Session State Pattern**: Maintains `html_content`, `soup`, and `url` for the current scraping context.

### Extraction Methods
- **Manual Selector-Based Extraction**: Supports CSS Selectors, XPath, HTML Tags, Class, ID, and an Advanced multi-attribute extraction.
- **AI-Powered Extraction**:
    - **Identify Selectors with AI**: AI identifies reusable selectors based on natural language descriptions.
    - **Direct Data Extraction with AI**: AI directly extracts data without requiring selector identification, ideal for one-off tasks.
- **Multi-URL Workflow**: Two-phase process for loading and then processing multiple URLs with AI, offering options for applying a single set of selectors or individual AI analysis per URL. Includes robust error detection, filtering, and selective download capabilities.
- **Automated Scraping**: Intuitive task configuration, flexible scheduling (pre-defined or cron), multi-provider email notifications (SMTP, SendGrid, Resend, Gmail), CRUD task management, execution history, and persistent data storage.

### Design Decisions
- **User-Agent Spoofing**: Custom headers to mimic browser behavior and avoid blocking.
- **Error Handling**: HTTP status validation, timeout configuration, and robust JSON parsing for AI responses.
- **Parser Choice**: `lxml` chosen for speed and robustness.
- **Localization**: Full Portuguese interface.
- **Security**: Simple username/password authentication via Streamlit Secrets for restricted access.
- **API Key Management**: All API keys configured via Streamlit Secrets for security and compatibility with Streamlit Cloud.
- **Proxy Support**: Direct integration with `corsproxy.io` to bypass CORS issues and age gates, compatible with various deployment environments.
- **Optimized AI Calls**: Intelligent HTML cleaning (`clean_html_for_ai()`) removes unnecessary elements to reduce token consumption by 50-80%.
- **Enhanced Export**: HTML export includes styled, responsive card-based layout with featured images (300px), organized fields, and smart detection for image URLs and clickable links.
- **Robust Error Handling**: Bulk scraping validates HTML fetch success before extraction, displays clear error messages for failed URLs, and doesn't discard valid values like "0" or empty strings.

## External Dependencies

### Python Libraries
- **streamlit**: Web application framework.
- **requests**: HTTP client.
- **beautifulsoup4**: HTML/XML parsing.
- **lxml**: Faster XML/HTML parser backend.
- **pandas**: Data manipulation.
- **openai**: OpenAI API client.
- **anthropic**: Anthropic API client.
- **google-genai**: Google Gemini API client.

### External Services
- **Target Websites**: Web pages fetched for scraping.
- **OpenAI API**: For AI-assisted operations.
- **Anthropic API**: For AI-assisted operations.
- **Google Gemini API**: For AI-assisted operations.
- **corsproxy.io**: Used for proxying requests to bypass CORS and age gates.
- **Email Services**: SMTP, SendGrid, Resend, Gmail for automated task notifications.

### API Key Management
- **Streamlit Secrets**: `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `SESSION_SECRET`, `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` are managed via Streamlit Secrets.