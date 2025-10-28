import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
from io import StringIO
from lxml import html as lxml_html
from lxml import etree

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
        # Se for atributo XPath, retornar direto
        if is_xpath_attr and isinstance(elem, str):
            return elem
        
        # Detecção automática de imagens/atributos
        auto_detect_img = False
        auto_detect_attr = None
        
        if tipo == 'css':
            # CSS: detectar tags de imagem ou seletores com atributos
            if hasattr(elem, 'name'):
                if elem.name == 'img':
                    auto_detect_img = True
                    auto_detect_attr = 'src'
                elif elem.name == 'a' and elem.get('href'):
                    # Se for link, pode querer o href
                    if 'href' in selector.lower() or '@href' in selector:
                        auto_detect_attr = 'href'
        
        # Se detectou imagem, extrair src
        if auto_detect_img and auto_detect_attr and hasattr(elem, 'get'):
            value = elem.get(auto_detect_attr, '')
            if value:
                return value
        
        # Se deve extrair HTML completo
        if extrair_html:
            if tipo == 'css':
                return str(elem)
            elif tipo == 'xpath' and hasattr(elem, 'tag'):
                return lxml_html.tostring(elem, encoding='unicode')
        
        # Extração padrão de texto
        if tipo == 'css':
            return elem.get_text(strip=True)
        elif tipo == 'xpath':
            if hasattr(elem, 'text_content'):
                return elem.text_content().strip()
            else:
                return str(elem)
        
        return str(elem)
    except:
        return str(elem)

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

def extract_with_ai(html_content, user_query, ai_provider, api_key):
    """
    Usa IA para identificar seletores CSS/XPath baseado na descrição do usuário.
    Referência: blueprint:python_openai, blueprint:python_anthropic, blueprint:python_gemini
    """
    
    # Limpar HTML: remover scripts, CSS, comentários - manter apenas estrutura e conteúdo
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Remover tags desnecessárias (MAS manter <img> que é importante!)
    for tag in soup(['script', 'style', 'noscript', 'iframe']):
        tag.decompose()
    
    # Remover SVGs mas manter IMGs
    for tag in soup.find_all('svg'):
        tag.decompose()
    
    # Remover comentários
    for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
        comment.extract()
    
    # Remover atributos de evento (onclick, onload, etc)
    for tag in soup.find_all():
        attrs_to_remove = [attr for attr in tag.attrs if attr.startswith('on')]
        for attr in attrs_to_remove:
            del tag[attr]
    
    # Converter para string limpa
    html_clean = str(soup)
    
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
            
            st.markdown("**Descreva o que você quer extrair:**")
            user_query = st.text_area(
                "Descrição",
                placeholder="Exemplo: Quero extrair o título do produto, o preço e a descrição",
                height=100,
                key="ai_query"
            )
            
            col_btn, col_clear = st.columns([3, 1])
            with col_btn:
                if st.button("🤖 Identificar Seletores com IA", type="primary", key="ai_extract_button", use_container_width=True):
                    if not api_key:
                        st.warning("⚠️ Por favor, forneça uma API Key")
                    elif not user_query:
                        st.warning("⚠️ Por favor, descreva o que você quer extrair")
                    else:
                        with st.spinner(f"Consultando {ai_provider}..."):
                            result = extract_with_ai(
                                st.session_state.html_content,
                                user_query,
                                ai_provider,
                                api_key
                            )
                            st.session_state.ai_result = result
            
            with col_clear:
                if st.button("🗑️ Limpar", key="clear_ai_results", use_container_width=True):
                    st.session_state.ai_result = None
                    st.rerun()
            
            if st.session_state.ai_result is not None:
                result = st.session_state.ai_result
                
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.success("✅ Seletores identificados pela IA!")
                    
                    if "explicacao" in result:
                        st.info(f"💡 **Explicação:** {result['explicacao']}")
                    
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
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                csv = df_extracted.to_csv(index=False).encode('utf-8')
                                st.download_button(
                                    "📥 Download CSV",
                                    csv,
                                    "dados_ia_extraidos.csv",
                                    "text/csv",
                                    key='ai_csv'
                                )
                            with col2:
                                json_str = df_extracted.to_json(orient='records', force_ascii=False, indent=2)
                                st.download_button(
                                    "📥 Download JSON",
                                    json_str,
                                    "dados_ia_extraidos.json",
                                    "application/json",
                                    key='ai_json'
                                )
                            with col3:
                                if st.button("🎨 Visualização Melhorada", use_container_width=True, key="better_view_btn"):
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
                                        if extrair_html:
                                            # Para imagens e descrições completas, extrair HTML
                                            valores = []
                                            for elem in elements:
                                                # Se for tag <img>, pegar o src
                                                if elem.name == 'img':
                                                    valores.append(elem.get('src', ''))
                                                else:
                                                    # Para outros casos, pegar o HTML completo (com imagens)
                                                    valores.append(str(elem))
                                        else:
                                            # Para texto normal
                                            valores = [elem.get_text(strip=True) for elem in elements]
                                    elif tipo == 'xpath':
                                        tree = lxml_html.fromstring(html_content if html_content else response.text)
                                        elements = tree.xpath(seletor)
                                        valores = []
                                        for elem in elements:
                                            if isinstance(elem, str):
                                                valores.append(elem)
                                            elif hasattr(elem, 'text_content'):
                                                if extrair_html:
                                                    # Para HTML completo
                                                    valores.append(etree.tostring(elem, encoding='unicode'))
                                                else:
                                                    valores.append(elem.text_content().strip())
                                            else:
                                                valores.append(str(elem))
                                    else:
                                        valores = []
                                    row[descricao] = valores[0] if len(valores) == 1 else ', '.join(valores[:5]) + ('...' if len(valores) > 5 else '')
                                except:
                                    row[descricao] = ''
                            all_data.append(row)
                        elif bulk_method == "⚡ Método Universal (Múltiplos Seletores)" and bulk_selectors_text:
                            # Processar múltiplos seletores - uma linha por URL
                            row = {'Fonte': identifier}
                            selectors_list = [s.strip() for s in bulk_selectors_text.strip().split('\n') if s.strip()]
                            
                            for selector_idx, selector in enumerate(selectors_list, 1):
                                try:
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
                                        for elem in elements[:5]:
                                            valor = extract_element_value(elem, selector, tipo='xpath', is_xpath_attr=is_xpath_attr)
                                            if valor:
                                                valores.append(valor)
                                    else:
                                        # CSS
                                        elements = soup.select(selector)
                                        valores = []
                                        for elem in elements[:5]:
                                            valor = extract_element_value(elem, selector, tipo='css')
                                            if valor:
                                                valores.append(valor)
                                    
                                    # Nome da coluna: Seletor_{número} ou usa o próprio seletor se for curto
                                    col_name = f"Seletor_{selector_idx}" if len(selector) > 30 else selector
                                    row[col_name] = valores[0] if len(valores) == 1 else ', '.join(str(v) for v in valores) + ('...' if len(valores) >= 5 else '')
                                except Exception as e:
                                    row[f"Seletor_{selector_idx}"] = f"ERRO: {str(e)}"
                            
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
                    df = pd.DataFrame(all_data)
                    st.success(f"✅ Scraping concluído! {len(all_data)} elementos extraídos de {total} fonte(s)")
                    st.dataframe(df, use_container_width=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "📥 Download CSV (Todos os Dados)",
                            csv,
                            "scraping_massa.csv",
                            "text/csv",
                            key='bulk_csv'
                        )
                    with col2:
                        json_str = df.to_json(orient='records', force_ascii=False, indent=2)
                        st.download_button(
                            "📥 Download JSON (Todos os Dados)",
                            json_str,
                            "scraping_massa.json",
                            "application/json",
                            key='bulk_json'
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
