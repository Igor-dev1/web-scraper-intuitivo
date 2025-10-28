from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Permitir todas as origens

@app.route('/proxy', methods=['GET'])
def proxy():
    """
    Endpoint que funciona como proxy CORS para buscar páginas web.
    Uso: /proxy?url=https://exemplo.com
    """
    target_url = request.args.get('url')
    
    if not target_url:
        return jsonify({'error': 'URL não fornecida'}), 400
    
    try:
        # Usar corsproxy.io como intermediário
        proxy_url = f'https://corsproxy.io/?{target_url}'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(proxy_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Retornar HTML com headers CORS corretos
        return response.text, 200, {
            'Content-Type': 'text/html; charset=utf-8',
            'Access-Control-Allow-Origin': '*'
        }
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Endpoint para verificar se o servidor está rodando"""
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    # Rodar na porta 5001 (5000 é do Streamlit)
    app.run(host='0.0.0.0', port=5001, debug=False)
