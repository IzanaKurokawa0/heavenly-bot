from flask import Flask, request, jsonify
import requests
import os
import logging

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Главная страница
@app.route('/')
def home():
    return jsonify({
        "service": "Brawl Stars Proxy",
        "status": "online",
        "endpoints": {
            "health": "/health",
            "real_ip": "/realip",
            "player_info": "/players/<tag>",
            "club_info": "/clubs/<tag>",
            "test_brawl": "/test/<tag>"
        },
        "instructions": "Add header: Authorization: Bearer YOUR_API_KEY",
        "server_url": "https://heavenly-bot75577.onrender.com"
    })

# Проверка работы
@app.route('/health')
def health():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return jsonify({
        "status": "online",
        "service": "brawl-proxy",
        "client_ip": client_ip,
        "server_host": request.host
    })

# Определение реального IP сервера
@app.route('/realip')
def realip():
    """Определяет реальный внешний IP сервера Render"""
    ip_services = [
        'https://api.ipify.org',
        'https://icanhazip.com',
        'https://checkip.amazonaws.com',
        'https://ipinfo.io/ip',
        'https://ifconfig.me/ip'
    ]
    
    results = {}
    
    for service in ip_services:
        try:
            response = requests.get(service, timeout=3)
            if response.status_code == 200:
                ip = response.text.strip()
                if ip and '.' in ip:  # Простая проверка что это IPv4
                    results[service] = ip
        except Exception as e:
            results[service] = f"error: {str(e)}"
    
    # Определяем наиболее вероятный IP
    from collections import Counter
    ip_counts = Counter(results.values())
    most_common_ip = ip_counts.most_common(1)[0][0] if ip_counts else "unknown"
    
    return jsonify({
        "detected_ip": most_common_ip,
        "all_results": results,
        "note": "Use this IP for Brawl Stars API registration",
        "recommendation": "Register API key with this IP on developer.brawlstars.com"
    })

# Тестовый запрос к Brawl Stars API
@app.route('/test/<tag>')
def test_brawl(tag):
    """Тестовый запрос для определения IP который видит Brawl Stars"""
    # Используем публичный тестовый ключ (ограниченный)
    test_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImQ5M2Q1NDA2LTFjNmYtNDRkMS1hOTcwLWRhMmIzMTAyODQxZiIsImlhdCI6MTczODI0MDc5NCwic3ViIjoiZGV2ZWxvcGVyLzA2MjNmYjVjLTcwYWYtNGNiZC1hYjAwLTAyNzI0Y2VkYmQ3YSIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiMC4wLjAuMC8wIl0sInR5cGUiOiJjbGllbnQifV19.4fC0cSfW4Qq1z8q4Q4q4Q4q4Q4q4Q4q4Q4q4Q4q4Q"
    
    headers = {
        "Authorization": f"Bearer {test_key}",
        "Accept": "application/json"
    }
    
    try:
        clean_tag = tag.replace('#', '')
        url = f"https://api.brawlstars.com/v1/players/%23{clean_tag}"
        
        logger.info(f"Making test request to Brawl Stars API")
        logger.info(f"URL: {url}")
        logger.info(f"Headers: {headers}")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        # Логируем всё
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                "success": True,
                "player_tag": data.get('tag'),
                "player_name": data.get('name'),
                "note": "Test successful! Now check Render logs to see which IP was used"
            })
        else:
            return jsonify({
                "success": False,
                "status_code": response.status_code,
                "response": response.json(),
                "note": "Check error details above"
            })
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "note": "Check server logs for details"
        }), 500

# Получить информацию об игроке
@app.route('/players/<tag>')
def get_player(tag):
    """Основной endpoint для получения данных игрока"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({
            "error": "API key required",
            "example": "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9..."
        }), 401
    
    api_key = auth_header.replace('Bearer ', '')
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    try:
        clean_tag = tag.replace('#', '')
        url = f"https://api.brawlstars.com/v1/players/%23{clean_tag}"
        
        # Логируем запрос
        logger.info(f"Player request - Tag: {tag}, API Key: {api_key[:10]}..., URL: {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        # Логируем ответ
        logger.info(f"Brawl Stars response - Status: {response.status_code}")
        
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return jsonify({
            "error": "Failed to connect to Brawl Stars API",
            "details": str(e)
        }), 500

# Получить информацию о клубе
@app.route('/clubs/<tag>')
def get_club(tag):
    """Основной endpoint для получения данных клуба"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return jsonify({
            "error": "API key required",
            "example": "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9..."
        }), 401
    
    api_key = auth_header.replace('Bearer ', '')
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    try:
        clean_tag = tag.replace('#', '')
        url = f"https://api.brawlstars.com/v1/clubs/%23{clean_tag}"
        
        logger.info(f"Club request - Tag: {tag}, API Key: {api_key[:10]}...")
        
        response = requests.get(url, headers=headers, timeout=10)
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return jsonify({
            "error": "Failed to connect to Brawl Stars API",
            "details": str(e)
        }), 500

# Endpoint для логов (только для отладки)
@app.route('/logs')
def show_logs():
    """Показывает последние логи (только для отладки)"""
    import io
    log_capture_string = io.StringIO()
    ch = logging.StreamHandler(log_capture_string)
    ch.setLevel(logging.INFO)
    
    # Добавляем хендлер к логгеру
    logger.addHandler(ch)
    
    # Получаем логи
    log_contents = log_capture_string.getvalue()
    log_capture_string.close()
    logger.removeHandler(ch)
    
    return jsonify({
        "logs": log_contents.split('\n')[-50:]  # Последние 50 строк
    })

# Обработчик ошибок
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
