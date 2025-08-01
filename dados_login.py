import sys
print("🧪 sys.argv:", sys.argv)
print("🧪 __file__:", __file__)

from login import fazer_login
from puxar_eventos import buscar_eventos  # ✅ deve bater com o nome do seu arquivo.py
from read_block import buscar_bloqueios  # ✅ deve bater com o nome do seu arquivo.py


email = "garcia.phsp@hotmail.com"
senha = "Phsp38082902"


modo = sys.argv[1].strip().lower() if len(sys.argv) > 1 else "eventos"
print("🧪 Modo detectado:", modo)


if modo == "eventos":
    sucesso = fazer_login(email, senha, headless=True)
    print("🧪 Sucesso login?", sucesso)
    if sucesso:
        print("🧪 Chamando buscar_eventos()...")
        buscar_eventos()
        
elif modo == "bloqueios":
    sucesso = fazer_login(email, senha, headless=True)
    if sucesso:
        from read_block import buscar_bloqueios
        buscar_bloqueios()



else:
    print("⚠️ Use:")
    print("   python dados_login.py login")
    print("   python dados_login.py eventos")
