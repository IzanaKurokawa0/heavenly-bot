from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Главная страница
@app.route('/')
def home():
    return jsonify({
        "service": "Brawl Stars Proxy",
        "status": "online",
        "endpoints": {
            "health": "/health",
            "player_info": "/players/<tag>",
            "club_info": "/clubs/<tag>"
        },
        "instructions": "Add header: Authorization: Bearer YOUR_API_KEY"
    })

# Проверка работы
@app.route('/health')
def health():
    return jsonify({
        "status": "online",
        "service": "brawl-proxy",
        "ip": request.remote_addr
    })

# Получить информацию об игроке
@app.route('/players/<tag>')
def get_player(tag):
    # Получаем API ключ из заголовка
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({
            "error": "API key required",
            "example": "Authorization: Bearer eyJ0eXAiOiJKV1..."
        }), 401
    
    api_key = auth_header.replace('Bearer ', '')
    
    # Формируем запрос к Brawl Stars API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    try:
        # Убираем # из тега если есть
        clean_tag = tag.replace('#', '')
        url = f"https://api.brawlstars.com/v1/players/%23{clean_tag}"
        
        response = requests.get(url, headers=headers, timeout=10)
        
        # Возвращаем ответ как есть
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Failed to connect to Brawl Stars API",
            "details": str(e)
        }), 500

# Получить информацию о клубе
@app.route('/clubs/<tag>')
def get_club(tag):
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({
            "error": "API key required",
            "example": "Authorization: Bearer eyJ0eXAiOiJKV1..."
        }), 401
    
    api_key = auth_header.replace('Bearer ', '')
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    try:
        clean_tag = tag.replace('#', '')
        url = f"https://api.brawlstars.com/v1/clubs/%23{clean_tag}"
        
        response = requests.get(url, headers=headers, timeout=10)
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Failed to connect to Brawl Stars API",
            "details": str(e)
        }), 500

# Обработчик ошибок
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
