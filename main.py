from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# Глобально храним IP ESP32 (устанавливается через /receive_ip)
esp32_ip = "http://192.168.0.100"  # для теста можно оставить фиксированным

# HTML-шаблон страницы управления с тёмной темой
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Управление вентилятором ESP32</title>
    <style>
        :root {
            --bg-color: #121212;
            --text-color: #ffffff;
            --accent-color: #00d4ff;
            --slider-bg: #333;
            --slider-thumb: #00d4ff;
        }

        body {
            margin: 0;
            padding: 0;
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: start;
            min-height: 100vh;
            padding-top: 50px;
        }

        h1 {
            color: var(--accent-color);
            margin-bottom: 10px;
        }

        .ip {
            font-size: 16px;
            color: #aaa;
            margin-bottom: 30px;
        }

        .slider-container {
            width: 80%;
            max-width: 500px;
            margin: 0 auto;
        }

        input[type=range] {
            -webkit-appearance: none;
            width: 100%;
            height: 10px;
            border-radius: 5px;
            background: var(--slider-bg);
            outline: none;
            margin: 20px 0;
        }

        input[type=range]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: var(--slider-thumb);
            cursor: pointer;
            box-shadow: 0 0 8px rgba(0, 212, 255, 0.7);
        }

        #value {
            font-size: 28px;
            color: var(--accent-color);
            margin-top: 10px;
            transition: color 0.3s ease;
        }

        footer {
            margin-top: auto;
            padding: 20px;
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <h1>🎛️ Управление вентилятором ESP32</h1>
    <div class="ip">
        {% if esp32_ip %}
            📍 IP ESP32: {{ esp32_ip }}
        {% else %}
            ❌ ESP32 не подключён
        {% endif %}
    </div>

    <div class="slider-container">
        <input type="range" min="0" max="255" value="0" id="speedSlider">
        <div id="value">Скорость: 0</div>
    </div>

    <script>
        const slider = document.getElementById("speedSlider");
        const valueDisplay = document.getElementById("value");

        slider.oninput = function() {
            let speed = this.value;
            valueDisplay.textContent = "Скорость: " + speed;

            fetch('/update?speed=' + speed)
                .catch(err => console.error('Ошибка запроса:', err));
        };
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, esp32_ip=esp32_ip)

@app.route("/update")
def update_speed():
    global esp32_ip
    speed = request.args.get("speed", default=None)

    if not esp32_ip:
        return "ESP32 не подключён", 400

    if speed is not None and speed.isdigit():
        speed_val = int(speed)
        if 0 <= speed_val <= 255:
            try:
                url = f"{esp32_ip}/setSpeed?speed={speed_val}"
                print(f"[DEBUG] Запрос к ESP32: {url}")
                response = requests.get(url, timeout=2)
                return response.text, response.status_code
            except Exception as e:
                print(f"[ERROR] Ошибка при подключении к ESP32: {e}")
                return f"Ошибка подключения к ESP32: {e}", 500
    return "Неверное значение скорости", 400

@app.route("/receive_ip", methods=["POST"])
def receive_ip():
    global esp32_ip
    data = request.get_json()
    ip = data.get("ip")
    if ip:
        esp32_ip = f"http://{ip}"
        print(f"[INFO] Получен IP от ESP32: {esp32_ip}")
        return jsonify({"status": "success", "ip": ip}), 200
    else:
        return jsonify({"status": "error", "message": "IP не передан"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)