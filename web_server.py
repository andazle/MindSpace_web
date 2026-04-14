from waitress import serve
from app import app  # Импортируем твой объект Flask из app.py

if __name__ == '__main__':
    print("Сервер MindSpace запущен на порту 8080...")
    print("Локальный адрес: http://localhost:8080")
    # host='0.0.0.0' позволяет принимать подключения из локальной сети
    serve(app, host='0.0.0.0', port=8080, threads=4)