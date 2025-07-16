from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
    nivel = Column(Integer, nullable=False)  # Nível de habilidade de 1 a 5

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

# --- Configuração do Banco de Dados MySQL ---

engine = create_engine("mysql+mysqlconnector://usuario:senha@localhost/escala_db", echo=True)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
