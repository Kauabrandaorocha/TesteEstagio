from flask import Blueprint, request, jsonify
from controllers import operadoras_controller

operadoras_bp = Blueprint("operadoras", __name__)


@operadoras_bp.route("/api/operadoras", methods=["GET"])
def listar_operadoras():
    page = int(request.args.get("page", 1, type=int))
    limit = int(request.args.get("limit", 10, type=int))

    response = operadoras_controller.lista_operadoras(page, limit)
    return jsonify(response)


@operadoras_bp.route("/api/operadoras/<cnpj>", methods=["GET"])
def detalhe_operadora(cnpj):
    data, erro = operadoras_controller.detalhe_operadora(cnpj)

    if erro:
        return jsonify({"erro": erro}), 400 if "inválido" in erro else 404

    return jsonify(data)


@operadoras_bp.route("/api/operadoras/<cnpj>/despesas", methods=["GET"])
def despesas_operadora(cnpj):
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    data, erro = operadoras_controller.despesas_operadora(cnpj, page, limit)

    if erro:
        return jsonify({"erro": erro}), 400

    return jsonify(data)