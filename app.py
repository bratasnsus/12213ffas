from flask import Flask, render_template, request, jsonify
import requests
import random
import string
import re
from threading import Lock

app = Flask(__name__)

# --- Proxy Ayarları ---
proxies_list = []
proxy_index = 0
proxy_lock = Lock()

def fetch_proxies():
    global proxies_list
    if proxies_list:
        return proxies_list
    sources = [
        "https://raw.githubusercontent.com/hproxy-com/free-proxy-list/main/http.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    ]
    for url in sources:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                for line in r.text.split('\n'):
                    line = line.strip()
                    if re.match(r'\d+\.\d+\.\d+\.\d+:\d+', line):
                        proxies_list.append(line)
                if proxies_list:
                    break
        except:
            continue
    return proxies_list

def get_proxy():
    global proxy_index
    if not proxies_list:
        return None
    with proxy_lock:
        p = proxies_list[proxy_index % len(proxies_list)]
        proxy_index += 1
        return {"http": f"http://{p}", "https": f"http://{p}"}

def gen_user():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))

def gen_pass():
    return ''.join(random.choice(string.ascii_letters + string.digits + "!@#$%^&*") for _ in range(12))

def create_one():
    domains = ["mailto.plus", "bugfoo.com", "usetoilet.com", "toomail.com", "mailbox.in.ua"]
    email = f"{gen_user()}@{random.choice(domains)}"
    password = gen_pass()
    
    for _ in range(5):  # 5 deneme
        proxy = get_proxy()
        try:
            r = requests.post(
                "https://api.mail.tm/accounts",
                json={"address": email, "password": password},
                headers={"Content-Type": "application/json"},
                proxies=proxy,
                timeout=10
            )
            if r.status_code in [200, 201]:
                return {"email": email, "password": password, "proxy": "OK"}
        except:
            pass
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    count = int(data.get('count', 1))
    if count > 50:
        count = 50
    
    fetch_proxies()
    results = []
    for _ in range(count):
        acc = create_one()
        if acc:
            results.append(acc)
    
    return jsonify({"accounts": results, "proxy_count": len(proxies_list)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)