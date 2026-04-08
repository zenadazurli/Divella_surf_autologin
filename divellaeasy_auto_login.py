#!/usr/bin/env python3
# test_step_by_step.py - Test ogni singolo passo

import requests
import time
import json
from datetime import datetime

# ================ CONFIGURAZIONE ====================
# Usa una sola chiave per test (la prima valida)
TEST_KEY = "2UG2N7qWFYK8FpG61e2f9913ec3368d2f02f87839db356dcc"
BROWSERLESS_URL = "https://production-sfo.browserless.io/chrome/bql"

EASYHITS_EMAIL = "sandrominori50+Uinrzrgtlqe@gmail.com"
EASYHITS_PASSWORD = "DDnmVV45!!"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def test_connection():
    """TEST 1: Verifica che la chiave sia valida (connessione base)"""
    log("📡 TEST 1: Verifica connessione a Browserless...")
    query = "{ status }"
    url = f"{BROWSERLESS_URL}?token={TEST_KEY}"
    
    try:
        start = time.time()
        response = requests.post(url, json={"query": query}, timeout=30)
        elapsed = time.time() - start
        log(f"   Status: {response.status_code} (tempo: {elapsed:.1f}s)")
        if response.status_code == 200:
            log("   ✅ Connessione OK")
            return True
        else:
            log(f"   ❌ Connessione fallita: {response.status_code}")
            return False
    except Exception as e:
        log(f"   ❌ Errore: {e}")
        return False

def test_solve_only():
    """TEST 2: Solo risoluzione Turnstile (senza goto)"""
    log("📡 TEST 2: Solo risoluzione Turnstile...")
    query = """
    mutation {
      solve(type: cloudflare, timeout: 60000) {
        solved
        token
        time
      }
    }
    """
    url = f"{BROWSERLESS_URL}?token={TEST_KEY}"
    
    try:
        start = time.time()
        response = requests.post(url, json={"query": query}, timeout=120)
        elapsed = time.time() - start
        log(f"   Status: {response.status_code} (tempo: {elapsed:.1f}s)")
        
        if response.status_code != 200:
            log(f"   ❌ HTTP {response.status_code}")
            return None
        
        data = response.json()
        if "errors" in data:
            log(f"   ❌ BQL error: {data['errors']}")
            return None
        
        solve_info = data.get("data", {}).get("solve", {})
        log(f"   Solved: {solve_info.get('solved')}")
        
        if solve_info.get("solved"):
            token = solve_info.get("token")
            log(f"   ✅ Token ottenuto: {token[:50]}...")
            return token
        else:
            log(f"   ❌ Token non risolto")
            return None
    except Exception as e:
        log(f"   ❌ Errore: {e}")
        return None

def test_goto_only():
    """TEST 3: Solo navigazione (senza solve)"""
    log("📡 TEST 3: Solo navigazione alla pagina...")
    query = """
    mutation {
      goto(url: "https://www.easyhits4u.com/logon/", waitUntil: networkIdle, timeout: 60000) {
        status
      }
    }
    """
    url = f"{BROWSERLESS_URL}?token={TEST_KEY}"
    
    try:
        start = time.time()
        response = requests.post(url, json={"query": query}, timeout=120)
        elapsed = time.time() - start
        log(f"   Status: {response.status_code} (tempo: {elapsed:.1f}s)")
        
        if response.status_code != 200:
            log(f"   ❌ HTTP {response.status_code}")
            return False
        
        data = response.json()
        if "errors" in data:
            log(f"   ❌ BQL error: {data['errors']}")
            return False
        
        goto_info = data.get("data", {}).get("goto", {})
        log(f"   Status: {goto_info.get('status')}")
        log(f"   ✅ Navigazione OK")
        return True
    except Exception as e:
        log(f"   ❌ Errore: {e}")
        return False

def test_goto_and_solve():
    """TEST 4: Navigazione + risoluzione Turnstile"""
    log("📡 TEST 4: Navigazione + risoluzione Turnstile...")
    query = """
    mutation {
      goto(url: "https://www.easyhits4u.com/logon/", waitUntil: networkIdle, timeout: 60000) {
        status
      }
      solve(type: cloudflare, timeout: 60000) {
        solved
        token
        time
      }
    }
    """
    url = f"{BROWSERLESS_URL}?token={TEST_KEY}"
    
    try:
        start = time.time()
        response = requests.post(url, json={"query": query}, timeout=120)
        elapsed = time.time() - start
        log(f"   Status: {response.status_code} (tempo: {elapsed:.1f}s)")
        
        if response.status_code != 200:
            log(f"   ❌ HTTP {response.status_code}")
            return None
        
        data = response.json()
        if "errors" in data:
            log(f"   ❌ BQL error: {data['errors']}")
            return None
        
        solve_info = data.get("data", {}).get("solve", {})
        log(f"   Solved: {solve_info.get('solved')}")
        
        if solve_info.get("solved"):
            token = solve_info.get("token")
            log(f"   ✅ Token ottenuto: {token[:50]}...")
            return token
        else:
            log(f"   ❌ Token non risolto")
            return None
    except Exception as e:
        log(f"   ❌ Errore: {e}")
        return None

def test_full_login_with_post(token):
    """TEST 5: Login con POST usando il token"""
    log("📡 TEST 5: Login con POST...")
    
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
    
    try:
        response = session.post("https://www.easyhits4u.com/logon/", data=data, headers=headers, allow_redirects=True, timeout=30)
        cookies = session.cookies.get_dict()
        log(f"   Status: {response.status_code}")
        log(f"   Cookie ricevuti: {list(cookies.keys())}")
        
        if 'user_id' in cookies:
            log(f"   ✅✅✅ LOGIN OK! user_id={cookies['user_id']}")
            return True
        else:
            log(f"   ❌ Login fallito - user_id non trovato")
            return False
    except Exception as e:
        log(f"   ❌ Errore: {e}")
        return False

def main():
    print("=" * 60)
    print("🔬 TEST PASSO-PASSO BROWSERLESS")
    print("=" * 60)
    
    results = {}
    
    # TEST 1: Connessione base
    results['connection'] = test_connection()
    
    if not results['connection']:
        log("❌ Test interrotto: connessione fallita")
        return
    
    # TEST 2: Solo solve
    token = test_solve_only()
    results['solve_only'] = token is not None
    
    # TEST 3: Solo goto
    results['goto_only'] = test_goto_only()
    
    # TEST 4: Goto + Solve
    token2 = test_goto_and_solve()
    results['goto_solve'] = token2 is not None
    
    # TEST 5: Login con POST (usa token dal test 2 o 4)
    final_token = token or token2
    if final_token:
        results['login_post'] = test_full_login_with_post(final_token)
    else:
        results['login_post'] = False
        log("❌ Nessun token disponibile per il login")
    
    # RIEPILOGO
    print("\n" + "=" * 60)
    print("📊 RIEPILOGO TEST")
    print("=" * 60)
    print(f"TEST 1 - Connessione base:      {'✅' if results['connection'] else '❌'}")
    print(f"TEST 2 - Solo solve:           {'✅' if results['solve_only'] else '❌'}")
    print(f"TEST 3 - Solo goto:            {'✅' if results['goto_only'] else '❌'}")
    print(f"TEST 4 - Goto + solve:         {'✅' if results['goto_solve'] else '❌'}")
    print(f"TEST 5 - Login con POST:       {'✅' if results['login_post'] else '❌'}")
    print("=" * 60)
    
    if results['login_post']:
        print("🎉 SUCCESSO! Il login funziona!")
    else:
        print("❌ Il login non funziona. Analizza i singoli test per capire dove fallisce.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()