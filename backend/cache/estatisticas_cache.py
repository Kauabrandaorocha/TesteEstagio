import time

CACHE_TTL = 300  # Cachear resultado por 5 minutos (300 segundos)

estatisticas_cache = {
    "data": None,
    "timestamp": 0
}

def cache_valido():
    return (
        estatisticas_cache["data"] is not None
        and time.time() - estatisticas_cache["timestamp"] < CACHE_TTL
    )

def get_cache():
    return estatisticas_cache["data"]

def set_cache(data):
    estatisticas_cache["data"] = data
    estatisticas_cache["timestamp"] = time.time()