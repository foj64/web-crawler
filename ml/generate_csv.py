import pandas as pd
import numpy as np

# Definindo as áreas de atuação
areas_atuacao = [
    'technology', 'health', 'finance', 'education', 'entertainment',
    'ecommerce', 'social_media', 'news', 'travel', 'public_services', 'blogs'
]

# Gerar dados fictícios
num_samples = 20
data = {
    'url': [f'http://example{i}.com' for i in range(num_samples)],
    'profundidade': np.random.randint(0, 4, num_samples),
    'paginas_extraidas': np.random.randint(5, 200, num_samples),
    'area_atuacao': np.random.choice(areas_atuacao, num_samples)
}

# Criar DataFrame
df = pd.DataFrame(data)

# Salvar em CSV
file_path = 'history_sample.csv'
df.to_csv(file_path, index=False)
