import streamlit as st
import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
import json
import os
import re
from io import StringIO
from lxml import html as lxml_html
from lxml import etree
from urllib.parse import quote_plus

# Requests-HTML removido - não funciona com Streamlit threading

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# 🔑 GERENCIAMENTO SIMPLIFICADO DE API KEYS
def get_secret(key_name, default=None):
    """
    Obtém secret de forma compatível com Replit e Streamlit Cloud
    Tenta st.secrets primeiro (Streamlit Cloud), depois os.environ (Replit)
    """
    try:
        # Streamlit Cloud: usa st.secrets
        return st.secrets.get(key_name, default)
    except:
        # Replit: usa variáveis de ambiente
        return os.environ.get(key_name, default)

def get_api_key(key_name):
    """
    Obtém API key (wrapper para compatibilidade)
    """
    return get_secret(key_name)

def generate_html_table(data, title="Dados Extraídos", url=None):
    """
    Gera HTML bonito e formatado a partir dos dados
    
    Args:
        data: DataFrame ou lista de dicts com os dados
        title: Título da página HTML
        url: URL de origem (opcional)
    
    Returns:
        str: HTML formatado pronto para download
    """
    # Converter para DataFrame se necessário
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data
    
    # Construir HTML
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .content {{
            padding: 30px;
        }}
        .url-info {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 25px;
            border-left: 4px solid #667eea;
        }}
        .url-info strong {{
            color: #667eea;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            min-width: 150px;
            margin: 10px;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }}
        .stat-card h3 {{
            font-size: 2em;
            margin-bottom: 5px;
        }}
        .stat-card p {{
            opacity: 0.9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 0.5px;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        tbody tr {{
            transition: background 0.3s ease;
        }}
        tbody tr:hover {{
            background: #f5f5f5;
        }}
        tbody tr:nth-child(even) {{
            background: #fafafa;
        }}
        tbody tr:nth-child(even):hover {{
            background: #f0f0f0;
        }}
        a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #888;
            font-size: 0.9em;
            border-top: 1px solid #e0e0e0;
        }}
        img {{
            max-width: 100px;
            max-height: 100px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 {title}</h1>
            <p>Dados extraídos com Web Scraper Intuitivo</p>
        </div>
        <div class="content">
"""
    
    # Adicionar URL se fornecida
    if url:
        html += f"""
            <div class="url-info">
                <strong>📍 URL:</strong> <a href="{url}" target="_blank">{url}</a>
            </div>
"""
    
    # Adicionar estatísticas
    html += f"""
            <div class="stats">
                <div class="stat-card">
                    <h3>{len(df)}</h3>
                    <p>Registros</p>
                </div>
                <div class="stat-card">
                    <h3>{len(df.columns)}</h3>
                    <p>Campos</p>
                </div>
            </div>
"""
    
    # Adicionar tabela
    html += """
            <table>
                <thead>
                    <tr>
"""
    
    for col in df.columns:
        html += f"                        <th>{col}</th>\n"
    
    html += """
                    </tr>
                </thead>
                <tbody>
"""
    
    for _, row in df.iterrows():
        html += "                    <tr>\n"
        for col in df.columns:
            value = row[col]
            # Detectar URLs de imagens e renderizar como <img>
            if isinstance(value, str) and (value.startswith('http') and any(ext in value.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])):
                html += f'                        <td><img src="{value}" alt="Imagem"></td>\n'
            # Detectar URLs normais e tornar clicáveis
            elif isinstance(value, str) and value.startswith('http'):
                html += f'                        <td><a href="{value}" target="_blank">{value[:50]}...</a></td>\n'
            else:
                html += f"                        <td>{value}</td>\n"
        html += "                    </tr>\n"
    
    html += """
                </tbody>
            </table>
        </div>
        <div class="footer">
            <p>Gerado automaticamente pelo Web Scraper Intuitivo 🚀</p>
        </div>
    </div>
</body>
</html>"""
    
    return html

def clean_html_for_ai(html_content):
    """
    Limpa HTML removendo elementos inúteis para IA, mas mantém:
    - Links (href)
    - Imagens (src, alt)
    - Conteúdo de texto
    - Estrutura (classes, IDs)
    - Atributos de dados (data-*)
    
    Remove:
    - Scripts JavaScript
    - Estilos CSS
    - Comentários HTML
    - Atributos de eventos (onclick, onload, etc.)
    - Tags inúteis (noscript, iframe embed externos)
    
    Economia estimada: 50-80% de tokens
    """
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Remover scripts, styles, noscript
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()
        
        # Remover comentários HTML (bs4.element.Comment)
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # Remover iframes externos (mantém vídeos do YouTube, etc que podem ter info)
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src', '')
            # Manter só iframes de vídeo conhecidos
            if not any(domain in src for domain in ['youtube.com', 'vimeo.com', 'dailymotion.com']):
                iframe.decompose()
        
        # Remover atributos de eventos e outros inúteis
        # MANTÉM: href, src, alt, class, id, data-*, aria-*, title, name, value, type, placeholder
        for tag in soup.find_all(True):
            attrs_to_remove = []
            for attr in tag.attrs:
                # Remover eventos (onclick, onload, etc.)
                if attr.startswith('on'):
                    attrs_to_remove.append(attr)
                # Remover atributos de estilo inline
                elif attr == 'style':
                    attrs_to_remove.append(attr)
                # Remover tracking e analytics
                elif attr in ['data-gtm', 'data-analytics', 'data-track']:
                    attrs_to_remove.append(attr)
            
            for attr in attrs_to_remove:
                del tag[attr]
        
        return str(soup)
    
    except Exception as e:
        # Se der erro na limpeza, retorna HTML original
        return html_content

def fetch_html(url, extraction_method='python', timeout=10):
    """
    Função helper para fazer request e baixar HTML de uma URL
    
    Args:
        url: URL para fazer scraping
        extraction_method: 'python' ou 'proxy' - método de extração do HTML
        timeout: Timeout para requisição
    
    Returns:
        dict: {'url': url, 'html_content': html, 'status': 'success'/'error', 'error': None/mensagem}
    """
    try:
        if extraction_method == 'proxy':
            # Usar corsproxy.io DIRETAMENTE (funciona em Replit e Streamlit Cloud)
            proxy_url = f'https://corsproxy.io/?{url}'
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            
            # Se for Steam, adicionar cookies de age gate
            cookies = {}
            if 'steampowered.com' in url:
                cookies = {
                    'wants_mature_content': '1',
                    'birthtime': '631152000',
                    'lastagecheckage': '1-0-1990',
                    'mature_content': '1'
                }
            
            response = requests.get(proxy_url, headers=headers, cookies=cookies, timeout=timeout)
            response.raise_for_status()
            html_content = response.text
        else:
            # Usar Python direto
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            
            # Se for Steam, adicionar cookies de age gate mesmo no modo Python
            cookies = {}
            if 'steampowered.com' in url:
                cookies = {
                    'wants_mature_content': '1',
                    'birthtime': '631152000',
                    'lastagecheckage': '1-0-1990',
                    'mature_content': '1'
                }
            
            response = requests.get(url, headers=headers, cookies=cookies, timeout=timeout)
            response.raise_for_status()
            html_content = response.text
        
        return {
            'url': url,
            'html_content': html_content,
            'status': 'success',
            'error': None
        }
    except Exception as e:
        return {
            'url': url,
            'html_content': None,
            'status': 'error',
            'error': str(e)
        }

def load_urls(urls, extraction_method='python', timeout=10):
    """
    Carrega múltiplas URLs e retorna status de cada uma
    
    Args:
        urls: Lista de URLs para carregar
        extraction_method: 'python' ou 'proxy'
        timeout: Timeout para cada requisição
    
    Returns:
        list: Lista de dicts com url, html_content, status, error
    """
    results = []
    for url in urls:
        result = fetch_html(url, extraction_method, timeout)
        results.append(result)
    return results

def apply_selectors_to_url(url, seletores, timeout=10, extraction_method='python'):
    """
    Aplica seletores identificados pela IA em uma URL específica
    
    Args:
        url: URL para fazer scraping
        seletores: Lista de seletores identificados pela IA
        timeout: Timeout para requisição
        extraction_method: 'python' ou 'proxy' - método de extração do HTML
    
    Returns:
        dict: {
            'url': url,
            'data_preview': lista com preview dos dados (para exibição),
            'data_full': lista com TODOS os valores estruturados por linha (para download),
            'error': None
        }
    """
    try:
        # Baixar HTML usando fetch_html
        fetch_result = fetch_html(url, extraction_method, timeout)
        
        if fetch_result['status'] == 'error':
            return {'url': url, 'data_preview': None, 'data_full': None, 'error': fetch_result['error']}
        
        html_content = fetch_result['html_content']
        soup = BeautifulSoup(html_content, 'lxml')
        
        data_preview = []
        all_valores = {}  # {descricao: [valores]}
        
        for sel in seletores:
            seletor = sel.get('seletor', '')
            tipo = sel.get('tipo', 'css')
            descricao = sel.get('descricao', 'Campo')
            
            try:
                extrair_html = any(palavra in descricao.lower() for palavra in ['imagem', 'imagens', 'gif', 'gifs', 'completa', 'completo', 'html', 'screenshot', 'media'])
                
                if tipo == 'css':
                    elements = soup.select(seletor)
                    valores = []
                    for elem in elements:
                        valor = extract_element_value(elem, seletor, tipo='css', extrair_html=extrair_html)
                        if valor:
                            valores.append(valor)
                elif tipo == 'xpath':
                    tree = lxml_html.fromstring(html_content)
                    elements = tree.xpath(seletor)
                    is_xpath_attr = isinstance(elements[0], str) if elements else False
                    valores = []
                    for elem in elements:
                        valor = extract_element_value(elem, seletor, tipo='xpath', is_xpath_attr=is_xpath_attr, extrair_html=extrair_html)
                        if valor:
                            valores.append(valor)
                else:
                    valores = []
                
                # Armazenar valores para estruturação posterior
                all_valores[descricao] = valores
                
                # Preview: resumo para exibição na tela
                if valores:
                    data_preview.append({
                        'Campo': descricao,
                        'Valor': valores[0] if len(valores) == 1 else ', '.join(str(v)[:100] for v in valores[:3]) + ('...' if len(valores) > 3 else ''),
                        'Total Encontrado': len(valores)
                    })
                else:
                    data_preview.append({
                        'Campo': descricao,
                        'Valor': 'Nenhum resultado',
                        'Total Encontrado': 0
                    })
            except Exception as e:
                all_valores[descricao] = []
                data_preview.append({
                    'Campo': descricao,
                    'Valor': f'Erro: {str(e)}',
                    'Total Encontrado': 0
                })
        
        # Estruturar data_full: criar linhas com todos os campos
        # Cada linha representa um conjunto de valores alinhados por índice
        data_full = []
        if all_valores:
            max_len = max(len(v) for v in all_valores.values())
            for i in range(max_len):
                row = {}
                for descricao, valores in all_valores.items():
                    row[descricao] = valores[i] if i < len(valores) else ''
                data_full.append(row)
        
        return {'url': url, 'data_preview': data_preview, 'data_full': data_full, 'error': None}
    except Exception as e:
        return {'url': url, 'data_preview': None, 'data_full': None, 'error': str(e)}

def apply_ai_per_url(url, user_query, ai_provider, api_key, timeout=10, extraction_method='python'):
    """
    Analisa uma URL individualmente com IA e extrai os dados
    
    Args:
        url: URL para processar
        user_query: Descrição do que extrair
        ai_provider: Provedor de IA (OpenAI, Anthropic, Gemini)
        api_key: API key do provedor
        timeout: Timeout para requisição
        extraction_method: 'python' ou 'proxy' - método de extração do HTML
    
    Returns:
        dict: {
            'url': url,
            'data_preview': lista com preview dos dados,
            'data_full': lista com dados completos,
            'ai_explanation': explicação da IA,
            'error': None ou mensagem de erro
        }
    """
    try:
        # 1. Baixar HTML usando fetch_html
        fetch_result = fetch_html(url, extraction_method, timeout)
        
        if fetch_result['status'] == 'error':
            return {
                'url': url,
                'data_preview': None,
                'data_full': None,
                'ai_explanation': None,
                'error': fetch_result['error']
            }
        
        html_content = fetch_result['html_content']
        
        # 2. Chamar IA para identificar seletores
        ai_result = extract_with_ai(html_content, user_query, ai_provider, api_key)
        
        if "error" in ai_result:
            return {
                'url': url,
                'data_preview': None,
                'data_full': None,
                'ai_explanation': None,
                'error': f"Erro na IA: {ai_result['error']}"
            }
        
        # 3. Extrair dados usando os seletores identificados
        soup = BeautifulSoup(html_content, 'lxml')
        
        data_preview = []
        all_valores = {}
        
        for sel in ai_result.get('seletores', []):
            seletor = sel.get('seletor', '')
            tipo = sel.get('tipo', 'css')
            descricao = sel.get('descricao', 'Campo')
            
            try:
                extrair_html = any(palavra in descricao.lower() for palavra in ['imagem', 'imagens', 'gif', 'gifs', 'completa', 'completo', 'html', 'screenshot', 'media'])
                
                if tipo == 'css':
                    elements = soup.select(seletor)
                    valores = []
                    for elem in elements:
                        valor = extract_element_value(elem, seletor, tipo='css', extrair_html=extrair_html)
                        if valor:
                            valores.append(valor)
                elif tipo == 'xpath':
                    tree = lxml_html.fromstring(html_content)
                    elements = tree.xpath(seletor)
                    is_xpath_attr = isinstance(elements[0], str) if elements else False
                    valores = []
                    for elem in elements:
                        valor = extract_element_value(elem, seletor, tipo='xpath', is_xpath_attr=is_xpath_attr, extrair_html=extrair_html)
                        if valor:
                            valores.append(valor)
                else:
                    valores = []
                
                all_valores[descricao] = valores
                
                if valores:
                    data_preview.append({
                        'Campo': descricao,
                        'Valor': valores[0] if len(valores) == 1 else ', '.join(str(v)[:100] for v in valores[:3]) + ('...' if len(valores) > 3 else ''),
                        'Total Encontrado': len(valores)
                    })
                else:
                    data_preview.append({
                        'Campo': descricao,
                        'Valor': 'Nenhum resultado',
                        'Total Encontrado': 0
                    })
            except Exception as e:
                all_valores[descricao] = []
                data_preview.append({
                    'Campo': descricao,
                    'Valor': f'Erro: {str(e)}',
                    'Total Encontrado': 0
                })
        
        # Estruturar data_full
        data_full = []
        if all_valores:
            max_len = max(len(v) for v in all_valores.values())
            for i in range(max_len):
                row = {}
                for descricao, valores in all_valores.items():
                    row[descricao] = valores[i] if i < len(valores) else ''
                data_full.append(row)
        
        return {
            'url': url,
            'data_preview': data_preview,
            'data_full': data_full,
            'ai_explanation': ai_result.get('explicacao', ''),
            'error': None
        }
    except Exception as e:
        return {
            'url': url,
            'data_preview': None,
            'data_full': None,
            'ai_explanation': None,
            'error': str(e)
        }

# 🔧 FUNÇÃO UNIFICADA DE EXTRAÇÃO (usada em todas as abas)
def extract_element_value(elem, selector, tipo='css', is_xpath_attr=False, extrair_html=False):
    """
    Função unificada para extrair valores de elementos HTML de forma inteligente.
    Usada por todas as abas para garantir consistência.
    
    Args:
        elem: Elemento BeautifulSoup ou lxml
        selector: O seletor usado (para detecção automática)
        tipo: 'css' ou 'xpath'
        is_xpath_attr: True se for atributo XPath (ex: /@src)
        extrair_html: True para forçar extração de HTML completo
    
    Returns:
        str: Valor extraído (texto, atributo ou HTML)
    """
    try:
        # 1. Se for atributo XPath (string), retornar direto
        if is_xpath_attr and isinstance(elem, str):
            return elem
        
        # 2. Detectar automaticamente o tipo de extração baseado no seletor
        selector_lower = selector.lower() if selector else ''
        
        # Detectar se o seletor pede atributos específicos
        wants_src = '/@src' in selector or 'src' in selector_lower
        wants_href = '/@href' in selector or 'href' in selector_lower
        wants_img = 'img' in selector_lower or wants_src
        
        # 3. CSS: Extrair de forma inteligente
        if tipo == 'css' and hasattr(elem, 'name'):
            # Se for tag IMG ou seletor pede SRC
            if elem.name == 'img' or wants_img:
                src = elem.get('src', '') or elem.get('data-src', '')
                if src:
                    return src
            
            # Se for tag A ou seletor pede HREF
            if elem.name == 'a' or wants_href:
                href = elem.get('href', '')
                if href:
                    return href
            
            # Se deve extrair HTML completo (descrições com imagens/GIFs)
            if extrair_html:
                return str(elem)
            
            # Extração padrão de texto
            return elem.get_text(strip=True)
        
        # 4. XPath: Extrair de forma inteligente
        elif tipo == 'xpath':
            # Se deve extrair HTML completo
            if extrair_html and hasattr(elem, 'tag'):
                return lxml_html.tostring(elem, encoding='unicode')
            
            # Extração padrão de texto
            if hasattr(elem, 'text_content'):
                return elem.text_content().strip()
            else:
                return str(elem)
        
        # 5. Fallback padrão
        if tipo == 'css':
            return elem.get_text(strip=True) if hasattr(elem, 'get_text') else str(elem)
        else:
            return elem.text_content().strip() if hasattr(elem, 'text_content') else str(elem)
            
    except Exception as e:
        # Em caso de erro, retornar string vazia ao invés de gerar exceção
        return ''

# 🤖 GERENCIAMENTO DE SCRAPING AUTOMÁTICO
SCRAPING_TASKS_FILE = "scraping_tasks.json"
SCRAPING_HISTORY_FILE = "scraping_history.json"

def load_scraping_tasks():
    """Carrega tarefas de scraping automático"""
    try:
        if os.path.exists(SCRAPING_TASKS_FILE):
            with open(SCRAPING_TASKS_FILE, 'r') as f:
                return json.load(f)
        return []
    except:
        return []

def save_scraping_tasks(tasks):
    """Salva tarefas de scraping automático"""
    try:
        with open(SCRAPING_TASKS_FILE, 'w') as f:
            json.dump(tasks, f, indent=2)
        return True
    except:
        return False

def add_scraping_task(task_config):
    """Adiciona nova tarefa de scraping automático"""
    import uuid
    tasks = load_scraping_tasks()
    task_config['id'] = str(uuid.uuid4())[:8]  # UUID único e curto
    task_config['created_at'] = pd.Timestamp.now().isoformat()
    task_config['enabled'] = True
    tasks.append(task_config)
    return save_scraping_tasks(tasks)

def load_scraping_history():
    """Carrega histórico de execuções"""
    try:
        if os.path.exists(SCRAPING_HISTORY_FILE):
            with open(SCRAPING_HISTORY_FILE, 'r') as f:
                return json.load(f)
        return []
    except:
        return []

def save_scraping_history(history):
    """Salva histórico de execuções"""
    try:
        with open(SCRAPING_HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
        return True
    except:
        return False

def execute_scraping_task(task):
    """Executa uma tarefa de scraping"""
    try:
        # 1. Buscar produtos na fonte
        st.info(f"🔍 Carregando página: {task['source_url']}")
        html_content = load_page_with_browser(task['source_url'])
        
        if html_content.startswith('ERROR:'):
            return {'success': False, 'error': html_content}
        
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 2. Extrair lançamentos usando IA
        st.info(f"🤖 Identificando lançamentos usando IA...")
        
        # Preparar prompt para IA identificar produtos
        ai_prompt = f"""Analise este HTML de uma página de lançamentos e identifique os seletores CSS para extrair:
{', '.join(task['fields'])}

HTML (primeiros 5000 caracteres):
{html_content[:5000]}

Retorne APENAS um JSON com este formato:
{{"selectors": [{{"field": "nome_campo", "selector": "seletor_css", "type": "text/attribute/html"}}]}}"""

        # Usar API disponível (prioridade: Gemini > OpenAI > Claude)
        ai_response = None
        gemini_key = get_api_key('GEMINI_API_KEY')
        openai_key = get_api_key('OPENAI_API_KEY')
        anthropic_key = get_api_key('ANTHROPIC_API_KEY')
        
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                response = model.generate_content(ai_prompt)
                ai_response = response.text
            except:
                pass
        
        if not ai_response and openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": ai_prompt}]
                )
                ai_response = response.choices[0].message.content
            except:
                pass
        
        if not ai_response:
            return {'success': False, 'error': 'Nenhuma API de IA disponível'}
        
        # Parse resposta IA
        import re
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            selectors_data = json.loads(json_match.group())
            selectors = selectors_data.get('selectors', [])
        else:
            return {'success': False, 'error': 'Erro ao parsear resposta da IA'}
        
        # 3. Extrair dados usando seletores identificados
        # Extrair cada campo separadamente
        all_fields = {}
        max_items = 0
        
        for selector_info in selectors:
            field_name = selector_info['field']
            selector = selector_info['selector']
            elements = soup.select(selector)
            
            values = []
            for elem in elements:
                if selector_info['type'] == 'attribute':
                    attr_name = selector.split('@')[-1] if '@' in selector else 'href'
                    values.append(elem.get(attr_name, ''))
                else:
                    values.append(elem.get_text(strip=True))
            
            all_fields[field_name] = values
            max_items = max(max_items, len(values))
        
        # Alinhar produtos: cada produto pega valores do mesmo índice
        products = []
        for i in range(max_items):
            product = {}
            for field_name, values in all_fields.items():
                product[field_name] = values[i] if i < len(values) else ''
            products.append(product)
        
        # 4. Buscar produtos no site alvo (se configurado)
        if task.get('target_site'):
            st.info(f"🔎 Buscando produtos em {task['target_site']}...")
            # Esta parte será implementada na próxima iteração
        
        return {
            'success': True,
            'products': products,
            'total': len(products)
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def send_email_notification(task, result):
    """Envia email com resultados do scraping"""
    try:
        email_config = task.get('smtp_config')
        provider = task.get('email_provider', 'SMTP Customizado')
        
        # Preparar conteúdo do email
        subject = f"🤖 Scraping Automático: {task['name']}"
        
        if result['success']:
            body = f"""
            <h2>Scraping Concluído!</h2>
            <p><strong>Tarefa:</strong> {task['name']}</p>
            <p><strong>Total de produtos encontrados:</strong> {result['total']}</p>
            <p><strong>Data:</strong> {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}</p>
            
            <h3>Produtos Encontrados:</h3>
            <ul>
            """
            
            for product in result.get('products', [])[:10]:  # Limitar a 10 produtos
                body += f"<li>{product}</li>"
            
            body += "</ul>"
        else:
            body = f"""
            <h2>Erro no Scraping</h2>
            <p><strong>Tarefa:</strong> {task['name']}</p>
            <p><strong>Erro:</strong> {result['error']}</p>
            """
        
        # Enviar email baseado no provedor
        if provider == "SMTP Customizado" and email_config:
            try:
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                
                msg = MIMEMultipart()
                msg['From'] = email_config['user']
                msg['To'] = task['recipient_email']
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'html'))
                
                server = smtplib.SMTP(email_config['server'], email_config['port'])
                server.starttls()
                server.login(email_config['user'], email_config['pass'])
                server.send_message(msg)
                server.quit()
                return True
            except Exception as e:
                return f"Erro SMTP: {str(e)}"
        elif provider in ["SendGrid", "Resend", "Gmail"]:
            # Para integrations Replit, salvar resultado e avisar usuário
            return f"⚠️ {provider}: Configure a integração no Replit para envio automático"
        else:
            return "Provedor de email não configurado"
            
    except Exception as e:
        return f"Erro ao enviar email: {str(e)}"

def load_page_with_browser(url):
    """
    Carrega página usando proxy CORS direto no Python.
    Contorna bloqueios que sites fazem ao Python puro.
    """
    try:
        # Usar corsproxy.io para contornar bloqueios
        proxy_url = f'https://corsproxy.io/?{url}'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        
        # Se for Steam, adicionar cookies de verificação de idade
        cookies = {}
        if 'steampowered.com' in url:
            # Cookies para pular verificação de idade
            cookies = {
                'wants_mature_content': '1',
                'birthtime': '631152000',
                'lastagecheckage': '1-0-1990'
            }
        
        response = requests.get(proxy_url, headers=headers, cookies=cookies, timeout=20)
        response.raise_for_status()
        
        if len(response.text) < 100:
            return 'ERROR:Resposta muito curta ou vazia'
        
        return response.text
        
    except requests.exceptions.Timeout:
        return 'ERROR:Tempo esgotado ao carregar página'
    except requests.exceptions.RequestException as e:
        return f'ERROR:{str(e)}'
    except Exception as e:
        return f'ERROR:{str(e)}'

def reset_single_extraction():
    """Limpa resultados de extração de página única"""
    st.session_state.ai_result = None
    st.session_state.ai_direct_result = None

def reset_multi_url_extraction():
    """Limpa resultados de extração multi-URL"""
    st.session_state.multi_url_results = None
    st.session_state.loaded_urls = []
    st.session_state.selected_url_indices = []

def extract_data_directly_with_ai(html_content, user_query, ai_provider, api_key):
    """
    Usa IA para extrair dados DIRETAMENTE do HTML sem identificar seletores.
    Mais rápido e barato - ideal para consultas únicas.
    """
    
    # Limpar HTML usando função inteligente (remove lixo, mantém conteúdo importante)
    html_clean = clean_html_for_ai(html_content)
    html_preview = html_clean[:200000] if len(html_clean) > 200000 else html_clean
    
    prompt = f"""Você é um especialista em extração de dados web. Analise o HTML e extraia DIRETAMENTE os dados solicitados.

HTML da página (limpo):
{html_preview}

Solicitação do usuário:
{user_query}

IMPORTANTE:
- Extraia os dados DIRETAMENTE do HTML
- NÃO retorne seletores CSS/XPath
- Retorne apenas os valores encontrados
- Se um campo tiver múltiplos valores, liste todos
- Se não encontrar algo, retorne "Não encontrado"

Formato de resposta JSON:
{{
    "dados": [
        {{
            "campo": "nome do campo",
            "valor": "valor extraído ou lista de valores",
            "encontrado": true
        }}
    ],
    "resumo": "breve resumo do que foi encontrado"
}}

Retorne APENAS o JSON válido, sem markdown ou texto adicional."""

    try:
        if ai_provider == "OpenAI (ChatGPT)":
            if not OPENAI_AVAILABLE:
                return {"error": "OpenAI não está disponível"}
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        
        elif ai_provider == "Anthropic (Claude)":
            if not ANTHROPIC_AVAILABLE:
                return {"error": "Anthropic não está disponível"}
            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )
            content_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    content_text += block.text
            if not content_text.strip():
                return {"error": "Resposta vazia da API Anthropic"}
            return json.loads(content_text)
        
        elif ai_provider == "Google (Gemini)":
            if not GEMINI_AVAILABLE:
                return {"error": "Gemini não está disponível"}
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        
        else:
            return {"error": f"Provedor de IA não reconhecido: {ai_provider}"}
        
    except Exception as e:
        return {"error": f"Erro ao chamar a IA: {str(e)}"}

def extract_with_ai(html_content, user_query, ai_provider, api_key):
    """
    Usa IA para identificar seletores CSS/XPath baseado na descrição do usuário.
    Referência: blueprint:python_openai, blueprint:python_anthropic, blueprint:python_gemini
    """
    
    # Limpar HTML usando função inteligente (remove lixo, mantém conteúdo importante)
    html_clean = clean_html_for_ai(html_content)
    
    # Limitar a 200k caracteres (muito generoso, cobre páginas grandes)
    html_preview = html_clean[:200000] if len(html_clean) > 200000 else html_clean
    
    prompt = f"""Você é um especialista em web scraping. Analise o HTML LIMPO (sem scripts/CSS) e identifique seletores CSS/XPath para CADA campo solicitado pelo usuário.

HTML da página (limpo, até 200k caracteres):
{html_preview}

Solicitação do usuário:
{user_query}

REGRAS IMPORTANTES:
1. Retorne um seletor para CADA campo mencionado pelo usuário
2. Se o usuário pede "título, preço, descrição, imagens", retorne 4 seletores (um para cada)
3. Se um campo não for encontrado, inclua mesmo assim com seletor vazio e explique
4. Para IMAGENS, retorne seletores que capturam tags <img>:
   - Se pede "imagens de screenshots": retorne seletor para <img> ou <a> que contém imagens
   - Exemplo: "img.screenshot" ou "a.screenshot_link > img" ou "//img[@class='screenshot']"
   - IMPORTANTE: capture o atributo src das imagens!
5. Para "descrição com imagens/GIFs":
   - Retorne o seletor do CONTAINER (div que contém tudo)
   - Exemplo: "#game_area_description" (pega texto E imagens dentro)
   - NÃO retorne só o texto - retorne o container completo
6. Seja COMPLETO - não omita campos pedidos

Formato de resposta JSON:
{{
    "seletores": [
        {{
            "tipo": "css" ou "xpath",
            "seletor": "o seletor completo (ou vazio se não encontrado)",
            "descricao": "nome exato do campo (ex: 'Título', 'Preço', 'Descrição completa com imagens')",
            "exemplo_resultado": "exemplo real do HTML ou 'Não encontrado'"
        }}
    ],
    "explicacao": "resumo de quantos campos foram encontrados vs solicitados"
}}

Retorne APENAS o JSON válido, sem markdown ou texto adicional."""

    try:
        if ai_provider == "OpenAI (ChatGPT)":
            if not OPENAI_AVAILABLE:
                return {"error": "OpenAI não está disponível"}
            client = OpenAI(api_key=api_key)
            # O modelo mais recente da OpenAI é o gpt-5, lançado em 7 de agosto de 2025
            # Não altere isso a menos que explicitamente solicitado pelo usuário
            response = client.chat.completions.create(
                model="gpt-5",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        
        elif ai_provider == "Anthropic (Claude)":
            if not ANTHROPIC_AVAILABLE:
                return {"error": "Anthropic não está disponível"}
            client = Anthropic(api_key=api_key)
            # O modelo mais recente da Anthropic é claude-sonnet-4-20250514
            # Não altere isso a menos que explicitamente solicitado pelo usuário
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )
            content_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    content_text += block.text
            if not content_text.strip():
                return {"error": "Resposta vazia da API Anthropic"}
            return json.loads(content_text)
        
        elif ai_provider == "Google (Gemini)":
            if not GEMINI_AVAILABLE:
                return {"error": "Gemini não está disponível"}
            client = genai.Client(api_key=api_key)
            # O modelo mais recente da Google é gemini-2.5-flash
            # Não altere isso a menos que explicitamente solicitado pelo usuário
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        
    except Exception as e:
        return {"error": f"Erro ao chamar a IA: {str(e)}"}

st.set_page_config(
    page_title="Web Scraper Intuitivo",
    page_icon="🕷️",
    layout="wide"
)

# 🔐 AUTENTICAÇÃO SIMPLES COM LOGIN/SENHA
def check_login(username, password):
    """Verifica credenciais de login"""
    admin_username = get_secret('ADMIN_USERNAME', 'admin')
    admin_password = get_secret('ADMIN_PASSWORD', 'admin123')
    
    return username == admin_username and password == admin_password

# Inicializar session state para autenticação
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_name = None
    st.session_state.is_admin = False

# Tela de login
if not st.session_state.authenticated:
    st.title("🔐 Login - Web Scraper Intuitivo")
    st.markdown("### Entre com suas credenciais para acessar o sistema")
    
    with st.form("login_form"):
        username = st.text_input("👤 Usuário", placeholder="Digite seu usuário")
        password = st.text_input("🔑 Senha", type="password", placeholder="Digite sua senha")
        submit = st.form_submit_button("🚀 Entrar", use_container_width=True)
        
        if submit:
            if check_login(username, password):
                st.session_state.authenticated = True
                st.session_state.user_name = username
                st.session_state.is_admin = True
                st.success("✅ Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("❌ Usuário ou senha incorretos!")
    
    st.info("💡 **Credenciais:** configuradas via Streamlit Secrets")
    st.caption("Configure em: Settings → Secrets → ADMIN_USERNAME e ADMIN_PASSWORD")
    st.stop()

# Botão de logout no sidebar
with st.sidebar:
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_name = None
        st.session_state.is_admin = False
        st.rerun()
    
    st.divider()
    
    # Botão de download do prompt completo
    st.markdown("### 📄 Documentação")
    if os.path.exists("PROMPT_COMPLETO.md"):
        with open("PROMPT_COMPLETO.md", "r", encoding="utf-8") as f:
            prompt_content = f.read()
        st.download_button(
            "📥 Download Prompt Completo",
            prompt_content,
            "PROMPT_COMPLETO.md",
            "text/markdown",
            use_container_width=True,
            help="Baixe a documentação completa do sistema"
        )

st.title("🕷️ Web Scraper Intuitivo")
st.markdown("**Extraia dados de qualquer página web de forma fácil e visual**")

# Inicializar estado da sessão
if 'html_content' not in st.session_state:
    st.session_state.html_content = None
if 'soup' not in st.session_state:
    st.session_state.soup = None
if 'url' not in st.session_state:
    st.session_state.url = ""

# Sidebar para configurações
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # Método de carregamento
    st.markdown("**Método de Carregamento:**")
    loading_method = st.radio(
        "Método",
        ["⚡ Rápido (Python)", "🌐 Proxy CORS"],
        help="Rápido: carregamento Python direto. Proxy CORS: usa corsproxy.io para contornar bloqueios (Steam, Amazon, etc)",
        label_visibility="collapsed"
    )
    
    # Salvar em session_state para uso em Multi-URL e outras funções
    st.session_state.extraction_method = 'proxy' if loading_method == "🌐 Proxy CORS" else 'python'
    
    st.divider()
    
    # Opção de carregar HTML ou fazer upload
    load_option = st.radio(
        "Como carregar a página?",
        ["📡 Carregar de URL", "📁 Upload de arquivo HTML"],
        label_visibility="collapsed"
    )
    
    if load_option == "📁 Upload de arquivo HTML":
        uploaded_file = st.file_uploader(
            "Escolha um arquivo HTML",
            type=['html', 'htm'],
            help="Baixe o HTML da página (Ctrl+S no navegador ou Ctrl+U → Salvar)"
        )
        
        if uploaded_file is not None:
            if st.button("📥 Processar HTML", type="primary", use_container_width=True):
                try:
                    html_content = uploaded_file.read().decode('utf-8')
                    st.session_state.html_content = html_content
                    st.session_state.soup = BeautifulSoup(html_content, 'lxml')
                    st.session_state.url = f"[Arquivo: {uploaded_file.name}]"
                    st.success(f"✅ HTML carregado! ({len(html_content)} caracteres)")
                except Exception as e:
                    st.error(f"❌ Erro ao processar arquivo: {str(e)}")
    else:
        url = st.text_input(
            "URL da Página Web",
            placeholder="https://exemplo.com",
            value=st.session_state.url if not st.session_state.url.startswith("[Arquivo:") else ""
        )
        
        if st.button("🔍 Carregar Página", type="primary", use_container_width=True):
            if url:
                try:
                    use_proxy = loading_method == "🌐 Proxy CORS"
                
                    if use_proxy:
                        st.info("🌐 Preparando carregamento via proxy...")
                        st.session_state.loading_url = url
                        st.session_state.loading_mode = 'browser'
                        st.rerun()
                    else:
                        with st.spinner("Carregando página..."):
                            headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
                            }
                            
                            # Se for Steam, adicionar cookies de verificação de idade
                            cookies = {}
                            if 'steampowered.com' in url:
                                cookies = {
                                    'wants_mature_content': '1',
                                    'birthtime': '631152000',
                                    'lastagecheckage': '1-0-1990'
                                }
                            
                            response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
                            response.raise_for_status()
                            
                            st.session_state.html_content = response.text
                            st.session_state.soup = BeautifulSoup(response.text, 'lxml')
                            st.session_state.url = url
                            st.session_state.loading_mode = None
                            st.success("✅ Página carregada!")
                except Exception as e:
                    st.error(f"❌ Erro ao carregar página: {str(e)}")
            else:
                st.warning("⚠️ Por favor, insira uma URL válida")
    
    # Se está em modo de carregamento via proxy
    if st.session_state.get('loading_mode') == 'browser':
        st.divider()
        with st.spinner('🌐 Carregando via Proxy CORS... Aguarde (pode demorar até 20 segundos)'):
            result = load_page_with_browser(st.session_state.loading_url)
        
        st.session_state.loading_mode = None
        
        if result and isinstance(result, str):
            if result.startswith('ERROR:'):
                st.error(f"❌ {result.replace('ERROR:', '')}")
            else:
                st.session_state.html_content = result
                st.session_state.soup = BeautifulSoup(result, 'lxml')
                st.session_state.url = st.session_state.loading_url
                st.success("✅ Página carregada via proxy!")
                st.rerun()
        else:
            st.error("❌ Não foi possível carregar a página")
    
    st.divider()
    
    # Botão para baixar HTML
    if st.session_state.html_content:
        st.download_button(
            "💾 Baixar HTML da Página",
            st.session_state.html_content,
            f"pagina_{st.session_state.url.split('//')[-1].split('/')[0]}.html",
            "text/html",
            help="Baixe o HTML completo da página carregada",
            key="download_html"
        )
    
    if st.session_state.soup:
        st.success("✅ Página carregada e pronta para scraping!")
        st.caption(f"URL: {st.session_state.url}")

# Conteúdo principal - Abas sempre visíveis
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📖 Início",
    "📄 Estrutura HTML",
    "🤖 Extração com IA",
    "🚀 Scraping em Massa",
    "⚡ Validador de Seletores",
    "🤖 Scraping Automático"
])

# Tab 1: Início (instruções quando não há página carregada)
with tab1:
    if st.session_state.soup is None:
        st.info("👈 Insira uma URL na barra lateral e clique em 'Carregar Página' para começar")
        
        st.markdown("### 📖 Como usar:")
        st.markdown("""
        1. **Insira a URL** da página que deseja fazer scraping na barra lateral
        2. **Clique em 'Carregar Página'** para buscar o conteúdo
        3. **Escolha o método de extração** (Seletor CSS, Tag, Classe, etc.)
        4. **Visualize os dados** extraídos em tempo real
        5. **Faça o download** dos dados em CSV ou JSON
        """)
        
        st.markdown("### 💡 Exemplos de uso:")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Extrair títulos:**")
            st.code("Tag: h1")
            st.markdown("**Extrair parágrafos:**")
            st.code("Tag: p")
        with col2:
            st.markdown("**Extrair links:**")
            st.code("Tag: a")
            st.markdown("**Extrair por classe:**")
            st.code("Classe: produto-preco")
    else:
        st.success("✅ Página carregada e pronta para scraping!")
        st.caption(f"📍 URL: {st.session_state.url}")
        st.info("👆 Use as abas acima para extrair dados da página")

# Restante das abas (só funcionam com página carregada)
if st.session_state.soup is not None:
    
    # Tab 2: Visualização da Estrutura HTML
    with tab2:
        st.subheader("Estrutura HTML da Página")
        st.caption("Visualize a estrutura da página para identificar os elementos que deseja extrair")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**Estatísticas da Página:**")
            
            # Contar elementos
            all_tags = st.session_state.soup.find_all()
            unique_tags = set([tag.name for tag in all_tags])
            
            stats_data = {
                'Métrica': ['Total de Elementos', 'Tipos de Tags', 'Links (a)', 'Imagens (img)', 'Divs', 'Parágrafos (p)', 'Títulos (h1-h6)'],
                'Quantidade': [
                    len(all_tags),
                    len(unique_tags),
                    len(st.session_state.soup.find_all('a')),
                    len(st.session_state.soup.find_all('img')),
                    len(st.session_state.soup.find_all('div')),
                    len(st.session_state.soup.find_all('p')),
                    len(st.session_state.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
                ]
            }
            st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("**Tags Disponíveis:**")
            sorted_tags = sorted(list(unique_tags))
            st.text_area("", value=", ".join(sorted_tags), height=200, disabled=True)
        
        st.divider()
        
        st.markdown("**Classes CSS Disponíveis:**")
        all_classes = set()
        for tag in all_tags:
            if tag.get('class'):
                all_classes.update(tag.get('class'))
        
        if all_classes:
            sorted_classes = sorted(list(all_classes))
            st.text_area("", value=", ".join(sorted_classes), height=150, disabled=True, key="classes_display")
        else:
            st.info("Nenhuma classe CSS encontrada nesta página")
        
        st.divider()
        
        st.markdown("**IDs Disponíveis:**")
        all_ids = set()
        for tag in all_tags:
            if tag.get('id'):
                all_ids.add(tag.get('id'))
        
        if all_ids:
            sorted_ids = sorted(list(all_ids))
            st.text_area("", value=", ".join(sorted_ids), height=100, disabled=True, key="ids_display")
        else:
            st.info("Nenhum ID encontrado nesta página")
        
        st.divider()
        
        st.markdown("**Prévia do HTML (primeiros 5000 caracteres):**")
        html_preview = st.session_state.soup.prettify()[:5000]
        st.code(html_preview, language="html")
    
    # Tab 3: Extração com IA
    with tab3:
        st.subheader("🤖 Extração Assistida por IA")
        st.caption("Descreva o que você quer extrair e deixe a IA identificar os seletores corretos para você!")
        
        if 'ai_result' not in st.session_state:
            st.session_state.ai_result = None
        
        st.markdown("**Selecione o provedor de IA:**")
        ai_options = []
        if OPENAI_AVAILABLE:
            ai_options.append("OpenAI (ChatGPT)")
        if ANTHROPIC_AVAILABLE:
            ai_options.append("Anthropic (Claude)")
        if GEMINI_AVAILABLE:
            ai_options.append("Google (Gemini)")
        
        if not ai_options:
            st.error("❌ Nenhuma API de IA está disponível. Instale pelo menos uma: openai, anthropic ou google-genai")
        else:
            ai_provider = st.selectbox("Provedor de IA", ai_options, key="ai_provider")
            
            st.markdown("**Configure sua API Key:**")
            
            if ai_provider == "OpenAI (ChatGPT)":
                api_key_hint = "Obtenha em: https://platform.openai.com/api-keys"
                env_var_name = "OPENAI_API_KEY"
            elif ai_provider == "Anthropic (Claude)":
                api_key_hint = "Obtenha em: https://console.anthropic.com/settings/keys"
                env_var_name = "ANTHROPIC_API_KEY"
            else:
                api_key_hint = "Obtenha em: https://ai.google.dev/gemini-api/docs/api-key"
                env_var_name = "GEMINI_API_KEY"
            
            # Usar sistema híbrido de API keys
            api_key_value = get_api_key(env_var_name)
            
            if api_key_value:
                # Detectar origem da key
                is_from_secrets = (os.environ.get(env_var_name) == api_key_value)
                source = "Replit Secrets (🔒)" if is_from_secrets else "Customizada (🔑)"
                
                st.success(f"✅ API Key encontrada: {env_var_name} ({source})")
                use_saved_key = st.checkbox("Usar API Key salva", value=True, key="use_env_key")
                if use_saved_key:
                    api_key = api_key_value
                else:
                    api_key = st.text_input("API Key", type="password", key="ai_api_key_manual")
            else:
                st.info(f"ℹ️ {api_key_hint}")
                st.caption("💡 Configure suas API keys em Settings → Secrets no Streamlit Cloud")
                api_key = st.text_input(f"API Key do {ai_provider}", type="password", key="ai_api_key")
            
            st.divider()
            
            # ========== SEÇÃO 1: CARREGAR URLS ==========
            st.divider()
            st.markdown("### 📥 Modo Multi-URL")
            
            multi_url_mode = st.checkbox(
                "Ativar processamento de múltiplas URLs",
                help="Carregue várias URLs e depois processe com IA",
                key="multi_url_ai_mode"
            )
            
            # Detectar mudança de modo e limpar dados antigos
            previous_mode = st.session_state.get('previous_multi_url_mode', False)
            if multi_url_mode != previous_mode:
                st.session_state.previous_multi_url_mode = multi_url_mode
                if multi_url_mode:
                    # Ativou multi-URL: limpar resultados de página única
                    reset_single_extraction()
                else:
                    # Desativou multi-URL: limpar resultados multi-URL
                    reset_multi_url_extraction()
                st.rerun()
            
            if multi_url_mode:
                with st.expander("**ETAPA 1: Carregar URLs**", expanded=not st.session_state.get('loaded_urls', [])):
                    urls_text = st.text_area(
                        "URLs para carregar (uma por linha):",
                        placeholder="https://exemplo.com/pagina1\nhttps://exemplo.com/pagina2\nhttps://exemplo.com/pagina3",
                        height=120,
                        key="ai_multi_urls_input"
                    )
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.button("📥 Carregar URLs", type="primary", use_container_width=True, key="load_urls_btn"):
                            if urls_text:
                                urls_to_load = [url.strip() for url in urls_text.split('\n') if url.strip()]
                                if urls_to_load:
                                    # Limpar resultados anteriores ao carregar novas URLs
                                    st.session_state.multi_url_results = None
                                    
                                    extraction_method = st.session_state.get('extraction_method', 'python')
                                    
                                    progress_bar = st.progress(0)
                                    status_text = st.empty()
                                    
                                    loaded_results = []
                                    for idx, url in enumerate(urls_to_load):
                                        status_text.text(f"Carregando {idx + 1}/{len(urls_to_load)}: {url[:50]}...")
                                        result = fetch_html(url, extraction_method, timeout=10)
                                        loaded_results.append(result)
                                        progress_bar.progress((idx + 1) / len(urls_to_load))
                                    
                                    st.session_state.loaded_urls = loaded_results
                                    st.session_state.selected_url_indices = list(range(len(loaded_results)))  # Selecionar todas por padrão
                                    progress_bar.empty()
                                    status_text.empty()
                                    st.success(f"✅ {len(loaded_results)} URL(s) carregada(s)!")
                                    st.rerun()
                            else:
                                st.warning("⚠️ Insira pelo menos uma URL")
                    
                    with col2:
                        if st.button("🗑️ Limpar", key="clear_loaded_urls", use_container_width=True):
                            st.session_state.loaded_urls = []
                            st.session_state.selected_url_indices = []
                            st.rerun()
                
                # Mostrar URLs carregadas
                if st.session_state.get('loaded_urls', []):
                    with st.expander("**URLs Carregadas**", expanded=True):
                        st.markdown(f"**{len(st.session_state.loaded_urls)} URL(s) carregada(s)**")
                        
                        # Tabela com checkboxes
                        for idx, loaded_url in enumerate(st.session_state.loaded_urls):
                            col1, col2, col3 = st.columns([1, 8, 2])
                            
                            with col1:
                                is_selected = idx in st.session_state.get('selected_url_indices', [])
                                if st.checkbox("", value=is_selected, key=f"url_select_{idx}", label_visibility="collapsed"):
                                    if idx not in st.session_state.selected_url_indices:
                                        st.session_state.selected_url_indices.append(idx)
                                else:
                                    if idx in st.session_state.selected_url_indices:
                                        st.session_state.selected_url_indices.remove(idx)
                            
                            with col2:
                                status_icon = "✅" if loaded_url['status'] == 'success' else "❌"
                                url_display = loaded_url['url'][:70] + "..." if len(loaded_url['url']) > 70 else loaded_url['url']
                                st.text(f"{status_icon} {url_display}")
                            
                            with col3:
                                if loaded_url['status'] == 'error':
                                    st.caption(f"❌ {loaded_url['error'][:30]}...")
                        
                        selected_count = len(st.session_state.get('selected_url_indices', []))
                        st.info(f"📊 {selected_count} URL(s) selecionada(s) para processar")
            
            st.markdown("**Descreva o que você quer extrair:**")
            user_query = st.text_area(
                "Descrição",
                placeholder="Exemplo: Quero extrair o título do produto, o preço e a descrição",
                height=100,
                key="ai_query"
            )
            
            # ========== EXIBIR RESULTADOS DO PROCESSAMENTO MULTI-URL ==========
            if multi_url_mode and st.session_state.get('multi_url_results'):
                st.divider()
                st.success(f"✅ {len(st.session_state.multi_url_results)} URL(s) processada(s)!")
                
                # Exibir resultados organizados por URL
                st.markdown("### 📊 Resultados do Processamento")
                
                for idx, url_result in enumerate(st.session_state.multi_url_results, 1):
                    with st.expander(f"📄 URL {idx}: {url_result['url'][:80]}...", expanded=(idx == 1)):
                        if url_result.get('error'):
                            st.error(f"❌ Erro ao processar: {url_result['error']}")
                        elif url_result.get('data_preview'):
                            # Mostrar explicação da IA se disponível (modo individual)
                            if url_result.get('ai_explanation'):
                                st.info(f"🤖 **IA:** {url_result['ai_explanation']}")
                            
                            # Exibir preview dos dados
                            df_preview = pd.DataFrame(url_result['data_preview'])
                            st.dataframe(df_preview, use_container_width=True)
                            
                            # Download com dados COMPLETOS
                            if url_result.get('data_full'):
                                df_full = pd.DataFrame(url_result['data_full'])
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    csv = df_full.to_csv(index=False).encode('utf-8')
                                    st.download_button(
                                        "📥 CSV",
                                        csv,
                                        f"dados_url_{idx}.csv",
                                        "text/csv",
                                        key=f'multi_new_csv_{idx}',
                                        use_container_width=True
                                    )
                                with col2:
                                    json_str = df_full.to_json(orient='records', force_ascii=False, indent=2)
                                    st.download_button(
                                        "📥 JSON",
                                        json_str,
                                        f"dados_url_{idx}.json",
                                        "application/json",
                                        key=f'multi_new_json_{idx}',
                                        use_container_width=True
                                    )
                                with col3:
                                    html_output = generate_html_table(
                                        df_full, 
                                        title=f"Dados URL {idx}",
                                        url=url_result['url']
                                    )
                                    st.download_button(
                                        "📥 HTML",
                                        html_output,
                                        f"dados_url_{idx}.html",
                                        "text/html",
                                        key=f'multi_new_html_{idx}',
                                        use_container_width=True
                                    )
                        else:
                            st.warning("⚠️ Nenhum dado extraído desta URL")
                
                # Download combinado com seleção de URLs
                st.markdown("---")
                st.markdown("### 📦 Download Seletivo")
                
                # Inicializar checkboxes de download se não existir
                if 'download_url_selection' not in st.session_state:
                    st.session_state.download_url_selection = {i: True for i in range(len(st.session_state.multi_url_results))}
                
                # Botões para marcar/desmarcar todas
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    if st.button("✅ Marcar Todas", use_container_width=True):
                        st.session_state.download_url_selection = {i: True for i in range(len(st.session_state.multi_url_results))}
                        st.rerun()
                with col_btn2:
                    if st.button("❌ Desmarcar Todas", use_container_width=True):
                        st.session_state.download_url_selection = {i: False for i in range(len(st.session_state.multi_url_results))}
                        st.rerun()
                with col_btn3:
                    selected_count = sum(1 for v in st.session_state.download_url_selection.values() if v)
                    st.metric("URLs Selecionadas", f"{selected_count}/{len(st.session_state.multi_url_results)}")
                
                # Checkboxes para cada URL
                st.markdown("**Selecione quais URLs incluir no download:**")
                for idx, url_result in enumerate(st.session_state.multi_url_results):
                    col_check, col_url = st.columns([1, 9])
                    with col_check:
                        checked = st.checkbox(
                            "✓",
                            value=st.session_state.download_url_selection.get(idx, True),
                            key=f'download_check_{idx}',
                            label_visibility="collapsed"
                        )
                        st.session_state.download_url_selection[idx] = checked
                    with col_url:
                        status_icon = "✅" if not url_result.get('error') else "❌"
                        url_short = url_result['url'][:80] + "..." if len(url_result['url']) > 80 else url_result['url']
                        records_count = len(url_result.get('data_full', [])) if url_result.get('data_full') else 0
                        st.caption(f"{status_icon} **URL {idx+1}:** {url_short} ({records_count} registros)")
                
                # Coletar dados selecionados
                selected_combined_data = []
                for idx, url_result in enumerate(st.session_state.multi_url_results):
                    if st.session_state.download_url_selection.get(idx, False):
                        if url_result.get('data_full') and not url_result.get('error'):
                            for item in url_result['data_full']:
                                row = {'URL': url_result['url']}
                                row.update(item)
                                selected_combined_data.append(row)
                
                if selected_combined_data:
                    df_selected = pd.DataFrame(selected_combined_data)
                    selected_count = sum(1 for v in st.session_state.download_url_selection.values() if v)
                    st.info(f"📊 Total de registros selecionados: {len(selected_combined_data)} de {selected_count} URL(s)")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        csv_selected = df_selected.to_csv(index=False).encode('utf-8')
                        filename_csv = f"dados_{selected_count}_urls.csv" if selected_count > 1 else "dados_1_url.csv"
                        st.download_button(
                            "📥 CSV Selecionadas",
                            csv_selected,
                            filename_csv,
                            "text/csv",
                            key='multi_selected_csv',
                            use_container_width=True
                        )
                    with col2:
                        json_selected = df_selected.to_json(orient='records', force_ascii=False, indent=2)
                        filename_json = f"dados_{selected_count}_urls.json" if selected_count > 1 else "dados_1_url.json"
                        st.download_button(
                            "📥 JSON Selecionadas",
                            json_selected,
                            filename_json,
                            "application/json",
                            key='multi_selected_json',
                            use_container_width=True
                        )
                    with col3:
                        html_selected = generate_html_table(
                            df_selected,
                            title=f"Dados de {selected_count} URL(s) Selecionada(s)",
                            url=None
                        )
                        filename_html = f"dados_{selected_count}_urls.html" if selected_count > 1 else "dados_1_url.html"
                        st.download_button(
                            "📥 HTML Selecionadas",
                            html_selected,
                            filename_html,
                            "text/html",
                            key='multi_selected_html',
                            use_container_width=True
                        )
                else:
                    st.warning("⚠️ Nenhuma URL selecionada ou sem dados válidos")
                
                # Botão para limpar resultados e processar novamente
                if st.button("🔄 Processar Novamente", use_container_width=True):
                    st.session_state.multi_url_results = None
                    st.rerun()
            
            # Escolha do método de extração
            st.divider()
            st.markdown("### 🤖 Método de Extração")
            
            extraction_mode = st.radio(
                "Escolha como a IA vai processar:",
                options=["identify_selectors", "extract_direct"],
                format_func=lambda x: {
                    "identify_selectors": "🔍 Identificar Seletores - Gera seletores CSS/XPath reutilizáveis",
                    "extract_direct": "⚡ Extrair Dados Direto - Extração rápida sem seletores"
                }[x],
                key="extraction_mode_radio",
                horizontal=False
            )
            
            # Botão único de processamento
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button("🚀 Processar com IA", type="primary", use_container_width=True, key="process_ai_button"):
                    if not api_key:
                        st.warning("⚠️ Por favor, forneça uma API Key")
                    elif not user_query:
                        st.warning("⚠️ Por favor, descreva o que você quer extrair")
                    else:
                        # Limpar resultados anteriores
                        st.session_state.ai_result = None
                        st.session_state.ai_direct_result = None
                        st.session_state.multi_url_results = None
                        
                        # Verificar se está no modo multi-URL com URLs carregadas
                        if multi_url_mode and st.session_state.get('loaded_urls', []):
                            # PROCESSAR MULTI-URL
                            selected_indices = st.session_state.get('selected_url_indices', [])
                            if not selected_indices:
                                st.warning("⚠️ Selecione pelo menos uma URL para processar")
                            else:
                                extraction_method = st.session_state.get('extraction_method', 'python')
                                selected_urls = [st.session_state.loaded_urls[i] for i in selected_indices]
                                total = len(selected_urls)
                                
                                # Inicializar controles de processamento
                                if 'processing_control' not in st.session_state:
                                    st.session_state.processing_control = 'running'
                                if 'processing_results' not in st.session_state:
                                    st.session_state.processing_results = []
                                if 'processing_index' not in st.session_state:
                                    st.session_state.processing_index = 0
                                
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                control_container = st.empty()
                                results = st.session_state.processing_results
                                
                                # Mostrar botões de controle
                                with control_container.container():
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        if st.button("⏸️ Pausar", key="pause_processing", use_container_width=True):
                                            st.session_state.processing_control = 'paused'
                                            st.rerun()
                                    with col_b:
                                        if st.button("⏹️ Parar", key="stop_processing", use_container_width=True):
                                            st.session_state.processing_control = 'stopped'
                                            st.rerun()
                                
                                for idx, loaded_url in enumerate(selected_urls[st.session_state.processing_index:], start=st.session_state.processing_index):
                                    # Verificar controle de processamento
                                    if st.session_state.processing_control == 'stopped':
                                        status_text.warning("⏹️ Processamento interrompido pelo usuário")
                                        break
                                    elif st.session_state.processing_control == 'paused':
                                        status_text.info(f"⏸️ Processamento pausado em {idx}/{total}")
                                        st.session_state.processing_index = idx
                                        if st.button("▶️ Retomar Processamento", type="primary", key="resume_processing"):
                                            st.session_state.processing_control = 'running'
                                            st.rerun()
                                        st.stop()
                                    
                                    if loaded_url['status'] == 'error':
                                        results.append({
                                            'url': loaded_url['url'],
                                            'data_preview': None,
                                            'data_full': None,
                                            'error': loaded_url['error']
                                        })
                                        continue
                                    
                                    status_text.text(f"Processando {idx + 1}/{total}: {loaded_url['url'][:50]}...")
                                    
                                    if extraction_mode == "identify_selectors":
                                        # Identificar seletores para essa URL
                                        with st.spinner(f"Analisando com IA..."):
                                            ai_result = extract_with_ai(
                                                loaded_url['html_content'],
                                                user_query,
                                                ai_provider,
                                                api_key
                                            )
                                        
                                        if "error" in ai_result:
                                            results.append({'url': loaded_url['url'], 'data_preview': None, 'data_full': None, 'error': ai_result['error']})
                                        else:
                                            # Aplicar seletores identificados
                                            soup = BeautifulSoup(loaded_url['html_content'], 'lxml')
                                            data_preview = []
                                            all_valores = {}
                                            
                                            for sel in ai_result.get('seletores', []):
                                                seletor = sel.get('seletor', '')
                                                tipo = sel.get('tipo', 'css')
                                                descricao = sel.get('descricao', 'Campo')
                                                
                                                try:
                                                    extrair_html = any(palavra in descricao.lower() for palavra in ['imagem', 'imagens', 'gif', 'gifs', 'completa', 'completo', 'html', 'screenshot', 'media'])
                                                    
                                                    if tipo == 'css':
                                                        elements = soup.select(seletor)
                                                        valores = [extract_element_value(elem, seletor, tipo='css', extrair_html=extrair_html) for elem in elements if extract_element_value(elem, seletor, tipo='css', extrair_html=extrair_html)]
                                                    elif tipo == 'xpath':
                                                        tree = lxml_html.fromstring(loaded_url['html_content'])
                                                        elements = tree.xpath(seletor)
                                                        is_xpath_attr = isinstance(elements[0], str) if elements else False
                                                        valores = [extract_element_value(elem, seletor, tipo='xpath', is_xpath_attr=is_xpath_attr, extrair_html=extrair_html) for elem in elements if extract_element_value(elem, seletor, tipo='xpath', is_xpath_attr=is_xpath_attr, extrair_html=extrair_html)]
                                                    else:
                                                        valores = []
                                                    
                                                    all_valores[descricao] = valores
                                                    
                                                    if valores:
                                                        data_preview.append({
                                                            'Campo': descricao,
                                                            'Valor': valores[0] if len(valores) == 1 else ', '.join(str(v)[:100] for v in valores[:3]) + ('...' if len(valores) > 3 else ''),
                                                            'Total Encontrado': len(valores)
                                                        })
                                                    else:
                                                        data_preview.append({'Campo': descricao, 'Valor': 'Nenhum resultado', 'Total Encontrado': 0})
                                                except Exception as e:
                                                    all_valores[descricao] = []
                                                    data_preview.append({'Campo': descricao, 'Valor': f'Erro: {str(e)}', 'Total Encontrado': 0})
                                            
                                            # Estruturar data_full
                                            data_full = []
                                            if all_valores:
                                                max_len = max(len(v) for v in all_valores.values())
                                                for i in range(max_len):
                                                    row = {desc: vals[i] if i < len(vals) else '' for desc, vals in all_valores.items()}
                                                    data_full.append(row)
                                            
                                            results.append({
                                                'url': loaded_url['url'], 
                                                'data_preview': data_preview, 
                                                'data_full': data_full, 
                                                'ai_explanation': ai_result.get('explicacao', ''),
                                                'error': None
                                            })
                                    
                                    else:  # extract_direct
                                        # Extração direta para essa URL
                                        with st.spinner(f"Extraindo dados..."):
                                            direct_result = extract_data_directly_with_ai(
                                                loaded_url['html_content'],
                                                user_query,
                                                ai_provider,
                                                api_key
                                            )
                                        
                                        if "error" in direct_result:
                                            results.append({'url': loaded_url['url'], 'data_preview': None, 'data_full': None, 'ai_explanation': None, 'error': direct_result['error']})
                                        else:
                                            # Converter resultado direto para formato de preview
                                            data_preview = []
                                            data_full = []
                                            for item in direct_result.get('dados', []):
                                                data_preview.append({
                                                    'Campo': item['campo'],
                                                    'Valor': str(item['valor'])[:200],
                                                    'Encontrado': '✅' if item['encontrado'] else '❌'
                                                })
                                                data_full.append({
                                                    item['campo']: item['valor']
                                                })
                                            
                                            results.append({
                                                'url': loaded_url['url'], 
                                                'data_preview': data_preview, 
                                                'data_full': data_full,
                                                'ai_explanation': direct_result.get('resumo', ''),
                                                'error': None
                                            })
                                    
                                    progress_bar.progress((idx + 1) / total)
                                    st.session_state.processing_results = results
                                
                                # Limpar controles se processamento completou sem interrupção
                                if st.session_state.processing_control == 'running':
                                    st.session_state.multi_url_results = results
                                    st.session_state.processing_control = 'completed'
                                    st.session_state.processing_results = []
                                    st.session_state.processing_index = 0
                                    control_container.empty()
                                    progress_bar.empty()
                                    status_text.empty()
                                    st.success(f"✅ {len(results)} URL(s) processada(s)!")
                                    st.rerun()
                                else:
                                    # Processameto parado/pausado - manter estado
                                    st.session_state.processing_results = results
                        else:
                            # PROCESSAR PÁGINA ÚNICA
                            if extraction_mode == "identify_selectors":
                                with st.spinner(f"Identificando seletores com {ai_provider}..."):
                                    result = extract_with_ai(
                                        st.session_state.html_content,
                                        user_query,
                                        ai_provider,
                                        api_key
                                    )
                                    st.session_state.ai_result = result
                            else:  # extract_direct
                                with st.spinner(f"Extraindo dados com {ai_provider}..."):
                                    result = extract_data_directly_with_ai(
                                        st.session_state.html_content,
                                        user_query,
                                        ai_provider,
                                        api_key
                                    )
                                    st.session_state.ai_direct_result = result
            
            with col2:
                if st.button("🗑️ Limpar", key="clear_ai_results", use_container_width=True):
                    st.session_state.ai_result = None
                    st.session_state.ai_direct_result = None
                    # Limpar controles de processamento
                    st.session_state.processing_control = 'running'
                    st.session_state.processing_results = []
                    st.session_state.processing_index = 0
                    st.rerun()
            
            if st.session_state.ai_result is not None:
                result = st.session_state.ai_result
                
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.success("✅ Seletores identificados pela IA!")
                    
                    if "explicacao" in result:
                        st.info(f"💡 **Explicação:** {result['explicacao']}")
                    
                    # Se modo multi-URL está ativo e há URLs adicionais
                    if st.session_state.get('multi_url_mode', False) and st.session_state.get('additional_urls', []):
                        st.markdown("---")
                        st.markdown("### 🌐 Processamento Multi-URL")
                        
                        # Botão para processar todas as URLs
                        if not st.session_state.get('multi_url_results', []):
                            if st.button("🚀 Processar Todas as URLs", type="primary", use_container_width=True, key="process_multi_urls"):
                                urls_to_process = [st.session_state.url] + st.session_state.additional_urls
                                total_urls = len(urls_to_process)
                                strategy = st.session_state.get('multi_url_strategy', 'same_selectors')
                                extraction_method = st.session_state.get('extraction_method', 'python')
                                
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                # Informar qual estratégia está sendo usada
                                if strategy == 'individual_ai':
                                    st.info("🎯 Modo: Seletores individuais - IA analisará cada URL separadamente")
                                else:
                                    st.info("⚡ Modo: Mesmos seletores - aplicando seletores identificados em todas as URLs")
                                
                                results = []
                                for idx, url in enumerate(urls_to_process):
                                    status_text.text(f"Processando {idx + 1}/{total_urls}: {url[:50]}...")
                                    
                                    if url == st.session_state.url:
                                        # Já temos os dados da página atual
                                        all_data = []
                                        all_valores = {}
                                        
                                        for sel_idx, sel in enumerate(result['seletores'], 1):
                                            seletor = sel.get('seletor', '')
                                            tipo = sel.get('tipo', 'css')
                                            descricao = sel.get('descricao', f'Campo {sel_idx}')
                                            
                                            try:
                                                extrair_html = any(palavra in descricao.lower() for palavra in ['imagem', 'imagens', 'gif', 'gifs', 'completa', 'completo', 'html', 'screenshot', 'media'])
                                                
                                                if tipo == 'css':
                                                    elements = st.session_state.soup.select(seletor)
                                                    valores = []
                                                    for elem in elements:
                                                        valor = extract_element_value(elem, seletor, tipo='css', extrair_html=extrair_html)
                                                        if valor:
                                                            valores.append(valor)
                                                elif tipo == 'xpath':
                                                    tree = lxml_html.fromstring(st.session_state.html_content)
                                                    elements = tree.xpath(seletor)
                                                    is_xpath_attr = isinstance(elements[0], str) if elements else False
                                                    valores = []
                                                    for elem in elements:
                                                        valor = extract_element_value(elem, seletor, tipo='xpath', is_xpath_attr=is_xpath_attr, extrair_html=extrair_html)
                                                        if valor:
                                                            valores.append(valor)
                                                else:
                                                    valores = []
                                                
                                                all_valores[descricao] = valores
                                                
                                                if valores:
                                                    all_data.append({
                                                        'Campo': descricao,
                                                        'Valor': valores[0] if len(valores) == 1 else ', '.join(str(v)[:100] for v in valores[:3]) + ('...' if len(valores) > 3 else ''),
                                                        'Total Encontrado': len(valores)
                                                    })
                                                else:
                                                    all_data.append({
                                                        'Campo': descricao,
                                                        'Valor': 'Nenhum resultado',
                                                        'Total Encontrado': 0
                                                    })
                                            except Exception as e:
                                                all_valores[descricao] = []
                                                all_data.append({
                                                    'Campo': descricao,
                                                    'Valor': f'Erro: {str(e)}',
                                                    'Total Encontrado': 0
                                                })
                                        
                                        # Estruturar data_full
                                        data_full = []
                                        if all_valores:
                                            max_len = max(len(v) for v in all_valores.values())
                                            for i in range(max_len):
                                                row = {}
                                                for descricao, valores in all_valores.items():
                                                    row[descricao] = valores[i] if i < len(valores) else ''
                                                data_full.append(row)
                                        
                                        results.append({'url': url, 'data_preview': all_data, 'data_full': data_full, 'error': None})
                                    else:
                                        # Processar URLs adicionais
                                        if strategy == 'individual_ai':
                                            # Modo individual: IA analisa cada URL separadamente
                                            url_result = apply_ai_per_url(
                                                url, 
                                                st.session_state.get('user_query', user_query),
                                                st.session_state.get('ai_provider', ai_provider),
                                                st.session_state.get('ai_api_key', api_key),
                                                timeout=10,
                                                extraction_method=extraction_method
                                            )
                                        else:
                                            # Modo rápido: aplicar mesmos seletores
                                            url_result = apply_selectors_to_url(
                                                url, 
                                                result['seletores'],
                                                timeout=10,
                                                extraction_method=extraction_method
                                            )
                                        
                                        results.append(url_result)
                                    
                                    progress_bar.progress((idx + 1) / total_urls)
                                
                                st.session_state.multi_url_results = results
                                progress_bar.empty()
                                status_text.empty()
                                st.rerun()
                        else:
                            st.success(f"✅ {len(st.session_state.multi_url_results)} URL(s) processada(s)!")
                            
                            # Exibir resultados organizados por URL
                            st.markdown("### 📊 Resultados por URL")
                            
                            for idx, url_result in enumerate(st.session_state.multi_url_results, 1):
                                with st.expander(f"📄 URL {idx}: {url_result['url'][:80]}...", expanded=(idx == 1)):
                                    if url_result['error']:
                                        st.error(f"❌ Erro ao processar: {url_result['error']}")
                                    elif url_result.get('data_preview'):
                                        # Mostrar explicação da IA se disponível (modo individual)
                                        if url_result.get('ai_explanation'):
                                            st.info(f"🤖 **IA:** {url_result['ai_explanation']}")
                                        
                                        # Exibir preview dos dados
                                        df_preview = pd.DataFrame(url_result['data_preview'])
                                        st.dataframe(df_preview, use_container_width=True)
                                        
                                        # Download com dados COMPLETOS
                                        if url_result.get('data_full'):
                                            df_full = pd.DataFrame(url_result['data_full'])
                                            
                                            col1, col2 = st.columns(2)
                                            with col1:
                                                csv = df_full.to_csv(index=False).encode('utf-8')
                                                st.download_button(
                                                    "📥 Download CSV (Completo)",
                                                    csv,
                                                    f"dados_url_{idx}.csv",
                                                    "text/csv",
                                                    key=f'multi_csv_{idx}'
                                                )
                                            with col2:
                                                json_str = df_full.to_json(orient='records', force_ascii=False, indent=2)
                                                st.download_button(
                                                    "📥 Download JSON (Completo)",
                                                    json_str,
                                                    f"dados_url_{idx}.json",
                                                    "application/json",
                                                    key=f'multi_json_{idx}'
                                                )
                                    else:
                                        st.warning("⚠️ Nenhum dado extraído desta URL")
                            
                            # Download combinado de todas as URLs
                            st.markdown("---")
                            st.markdown("### 📦 Download Combinado")
                            
                            all_combined_data = []
                            for url_result in st.session_state.multi_url_results:
                                if url_result.get('data_full') and not url_result['error']:
                                    for item in url_result['data_full']:
                                        row = {'URL': url_result['url']}
                                        row.update(item)
                                        all_combined_data.append(row)
                            
                            if all_combined_data:
                                df_combined = pd.DataFrame(all_combined_data)
                                st.info(f"📊 Total de registros: {len(all_combined_data)}")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    csv_combined = df_combined.to_csv(index=False).encode('utf-8')
                                    st.download_button(
                                        "📥 Download CSV (Todas as URLs)",
                                        csv_combined,
                                        "dados_todas_urls.csv",
                                        "text/csv",
                                        key='multi_all_csv',
                                        use_container_width=True
                                    )
                                with col2:
                                    json_combined = df_combined.to_json(orient='records', force_ascii=False, indent=2)
                                    st.download_button(
                                        "📥 Download JSON (Todas as URLs)",
                                        json_combined,
                                        "dados_todas_urls.json",
                                        "application/json",
                                        key='multi_all_json',
                                        use_container_width=True
                                    )
                        
                        st.markdown("---")
                    
                    if "seletores" in result:
                        st.markdown("---")
                        st.markdown("### 📊 Dados Extraídos Automaticamente")
                        st.caption("A IA identificou os seletores e extraiu os dados para você!")
                        
                        all_data = []
                        for idx, sel in enumerate(result['seletores'], 1):
                            seletor = sel.get('seletor', '')
                            tipo = sel.get('tipo', 'css')
                            descricao = sel.get('descricao', f'Campo {idx}')
                            
                            try:
                                extrair_html = any(palavra in descricao.lower() for palavra in ['imagem', 'imagens', 'gif', 'gifs', 'completa', 'completo', 'html', 'screenshot', 'media'])
                                
                                if tipo == 'css':
                                    elements = st.session_state.soup.select(seletor)
                                    if extrair_html:
                                        valores = []
                                        for elem in elements:
                                            html_content = str(elem)
                                            valores.append(html_content)
                                    else:
                                        valores = [elem.get_text(strip=True) for elem in elements]
                                elif tipo == 'xpath':
                                    tree = lxml_html.fromstring(st.session_state.html_content)
                                    elements = tree.xpath(seletor)
                                    valores = []
                                    for elem in elements:
                                        if isinstance(elem, str):
                                            valores.append(elem)
                                        elif extrair_html and hasattr(elem, 'tag'):
                                            valores.append(lxml_html.tostring(elem, encoding='unicode'))
                                        elif hasattr(elem, 'text_content'):
                                            valores.append(elem.text_content().strip())
                                        else:
                                            valores.append(str(elem))
                                else:
                                    valores = []
                                
                                if valores:
                                    all_data.append({
                                        'Campo': descricao,
                                        'Valor': valores[0] if len(valores) == 1 else ', '.join(valores[:3]) + ('...' if len(valores) > 3 else ''),
                                        'Total Encontrado': len(valores)
                                    })
                            except Exception as e:
                                all_data.append({
                                    'Campo': descricao,
                                    'Valor': f'Erro: {str(e)}',
                                    'Total Encontrado': 0
                                })
                        
                        if all_data:
                            df_extracted = pd.DataFrame(all_data)
                            st.dataframe(df_extracted, use_container_width=True)
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                csv = df_extracted.to_csv(index=False).encode('utf-8')
                                st.download_button(
                                    "📥 CSV",
                                    csv,
                                    "dados_ia_extraidos.csv",
                                    "text/csv",
                                    key='ai_csv',
                                    use_container_width=True
                                )
                            with col2:
                                json_str = df_extracted.to_json(orient='records', force_ascii=False, indent=2)
                                st.download_button(
                                    "📥 JSON",
                                    json_str,
                                    "dados_ia_extraidos.json",
                                    "application/json",
                                    key='ai_json',
                                    use_container_width=True
                                )
                            with col3:
                                html_output = generate_html_table(
                                    df_extracted,
                                    title="Dados Extraídos com IA",
                                    url=st.session_state.get('url')
                                )
                                st.download_button(
                                    "📥 HTML",
                                    html_output,
                                    "dados_ia_extraidos.html",
                                    "text/html",
                                    key='ai_html',
                                    use_container_width=True
                                )
                            with col4:
                                if st.button("🎨 Visualizar", use_container_width=True, key="better_view_btn"):
                                    st.session_state.show_better_view = not st.session_state.get('show_better_view', False)
                            
                            if st.session_state.get('show_better_view', False):
                                st.markdown("---")
                                st.markdown("### 🎨 Visualização Melhorada")
                                
                                st.markdown("""
                                <style>
                                .campo-container {
                                    background-color: rgba(255, 255, 255, 0.05);
                                    padding: 20px;
                                    border-radius: 10px;
                                    margin: 15px 0;
                                    display: block;
                                    clear: both;
                                    overflow: auto;
                                }
                                .campo-titulo {
                                    font-size: 1.2em;
                                    font-weight: bold;
                                    color: #58a6ff;
                                    margin-bottom: 15px;
                                    display: block;
                                    clear: both;
                                }
                                .campo-texto {
                                    line-height: 1.8;
                                    margin: 15px 0;
                                    color: #c9d1d9;
                                    display: block;
                                    clear: both;
                                }
                                .campo-texto h1, .campo-texto h2, .campo-texto h3, .campo-texto h4 {
                                    display: block;
                                    clear: both;
                                    margin: 15px 0 10px 0;
                                }
                                .campo-texto p {
                                    display: block;
                                    margin: 10px 0;
                                }
                                .campo-texto img {
                                    display: block;
                                    max-width: 100%;
                                    height: auto;
                                    margin: 15px 0;
                                    border-radius: 5px;
                                }
                                </style>
                                """, unsafe_allow_html=True)
                                
                                for item in all_data:
                                    campo = item['Campo']
                                    valor = str(item['Valor'])
                                    
                                    with st.container():
                                        st.markdown(f'<div class="campo-container"><div class="campo-titulo">📌 {campo}</div>', unsafe_allow_html=True)
                                        
                                        if '<' in valor and '>' in valor:
                                            from bs4 import BeautifulSoup
                                            from urllib.parse import urljoin
                                            
                                            soup_valor = BeautifulSoup(valor, 'lxml')
                                            
                                            for img in soup_valor.find_all('img'):
                                                src = img.get('data-src') or img.get('data-screenshot') or img.get('src', '')
                                                
                                                parent_a = img.find_parent('a')
                                                if parent_a and parent_a.get('href'):
                                                    href = parent_a.get('href')
                                                    if any(ext in href.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                                                        src = href
                                                
                                                if src:
                                                    if src.startswith('//'):
                                                        src = 'https:' + src
                                                    elif src.startswith('/') and st.session_state.url:
                                                        src = urljoin(st.session_state.url, src)
                                                    
                                                    img['src'] = src
                                                    img['style'] = 'max-width: 100%; height: auto; margin: 10px 0; border-radius: 5px;'
                                            
                                            html_content = str(soup_valor)
                                            
                                            st.markdown(f'''
                                            <div class="campo-texto" style="line-height: 1.8;">
                                                {html_content}
                                            </div>
                                            ''', unsafe_allow_html=True)
                                        else:
                                            st.markdown(f'<div class="campo-texto">{valor}</div>', unsafe_allow_html=True)
                                        
                                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        st.markdown("---")
                        st.markdown("### 📋 Copiar Seletores")
                        
                        seletores_funcionaram = []
                        for item in all_data:
                            if item['Total Encontrado'] > 0:
                                for sel in result['seletores']:
                                    if sel.get('descricao', '') == item['Campo']:
                                        seletores_funcionaram.append({
                                            'descricao': item['Campo'],
                                            'seletor': sel.get('seletor', ''),
                                            'tipo': sel.get('tipo', 'css'),
                                            'valor': item['Valor']
                                        })
                                        break
                        
                        if seletores_funcionaram:
                            st.success(f"✅ {len(seletores_funcionaram)} seletor(es) funcionaram!")
                            
                            with st.expander("Ver detalhes dos seletores", expanded=False):
                                for idx, sel_data in enumerate(seletores_funcionaram, 1):
                                    st.markdown(f"**{idx}. {sel_data['descricao']}**")
                                    col1, col2 = st.columns([1, 1])
                                    with col1:
                                        st.caption(f"Tipo: `{sel_data['tipo']}`")
                                        st.code(sel_data['seletor'], language='css')
                                    with col2:
                                        st.caption("**Valor encontrado:**")
                                        st.caption(str(sel_data['valor'])[:150])
                                    st.divider()
                            
                            all_working_selectors = "\n".join([s['seletor'] for s in seletores_funcionaram])
                            
                            st.text_area(
                                "Seletores prontos para copiar:",
                                value=all_working_selectors,
                                height=150,
                                help="Cole isso na aba 'Teste Universal' ou use em outras ferramentas",
                                key="working_selectors_display"
                            )
                            
                            st.download_button(
                                "💾 Baixar Seletores (TXT)",
                                all_working_selectors,
                                "seletores_funcionando.txt",
                                "text/plain",
                                key="download_selectors"
                            )
                        else:
                            st.warning("⚠️ Nenhum seletor funcionou. Tente descrever de forma diferente.")
            
            # Exibir resultado da EXTRAÇÃO DIRETA
            if st.session_state.get('ai_direct_result') is not None:
                direct_result = st.session_state.ai_direct_result
                
                if "error" in direct_result:
                    st.error(f"❌ {direct_result['error']}")
                else:
                    st.success("✅ Dados extraídos diretamente pela IA!")
                    
                    if "resumo" in direct_result:
                        st.info(f"💡 **Resumo:** {direct_result['resumo']}")
                    
                    if "dados" in direct_result:
                        st.markdown("---")
                        st.markdown("### 📊 Dados Extraídos")
                        
                        # Criar tabela com os dados
                        dados_tabela = []
                        for campo_info in direct_result['dados']:
                            campo = campo_info.get('campo', 'Campo')
                            valor = campo_info.get('valor', '')
                            encontrado = campo_info.get('encontrado', False)
                            
                            status = "✅" if encontrado else "❌"
                            
                            # Se o valor for uma lista, juntar em string
                            if isinstance(valor, list):
                                valor_str = ', '.join(str(v) for v in valor[:5]) + ('...' if len(valor) > 5 else '')
                                total = len(valor)
                            else:
                                valor_str = str(valor)[:200]
                                total = 1 if encontrado else 0
                            
                            dados_tabela.append({
                                'Status': status,
                                'Campo': campo,
                                'Valor': valor_str,
                                'Total': total
                            })
                        
                        df_direct = pd.DataFrame(dados_tabela)
                        st.dataframe(df_direct, use_container_width=True)
                        
                        # Downloads
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            csv_direct = df_direct.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                "📥 CSV",
                                csv_direct,
                                "dados_ia_direto.csv",
                                "text/csv",
                                key='direct_csv',
                                use_container_width=True
                            )
                        with col2:
                            # JSON com dados originais (não da tabela)
                            json_direct = json.dumps(direct_result['dados'], ensure_ascii=False, indent=2)
                            st.download_button(
                                "📥 JSON",
                                json_direct,
                                "dados_ia_direto.json",
                                "application/json",
                                key='direct_json',
                                use_container_width=True
                            )
                        with col3:
                            html_output = generate_html_table(
                                df_direct,
                                title="Dados Extraídos Direto com IA",
                                url=st.session_state.get('url')
                            )
                            st.download_button(
                                "📥 HTML",
                                html_output,
                                "dados_ia_direto.html",
                                "text/html",
                                key='direct_html',
                                use_container_width=True
                            )
    
    # Tab 4: Scraping em Massa
    with tab4:
        st.subheader("🚀 Scraping em Massa")
        st.caption("Extraia dados de múltiplas URLs de uma vez usando os mesmos seletores")
        # Inicializar checkbox de IA como marcado se houver seletores disponíveis
        has_ai_selectors = st.session_state.get('ai_result') and 'seletores' in st.session_state.ai_result
        if has_ai_selectors:
            # Garantir que o checkbox inicia marcado na primeira vez
            if 'use_ai_bulk' not in st.session_state:
                st.session_state.use_ai_bulk = True
            st.success("🤖 Seletores da IA disponíveis! Você pode usá-los para extrair dados de múltiplas páginas")
            use_ai_selectors = st.checkbox("✨ Usar seletores identificados pela IA", value=True, key="use_ai_bulk")
        else:
            use_ai_selectors = False
        # Escolha entre URLs ou Upload de HTMLs
        input_method = st.radio(
            "Escolha o método de entrada:",
            ["📝 Inserir URLs", "📄 Upload de Arquivos HTML"],
            horizontal=True,
            key="bulk_input_method"
        )
        
        if input_method == "📝 Inserir URLs":
            st.markdown("**Insira as URLs (uma por linha):**")
            urls_text = st.text_area(
                "URLs",
                placeholder="https://exemplo.com/produto1\nhttps://exemplo.com/produto2\nhttps://exemplo.com/produto3",
                height=150,
                key="bulk_urls"
            )
            uploaded_files = None
        else:
            st.markdown("**Faça upload de múltiplos arquivos HTML:**")
            uploaded_files = st.file_uploader(
                "Selecione um ou mais arquivos HTML",
                type=['html', 'htm'],
                accept_multiple_files=True,
                key="bulk_html_files"
            )
            urls_text = ""
            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} arquivo(s) carregado(s): {', '.join([f.name for f in uploaded_files])}")
        if not use_ai_selectors:
            st.divider()
            st.markdown("**Escolha o método de extração:**")
            bulk_method = st.radio(
                "Método",
                ["⚡ Método Universal (Múltiplos Seletores)", "Seletor CSS", "XPath", "Tag HTML", "Classe CSS"],
                horizontal=False,
                key="bulk_method"
            )
            if bulk_method == "⚡ Método Universal (Múltiplos Seletores)":
                st.info("💡 Cole múltiplos seletores (CSS, XPath, etc) - um por linha. Cada seletor virará uma coluna no resultado!")
                bulk_selectors_text = st.text_area(
                    "Seletores (um por linha)",
                    placeholder="div.apphub_AppName\n//div[@class='game_area_purchase_game']/h1\nspan.discount_final_price\n//img[@class='game_header_image_full']/@src",
                    height=150,
                    key="bulk_universal_selectors"
                )
                bulk_selector = None
            elif bulk_method == "Seletor CSS":
                bulk_selector = st.text_input("Seletor CSS", placeholder="div.produto", key="bulk_css")
                bulk_selectors_text = None
            elif bulk_method == "XPath":
                bulk_selector = st.text_input("Expressão XPath", placeholder="//div[@class='produto']", key="bulk_xpath")
                bulk_selectors_text = None
            elif bulk_method == "Tag HTML":
                bulk_selector = st.text_input("Nome da Tag", placeholder="h1", key="bulk_tag")
                bulk_selectors_text = None
            else:
                bulk_selector = st.text_input("Nome da Classe", placeholder="produto-preco", key="bulk_class")
                bulk_selectors_text = None
            
            if bulk_method != "⚡ Método Universal (Múltiplos Seletores)":
                col1, col2 = st.columns([1, 1])
                with col1:
                    extract_bulk_text = st.checkbox("Extrair texto", value=True, key="bulk_text")
                with col2:
                    extract_bulk_attrs = st.checkbox("Extrair atributos", key="bulk_attrs")
                if extract_bulk_attrs:
                    bulk_attr_name = st.text_input("Nome do atributo", placeholder="href", key="bulk_attr")
        else:
            st.info("💡 Os seletores da IA serão aplicados automaticamente em todas as URLs!")
        if st.button("🚀 Iniciar Scraping em Massa", type="primary", key="bulk_scrape_button"):
            urls_list = [url.strip() for url in urls_text.split('\n') if url.strip()] if urls_text else []
            
            if not urls_list and not uploaded_files:
                st.warning("⚠️ Insira pelo menos uma URL ou faça upload de arquivos HTML")
            elif not use_ai_selectors and not bulk_selector and not bulk_selectors_text:
                st.warning("⚠️ Insira um seletor")
            else:
                all_data = []
                
                # Processar URLs ou arquivos HTML
                if uploaded_files:
                    items_to_process = [(f.name, f.getvalue().decode('utf-8', errors='ignore')) for f in uploaded_files]
                    total = len(items_to_process)
                else:
                    items_to_process = [(url, None) for url in urls_list]
                    total = len(urls_list)
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, (identifier, html_content) in enumerate(items_to_process):
                    status_text.text(f"Processando {idx + 1}/{total}: {identifier}")
                    try:
                        # Se for arquivo HTML, usar o conteúdo carregado
                        if html_content:
                            soup = BeautifulSoup(html_content, 'lxml')
                        else:
                            # Se for URL, fazer requisição
                            headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                            }
                            response = requests.get(identifier, headers=headers, timeout=10)
                            response.raise_for_status()
                            soup = BeautifulSoup(response.text, 'lxml')
                        if use_ai_selectors:
                            row = {'Fonte': identifier}
                            for sel in st.session_state.ai_result['seletores']:
                                seletor = sel.get('seletor', '')
                                tipo = sel.get('tipo', 'css')
                                descricao = sel.get('descricao', 'Campo')
                                try:
                                    # Detectar se precisa extrair HTML (imagens, descrições completas, etc)
                                    extrair_html = any(palavra in descricao.lower() for palavra in ['imagem', 'imagens', 'gif', 'gifs', 'completa', 'completo', 'html', 'screenshot', 'media'])
                                    
                                    if tipo == 'css':
                                        elements = soup.select(seletor)
                                        valores = []
                                        for elem in elements:
                                            valor = extract_element_value(elem, seletor, tipo='css', extrair_html=extrair_html)
                                            if valor:
                                                valores.append(valor)
                                    elif tipo == 'xpath':
                                        tree = lxml_html.fromstring(html_content if html_content else response.text)
                                        elements = tree.xpath(seletor)
                                        is_xpath_attr = isinstance(elements[0], str) if elements else False
                                        valores = []
                                        for elem in elements:
                                            valor = extract_element_value(elem, seletor, tipo='xpath', is_xpath_attr=is_xpath_attr, extrair_html=extrair_html)
                                            if valor:
                                                valores.append(valor)
                                    else:
                                        valores = []
                                    row[descricao] = valores[0] if len(valores) == 1 else ', '.join(valores[:5]) + ('...' if len(valores) > 5 else '')
                                except Exception as e:
                                    row[descricao] = ''
                            all_data.append(row)
                        elif bulk_method == "⚡ Método Universal (Múltiplos Seletores)" and bulk_selectors_text:
                            # Processar múltiplos seletores - uma linha por URL
                            row = {'Fonte': identifier}
                            selectors_list = [s.strip() for s in bulk_selectors_text.strip().split('\n') if s.strip()]
                            
                            for selector_idx, selector in enumerate(selectors_list, 1):
                                try:
                                    # Detectar automaticamente se precisa extrair HTML (imagens, descrições, etc)
                                    # Baseado no seletor (img, src, href, etc)
                                    selector_lower = selector.lower()
                                    extrair_html = any(palavra in selector_lower for palavra in ['img', 'src', 'screenshot', 'image', 'description', 'game_area_description'])
                                    
                                    # Detectar se é XPath ou CSS
                                    is_xpath = any([
                                        selector.startswith('//'),
                                        selector.startswith('/'),
                                        selector.startswith('./'),
                                        selector.startswith('(//'),
                                        '::' in selector,
                                        '@' in selector and '/' in selector
                                    ])
                                    
                                    if is_xpath:
                                        tree = lxml_html.fromstring(html_content if html_content else response.text)
                                        elements = tree.xpath(selector)
                                        is_xpath_attr = isinstance(elements[0], str) if elements else False
                                        valores = []
                                        for elem in elements:  # Remover limite [:5] para pegar todos
                                            valor = extract_element_value(elem, selector, tipo='xpath', is_xpath_attr=is_xpath_attr, extrair_html=extrair_html)
                                            if valor:
                                                valores.append(valor)
                                    else:
                                        # CSS
                                        elements = soup.select(selector)
                                        valores = []
                                        for elem in elements:  # Remover limite [:5] para pegar todos
                                            valor = extract_element_value(elem, selector, tipo='css', extrair_html=extrair_html)
                                            if valor:
                                                valores.append(valor)
                                    
                                    # Usar sempre o seletor completo como nome da coluna
                                    # Se for muito longo, o Streamlit trunca automaticamente na exibição
                                    row[selector] = valores[0] if len(valores) == 1 else ', '.join(str(v) for v in valores[:5]) + ('...' if len(valores) > 5 else '')
                                except Exception as e:
                                    row[selector] = f"ERRO: {str(e)}"
                            
                            all_data.append(row)
                        else:
                            if bulk_method == "Seletor CSS":
                                elements = soup.select(bulk_selector)
                            elif bulk_method == "XPath":
                                tree = lxml_html.fromstring(html_content if html_content else response.text)
                                elements = tree.xpath(bulk_selector)
                            elif bulk_method == "Tag HTML":
                                elements = soup.find_all(bulk_selector)
                            else:
                                elements = soup.find_all(class_=bulk_selector)
                            for elem_idx, elem in enumerate(elements, 1):
                                row = {
                                    'Fonte': identifier,
                                    '#': elem_idx
                                }
                                if bulk_method == "XPath":
                                    if isinstance(elem, str):
                                        row['Valor'] = elem
                                    elif hasattr(elem, 'text_content'):
                                        if extract_bulk_text:
                                            row['Texto'] = elem.text_content().strip()
                                        if extract_bulk_attrs and bulk_attr_name:
                                            row[bulk_attr_name] = elem.get(bulk_attr_name, '')
                                    else:
                                        row['Valor'] = str(elem)
                                else:
                                    if extract_bulk_text:
                                        row['Texto'] = elem.get_text(strip=True)
                                    if extract_bulk_attrs and bulk_attr_name:
                                        row[bulk_attr_name] = elem.get(bulk_attr_name, '')
                                all_data.append(row)
                    except Exception as e:
                        st.warning(f"⚠️ Erro ao processar {identifier}: {str(e)}")
                    progress_bar.progress((idx + 1) / total)
                status_text.empty()
                progress_bar.empty()
                if all_data:
                    # Salvar resultados no session_state para permitir seleção
                    st.session_state.bulk_results = all_data
                    
                    # Agrupar dados por fonte (URL ou arquivo)
                    df = pd.DataFrame(all_data)
                    fontes_unicas = df['Fonte'].unique()
                    
                    # Detectar URLs com problemas (campos vazios ou com "erro")
                    urls_com_problemas = []
                    urls_completas = []
                    
                    for fonte in fontes_unicas:
                        dados_fonte = df[df['Fonte'] == fonte]
                        # Verificar se há campos vazios ou com erro
                        tem_problema = False
                        for _, row in dados_fonte.iterrows():
                            for col in row.index:
                                if col != 'Fonte' and col != '#':
                                    valor = str(row[col]).lower()
                                    if valor in ['', 'nan', 'none'] or 'erro' in valor or len(valor.strip()) == 0:
                                        tem_problema = True
                                        break
                            if tem_problema:
                                break
                        
                        if tem_problema:
                            urls_com_problemas.append(fonte)
                        else:
                            urls_completas.append(fonte)
                    
                    # SEMPRE reinicializar seleção em cada scraping (todas marcadas por padrão)
                    st.session_state.bulk_selected_sources = list(fontes_unicas)
                    
                    st.success(f"✅ Scraping concluído! {len(all_data)} elementos extraídos de {total} fonte(s)")
                    
                    # Resumo com indicadores
                    col_info1, col_info2, col_info3 = st.columns(3)
                    with col_info1:
                        st.metric("Total de URLs", len(fontes_unicas))
                    with col_info2:
                        st.metric("✅ URLs Completas", len(urls_completas))
                    with col_info3:
                        st.metric("⚠️ URLs com Problemas", len(urls_com_problemas))
                    
                    st.divider()
                    
                    # Filtros
                    st.markdown("**Filtrar Resultados:**")
                    filtro = st.radio(
                        "Mostrar:",
                        ["📋 Todas as URLs", "✅ Apenas URLs Completas", "⚠️ Apenas URLs com Problemas"],
                        horizontal=True,
                        key="bulk_filter"
                    )
                    
                    # Aplicar filtro
                    if filtro == "✅ Apenas URLs Completas":
                        fontes_filtradas = urls_completas
                    elif filtro == "⚠️ Apenas URLs com Problemas":
                        fontes_filtradas = urls_com_problemas
                    else:
                        fontes_filtradas = list(fontes_unicas)
                    
                    st.divider()
                    
                    # Seleção de URLs para download
                    st.markdown("**Selecione as URLs para baixar:**")
                    
                    col_select_all, col_deselect_all = st.columns(2)
                    with col_select_all:
                        if st.button("✅ Marcar Todas (Filtradas)", key="select_all_bulk", use_container_width=True):
                            st.session_state.bulk_selected_sources = fontes_filtradas.copy()
                            st.rerun()
                    with col_deselect_all:
                        if st.button("❌ Desmarcar Todas", key="deselect_all_bulk", use_container_width=True):
                            st.session_state.bulk_selected_sources = []
                            st.rerun()
                    
                    # Mostrar checkboxes para cada URL
                    for fonte in fontes_filtradas:
                        dados_fonte = df[df['Fonte'] == fonte]
                        
                        # Indicador de problema
                        is_problema = fonte in urls_com_problemas
                        status_icon = "⚠️" if is_problema else "✅"
                        
                        col_check, col_url, col_preview = st.columns([1, 6, 3])
                        
                        with col_check:
                            is_selected = fonte in st.session_state.bulk_selected_sources
                            if st.checkbox("", value=is_selected, key=f"bulk_select_{fonte}", label_visibility="collapsed"):
                                if fonte not in st.session_state.bulk_selected_sources:
                                    st.session_state.bulk_selected_sources.append(fonte)
                            else:
                                if fonte in st.session_state.bulk_selected_sources:
                                    st.session_state.bulk_selected_sources.remove(fonte)
                        
                        with col_url:
                            url_display = fonte[:80] + "..." if len(fonte) > 80 else fonte
                            st.text(f"{status_icon} {url_display}")
                        
                        with col_preview:
                            st.caption(f"{len(dados_fonte)} registro(s)")
                        
                        # Mostrar detalhes se tiver problemas
                        if is_problema:
                            with st.expander(f"🔍 Ver problemas - {fonte[:50]}..."):
                                for _, row in dados_fonte.iterrows():
                                    problemas = []
                                    for col in row.index:
                                        if col != 'Fonte' and col != '#':
                                            valor = str(row[col]).lower()
                                            if valor in ['', 'nan', 'none'] or 'erro' in valor or len(valor.strip()) == 0:
                                                problemas.append(f"**{col}**: {valor if valor else '(vazio)'}")
                                    if problemas:
                                        st.warning(" • " + "\n • ".join(problemas))
                    
                    st.divider()
                    
                    # Contador de selecionados
                    st.info(f"📊 **{len(st.session_state.bulk_selected_sources)} URL(s) selecionada(s)** de {len(fontes_filtradas)} ({len(fontes_unicas)} total)")
                    
                    # Preview dos dados selecionados
                    if st.session_state.bulk_selected_sources:
                        df_selecionado = df[df['Fonte'].isin(st.session_state.bulk_selected_sources)]
                        
                        with st.expander("👁️ Preview dos Dados Selecionados", expanded=False):
                            st.dataframe(df_selecionado, use_container_width=True)
                        
                        # Botões de download
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            csv = df_selecionado.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                "📥 Download CSV Selecionados",
                                csv,
                                f"scraping_massa_{len(st.session_state.bulk_selected_sources)}_urls.csv",
                                "text/csv",
                                key='bulk_csv_selected',
                                use_container_width=True
                            )
                        
                        with col2:
                            json_str = df_selecionado.to_json(orient='records', force_ascii=False, indent=2)
                            st.download_button(
                                "📥 Download JSON Selecionados",
                                json_str,
                                f"scraping_massa_{len(st.session_state.bulk_selected_sources)}_urls.json",
                                "application/json",
                                key='bulk_json_selected',
                                use_container_width=True
                            )
                        
                        with col3:
                            # Download individual por URL
                            if len(st.session_state.bulk_selected_sources) == 1:
                                fonte_individual = st.session_state.bulk_selected_sources[0]
                                df_individual = df[df['Fonte'] == fonte_individual]
                                csv_individual = df_individual.to_csv(index=False).encode('utf-8')
                                
                                # Nome de arquivo limpo
                                nome_arquivo = fonte_individual.split('/')[-1].replace('.html', '').replace('https://', '').replace('http://', '')[:30]
                                
                                st.download_button(
                                    "📥 Download Individual",
                                    csv_individual,
                                    f"{nome_arquivo}.csv",
                                    "text/csv",
                                    key='bulk_csv_individual',
                                    use_container_width=True
                                )
                    else:
                        st.warning("⚠️ Selecione pelo menos uma URL para baixar")
                    
                    # Opção de baixar TUDO (não filtrado)
                    st.divider()
                    with st.expander("📦 Download de TODOS os Dados (não filtrado)", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            csv_all = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                "📥 Download CSV (TODAS as URLs)",
                                csv_all,
                                "scraping_massa_completo.csv",
                                "text/csv",
                                key='bulk_csv_all'
                            )
                        with col2:
                            json_all = df.to_json(orient='records', force_ascii=False, indent=2)
                            st.download_button(
                                "📥 Download JSON (TODAS as URLs)",
                                json_all,
                                "scraping_massa_completo.json",
                                "application/json",
                                key='bulk_json_all'
                            )
                else:
                    st.warning("⚠️ Nenhum dado foi extraído")
    
    # Tab 5: Validador de Seletores
    with tab5:
        st.subheader("⚡ Validador de Seletores")
        st.caption("Cole múltiplos seletores (CSS, XPath, etc) - um por linha - e teste todos de uma vez!")
        st.markdown("**Cole seus seletores aqui (um por linha):**")
        selectors_text = st.text_area(
            "Seletores",
            placeholder="div.apphub_AppName\n//div[@class='produto']/h1\nspan.price\n//a/@href",
            height=200,
            key="universal_selectors"
        )
        col1, col2 = st.columns([1, 1])
        with col1:
            extract_universal_text = st.checkbox("Extrair texto", value=True, key="universal_text")
        with col2:
            extract_universal_attrs = st.checkbox("Extrair atributos (quando aplicável)", key="universal_attrs")
        if st.button("🚀 Testar Todos os Seletores", type="primary", key="universal_button"):
            if selectors_text.strip():
                selectors_list = [s.strip() for s in selectors_text.strip().split('\n') if s.strip()]
                if selectors_list:
                    all_results = []
                    for idx, selector in enumerate(selectors_list, 1):
                        try:
                            # Detectar tipo de seletor - tenta XPath primeiro
                            is_xpath = False
                            # Indicadores comuns de XPath
                            xpath_indicators = [
                                selector.startswith('//'),
                                selector.startswith('/'),
                                selector.startswith('./'),
                                selector.startswith('(//'),
                                selector.startswith('(./'),
                                '::' in selector,  # eixos como descendant::, child::
                                '@' in selector and '/' in selector,  # atributos com path
                            ]
                            if any(xpath_indicators):
                                is_xpath = True
                            if is_xpath:
                                # XPath
                                tree = lxml_html.fromstring(st.session_state.html_content)
                                elements = tree.xpath(selector)
                                tipo = "XPath"
                                is_xpath_attr = isinstance(elements[0], str) if elements else False
                                valores = []
                                for elem in elements:
                                    valor = extract_element_value(elem, selector, tipo='xpath', is_xpath_attr=is_xpath_attr, extrair_html=extract_universal_attrs)
                                    if valor:
                                        valores.append(valor)
                            else:
                                # CSS
                                elements = st.session_state.soup.select(selector)
                                tipo = "CSS"
                                valores = []
                                for elem in elements:
                                    valor = extract_element_value(elem, selector, tipo='css', extrair_html=extract_universal_attrs)
                                    if valor:
                                        valores.append(valor)
                            # Adicionar resultado
                            total_encontrado = len(valores) if isinstance(valores, list) else (1 if valores else 0)
                            primeiro_valor = valores[0] if valores else "Nenhum resultado"
                            all_results.append({
                                '#': idx,
                                'Seletor': selector,
                                'Tipo': tipo,
                                'Total Encontrado': total_encontrado,
                                'Primeiro Valor': primeiro_valor if not isinstance(primeiro_valor, list) else str(primeiro_valor)[:100]
                            })
                        except Exception as e:
                            all_results.append({
                                '#': idx,
                                'Seletor': selector,
                                'Tipo': 'Erro',
                                'Total Encontrado': 0,
                                'Primeiro Valor': f"❌ Erro: {str(e)[:50]}"
                            })
                    if all_results:
                        df = pd.DataFrame(all_results)
                        st.success(f"✅ {len(selectors_list)} seletor(es) testado(s)!")
                        st.dataframe(df, use_container_width=True)
                        # Download options
                        col1, col2 = st.columns(2)
                        with col1:
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                "📥 Download CSV",
                                csv,
                                "teste_universal.csv",
                                "text/csv",
                                key='universal_csv'
                            )
                        with col2:
                            json_str = df.to_json(orient='records', force_ascii=False, indent=2)
                            st.download_button(
                                "📥 Download JSON",
                                json_str,
                                "teste_universal.json",
                                "application/json",
                                key='universal_json'
                            )
                else:
                    st.warning("⚠️ Insira pelo menos um seletor")
            else:
                st.warning("⚠️ Insira pelo menos um seletor")
    
# Tab 6: Scraping Automático (funciona sem página carregada)
with tab6:
    st.subheader("🤖 Scraping Automático de Lançamentos")
    st.caption("Configure scraping periódico de lançamentos de produtos com notificação por email")
    
    # Aviso de funcionalidade futura
    st.warning(
        "⚠️ **FUNCIONALIDADE FUTURA** - Esta funcionalidade está em desenvolvimento.\n\n"
        "**Limitação do Streamlit Community Cloud:** O Streamlit Cloud não possui suporte nativo para tarefas agendadas (cron jobs). "
        "Para implementar esta funcionalidade completamente, será necessário:\n\n"
        "1. **Integrar banco de dados externo** (ex: Supabase) para persistir tarefas cadastradas\n"
        "2. **Configurar execução externa** via GitHub Actions ou serviço de cron (cron-job.org)\n"
        "3. **Adaptar arquitetura** para separar agendamento da interface\n\n"
        "Por enquanto, a interface está disponível para visualização e testes, mas o agendamento automático não funcionará até essas mudanças serem implementadas.",
        icon="⚠️"
    )
    
    # Verificar se usuário é admin
    if not st.session_state.get('is_admin', False):
        st.warning("⚠️ Esta funcionalidade está disponível apenas para administradores")
        st.stop()
    
    # Duas colunas: Configuração | Tarefas Ativas
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("### ➕ Nova Tarefa de Scraping")
        
        with st.form("new_scraping_task"):
            st.markdown("**1️⃣ Configuração da Fonte**")
            task_name = st.text_input("Nome da Tarefa", placeholder="Ex: Lançamentos Steam Semanal")
            source_url = st.text_input("URL da Página de Lançamentos", placeholder="https://store.steampowered.com/...")
            
            st.divider()
            st.markdown("**2️⃣ Configuração de Busca**")
            target_site = st.text_input("Site Alvo para Buscar Produtos", placeholder="https://loja.com")
            search_method = st.selectbox("Método de Busca", ["Híbrido (Python + IA)", "Apenas Python", "Apenas IA"])
            
            st.divider()
            st.markdown("**3️⃣ Campos para Extrair**")
            fields_to_extract = st.text_area(
                "Campos Desejados (um por linha)",
                placeholder="Título\nPreço\nDisponibilidade\nLink\nImagem",
                height=100
            )
            
            st.divider()
            st.markdown("**4️⃣ Agendamento**")
            col_freq1, col_freq2 = st.columns(2)
            with col_freq1:
                frequency = st.selectbox("Frequência", ["Diário", "Semanal", "Mensal", "Personalizado"])
            with col_freq2:
                if frequency == "Personalizado":
                    custom_schedule = st.text_input("Cron Expression", placeholder="0 10 * * 1")
                else:
                    custom_schedule = ""
            
            st.divider()
            st.markdown("**5️⃣ Notificações por Email**")
            
            email_provider = st.selectbox(
                "Provedor de Email",
                ["SMTP Customizado", "SendGrid", "Resend", "Gmail"],
                help="Escolha como enviar os relatórios por email"
            )
            
            recipient_email = st.text_input("Email Destinatário", placeholder="seu@email.com")
            
            if email_provider == "SMTP Customizado":
                st.caption("Configure seu servidor SMTP:")
                smtp_col1, smtp_col2 = st.columns(2)
                with smtp_col1:
                    smtp_server = st.text_input("Servidor SMTP", placeholder="smtp.gmail.com")
                    smtp_port = st.number_input("Porta", value=587, min_value=1, max_value=65535)
                with smtp_col2:
                    smtp_user = st.text_input("Usuário SMTP")
                    smtp_pass = st.text_input("Senha SMTP", type="password")
            else:
                smtp_server = smtp_port = smtp_user = smtp_pass = None
                st.info(f"💡 Você precisará configurar a integração {email_provider} no Replit")
            
            submit_task = st.form_submit_button("✅ Criar Tarefa", use_container_width=True)
            
            if submit_task:
                if task_name and source_url and target_site and recipient_email:
                    task_config = {
                        'name': task_name,
                        'source_url': source_url,
                        'target_site': target_site,
                        'search_method': search_method,
                        'fields': [f.strip() for f in fields_to_extract.split('\n') if f.strip()],
                        'frequency': frequency,
                        'custom_schedule': custom_schedule,
                        'email_provider': email_provider,
                        'recipient_email': recipient_email,
                        'smtp_config': {
                            'server': smtp_server,
                            'port': smtp_port,
                            'user': smtp_user,
                            'pass': smtp_pass
                        } if email_provider == "SMTP Customizado" else None
                    }
                    
                    if add_scraping_task(task_config):
                        st.success(f"✅ Tarefa '{task_name}' criada com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao criar tarefa")
                else:
                    st.warning("⚠️ Preencha todos os campos obrigatórios")
    
    with col2:
        st.markdown("### 📋 Tarefas Configuradas")
        tasks = load_scraping_tasks()
        
        if tasks:
            for task in tasks:
                with st.expander(f"🤖 {task['name']}", expanded=False):
                    st.text(f"🔗 Fonte: {task['source_url'][:50]}...")
                    st.text(f"🎯 Alvo: {task['target_site'][:50]}...")
                    st.text(f"⏰ Frequência: {task['frequency']}")
                    st.text(f"📧 Email: {task['recipient_email']}")
                    st.text(f"📊 Campos: {len(task['fields'])} campos")
                    
                    if st.button("▶️ Executar Agora", key=f"run_{task['id']}", use_container_width=True):
                        with st.spinner("⚙️ Executando scraping..."):
                            result = execute_scraping_task(task)
                            
                            if result['success']:
                                st.success(f"✅ {result['total']} produto(s) encontrado(s)!")
                                
                                # Exibir produtos encontrados
                                if result.get('products'):
                                    st.dataframe(pd.DataFrame(result['products']), use_container_width=True)
                                
                                # Enviar email
                                email_result = send_email_notification(task, result)
                                if email_result == True:
                                    st.success("📧 Email enviado com sucesso!")
                                elif isinstance(email_result, str):
                                    st.info(f"📧 {email_result}")
                                
                                # Salvar no histórico
                                history = load_scraping_history()
                                history.append({
                                    'task_id': task['id'],
                                    'task_name': task['name'],
                                    'timestamp': pd.Timestamp.now().isoformat(),
                                    'success': True,
                                    'products_found': result['total']
                                })
                                save_scraping_history(history)
                            else:
                                st.error(f"❌ Erro: {result['error']}")
                                
                                # Salvar erro no histórico
                                history = load_scraping_history()
                                history.append({
                                    'task_id': task['id'],
                                    'task_name': task['name'],
                                    'timestamp': pd.Timestamp.now().isoformat(),
                                    'success': False,
                                    'error': result['error']
                                })
                                save_scraping_history(history)
                    
                    if st.button("🗑️ Excluir", key=f"del_{task['id']}", use_container_width=True):
                        tasks_updated = [t for t in tasks if t['id'] != task['id']]
                        if save_scraping_tasks(tasks_updated):
                            st.success("✅ Tarefa excluída!")
                            st.rerun()
        else:
            st.info("Nenhuma tarefa configurada ainda")
            st.caption("👈 Configure uma nova tarefa ao lado")
        
        st.divider()
        st.caption(f"📊 Total: {len(tasks)} tarefa(s)")
        
        if tasks:
            st.markdown("### 📜 Histórico")
            history = load_scraping_history()
            if history:
                # Mostrar apenas os últimos 5
                recent_history = sorted(history, key=lambda x: x['timestamp'], reverse=True)[:5]
                for h in recent_history:
                    status_icon = "✅" if h['success'] else "❌"
                    st.caption(f"{status_icon} {h['task_name']} - {pd.Timestamp(h['timestamp']).strftime('%d/%m %H:%M')}")
            else:
                st.caption("Nenhuma execução ainda")

st.divider()
st.caption("💡 Dica: Você pode inspecionar o código HTML da página usando as ferramentas de desenvolvedor do seu navegador (F12) para encontrar os seletores corretos.")
