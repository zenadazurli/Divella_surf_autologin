#!/usr/bin/env python3
# divellaeasy_auto_login.py - Versione ScraperAPI (NO Browserless)

import os
import time
import requests
import numpy as np
import cv2
import faiss
import json
import gc
import threading
import re
from datetime import datetime
from datasets import load_dataset
from http.server import HTTPServer, BaseHTTPRequestHandler

# ================ CONFIGURAZIONE SCRAPERAPI ====================
SCRAPERAPI_KEY = "83cbc3a45816261c6a2b003c64ed6288"

# Account EasyHits4U
EASYHITS_EMAIL = "sandrominori50+Uinrzrgtlqe@gmail.com"
EASYHITS_PASSWORD = "DDnmVV45!!"
REFERER_URL = "https://www.easyhits4u.com/?ref=nicolacaporale"

# ================ CONFIGURAZIONE PRINCIPALE ====================
DIM = 64
REQUEST_TIMEOUT = 15
ERRORI_DIR = "errori"
HEALTH_CHECK_PORT = int(os.environ.get('PORT', 10000))

server_ready = False
dataset = None
classes_fast = None
faiss_index = None
vector_dim = 33

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def get_turnstile_token():
    """Ottiene il token Turnstile dalla pagina di login via ScraperAPI"""
    url = "https://www.easyhits4u.com/logon/"
    api_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={requests.utils.quote(url)}&render=true"
    
    log("🌐 Richiedo token Turnstile a ScraperAPI...")
    try:
        response = requests.get(api_url, timeout=120)
        if response.status_code != 200:
            log(f"   ❌ Errore HTTP: {response.status_code}")
            return None
        
        html = response.text
        match = re.search(r'name="cf-turnstile-response".*?value="([^"]+)"', html, re.IGNORECASE)
        
        if match:
            token = match.group(1)
            log(f"   ✅ Token ottenuto: {token[:50]}...")
            return token
        else:
            log("   ❌ Token non trovato nella risposta")
            return None
    except Exception as e:
        log(f"   ❌ Errore: {e}")
        return None

def do_login():
    """Esegue login usando ScraperAPI per ottenere il token"""
    log("🔐 Esecuzione login con ScraperAPI...")
    
    token = get_turnstile_token()
    if not token:
        log("❌ Token non ottenuto")
        return None
    
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://www.easyhits4u.com/logon/',
    }
    
    data = {
        'manual': '1',
        'fb_id': '',
        'fb_token': '',
        'google_code': '',
        'username': EASYHITS_EMAIL,
        'password': EASYHITS_PASSWORD,
        'cf-turnstile-response': token,
    }
    
    session.get(REFERER_URL)
    response = session.post("https://www.easyhits4u.com/logon/", data=data, headers=headers, allow_redirects=True, timeout=30)
    cookies = session.cookies.get_dict()
    
    if 'user_id' in cookies:
        log(f"   ✅ Login OK! user_id={cookies['user_id']}")
        return cookies
    else:
        log(f"   ❌ Login fallito")
        return None

# ================ HEALTH CHECK =====================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
    def log_message(self, format, *args):
        pass

def run_health_server():
    global server_ready
    try:
        server = HTTPServer(('0.0.0.0', HEALTH_CHECK_PORT), HealthHandler)
        server_ready = True
        log(f"🏥 Health check server avviato sulla porta {HEALTH_CHECK_PORT}")
        server.serve_forever()
    except Exception as e:
        log(f"❌ ERRORE health check: {e}")
        server_ready = False

health_thread = threading.Thread(target=run_health_server, daemon=True)
health_thread.start()
timeout = 10
while not server_ready and timeout > 0:
    time.sleep(0.5)
    timeout -= 0.5

# ================ DATASET =====================
def load_dataset_hf():
    global dataset, classes_fast, faiss_index
    log("📥 Caricamento dataset...")
    try:
        dataset = load_dataset("zenadazurli/easyhits4u-dataset", split="train", token=None)
        log(f"✅ Dataset caricato: {len(dataset)} vettori")
        class_names = dataset.features['y'].names
        classes_fast = {i: name for i, name in enumerate(class_names)}
        
        X_list = []
        batch_size = 500
        for i in range(0, len(dataset), batch_size):
            batch = dataset[i:i+batch_size]
            X_list.append(np.array(batch['X'], dtype=np.float32))
        
        X_all = np.vstack(X_list)
        nlist = 100
        m = 3
        d = vector_dim
        quantizer = faiss.IndexFlatL2(d)
        index = faiss.IndexIVFPQ(quantizer, d, nlist, m, 8)
        index.train(X_all)
        index.add(X_all)
        faiss_index = index
        del X_list, X_all
        gc.collect()
        return True
    except Exception as e:
        log(f"❌ Errore dataset: {e}")
        return False

# ================ FUNZIONI PER IL SURF =====================
def centra_figura(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return cv2.resize(image, (DIM, DIM))
    cnt = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(cnt)
    crop = image[y:y+h, x:x+w]
    return cv2.resize(crop, (DIM, DIM))

def estrai_descrittori(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    circularity = aspect_ratio = 0.0
    if contours:
        cnt = max(contours, key=cv2.contourArea)
        peri = cv2.arcLength(cnt, True)
        area = cv2.contourArea(cnt)
        if peri != 0:
            circularity = 4.0 * np.pi * area / (peri * peri)
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w)/h if h != 0 else 0.0
    moments = cv2.moments(thresh)
    hu = cv2.HuMoments(moments).flatten().tolist()
    h, w = img.shape[:2]
    cx, cy = w//2, h//2
    raggi = [int(min(h,w)*r) for r in (0.2, 0.4, 0.6, 0.8)]
    radiale = []
    for r in raggi:
        mask = np.zeros((h,w), np.uint8)
        cv2.circle(mask, (cx,cy), r, 255, -1)
        mean = cv2.mean(img, mask=mask)[:3]
        radiale.extend([m/255.0 for m in mean])
    spaziale = []
    quadranti = [(0,0,cx,cy), (cx,0,w,cy), (0,cy,cx,h), (cx,cy,w,h)]
    for (x1,y1,x2,y2) in quadranti:
        roi = img[y1:y2, x1:x2]
        if roi.size > 0:
            mean = cv2.mean(roi)[:3]
            spaziale.extend([m/255.0 for m in mean])
    vettore = radiale + spaziale + [circularity, aspect_ratio] + hu
    return np.array(vettore, dtype=float)

def get_features(img):
    img_centrata = centra_figura(img)
    return estrai_descrittori(img_centrata)

def predict(img_crop):
    if img_crop is None or img_crop.size == 0:
        return None
    features = get_features(img_crop).astype(np.float32).reshape(1, -1)
    distances, indices = faiss_index.search(features, 1)
    best_idx = indices[0][0]
    true_label_idx = dataset['y'][best_idx]
    return classes_fast.get(int(true_label_idx), "errore")

def crop_safe(img, coords):
    try:
        x1, y1, x2, y2 = map(int, coords.split(","))
    except:
        return None
    h, w = img.shape[:2]
    x1 = max(0, min(w-1, x1))
    x2 = max(0, min(w, x2))
    y1 = max(0, min(h-1, y1))
    y2 = max(0, min(h, y2))
    if x2 <= x1 or y2 <= y1:
        return None
    return img[y1:y2, x1:x2]

def salva_errore(qpic, img, picmap, labels, chosen_idx, motivo, urlid=None):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = os.path.join(ERRORI_DIR, f"{timestamp}_{qpic}")
    os.makedirs(folder, exist_ok=True)
    full_path = os.path.join(folder, "full.jpg")
    cv2.imwrite(full_path, img)
    for i, p in enumerate(picmap):
        crop = crop_safe(img, p.get("coords", ""))
        if crop is not None and crop.size > 0:
            crop_path = os.path.join(folder, f"crop_{i+1}.jpg")
            cv2.imwrite(crop_path, crop)
    metadata = {"timestamp": timestamp, "qpic": qpic, "urlid": urlid, "motivo": motivo}
    with open(os.path.join(folder, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    log(f"📁 Errore salvato in {folder}")

# ================ MAIN =====================
def main():
    log("=" * 50)
    log("🚀 Avvio DivellaEasy - Versione ScraperAPI")
    
    if not load_dataset_hf():
        return
    
    while True:
        cookies = do_login()
        if not cookies:
            log("❌ Login fallito, riprovo tra 60 secondi...")
            time.sleep(60)
            continue
        
        COOKIE_STRING = f"sesids={cookies.get('sesids', '')}; user_id={cookies.get('user_id', '')}"
        log(f"🍪 Cookie: {COOKIE_STRING}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Cookie": COOKIE_STRING
        }
        session = requests.Session()
        captcha_counter = 0
        
        while True:
            try:
                r = session.post(
                    "https://www.easyhits4u.com/surf/?ajax=1&try=1",
                    headers=headers, verify=False, timeout=REQUEST_TIMEOUT
                )
                
                if r.status_code != 200:
                    log(f"❌ Status {r.status_code} - Cookie scaduti?")
                    break
                
                data = r.json()
                urlid = data.get("surfses", {}).get("urlid")
                qpic = data.get("surfses", {}).get("qpic")
                seconds = int(data.get("surfses", {}).get("seconds", 20))
                picmap = data.get("picmap", [])
                
                if not urlid or not qpic or not picmap or len(picmap) < 5:
                    log(f"❌ Dati incompleti - Cookie scaduti?")
                    break
                
                img_data = session.get(f"https://www.easyhits4u.com/simg/{qpic}.jpg", verify=False).content
                img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
                crops = [crop_safe(img, p.get("coords", "")) for p in picmap]
                labels = [predict(c) for c in crops]
                log(f"Labels: {labels}")
                
                seen = {}
                chosen_idx = None
                for i, label in enumerate(labels):
                    if label and label != "errore":
                        if label in seen:
                            chosen_idx = seen[label]
                            break
                        seen[label] = i
                
                if chosen_idx is None:
                    log("❌ Nessun duplicato")
                    salva_errore(qpic, img, picmap, labels, None, "nessun_duplicato", urlid)
                    break
                
                time.sleep(seconds)
                word = picmap[chosen_idx]["value"]
                resp = session.get(
                    f"https://www.easyhits4u.com/surf/?f=surf&urlid={urlid}&surftype=2"
                    f"&ajax=1&word={word}&screen_width=1024&screen_height=768",
                    headers=headers, verify=False
                )
                
                if resp.json().get("warning") == "wrong_choice":
                    log("❌ Wrong choice")
                    salva_errore(qpic, img, picmap, labels, chosen_idx, "wrong_choice", urlid)
                    break
                
                captcha_counter += 1
                log(f"✅ OK - indice {chosen_idx} - Totale: {captcha_counter}")
                
                if captcha_counter % 10 == 0:
                    gc.collect()
                
                time.sleep(2)
                
            except Exception as e:
                log(f"❌ Errore: {e}")
                break
        
        log("🔄 Rinnovo sessione...")
        time.sleep(5)

if __name__ == "__main__":
    main()