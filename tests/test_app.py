import os
import tempfile
import pytest
from app import create_app


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.environ["CUPCAKE_DB_PATH"] = db_path
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
    os.close(db_fd)
    os.unlink(db_path)


def test_health_check(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["arquitetura"] == "MVC"
    assert data["banco"] == "SQLite"


def test_listar_cupcakes_seed(client):
    res = client.get("/api/cupcakes")
    assert res.status_code == 200
    cupcakes = res.get_json()
    assert len(cupcakes) >= 6


def test_bloqueio_login_apos_tres_tentativas(client):
    for _ in range(2):
        res = client.post("/api/auth/login", json={"email": "cliente@cupcake.com", "senha": "errada"})
        assert res.status_code == 401
        assert not res.get_json().get("bloqueado")

    res_bloqueio = client.post("/api/auth/login", json={"email": "cliente@cupcake.com", "senha": "errada"})
    assert res_bloqueio.status_code == 401
    assert res_bloqueio.get_json().get("bloqueado") is True


def test_cadastro_e_pedido_com_cupom(client):
    cad = client.post("/api/auth/register", json={
        "nome": "Maria Teste",
        "email": "maria@teste.com",
        "senha": "abc",
        "cpf": "111.222.333-44"
    })
    assert cad.status_code == 201
    user_id = cad.get_json()["usuario"]["id"]

    pedido = client.post("/api/pedidos", json={
        "cliente_id": user_id,
        "endereco_entrega": "Av. Paulista, 1000 - Sao Paulo/SP",
        "forma_pagamento": "PIX",
        "cep": "80420000",
        "cupom": "CUPCAKE10",
        "itens": [{"id": 1, "nome": "Red Velvet Classico", "quantidade": 2, "preco": 15.00}]
    })
    assert pedido.status_code == 201
    dados_pedido = pedido.get_json()["pedido"]
    assert dados_pedido["subtotal"] == 30.00
    assert dados_pedido["desconto"] == 3.00
    assert dados_pedido["frete"] == 8.50
    assert dados_pedido["total"] == 35.50
