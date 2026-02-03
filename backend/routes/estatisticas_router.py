from flask import Blueprint, jsonify
from services.estatisticas_service import calcular_estatisticas
from cache.estatisticas_cache import cache_valido, get_cache, set_cache

estatisticas_bp = Blueprint("estatisticas", __name__)

@estatisticas_bp.route("/api/estatisticas", methods=["GET"])
def estatisticas():
    resultado = calcular_estatisticas()
    set_cache(resultado)

    if cache_valido():
        return jsonify({
            "cache": True,
            **get_cache()
        })

    return jsonify({
        "cache": False,
        **resultado
    })


