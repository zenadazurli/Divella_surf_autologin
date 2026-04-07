#!/usr/bin/env python3
# divellaeasy_auto_login.py - Versione finale per Render

import os
import time
import requests
import numpy as np
import cv2
import faiss
import json
import gc
import threading
from datetime import datetime
from datasets import load_dataset
from http.server import HTTPServer, BaseHTTPRequestHandler

# ================ CHIAVI BROWSERLESS (88 chiavi) ====================
BROWSERLESS_KEYS = [
    "2UI9I1FMeNAJT9X62b18b40ff03c0ab5a398738215c1a35bd", "2UI9JVRncuIpZrwe20186f338163de3534ad76e9e184c3f09",
    "2UI9xpzoJEYcY6nb2f6c397ca82c2d20dd03b736569bb072d", "2UI9yKT57zjUKeC17f2ef139dfb21e9391f2d96790e302f9b",
    "2UIA0m3dx66LBXE6a4b1186de64e0bd63678935960ad9372e", "2UIA2sljufDcaR475a778652b378cf6f77ac9fa9d4c5a32ef",
    "2UIA3tICKePo9wi2cbbf16afdab74a0660c1f7d582bf307fa", "2UIA56wVRPRiIJZf4be8d0d1ab54be1eb959f69334b81b6df",
    "2UIA72xUceBrbAC4beef9639833ec0d7edad133f85dfe1587", "2UIA8QdgmdsAc6v54560d55760e5919aab9f182f0f205b8d6",
    "2UIAAcCwwgjo8Jxda1d47ae047d722baa66197cef02c73df2", "2UIABDOnt0tb9cR4c4922c4e006e57e6c3570a7e08e605e9b",
    "2UFyHOdxsID23VMa0518a22c6b683ea3c11c1bdca148d5381", "2UIAHVuiTuotW5oa9a17ea35ffa0b176467ae249cb2e9c21d",
    "2UIAJ7EX7Cx0Isgc2a222a17b162723bec7c26999971cd4a8", "2UIAKZEPm9504lA7c89aff2d1a98319c74044d24fcfed1b8f",
    "2UIAM3ZqWKMs08wcd3acdc7cc7e95f61c1c6d58b70d30cdb2", "2UIANrMUJlMFYt97b604e6e370cf6ac938a182cc12888f03a",
    "2UIAPhsYM2P5F20b3a57ce055cadb610e4b1e488e498a23c3", "2UIAQdOwydhP3Llb1273217561612b92c0eceaf555cc3726b",
    "2UIASgiK5dB9KEkaf80d97f9bda1812e1cf8205c3389ff882", "2UIAUNFsUfCNq76c2288e39e2f4bdc49655630ee4ffdee31d",
    "2UIAeodfkrhgqDo0114e02b8f7c4ec7e64793f17f0de67497", "2UIAf0U41Twctlr77ecbfa2545692634758496b2eb88a170c",
    "2UIAhSj6AMSpgLM5400cb96e68c36236805887d583fa1c1a8", "2UIAjU7njVoSfKve470901ce3ba2544678cbd216af6700954",
    "2UIAkQ4DGbDLMB06db1a95369b032405097bcfe53b9b8d444", "2UIAm7L4ziritiqcedf7b01dd720a13d198be7f611936ad80",
    "2UIAoK9f3FItlml3f95c43bb78d2b15d3e274da5c52fcb5cd", "2UIAp4XWrMM0CET7bf5f8735c0e39a3f82fa9b631d7dde132",
    "2UIArIu84xpGFuV1b4e825a86352e4bec7b54db59df943bf0", "2UIAsvzIYtc0o6Pa719bbb072a635a0140cee8591aec0e617",
    "2UIAzLYxMfMvBTTf24fef2bee78bd26ccc8e423b6dbd9d72c", "2UIB0BADWlWBhpUd9b3113aae7aec11928693179b8e97adf7",
    "2UIB29qsdD8v3Vw8ba73f68bbd03cb6d26b344e49621909fb", "2UIB3HaKYNTplMU1532b53fbe5f3b48698cfae111c1ab6e2d",
    "2UIB58biba1EdFO560075a79336b620058976b070be297e50", "2UIB6YEl3joxmt513a32fea7091ad7a704774f80640aada78",
    "2UIB8rlEnDrj6Cv44d507f520ec52fa50046e7a70c30df6c6", "2UIB9J2tCnemabr9e97eff9685066c2072e18a52cfa283aa9",
    "2UIBB3QQ3H39YFu7d4fd1c778669ef19c8db22610905f23bb", "2UIBC8fgRMkg9wZ41fe0fe622994483be7093f33c02e53835",
    "2UIBGwfAlxxB6ni8919255b5bc976ec9ff72e0e7ee7f020de", "2UIBHpFuiMsVdXx3403174d9c61f08000e61d09260287e390",
    "2UIBJUl1ne3E92ya0949e27d64225c71a87e1d01458304c98", "2UIBKJ1ZL4HeXTTef781aa5c7c90ff94cc7d8e04545cf5ff9",
    "2UIBMTvCwvbW8zyeb1a2c2fc6d628643d2fc7837706f662d4", "2UIBOuJaRF5cBah589a83ba07a2bf4b4ae1e0bede889db139",
    "2UIBQDGaiPhyK5cc7d8d10689c2376b516809e26a4331bbe7", "2UIBRMkIfmmc5wU462f920ea771e4b0e8c29a96509179becd",
    "2UIBTMXwg0OXKdLdb313c233f7b40884382642b1336a75475", "2UIBUw762KYlNYe436d56b56b785ae327aea06af5c57b0856",
    "2UIBWGd7CenkAZP4e84a28fc45390849c04ec824c6b70c4aa", "2UIBX2qFOoT6UfQf0dca472d23a39ee0d2cc679711254df6e",
    "2UIBZ6iew6q5MjY587ca12d2ba6a8a7dec2887c680e0a295d", "2UIBalRcxjMmhLraa054e3a3fcc66019fa02e4756d40a97ca",
    "2UIBcJf0KJwjIJCc6aa92098f4b4d9677b277fa08bddaa52f", "2UIBdWa0VtcPa7l291b4497fca8ed7ad26b5c4d5927f54c52",
    "2UIBfg3C0DBareT4b3bc7b9de04934615085d885e0037c6a9", "2UIBg9igA9Adum65d15c87a1ebdbdd8462f2b769b9e6d0534",
    "2UIBiv7UFTo86PL7733f37e8662dc5ac1e44fbbfa69938c47", "2UIBjq41So7iISXc9b6488e29439c45ac81ec6655413598b7",
    "2UIBlZtTVvSSd9Mef4e7f74c7dadf262e366cf0d52a9278e1", "2UIBmotaoPEgiLGb4d8ff65588ad03856bca142e29d10f9d7",
    "2UIBoXymrMnL6rB7c0bf5d89b1d24423cf95f989c717a93da", "2UIBqLMCQct1MEc93871eac596a18158adf155055ea891b82",
    "2UIBsC5kqg908ss2b15a06dfd516f5477e644f4970239c2f3", "2UIBtryD9TY1rfLf40876aea895c6b19cfccd6d0423bb1a5a",
    "2UIBvZWEqIfKMABdb7ad2379d49b5fdb791668c5b8ae2872c", "2UIBwI8LlOkgnR2401030dc085c656433e9d9967c05cb8500",
    "2UIBzkNUiIo3aqf0fcbbefa77c3d721bcc90d6ea330d21b4b", "2UIC0txEnUKbs2e2011d4dbfcaccbf586e7cfd303ee25846c",
    "2UIC2RQTla00fnx09c8e8e078bda0be2ee065f87912fcf3ec", "2UIC3HmfnANB85ua2fafaa2b7d15fcddfaf43257ea8207a86",
    "2UIC5oOQStd9GOdd78704a1c13ede87f1ad076b3a3c5c014a", "2UIC6fQE3KZWxxF95f4c1b1514c6dd3d62ba0670368dbbdf0",
    "2UIC8HXKajhflGK4f6a4fc65b90703c46867dc5868233557d", "2UIC9N5NnxkvkiXc269dcbc7d2611f06b19dd6ac170a0e6a4",
    "2UICByRoMWLCFQP85171e81920c71c994e70f565ea94a5af9", "2UICCligGnceGaqb0567585836c440c4d21449a570494dfa6",
    "2UICEY4jAqkhpY0f3ecd736fb3d2b1df0f72a5ee544acf341", "2UICFz5KhinMtoGa87a2e4a5e156bb3e991297a8f794509c0",
    "2UICIQvD2zirSr161b5959fe434bec1ebe8e5ba0c62a03892", "2UICJ88uL7vxQXI13806d1cc2aab512c879ea4b47488aff01",
    "2UICLD7cUOCd06oe31be2d953915e565572bfc9990c96074b", "2UICM5P6tkSm3Qv2adc61218a5a7d6ea2f680320cd4db32ea",
    "2UICOGF3whhFISb5a4d943b2f658a0948de3321458f644f73", "2UICPYnut7CE37off5de03b2042b14aae1e1c8916eec85f6a",
    "2UICRMpGaWJQKP954bdcecee3ff7068055ac6c06af038c9e1",
]

BROWSERLESS_URL = "https://production-sfo.browserless.io/chrome/bql"

# Account EasyHits4U
EASYHITS_EMAIL = "sandrominori50+Uinrzrgtlqe@gmail.com"
EASYHITS_PASSWORD = "DDnmVV45!!"
REFERER_URL = "https://www.easyhits4u.com/?ref=nicolacaporale"

# ================ CONFIGURAZIONE ====================
DIM = 64
REQUEST_TIMEOUT = 15
ERRORI_DIR = "errori"
HEALTH_CHECK_PORT = int(os.environ.get('PORT', 10000))

current_key_index = 0
server_ready = False

dataset = None
classes_fast = None
faiss_index = None
vector_dim = 33

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def get_next_key():
    global current_key_index
    key = BROWSERLESS_KEYS[current_key_index % len(BROWSERLESS_KEYS)]
    current_key_index += 1
    log(f"   🔑 Usando chiave {current_key_index}/{len(BROWSERLESS_KEYS)}: {key[:10]}...")
    return key

def do_login():
    log("🔐 Esecuzione login...")
    
    for attempt in range(len(BROWSERLESS_KEYS)):
        api_key = get_next_key()
        
        query = f"""
        mutation {{
          goto(url: "https://www.easyhits4u.com/logon/", waitUntil: networkIdle, timeout: 60000) {{
            status
          }}
          solve(type: cloudflare, timeout: 60000) {{
            solved
            token
            time
          }}
          typeUsername: type(selector: "input[name='username']", text: "{EASYHITS_EMAIL}") {{
            time
          }}
          typePassword: type(selector: "input[name='password']", text: "{EASYHITS_PASSWORD}") {{
            time
          }}
          clickSubmit: click(selector: "form[action='/logon/'] input[type='submit']") {{
            time
          }}
        }}
        """
        
        url = f"{BROWSERLESS_URL}?token={api_key}&stealth=true&proxy=residential&proxyCountry=it"
        
        try:
            log(f"   📡 Invio richiesta a Browserless...")
            response = requests.post(url, json={"query": query}, timeout=120)
            log(f"   📡 Status code: {response.status_code}")
            
            if response.status_code != 200:
                log(f"   ❌ HTTP {response.status_code}")
                continue
            
            data = response.json()
            if "errors" in data:
                log(f"   ❌ BQL error: {data['errors']}")
                continue
            
            solve_info = data.get("data", {}).get("solve", {})
            log(f"   🛡️ Turnstile solved: {solve_info.get('solved')}")
            
            if not solve_info.get("solved"):
                log(f"   ❌ Turnstile non risolto")
                continue
            
            cookies = response.cookies.get_dict()
            log(f"   🍪 Cookie ricevuti: {list(cookies.keys())}")
            
            if 'user_id' in cookies:
                log(f"   ✅ Login OK! user_id={cookies['user_id']}")
                return cookies
            else:
                log(f"   ❌ user_id non trovato nei cookie")
                
        except Exception as e:
            log(f"   ❌ Eccezione: {e}")
            continue
    
    log("❌ Login fallito dopo tutti i tentativi")
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
    log("🚀 Avvio DivellaEasy - Auto Refresh")
    
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