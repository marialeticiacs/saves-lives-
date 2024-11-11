from sqlalchemy import create_engine, Column, Float, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Configuração do banco de dados SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./weather_data.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definição da tabela de dados climáticos
class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    local = Column(String, index=True)
    temperatura = Column(Float)
    clima = Column(String)
    umidade = Column(Float)
    vento = Column(Float)
    alertas = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    latitude = Column(Float)     # Novo campo de latitude
    longitude = Column(Float)    # Novo campo de longitude

# Cria a tabela no banco de dados, se ainda não existir
Base.metadata.create_all(bind=engine)
