def fazer_login(email, senha, headless=True):
    from playwright.sync_api import sync_playwright
    import json

    URL_LOGIN = "https://www.timbragemplan.com.br/Identity/Account/Login"
    COOKIE_PATH = "timbragem_cookies.json"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        print("➡️ Acessando login...")
        page.goto(URL_LOGIN)

        try:
            page.fill('input[name="Input.Email"]', email)
            page.fill('input[name="Input.Password"]', senha)
            page.click('button[type="submit"]')
            page.wait_for_url("**/Dashboard", timeout=15000)
            print("✅ Login realizado com sucesso!")
        except Exception as e:
            print("❌ Erro durante o login:", e)
            browser.close()
            return False  # <- garante retorno falso em erro

        # ✅ Se chegou até aqui, tudo OK
        cookies = context.cookies()
        with open(COOKIE_PATH, "w") as f:
            json.dump(cookies, f, indent=2)
        print(f"📁 Cookies salvos em: {COOKIE_PATH}")

        browser.close()
        return True  # ✅ retorno verdadeiro garantido
