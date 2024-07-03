import pandas as pd
from sqlalchemy.orm import sessionmaker
from models.database import engine, SessionLocal
from models.history import History

# Caminho para o arquivo CSV
file_path = 'history_sample.csv'

# Ler o arquivo CSV
df = pd.read_csv(file_path)

# Conectar ao banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# Importar os dados para o banco de dados
for index, row in df.iterrows():
    history_entry = History(
        url=row['url'],
        profundidade=row['profundidade'],
        paginas_extraidas=row['paginas_extraidas'],
        area_atuacao=row['area_atuacao']
    )
    session.add(history_entry)

# Commit e fechar a sessão
session.commit()
session.close()

print(f"Dados importados com sucesso de {file_path} para o banco de dados.")
