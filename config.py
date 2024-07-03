# config.py

MAX_LINKS_PER_PAGE = 100  # Limite para prevenir spider traps
DELAY = 0  # Delay entre requisições para evitar sobrecarregar o servidor
ALLOWED_FILE_TYPES = ['.html', '.htm', '']  # Por padrão, apenas HTML e URLs sem extensão são permitidos
MAX_WORKERS = 10  # Número máximo de threads
