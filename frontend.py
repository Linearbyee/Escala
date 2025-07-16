import tkinter as tk
from datetime import datetime
import os
from tkinter import ttk, messagebox
from backend import (
    carregar_membros, carregar_funcoes, carregar_cultos, carregar_bloqueios,
    carregar_escalas, carregar_funcoes_do_culto, carregar_vinculos,
    adicionar_pessoa, adicionar_funcao, adicionar_bloqueio, adicionar_culto,
    excluir_culto, gerar_escala, adicionar_vinculo, excluir_vinculo, exportar_escala_para_txt, excluir_todos_cultos, exportar_escala_para_notion
)

def validar_data(data_str):
    try:
        datetime.strptime(data_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False
    
# --- Funções de Atualização ---
def atualizar_lista_membros():
    lista_membros.delete(*lista_membros.get_children())
    for membro in carregar_membros():
        lista_membros.insert("", "end", values=(membro.id, membro.nome))

def atualizar_lista_funcoes():
    lista_funcoes.delete(*lista_funcoes.get_children())
    for funcao in carregar_funcoes():
        lista_funcoes.insert("", "end", values=(funcao.id, funcao.nome))

def atualizar_lista_bloqueios():
    lista_bloqueios.delete(*lista_bloqueios.get_children())
    for bloqueio in carregar_bloqueios():
        lista_bloqueios.insert("", "end", values=(bloqueio.id, bloqueio.membro.nome, bloqueio.data_inicio, bloqueio.data_fim))

def atualizar_lista_escalas():
    lista_escalas.delete(*lista_escalas.get_children())
    for escala in carregar_escalas():
        lista_escalas.insert("", "end", values=(escala.culto.data, escala.culto.turno, escala.funcao.nome, escala.membro.nome))

def atualizar_lista_cultos():
    lista_cultos.delete(*lista_cultos.get_children())
    for culto in carregar_cultos():
        funcoes = carregar_funcoes_do_culto(culto.id)
        lista_cultos.insert("", "end", values=(culto.id, culto.data, culto.turno, ", ".join(funcoes)))

def atualizar_lista_vinculos():
    lista_vinculos.delete(*lista_vinculos.get_children())
    for vinculo in carregar_vinculos():
        lista_vinculos.insert("", "end", values=(vinculo.id, vinculo.membro.nome, vinculo.funcao.nome, vinculo.nivel))

def atualizar_combobox_membros():
    membros = carregar_membros()
    lista_membros = [m.nome for m in membros]
    combo_membro["values"] = lista_membros

def atualizar_combobox_funcoes():
    funcoes = carregar_funcoes()
    lista_funcoes = [f.nome for f in funcoes]
    combo_funcao["values"] = lista_funcoes

# --- Funções de Adição/Exclusão ---
def adicionar_membro():
    nome = entrada_membro.get()
    if nome:
        try:
            adicionar_pessoa(nome)
            entrada_membro.delete(0, tk.END)
            atualizar_lista_membros()
            atualizar_combobox_membros()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar membro: {e}")

def adicionar_func():
    nome = entrada_funcao.get()
    if nome:
        try:
            adicionar_funcao(nome)
            entrada_funcao.delete(0, tk.END)
            atualizar_lista_funcoes()
            atualizar_combobox_funcoes()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar função: {e}")

def adicionar_bloqueio_gui():
    membro_id = entrada_membro_bloqueio.get()
    data_inicio = entrada_data_inicio.get()
    data_fim = entrada_data_fim.get()
    
    if not membro_id or not data_inicio or not data_fim:
        messagebox.showerror("Erro", "Preencha todos os campos!")
        return
    
    try:
        adicionar_bloqueio(int(membro_id), data_inicio, data_fim)
        atualizar_lista_bloqueios()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao adicionar bloqueio: {e}")

def adicionar_culto_gui():
    data = entrada_data_culto.get()
    turno = combo_turno_culto.get()
    funcoes_selecionadas = [f.id for f in funcoes_disponiveis if funcoes_var[f.id].get()]
    
    if not data or not turno or not funcoes_selecionadas:
        messagebox.showerror("Erro", "Preencha todos os campos e selecione pelo menos uma função!")
        return
    
    try:
        adicionar_culto(data, turno, funcoes_selecionadas)
        atualizar_lista_cultos()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao adicionar culto: {e}")

def excluir_culto_gui():
    culto_selecionado = lista_cultos.selection()
    if not culto_selecionado:
        messagebox.showerror("Erro", "Selecione um culto para excluir!")
        return
    
    culto_id = lista_cultos.item(culto_selecionado, "values")[0]
    try:
        excluir_culto(int(culto_id))
        atualizar_lista_cultos()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao excluir culto: {e}")

def gerar_escala_gui():
    try:
        # Pergunta ao usuário se deseja sobrescrever a escala existente
        if messagebox.askyesno(
            "Confirmar",
            "Isso irá gerar uma NOVA escala, substituindo a atual.\nDeseja continuar?"
        ):
            gerar_escala()
            atualizar_lista_escalas()
            messagebox.showinfo("Sucesso", "Nova escala gerada com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao gerar escala:\n{str(e)}")

def adicionar_vinculo_gui():
    membro_selecionado = combo_membro.get()
    funcao_selecionada = combo_funcao.get()
    nivel = combo_nivel.get()
    
    if not membro_selecionado or not funcao_selecionada or not nivel:
        messagebox.showerror("Erro", "Preencha todos os campos!")
        return
    
    try:
        membro_id = next(m.id for m in carregar_membros() if m.nome == membro_selecionado)
        funcao_id = next(f.id for f in carregar_funcoes() if f.nome == funcao_selecionada)
        adicionar_vinculo(membro_id, funcao_id, int(nivel))
        atualizar_lista_vinculos()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao adicionar vínculo: {e}")

def exportar_escala_txt(nome_arquivo):
    try:
        exportar_escala_para_txt(nome_arquivo)
        messagebox.showinfo("Sucesso", f"Escala exportada para:\n{os.path.abspath(nome_arquivo)}")
        
        # Abre o arquivo no bloco de notas (Windows)
        if os.name == 'nt':
            os.system(f'notepad "{nome_arquivo}"')
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao exportar:\n{str(e)}")

def excluir_todos_cultos_gui():
    try:
        # Confirmação EXTRA para operação perigosa
        if messagebox.askyesno(
            "CONFIRMAÇÃO CRÍTICA",
            "⚠️ ATENÇÃO! Isso removerá TODOS os cultos permanentemente.\n"
            "Todas as escalas associadas também serão perdidas.\n\n"
            "Tem certeza absoluta que deseja continuar?",
            icon='warning'
        ):
            excluir_todos_cultos()
            atualizar_lista_cultos()
            atualizar_lista_escalas()  # Atualiza a aba de escalas também
            messagebox.showinfo("Sucesso", "Todos os cultos foram removidos com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao excluir cultos:\n{str(e)}")

def excluir_vinculo_gui():
    vinculo_selecionado = lista_vinculos.selection()
    if not vinculo_selecionado:
        messagebox.showerror("Erro", "Selecione um vínculo para excluir!")
        return
    
    vinculo_id = lista_vinculos.item(vinculo_selecionado, "values")[0]
    try:
        excluir_vinculo(int(vinculo_id))
        atualizar_lista_vinculos()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao excluir vínculo: {e}")

def exportar_escala_para_notion_gui():
    try:
        exportar_escala_para_notion()  # ou a função correta que você pretende usar
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao exportar para Notion: {e}")

# --- Configuração da Janela Principal ---
root = tk.Tk()
root.title("Gerenciamento de Escala")
root.geometry("1000x600")

# Abas
abas = ttk.Notebook(root)
abas.pack(expand=1, fill="both")

# --- Aba Membros ---
aba_membros = ttk.Frame(abas)
abas.add(aba_membros, text="Membros")

tk.Label(aba_membros, text="Nome do Membro:").pack(pady=5)
entrada_membro = ttk.Entry(aba_membros, font=("Helvetica", 12))
entrada_membro.pack(pady=5)

btn_adicionar_membro = ttk.Button(aba_membros, text="Adicionar", command=adicionar_membro)
btn_adicionar_membro.pack(pady=10)

# Lista de Membros
frame_lista_membros = ttk.Frame(aba_membros)
frame_lista_membros.pack(fill="both", expand=True, padx=10, pady=10)

lista_membros = ttk.Treeview(frame_lista_membros, columns=("ID", "Nome"), show="headings")
lista_membros.heading("ID", text="ID")
lista_membros.heading("Nome", text="Nome")
lista_membros.pack(fill="both", expand=True)

scrollbar = ttk.Scrollbar(frame_lista_membros, orient="vertical", command=lista_membros.yview)
lista_membros.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

atualizar_lista_membros()

# --- Aba Funções ---
aba_funcoes = ttk.Frame(abas)
abas.add(aba_funcoes, text="Funções")

tk.Label(aba_funcoes, text="Nome da Função:").pack(pady=5)
entrada_funcao = ttk.Entry(aba_funcoes, font=("Helvetica", 12))
entrada_funcao.pack(pady=5)

btn_adicionar_funcao = ttk.Button(aba_funcoes, text="Adicionar", command=adicionar_func)
btn_adicionar_funcao.pack(pady=10)

# Lista de Funções
frame_lista_funcoes = ttk.Frame(aba_funcoes)
frame_lista_funcoes.pack(fill="both", expand=True, padx=10, pady=10)

lista_funcoes = ttk.Treeview(frame_lista_funcoes, columns=("ID", "Nome"), show="headings")
lista_funcoes.heading("ID", text="ID")
lista_funcoes.heading("Nome", text="Nome")
lista_funcoes.pack(fill="both", expand=True)

scrollbar = ttk.Scrollbar(frame_lista_funcoes, orient="vertical", command=lista_funcoes.yview)
lista_funcoes.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

atualizar_lista_funcoes()

# --- Aba Bloqueios ---
aba_bloqueios = ttk.Frame(abas)
abas.add(aba_bloqueios, text="Bloqueios")

tk.Label(aba_bloqueios, text="ID do Membro:").grid(row=0, column=0, padx=5, pady=5)
entrada_membro_bloqueio = ttk.Entry(aba_bloqueios)
entrada_membro_bloqueio.grid(row=0, column=1, padx=5, pady=5)

tk.Label(aba_bloqueios, text="Data de Início (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
entrada_data_inicio = ttk.Entry(aba_bloqueios)
entrada_data_inicio.grid(row=1, column=1, padx=5, pady=5)

tk.Label(aba_bloqueios, text="Data de Fim (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
entrada_data_fim = ttk.Entry(aba_bloqueios)
entrada_data_fim.grid(row=2, column=1, padx=5, pady=5)

btn_adicionar_bloqueio = ttk.Button(aba_bloqueios, text="Adicionar Bloqueio", command=adicionar_bloqueio_gui)
btn_adicionar_bloqueio.grid(row=3, column=0, columnspan=2, pady=10)

# Lista de Bloqueios
frame_lista_bloqueios = ttk.Frame(aba_bloqueios)
frame_lista_bloqueios.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

aba_bloqueios.grid_rowconfigure(4, weight=1)
aba_bloqueios.grid_columnconfigure(0, weight=1)
aba_bloqueios.grid_columnconfigure(1, weight=1)

lista_bloqueios = ttk.Treeview(frame_lista_bloqueios, columns=("ID", "Membro", "Início", "Fim"), show="headings")
lista_bloqueios.heading("ID", text="ID")
lista_bloqueios.heading("Membro", text="Membro")
lista_bloqueios.heading("Início", text="Início")
lista_bloqueios.heading("Fim", text="Fim")
lista_bloqueios.pack(fill="both", expand=True)

scrollbar = ttk.Scrollbar(frame_lista_bloqueios, orient="vertical", command=lista_bloqueios.yview)
lista_bloqueios.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

atualizar_lista_bloqueios()

# --- Aba Cultos ---
aba_cultos = ttk.Frame(abas)
abas.add(aba_cultos, text="Cultos")

tk.Label(aba_cultos, text="Data (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5)
entrada_data_culto = ttk.Entry(aba_cultos)
entrada_data_culto.grid(row=0, column=1, padx=5, pady=5)

tk.Label(aba_cultos, text="Turno:").grid(row=1, column=0, padx=5, pady=5)
combo_turno_culto = ttk.Combobox(aba_cultos, values=["Manhã", "Noite"])
combo_turno_culto.grid(row=1, column=1, padx=5, pady=5)

# Checkboxes para funções
funcoes_disponiveis = carregar_funcoes()
funcoes_var = {f.id: tk.BooleanVar() for f in funcoes_disponiveis}

for idx, funcao in enumerate(funcoes_disponiveis):
    chk = ttk.Checkbutton(aba_cultos, text=funcao.nome, variable=funcoes_var[funcao.id])
    chk.grid(row=2 + idx, column=0, columnspan=2, sticky="w", padx=10)

# Botões
btn_adicionar_culto = ttk.Button(aba_cultos, text="Adicionar Culto", command=adicionar_culto_gui)
btn_adicionar_culto.grid(row=2 + len(funcoes_disponiveis), column=0, padx=5, pady=10)

btn_excluir_culto = ttk.Button(aba_cultos, text="Excluir Culto", command=excluir_culto_gui)
btn_excluir_culto.grid(row=2 + len(funcoes_disponiveis), column=1, padx=5, pady=10)

# No frame da aba_cultos (após os outros botões)
btn_excluir_todos_cultos = ttk.Button(
    aba_cultos,
    text="⚠️ EXCLUIR TODOS OS CULTOS",
    command=excluir_todos_cultos_gui,
    style="Danger.TButton"  # Estilo especial para botão perigoso
)
btn_excluir_todos_cultos.grid(row=100, column=0, columnspan=2, pady=20, sticky="we")

# Adicione este estilo no início do seu frontend (com outros estilos):
style = ttk.Style()
style.configure("Danger.TButton", foreground="white", background="#dc3545", font=('Helvetica', 10, 'bold'))

# Lista de Cultos
frame_lista_cultos = ttk.Frame(aba_cultos)
frame_lista_cultos.grid(row=3 + len(funcoes_disponiveis), column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

aba_cultos.grid_rowconfigure(3 + len(funcoes_disponiveis), weight=1)
aba_cultos.grid_columnconfigure(0, weight=1)
aba_cultos.grid_columnconfigure(1, weight=1)

lista_cultos = ttk.Treeview(frame_lista_cultos, columns=("ID", "Data", "Turno", "Funções"), show="headings")
lista_cultos.heading("ID", text="ID")
lista_cultos.heading("Data", text="Data")
lista_cultos.heading("Turno", text="Turno")
lista_cultos.heading("Funções", text="Funções")
lista_cultos.pack(fill="both", expand=True)

scrollbar = ttk.Scrollbar(frame_lista_cultos, orient="vertical", command=lista_cultos.yview)
lista_cultos.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

atualizar_lista_cultos()

# --- Aba Escalas ---
aba_escalas = ttk.Frame(abas)
abas.add(aba_escalas, text="Escalas")

btn_gerar_escala = ttk.Button(aba_escalas, text="Gerar Escala", command=gerar_escala_gui)
btn_gerar_escala.pack(pady=10)
btn_exportar_txt = ttk.Button(
    aba_escalas, 
    text="Exportar para Bloco de Notas",
    command=lambda: exportar_escala_para_txt("escala_cultos.txt")
)
btn_exportar_txt.pack(pady=5)
btn_exportar_notion = ttk.Button(
    aba_escalas,
    text="Exportar para Notion",
    command=exportar_escala_para_notion_gui
)
btn_exportar_notion.pack(pady=5)

# Lista de Escalas
frame_lista_escalas = ttk.Frame(aba_escalas)
frame_lista_escalas.pack(fill="both", expand=True, padx=10, pady=10)

lista_escalas = ttk.Treeview(frame_lista_escalas, columns=("Data", "Turno", "Função", "Membro"), show="headings")
lista_escalas.heading("Data", text="Data")
lista_escalas.heading("Turno", text="Turno")
lista_escalas.heading("Função", text="Função")
lista_escalas.heading("Membro", text="Membro")
lista_escalas.pack(fill="both", expand=True)

scrollbar = ttk.Scrollbar(frame_lista_escalas, orient="vertical", command=lista_escalas.yview)
lista_escalas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")


# --- Aba Vínculos ---
aba_vinculos = ttk.Frame(abas)
abas.add(aba_vinculos, text="Vínculos")

frame_vinculo = ttk.Frame(aba_vinculos)
frame_vinculo.pack(pady=10)

# Comboboxes
tk.Label(frame_vinculo, text="Membro:").grid(row=0, column=0, padx=5)
combo_membro = ttk.Combobox(frame_vinculo, state="readonly")
combo_membro.grid(row=0, column=1, padx=5)
atualizar_combobox_membros()

tk.Label(frame_vinculo, text="Função:").grid(row=0, column=2, padx=5)
combo_funcao = ttk.Combobox(frame_vinculo, state="readonly")
combo_funcao.grid(row=0, column=3, padx=5)
atualizar_combobox_funcoes()

tk.Label(frame_vinculo, text="Nível:").grid(row=0, column=4, padx=5)
combo_nivel = ttk.Combobox(frame_vinculo, values=[1, 2, 3, 4, 5], state="readonly")
combo_nivel.grid(row=0, column=5, padx=5)

# Botões
btn_adicionar_vinculo = ttk.Button(frame_vinculo, text="Adicionar Vínculo", command=adicionar_vinculo_gui)
btn_adicionar_vinculo.grid(row=0, column=6, padx=5)

btn_excluir_vinculo = ttk.Button(frame_vinculo, text="Excluir Vínculo", command=excluir_vinculo_gui)
btn_excluir_vinculo.grid(row=0, column=7, padx=5)

# Lista de Vínculos com Scrollbar
frame_lista_vinculos = ttk.Frame(aba_vinculos)
frame_lista_vinculos.pack(fill="both", expand=True, padx=10, pady=10)

frame_lista_vinculos.grid_rowconfigure(0, weight=1)
frame_lista_vinculos.grid_columnconfigure(0, weight=1)

lista_vinculos = ttk.Treeview(frame_lista_vinculos, columns=("ID", "Membro", "Função", "Nível"), show="headings")
lista_vinculos.heading("ID", text="ID")
lista_vinculos.heading("Membro", text="Membro")
lista_vinculos.heading("Função", text="Função")
lista_vinculos.heading("Nível", text="Nível")
lista_vinculos.grid(row=0, column=0, sticky="nsew")

scrollbar_vinculos = ttk.Scrollbar(frame_lista_vinculos, orient="vertical", command=lista_vinculos.yview)
lista_vinculos.configure(yscrollcommand=scrollbar_vinculos.set)
scrollbar_vinculos.grid(row=0, column=1, sticky="ns")

atualizar_lista_vinculos()

root.mainloop()