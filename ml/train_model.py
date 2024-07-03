import sys
import os
from sqlalchemy.orm import sessionmaker
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import joblib

# Adiciona o caminho do diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.database import engine, SessionLocal
from models.history import History

def train_model():
    # Conectar ao banco de dados usando SQLAlchemy
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    # Carregar os dados
    data = session.query(History).all()
    session.close()

    # Converter os dados para um DataFrame do pandas
    df = pd.DataFrame([{
        'url': d.url,
        'profundidade': d.profundidade,
        'paginas_extraidas': d.paginas_extraidas,
        'area_atuacao': d.area_atuacao
    } for d in data])

    # Agrupar os dados por área de atuação e profundidade para calcular a média de páginas extraídas
    area_depth_grouped = df.groupby(['area_atuacao', 'profundidade'])['paginas_extraidas'].mean().reset_index()
    area_depth_grouped.columns = ['area_atuacao', 'profundidade', 'media_paginas_extraidas']

    # Mesclar a média de páginas extraídas por área de atuação e profundidade de volta ao DataFrame original
    df = pd.merge(df, area_depth_grouped, on=['area_atuacao', 'profundidade'], how='left')

    # Codificar a característica de área de atuação
    df = pd.get_dummies(df, columns=['area_atuacao'])

    # Garantir que todas as colunas dummy estejam presentes
    all_possible_areas = [
        'technology', 'health', 'finance', 'education', 'entertainment',
        'ecommerce', 'social_media', 'news', 'travel', 'public_services', 'blogs'
    ]
    for area in all_possible_areas:
        if f'area_atuacao_{area}' not in df.columns:
            df[f'area_atuacao_{area}'] = 0

    # Separar os recursos e o alvo
    X = df.drop(columns=['paginas_extraidas', 'url'])
    y = df['paginas_extraidas']

    # Dividir os dados em conjuntos de treinamento e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Treinar o modelo de regressão linear
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Fazer previsões
    y_pred = model.predict(X_test)

    # Avaliar o modelo
    mse = mean_squared_error(y_test, y_pred)
    print(f'Mean Squared Error: {mse}')

    # Salvar o modelo e as colunas
    joblib.dump(model, 'ml/page_estimator_model.pkl')
    joblib.dump(X.columns.tolist(), 'ml/model_columns.pkl')

if __name__ == "__main__":
    train_model()
