from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime
from notion_client import Client

# Configuração do banco de dados MySQL
engine = create_engine("mysql+pymysql://root:admin@localhost:3306/escala_db", echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# --- Modelos ---
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    senha_hash = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False)

class Membro(Base):
    __tablename__ = "membros"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), unique=True, nullable=False)
    funcoes = relationship("FuncaoMembro", back_populates="membro")
    bloqueios = relationship("Bloqueio", back_populates="membro")

class Funcao(Base):
    __tablename__ = "funcoes"
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), unique=True, nullable=False)

class FuncaoMembro(Base):
    __tablename__ = "funcoes_membros"
    id = Column(Integer, primary_key=True)
    membro_id = Column(Integer, ForeignKey("membros.id"))
    funcao_id = Column(Integer, ForeignKey("funcoes.id"))
    nivel = Column(Integer, nullable=False)

    membro = relationship("Membro", back_populates="funcoes")
    funcao = relationship("Funcao")

class Culto(Base):
    __tablename__ = "cultos"
    id = Column(Integer, primary_key=True)
    data = Column(Date, nullable=False)
    turno = Column(String(20), nullable=False)
    funcoes = relationship("CultoFuncao", back_populates="culto")

class CultoFuncao(Base):
    __tablename__ = "culto_funcoes"
    id = Column(Integer, primary_key=True)
    culto_id = Column(Integer, ForeignKey("cultos.id"))
    funcao_id = Column(Integer, ForeignKey("funcoes.id"))

    culto = relationship("Culto", back_populates="funcoes")
    funcao = relationship("Funcao")

class Escala(Base):
    __tablename__ = "escalas"
    id = Column(Integer, primary_key=True)
    culto_id = Column(Integer, ForeignKey("cultos.id"))
    funcao_id = Column(Integer, ForeignKey("funcoes.id"))
    membro_id = Column(Integer, ForeignKey("membros.id"), nullable=True)

    culto = relationship("Culto")
    funcao = relationship("Funcao")
    membro = relationship("Membro")

class Bloqueio(Base):
    __tablename__ = "bloqueios"
    id = Column(Integer, primary_key=True)
    membro_id = Column(Integer, ForeignKey("membros.id"))
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)

    membro = relationship("Membro", back_populates="bloqueios")

# Cria as tabelas no banco de dados
Base.metadata.create_all(engine)

notion = Client(auth="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")

def exportar_escala_para_notion(database_id):
    cultos = session.query(Culto).order_by(Culto.data).all()

    for culto in cultos:
        escalas = session.query(Escala).filter_by(culto_id=culto.id).all()
        escala_texto = ""

        for escala in escalas:
            membro = escala.membro.nome if escala.membro else "[VAGO]"
            escala_texto += f"{escala.funcao.nome}: {membro}\n"

        notion.pages.create(
            parent={"database_id": {"start": culto.data.isoformat()}},
            property={
                "Data": {"date": {"start" : culto.data.isoformat()}},
                "Turno": {"select": {"name": culto.turno}},
                "Escala": {"rich_text": [{"text": {"content": escala_texto}}]}

            }
        )

# Funções para manipulação de dados
def carregar_membros():
    return session.query(Membro).all()

def carregar_funcoes():
    return session.query(Funcao).all()

def carregar_cultos():
    return session.query(Culto).all()

def carregar_escalas():
    return session.query(Escala).all()

def carregar_bloqueios():
    return session.query(Bloqueio).all()

def carregar_vinculos():
    return session.query(FuncaoMembro).all()

def carregar_funcoes_do_culto(culto_id):
    culto = session.query(Culto).filter_by(id=culto_id).first()
    if culto:
        return [cf.funcao.nome for cf in culto.funcoes]
    return []

def adicionar_pessoa(nome):
    if not session.query(Membro).filter_by(nome=nome).first():
        session.add(Membro(nome=nome))
        session.commit()

def adicionar_funcao(nome):
    if not session.query(Funcao).filter_by(nome=nome).first():
        session.add(Funcao(nome=nome))
        session.commit()

def adicionar_bloqueio(membro_id, data_inicio, data_fim):
    data_inicio_formatada = datetime.strptime(data_inicio, "%Y-%m-%d").date()
    data_fim_formatada = datetime.strptime(data_fim, "%Y-%m-%d").date()
    
    # Verifica se já existe um bloqueio para o mesmo período
    bloqueio_existente = session.query(Bloqueio).filter(
        Bloqueio.membro_id == membro_id,
        Bloqueio.data_inicio <= data_fim_formatada,
        Bloqueio.data_fim >= data_inicio_formatada
    ).first()
    
    if bloqueio_existente:
        raise ValueError("Já existe um bloqueio para este período.")
    
    # Adiciona o novo bloqueio
    session.add(Bloqueio(membro_id=membro_id, data_inicio=data_inicio_formatada, data_fim=data_fim_formatada))
    session.commit()

def adicionar_vinculo(membro_id, funcao_id, nivel):
    if not session.query(FuncaoMembro).filter_by(membro_id=membro_id, funcao_id=funcao_id).first():
        session.add(FuncaoMembro(membro_id=membro_id, funcao_id=funcao_id, nivel=nivel))
        session.commit()

def excluir_vinculo(vinculo_id):
    """
    Exclui um vínculo com base no ID.
    """
    vinculo = session.query(FuncaoMembro).filter_by(id=vinculo_id).first()
    if vinculo:
        session.delete(vinculo)
        session.commit()
    else:
        raise ValueError("Vínculo não encontrado.")

def adicionar_culto(data, turno, funcoes):
    data_formatada = datetime.strptime(data, "%Y-%m-%d").date()
    novo_culto = Culto(data=data_formatada, turno=turno)
    session.add(novo_culto)
    session.commit()

    for funcao_id in funcoes:
        session.add(CultoFuncao(culto_id=novo_culto.id, funcao_id=funcao_id))
    session.commit()

def excluir_culto(culto_id):
    culto = session.query(Culto).filter_by(id=culto_id).first()
    if culto:
        session.delete(culto)
        session.commit()

def excluir_todos_cultos():
    """Remove todos os cultos e suas relações do banco de dados"""
    try:
        # Remove todas as escalas associadas primeiro
        session.query(Escala).delete()
        # Remove as relações de funções dos cultos
        session.query(CultoFuncao).delete()
        # Finalmente remove os cultos
        session.query(Culto).delete()
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e

def exportar_escala_para_txt(nome_arquivo="escalas.txt"):
    # Obtém todos os cultos ordenados por data
    cultos = session.query(Culto).order_by(Culto.data).all()
    
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write("ESCALA COMPLETA DE CULTOS\n")
        f.write("="*50 + "\n\n")
        
        for culto in cultos:
            # Cabeçalho do culto
            f.write(f"DATA: {culto.data.strftime('%d/%m/%Y (%A)')}\n")
            f.write(f"TURNO: {culto.turno}\n")
            f.write("-"*50 + "\n")
            
            # Obtém todas as funções definidas para este culto
            funcoes_do_culto = {cf.funcao for cf in culto.funcoes}
            
            # Obtém os membros escalados para este culto
            escalas_do_culto = {e.funcao: e.membro for e in session.query(Escala)
                               .filter_by(culto_id=culto.id).all()}
            
            # Escreve cada função da formação com o membro escalado
            for funcao in sorted(funcoes_do_culto, key=lambda x: x.nome):
                membro = escalas_do_culto.get(funcao)
                membro_nome = membro.nome if membro else "[VAGO]"
                f.write(f"{funcao.nome.upper():<20}: {membro_nome}\n")
            
            f.write("\n")  # Espaço entre cultos
        
        f.write("="*50 + "\n")
        f.write(f"Total de cultos: {len(cultos)}\n")
        f.write(f"Arquivo gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")   

def gerar_escala():
    # Limpa TODAS as escalas existentes antes de gerar novas
    session.query(Escala).delete()
    session.commit()

    cultos = session.query(Culto).order_by(Culto.data).all()
    membros = session.query(Membro).all()
    bloqueios = session.query(Bloqueio).all()
    vinculos = session.query(FuncaoMembro).all()

    # Dicionário para rastrear o último culto em que o membro foi escalado
    ultima_escala_membro = {membro.id: None for membro in membros}

    for culto in cultos:
        funcoes_do_culto = [cf.funcao for cf in culto.funcoes]
        membros_escalados = set()

        for funcao in funcoes_do_culto:
            candidatos = []

            for membro in membros:
                # Verifica se membro já está escalado neste culto
                if membro.id in membros_escalados:
                    continue

                # Verifica se membro está bloqueado no dia do culto
                bloqueado = any(
                    b.membro_id == membro.id and b.data_inicio <= culto.data <= b.data_fim
                    for b in bloqueios
                )
                if bloqueado:
                    continue

                # Verifica se o membro está vinculado à função
                vinculo = next((v for v in vinculos if v.membro_id == membro.id and v.funcao_id == funcao.id), None)
                if not vinculo:
                    continue

                # Penaliza membros que atuaram recentemente
                dias_desde_ultima_escala = (
                    (culto.data - ultima_escala_membro[membro.id]).days
                    if ultima_escala_membro[membro.id] else 9999
                )

                candidatos.append((membro, vinculo.nivel, dias_desde_ultima_escala))

            # Ordena os candidatos por maior nível e maior distância da última escala
            candidatos.sort(key=lambda x: (-x[1], -x[2]))

            if candidatos:
                escolhido = candidatos[0][0]
                membros_escalados.add(escolhido.id)
                ultima_escala_membro[escolhido.id] = culto.data

                nova_escala = Escala(culto_id=culto.id, funcao_id=funcao.id, membro_id=escolhido.id)
                session.add(nova_escala)

    session.commit()
