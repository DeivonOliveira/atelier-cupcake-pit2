from flask import Blueprint, request, jsonify, render_template
from models.entities import CupcakeModel, ClienteModel, PedidoModel

api = Blueprint("api", __name__)


@api.route("/")
def index():
    return render_template("index.html")


@api.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "online", "arquitetura": "MVC", "backend": "Python/Flask", "banco": "SQLite"})


@api.route("/api/cupcakes", methods=["GET"])
def listar_cupcakes():
    categoria = request.args.get("categoria")
    busca = request.args.get("busca")
    return jsonify(CupcakeModel.listar_todos(categoria=categoria, busca=busca))


@api.route("/api/cupcakes", methods=["POST"])
def criar_cupcake():
    data = request.get_json() or {}
    if not data.get("nome") or data.get("preco") is None:
        return jsonify({"ok": False, "erro": "Nome e preco sao obrigatorios."}), 400
    new_id = CupcakeModel.criar(
        data["nome"],
        data.get("categoria", "Tradicionais"),
        data.get("descricao", ""),
        data["preco"],
        data.get("imagem_emoji", "🧁")
    )
    return jsonify({"ok": True, "id": new_id}), 201


@api.route("/api/cupcakes/<int:cupcake_id>", methods=["PUT"])
def editar_cupcake(cupcake_id):
    data = request.get_json() or {}
    CupcakeModel.atualizar(
        cupcake_id,
        data.get("nome"),
        data.get("categoria"),
        data.get("descricao"),
        data.get("preco"),
        data.get("imagem_emoji", "🧁")
    )
    return jsonify({"ok": True})


@api.route("/api/cupcakes/<int:cupcake_id>", methods=["DELETE"])
def deletar_cupcake(cupcake_id):
    CupcakeModel.excluir(cupcake_id)
    return jsonify({"ok": True})


@api.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    res = ClienteModel.autenticar(data.get("email", ""), data.get("senha", ""))
    status_code = 200 if res.get("ok") else 401
    return jsonify(res), status_code


@api.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    if not data.get("nome") or not data.get("email") or not data.get("senha"):
        return jsonify({"ok": False, "erro": "Preencha nome, e-mail e senha."}), 400
    res = ClienteModel.cadastrar(
        data["nome"], data["email"], data["senha"],
        data.get("cpf", ""), data.get("rg", ""), data.get("telefone", "")
    )
    return jsonify(res), (201 if res.get("ok") else 400)


@api.route("/api/auth/recuperar", methods=["POST"])
def recuperar():
    data = request.get_json() or {}
    ok = ClienteModel.desbloquear_e_redefinir(data.get("email", ""), data.get("nova_senha", "123456"))
    if not ok:
        return jsonify({"ok": False, "erro": "E-mail nao encontrado."}), 404
    return jsonify({"ok": True, "mensagem": "Senha redefinida e conta desbloqueada com sucesso!"})


@api.route("/api/clientes/<int:cliente_id>", methods=["PUT"])
def atualizar_cliente(cliente_id):
    data = request.get_json() or {}
    ClienteModel.atualizar_perfil(
        cliente_id, data.get("nome", ""), data.get("cpf", ""), data.get("rg", ""), data.get("telefone", "")
    )
    return jsonify({"ok": True})


@api.route("/api/clientes/<int:cliente_id>/enderecos", methods=["POST"])
def adicionar_endereco(cliente_id):
    data = request.get_json() or {}
    if not data.get("rua") or not data.get("cep"):
        return jsonify({"ok": False, "erro": "Rua e CEP sao obrigatorios."}), 400
    new_id = ClienteModel.adicionar_endereco(
        cliente_id,
        data.get("apelido", "Entrega"),
        data["rua"],
        data.get("numero", "S/N"),
        data.get("complemento", ""),
        data.get("bairro", ""),
        data["cep"]
    )
    return jsonify({"ok": True, "id": new_id, "enderecos": ClienteModel.listar_enderecos(cliente_id)}), 201


@api.route("/api/frete", methods=["POST"])
def calcular_frete():
    data = request.get_json() or {}
    cep = "".join(filter(str.isdigit, data.get("cep", "")))
    if len(cep) != 8:
        return jsonify({"ok": False, "erro": "CEP invalido. Digite os 8 numeros."}), 400
    totais = PedidoModel.calcular_totais(data.get("itens", []), cep, data.get("cupom", ""))
    return jsonify({"ok": True, **totais})


@api.route("/api/pedidos", methods=["GET"])
def listar_pedidos():
    cliente_id = request.args.get("cliente_id", type=int)
    return jsonify(PedidoModel.listar(cliente_id=cliente_id))


@api.route("/api/pedidos", methods=["POST"])
def criar_pedido():
    data = request.get_json() or {}
    itens = data.get("itens", [])
    if not itens:
        return jsonify({"ok": False, "erro": "O carrinho esta vazio."}), 400
    if not data.get("cliente_id") or not data.get("endereco_entrega"):
        return jsonify({"ok": False, "erro": "Selecione um cliente e um endereco de entrega."}), 400
    pedido = PedidoModel.criar(
        data["cliente_id"],
        data["endereco_entrega"],
        data.get("forma_pagamento", "PIX"),
        itens,
        data.get("cep", ""),
        data.get("cupom", "")
    )
    return jsonify({"ok": True, "pedido": pedido}), 201


@api.route("/api/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status_pedido(pedido_id):
    data = request.get_json() or {}
    PedidoModel.atualizar_status(pedido_id, data.get("status", "Em Preparo"))
    return jsonify({"ok": True})
