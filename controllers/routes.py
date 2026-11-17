from flask import Blueprint, jsonify, request, session, render_template, redirect, url_for
from models.database import get_db_connection
import sqlite3

api = Blueprint('api', __name__)

login_attempts = {}

IMAGE_FALLBACKS = {
    1: '/static/img/red_velvet.jpg',
    2: '/static/img/belga_trufado.jpg',
    3: '/static/img/ninho_nutella.jpg',
    4: '/static/img/limao_siciliano.jpg',
    5: '/static/img/churros_gourmet.jpg',
    6: '/static/img/frutas_vermelhas.jpg'
}

@api.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@api.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "API Python MVC + SQLite Conectada",
        "arquitetura": "MVC",
        "banco": "SQLite",
        "versao": "2.0.0"
    }), 200

@api.route('/api/cupcakes', methods=['GET'])
def listar_cupcakes():
    conn = get_db_connection()
    cursor = conn.cursor()
    categoria = request.args.get('categoria')
    busca = request.args.get('busca')
    
    query = "SELECT * FROM cupcakes WHERE 1=1"
    params = []
    
    if categoria and categoria != 'Todos':
        query += " AND categoria = ?"
        params.append(categoria)
    if busca:
        query += " AND nome LIKE ?"
        params.append(f"%{busca}%")
        
    cursor.execute(query, params)
    cupcakes = []
    for row in cursor.fetchall():
        item = dict(row)
        if not item.get("imagem_url"):
            item["imagem_url"] = IMAGE_FALLBACKS.get(item.get("id"), "/static/img/red_velvet.jpg")
        if not item.get("imagem_emoji"):
            item["imagem_emoji"] = "🧁"
        cupcakes.append(item)
    conn.close()
    return jsonify(cupcakes), 200

@api.route('/api/frete', methods=['POST'])
def calcular_frete():
    dados = request.get_json(silent=True) or {}
    cep = dados.get('cep', '')
    
    cep_limpo = str(cep).replace('-', '').strip()
    if not cep_limpo or len(cep_limpo) != 8 or not cep_limpo.isdigit():
        return jsonify({"ok": False, "erro": "CEP inválido. Digite 8 dígitos numéricos."}), 400
        
    return jsonify({
        "ok": True,
        "cep": cep,
        "frete": 8.50,
        "prazo": "Entrega agendada em 2 a 3 dias úteis"
    }), 200

@api.route('/api/auth/login', methods=['POST'])
def login():
    dados = request.get_json(silent=True) or {}
    email = dados.get('email', '').strip()
    senha = dados.get('senha', '')
    
    attempts = login_attempts.get(email, 0)
    if attempts >= 3:
        return jsonify({
            "ok": False,
            "erro": "Conta temporariamente bloqueada por excesso de tentativas.",
            "bloqueado": True
        }), 401

    if email == 'cliente@cupcake.com' and senha == '123456':
        login_attempts[email] = 0
        usuario = {"id": 1, "nome": "Cliente Gourmet", "email": email}
        session['cliente_logado'] = usuario
        return jsonify({"ok": True, "usuario": usuario}), 200
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE email = ? AND senha = ?", (email, senha))
    cliente = cursor.fetchone()
    conn.close()
    
    if cliente:
        login_attempts[email] = 0
        usuario = {
            "id": cliente["id"],
            "nome": cliente["nome"],
            "email": cliente["email"]
        }
        session['cliente_logado'] = usuario
        return jsonify({"ok": True, "usuario": usuario}), 200
    else:
        login_attempts[email] = attempts + 1
        is_blocked = login_attempts[email] >= 3
        return jsonify({
            "ok": False, 
            "erro": "E-mail ou senha incorretos.",
            "bloqueado": is_blocked
        }), 401

@api.route('/api/auth/register', methods=['POST'])
def register():
    dados = request.get_json(silent=True) or {}
    email = (dados.get('email') or '').strip()
    senha = dados.get('senha')
    nome = (dados.get('nome') or 'Novo Cliente').strip()
    cpf = dados.get('cpf', '')
    telefone = dados.get('telefone', '')

    if not email or not senha:
        return jsonify({"ok": False, "erro": "Preencha e-mail e senha obrigatórios."}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO clientes (nome, email, senha, cpf, telefone) VALUES (?, ?, ?, ?, ?)",
            (nome, email, senha, cpf, telefone)
        )
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"ok": False, "erro": "Este e-mail já está cadastrado no sistema."}), 400
    except Exception as e:
        conn.close()
        return jsonify({"ok": False, "erro": str(e)}), 400
    
    conn.close()
    novo_usuario = {
        "id": user_id,
        "nome": nome,
        "email": email,
        "cpf": cpf
    }
    session['cliente_logado'] = novo_usuario
    return jsonify({"ok": True, "usuario": novo_usuario}), 201

@api.route('/api/pedidos', methods=['POST'])
def criar_pedido():
    dados = request.get_json(silent=True) or {}
    cliente_id = dados.get('cliente_id') or 1
    endereco = dados.get('endereco_entrega')
    forma_pagamento = dados.get('forma_pagamento', 'PIX')
    itens = dados.get('itens', [])
    cupom = dados.get('cupom', '') or ''
    frete = float(dados.get('frete', 8.50))

    if not endereco or not itens:
        return jsonify({"ok": False, "erro": "Endereço de entrega e itens do carrinho são obrigatórios."}), 400

    subtotal = round(sum(float(item.get('preco', 0)) * int(item.get('quantidade', 1)) for item in itens), 2)
    desconto = round(subtotal * 0.10, 2) if cupom.strip().upper() == 'CUPCAKE10' else 0.0
    total = round(max(0.0, subtotal - desconto + frete), 2)

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Garante que cliente_id exista no banco para evitar falha de chave estrangeira
        cursor.execute("SELECT id FROM clientes WHERE id = ?", (cliente_id,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT OR IGNORE INTO clientes (id, nome, email, senha) VALUES (?, ?, ?, ?)",
                (cliente_id, f"Cliente {cliente_id}", f"cliente{cliente_id}@cupcake.com", "123456")
            )

        cursor.execute("SELECT MAX(id) FROM pedidos")
        res = cursor.fetchone()
        next_id = (res[0] or 0) + 1
        codigo_pedido = f"#PED-{1000 + next_id}"

        cursor.execute(
            """INSERT INTO pedidos 
               (codigo, cliente_id, endereco_entrega, forma_pagamento, status, subtotal, frete, desconto, total) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (codigo_pedido, cliente_id, endereco, forma_pagamento, 'Pedido Recebido', subtotal, frete, desconto, total)
        )
        conn.commit()
        pedido_id = cursor.lastrowid
    except Exception as e:
        conn.close()
        return jsonify({"ok": False, "erro": str(e)}), 400
    
    conn.close()

    return jsonify({
        "ok": True, 
        "pedido": {
            "id": pedido_id,
            "codigo": codigo_pedido,
            "cliente_id": cliente_id,
            "status": "Pedido Recebido",
            "subtotal": subtotal,
            "frete": frete,
            "desconto": desconto,
            "total": total
        }
    }), 201

@api.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        senha = request.form.get('senha')
        if senha == '123':
            session['admin_logged'] = True
            return redirect(url_for('api.admin_panel'))
        return render_template('admin_login.html', erro='Senha administrativa incorreta!')
    return render_template('admin_login.html')

@api.route('/admin', methods=['GET'])
def admin_panel():
    if not session.get('admin_logged'):
        return redirect(url_for('api.admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos ORDER BY id DESC")
    pedidos = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT COUNT(*) FROM clientes")
    total_clientes = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(total) FROM pedidos")
    faturamento_total = cursor.fetchone()[0] or 0.0
    conn.close()
    
    return render_template('admin.html', pedidos=pedidos, total_clientes=total_clientes, faturamento_total=faturamento_total)

@api.route('/admin/logout', methods=['GET'])
def admin_logout():
    session.pop('admin_logged', None)
    return redirect(url_for('api.index'))
