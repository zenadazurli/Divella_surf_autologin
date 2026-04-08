#!/usr/bin/env python3
# login_with_scrape.py - Sintassi corretta per /scrape

import requests
import time
import json
from datetime import datetime

# ================ CHIAVI BROWSERLESS ====================
BROWSERLESS_KEYS = [
    "2UG2N7qWFYK8FpG61e2f9913ec3368d2f02f87839db356dcc",
    "2UG2Ovzb5pkwkdua0d400b43082a6ad138fc947b98ad962ba",
    "2UG2QjLUmcxfw9Kfc631f82350b42772cfe9291bfbaf2ed27",
    "2UG2RgbTdpVTYBOf5942d35cd9f3da7b52af0bd115b1b3bdf",
    "2UG2TlpDxsQJn2Wd1f204756127d4ac2136b41bd01baaa0ca",
    "2UGdbQnmFCJwS9Vd714eb85438cf63d00a8f878a898cfe865",
    "2UGdcalCbtmQNCt0c0a65e134b1833ed5d77b0c27fec4df7a",
    "2UGdeyvPnuYf2tm78f5d97e862f004feef3a8e41dfd58b3ef",
    "2UGdfrLYfztPfpy65ea1648786cdfe855a89073f49a24fa15",
    "2UGdh0XeC72wcccb12714bdae43194a6a8647ce9a836d9cf9",
    "2UGdiXdiszEa5rw5c83ff671b0f30e6b45cb159d1b7a8f221",
    "2UH1q8Mnj1ERdcZf243e8d19a8e05da8998570d64e212cc3a",
    "2UH1rvpwwnyIqKYf3d2b847c23f1bf100eb78217b4abe399e",
    "2UH1tCPjVWSuutr98a6d9529fb8c03b457496afe6466ebac0",
    "2UH1uDTJQKxWMi750e2ad5d114a378275b4f4963b81476824",
    "2UH1xtruDYkpN6qafcf735210a0d390f38b7934fee7020509",
    "2UH1yEsOSdMyVgBb79e5d9f7283da3ab24b099772a221c0c1",
    "2UH200RyjgTPJAyd69e6979481a42076d9715120add383b2f",
    "2UH21NyLelnPOXN89ef213e06c030d3a20fe91f74ed023cd6",
    "2UH23g4Tjer24qYda1b38b3bf4995babae59f6ade1b5d80d5",
    "2UH24rd152tYgA9bfd616f9e0a1eee38c91957e77f7388367",
    "2UH26buZuikxxt088fe658690e962e79f00f03bae1c9c23d3",
]

BROWSERLESS_URL = "https://production-sfo.browserless.io/scrape"

# Account EasyHits4U
EASYHITS_EMAIL = "sandrominori50+Uinrzrgtlqe@gmail.com"
EASYHITS_PASSWORD = "DDnmVV45!!"
REFERER_URL = "https://www.easyhits4u.com/?ref=nicolacaporale"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def test_scrape():
    """Test semplice per vedere se /scrape funziona"""
    api_key = BROWSERLESS_KEYS[0]
    url = f"{BROWSERLESS_URL}?token={api_key}"
    
    # Test con un selettore semplice
    payload = {
        "url": "https://www.easyhits4u.com/logon/",
        "elements": [{"selector": "title"}]
    }
    
    log("📡 Test /scrape con selettore 'title'...")
    try:
        response = requests.post(url, json=payload, timeout=30)
        log(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            log(f"   Risposta: {json.dumps(data, indent=2)[:500]}")
            return True
        else:
            log(f"   Errore: {response.text[:200]}")
            return False
    except Exception as e:
        log(f"   Errore: {e}")
        return False

def test_extract_token():
    """Test per estrarre il token Turnstile"""
    api_key = BROWSERLESS_KEYS[0]
    url = f"{BROWSERLESS_URL}?token={api_key}"
    
    # Usa JavaScript per estrarre il token
    payload = {
        "url": "https://www.easyhits4u.com/logon/",
        "js": """
            (async () => {
                await page.waitForSelector('input[name="cf-turnstile-response"]', { timeout: 30000 });
                const token = await page.$eval('input[name="cf-turnstile-response"]', el => el.value);
                return { token: token };
            })();
        """
    }
    
    log("📡 Test /scrape con JavaScript...")
    try:
        response = requests.post(url, json=payload, timeout=60)
        log(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            log(f"   Risposta: {json.dumps(data, indent=2)[:500]}")
            token = data.get("token")
            if token:
                log(f"   ✅ Token ottenuto: {token[:50]}...")
                return token
        else:
            log(f"   Errore: {response.text[:200]}")
            return None
    except Exception as e:
        log(f"   Errore: {e}")
        return None

def perform_login(token):
    """Esegue il login usando il token"""
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.easyhits4u.com',
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
    return session.cookies.get_dict()

def main():
    print("=" * 60)
    print("🔬 TEST ENDPOINT /scrape")
    print("=" * 60)
    
    # Test 1: Selettore semplice
    if not test_scrape():
        log("❌ Test selettore fallito")
        return
    
    # Test 2: Estrazione token
    token = test_extract_token()
    if not token:
        log("❌ Estrazione token fallita")
        return
    
    # Test 3: Login
    cookies = perform_login(token)
    if 'user_id' in cookies:
        log(f"   ✅✅✅ LOGIN OK! user_id={cookies['user_id']}")
        print("\n" + "=" * 60)
        print("🎉 SUCCESSO!")
        print(f"   user_id: {cookies['user_id']}")
        print(f"   sesids: {cookies.get('sesids', 'N/A')}")
        print("=" * 60)
    else:
        log(f"   ❌ Login fallito - cookie: {list(cookies.keys())}")

if __name__ == "__main__":
    main()