import joblib
import pandas as pd
import spacy

# Carregar o modelo treinado e as colunas
model = joblib.load('ml/page_estimator_model.pkl')
model_columns = joblib.load('ml/model_columns.pkl')

# Carregar o modelo de linguagem spaCy
nlp = spacy.load('en_core_web_sm')

# Definir as áreas de atuação suportadas
SUPPORTED_AREAS = [
    'technology', 'health', 'finance', 'education', 'entertainment',
    'ecommerce', 'social_media', 'news', 'travel', 'public_services', 'blogs'
]

def classify_text(content: str) -> str:
    doc = nlp(content)
    areas = {
        "technology": {"technology", "tech", "software", "hardware", "tecnologia", "software", "hardware"},
        "health": {"health", "medicine", "medical", "wellness", "saúde", "medicina", "médico", "bem-estar"},
        "finance": {"finance", "banking", "investment", "money", "finanças", "banco", "investimento", "dinheiro"},
        "education": {"education", "school", "university", "learning", "educação", "escola", "universidade", "aprendizado"},
        "entertainment": {"entertainment", "movies", "music", "games", "entretenimento", "filmes", "música", "jogos"},
        "ecommerce": {"e-commerce", "shopping", "store", "compras", "loja", "varejo"},
        "social_media": {"social media", "community", "rede social", "comunidade"},
        "news": {"news", "publications", "notícias", "publicações", "jornal", "revista"},
        "travel": {"travel", "tourism", "viagens", "turismo", "destino", "hotel", "resort"},
        "public_services": {"public services", "government", "portais", "serviços públicos", "governo"},
        "blogs": {"blogs", "forums", "fóruns", "blog"}
    }

    area_scores = {area: 0 for area in areas}

    for token in doc:
        for area, keywords in areas.items():
            if token.lemma_ in keywords:
                area_scores[area] += 1

    # Determinar a área com a maior pontuação
    classified_area = max(area_scores, key=area_scores.get)
    if area_scores[classified_area] == 0:
        return "other"
    return classified_area

def predict_pages(area_atuacao: str, profundidade: int) -> float:
    # Verificar se a área de atuação é suportada
    if area_atuacao not in SUPPORTED_AREAS:
        raise ValueError(f"Área de atuação '{area_atuacao}' não reconhecida")

    # Criar um DataFrame com os dados fornecidos
    data = {
        'profundidade': [profundidade],
        'media_paginas_extraidas': [0]  # Placeholder, este valor será ajustado posteriormente
    }
    df = pd.DataFrame(data)

    # Adicionar colunas de área de atuação com valor 0
    for area in SUPPORTED_AREAS:
        df[f'area_atuacao_{area}'] = 0

    # Definir a coluna correspondente à área de atuação fornecida como 1
    df[f'area_atuacao_{area_atuacao}'] = 1

    # Garantir que todas as colunas estejam presentes no DataFrame
    for col in model_columns:
        if col not in df.columns:
            df[col] = 0

    # Reordenar as colunas para garantir que correspondam ao modelo
    df = df[model_columns]

    # Fazer a previsão usando o modelo treinado
    predicted_pages = model.predict(df)[0]

    return predicted_pages
