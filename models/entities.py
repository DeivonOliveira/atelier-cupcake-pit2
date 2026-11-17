import random
from models.database import get_connection


class CupcakeModel:
    @staticmethod
    def listar_todos(categoria=None, busca=None):
        conn = get_connection()
        query = "SELECT * FROM cupcakes WHERE disponivel = 1"
        params = []
        if categoria and categoria != "Todos":
            query += " AND categoria = ?"
            params.append(categoria)
        if busca:
            query += " AND (LOWER(nome) LIKE ? OR LOWER(descricao) LIKE ?)"
            termo = f"%{busca.lower()}%"
            params.extend([termo, termo])
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def criar(nome, categoria, descricao, preco, imagem_emoji="🧁"):
        conn = get_connection()
        cur = conn.execute(
            "INSERT INTO cupcakes (nome, categoria, descricao, preco, imagem_emoji) VALUES (?, ?, ?, ?, ?)",
            (nome, categoria, descricao, float(preco), imagem_emoji or "🧁")
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return new_id

    @staticmethod
    def atualizar(cupcake_id, nome, categoria, descricao, preco, imagem_emoji):
        conn = get_connection()
        conn.execute(
            "UPDATE cupcakes SET nome = ?, categoria = ?, descricao = ?, preco = ?, imagem_emoji = ? WHERE id = ?",
            (nome, categoria, descricao, float(preco), imagem_emoji, cupcake_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def excluir(cupcake_id):
        conn = get_connection()
        conn.execute("UPDATE cupcakes SET disponivel = 0 WHERE id = ?", (cupcake_id,))
        conn.commit()
        conn.close()


class ClienteModel:
    @staticmethod
    def autenticar(email, senha):
        conn = get_connection()
        user = conn.execute("SELECT * FROM clientes WHERE LOWER(email) = ?", (email.lower().strip(),)).fetchone()
        if not user:
            conn.close()
            return {"ok": False, "erro": "E-mail nao cadastrado no sistema."}

        if user["bloqueado"] == 1:
            conn.close()
            return {"ok": False, "bloqueado": True, "erro": "Conta bloqueada apos 3 tentativas invalidas. Redefina a senha."}

        if user["senha"] != senha:
            tentativas = user["tentativas_falhas"] + 1
            bloqueado = 1 if tentativas >= 3 else 0
            conn.execute(
                "UPDATE clientes SET tentativas_falhas = ?, bloqueado = ? WHERE id = ?",
                (tentativas, bloqueado, user["id"])
            )
            conn.commit()
            conn.close()
            if bloqueado:
                return {"ok": False, "bloqueado": True, "erro": "Sua conta foi bloqueada por seguranca (3 erros consecutivos)."}
            restantes = 3 - tentativas
            return {"ok": False, "erro": f"Senha incorreta! Voce possui mais {restantes} tentativa(s)."}

        conn.execute("UPDATE clientes SET tentativas_falhas = 0 WHERE id = ?", (user["id"],))
        conn.commit()
        enderecos = conn.execute("SELECT * FROM enderecos WHERE cliente_id = ?", (user["id"],)).fetchall()
        conn.close()
        user_dict = dict(user)
        user_dict.pop("senha", None)
        user_dict["enderecos"] = [dict(e) for e in enderecos]
        return {"ok": True, "usuario": user_dict}

    @staticmethod
    def cadastrar(nome, email, senha, cpf="", rg="", telefone=""):
        conn = get_connection()
        existe = conn.execute("SELECT id FROM clientes WHERE LOWER(email) = ?", (email.lower().strip(),)).fetchone()
        if existe:
            conn.close()
            return {"ok": False, "erro": "Este e-mail ja esta cadastrado."}
        cur = conn.execute(
            "INSERT INTO clientes (nome, email, senha, cpf, rg, telefone) VALUES (?, ?, ?, ?, ?, ?)",
            (nome.strip(), email.lower().strip(), senha, cpf, rg, telefone)
        )
        conn.commit()
        new_id = cur.lastrowid
        user = conn.execute("SELECT id, nome, email, cpf, rg, telefone FROM clientes WHERE id = ?", (new_id,)).fetchone()
        conn.close()
        user_dict = dict(user)
        user_dict["enderecos"] = []
        return {"ok": True, "usuario": user_dict}

    @staticmethod
    def atualizar_perfil(cliente_id, nome, cpf, rg, telefone):
        conn = get_connection()
        conn.execute(
            "UPDATE clientes SET nome = ?, cpf = ?, rg = ?, telefone = ? WHERE id = ?",
            (nome, cpf, rg, telefone, cliente_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def adicionar_endereco(cliente_id, apelido, rua, numero, complemento, bairro, cep):
        conn = get_connection()
        cur = conn.execute(
            "INSERT INTO enderecos (cliente_id, apelido, rua, numero, complemento, bairro, cep) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (cliente_id, apelido or "Endereco", rua, numero, complemento, bairro, cep)
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return new_id

    @staticmethod
    def listar_enderecos(cliente_id):
        conn = get_connection()
        rows = conn.execute("SELECT * FROM enderecos WHERE cliente_id = ?", (cliente_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def desbloquear_e_redefinir(email, nova_senha):
        conn = get_connection()
        user = conn.execute("SELECT id FROM clientes WHERE LOWER(email) = ?", (email.lower().strip(),)).fetchone()
        if not user:
            conn.close()
            return False
        conn.execute(
            "UPDATE clientes SET senha = ?, tentativas_falhas = 0, bloqueado = 0 WHERE id = ?",
            (nova_senha, user["id"])
        )
        conn.commit()
        conn.close()
        return True


class PedidoModel:
    @staticmethod
    def calcular_totais(itens, cep="", cupom=""):
        subtotal = sum(float(i["preco"]) * int(i["quantidade"]) for i in itens)
        desconto = round(subtotal * 0.10, 2) if cupom.strip().upper() == "CUPCAKE10" else 0.0
        cep_limpo = "".join(filter(str.isdigit, cep or ""))
        if len(cep_limpo) == 8:
            frete = 0.0 if subtotal >= 60.0 else (8.50 if cep_limpo.startswith("80") else 12.90)
        else:
            frete = 10.00
        total = max(0.0, round(subtotal - desconto + frete, 2))
        return {"subtotal": round(subtotal, 2), "desconto": desconto, "frete": frete, "total": total}

    @staticmethod
    def criar(cliente_id, endereco_entrega, forma_pagamento, itens, cep="", cupom=""):
        totais = PedidoModel.calcular_totais(itens, cep, cupom)
        codigo = f"#PED-{random.randint(1000, 9999)}"
        conn = get_connection()
        cur = conn.execute(
            "INSERT INTO pedidos (codigo, cliente_id, endereco_entrega, forma_pagamento, subtotal, desconto, frete, total) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (codigo, cliente_id, endereco_entrega, forma_pagamento,
             totais["subtotal"], totais["desconto"], totais["frete"], totais["total"])
        )
        pedido_id = cur.lastrowid
        for item in itens:
            conn.execute(
                "INSERT INTO itens_pedido (pedido_id, cupcake_id, nome_produto, quantidade, preco_unitario) VALUES (?, ?, ?, ?, ?)",
                (pedido_id, item["id"], item["nome"], item["quantidade"], item["preco"])
            )
        conn.commit()
        conn.close()
        return {"id": pedido_id, "codigo": codigo, **totais, "status": "Pedido Recebido"}

    @staticmethod
    def listar(cliente_id=None):
        conn = get_connection()
        if cliente_id:
            pedidos = conn.execute(
                "SELECT p.*, c.nome as cliente_nome FROM pedidos p JOIN clientes c ON p.cliente_id = c.id WHERE p.cliente_id = ? ORDER BY p.id DESC",
                (cliente_id,)
            ).fetchall()
        else:
            pedidos = conn.execute(
                "SELECT p.*, c.nome as cliente_nome FROM pedidos p JOIN clientes c ON p.cliente_id = c.id ORDER BY p.id DESC"
            ).fetchall()

        resultado = []
        for p in pedidos:
            p_dict = dict(p)
            itens = conn.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (p["id"],)).fetchall()
            p_dict["itens"] = [dict(i) for i in itens]
            resultado.append(p_dict)
        conn.close()
        return resultado

    @staticmethod
    def atualizar_status(pedido_id, novo_status):
        conn = get_connection()
        conn.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
        conn.commit()
        conn.close()
