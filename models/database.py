import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "database")
DEFAULT_DB_PATH = os.path.join(DB_DIR, "atelier_cupcake.db")
SCHEMA_PATH = os.path.join(DB_DIR, "schema.sql")

SEED_CUPCAKES = [
    (1, 'Red Velvet Clássico', 'Tradicionais', 'Massa aveludada de cacau suave com cobertura cremosa de cream cheese autêntico.', 14.90, '🧁', '/static/img/red_velvet.jpg'),
    (2, 'Belga Trufado 70%', 'Especiais', 'Chocolate belga intenso recheado com ganache meio amargo e raspas nobres.', 16.50, '🍫', '/static/img/belga_trufado.jpg'),
    (3, 'Ninho com Nutella', 'Favoritos', 'Massa de baunilha amanteigada com recheio cremoso de Leite Ninho e cobertura generosa de Nutella.', 15.90, '⭐', '/static/img/ninho_nutella.jpg'),
    (4, 'Limão Siciliano', 'Tradicionais', 'Massa fofinha com raspas de limão siciliano, recheio curd ácido e suspiro tostado.', 13.90, '🍋', '/static/img/limao_siciliano.jpg'),
    (5, 'Churros Gourmet', 'Favoritos', 'Massa infusionada com canela, recheado com doce de leite argentino artesanal.', 14.00, '🥖', '/static/img/churros_gourmet.jpg'),
    (6, 'Frutas Vermelhas', 'Especiais', 'Massa leve de baunilha com geleia artesanal de mirtilo, framboesa e morango.', 16.00, '🍓', '/static/img/frutas_vermelhas.jpg')
]

def get_connection(db_path=None):
    path = db_path or os.environ.get("CUPCAKE_DB_PATH", DEFAULT_DB_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

get_db_connection = get_connection

def init_db(db_path=None):
    path = db_path or os.environ.get("CUPCAKE_DB_PATH", DEFAULT_DB_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = get_connection(path)
    
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
    else:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS cupcakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                descricao TEXT,
                preco REAL NOT NULL,
                imagem_emoji TEXT,
                imagem_url TEXT
            );
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                cpf TEXT,
                rg TEXT,
                telefone TEXT
            );
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT NOT NULL,
                cliente_id INTEGER,
                endereco_entrega TEXT,
                forma_pagamento TEXT,
                status TEXT,
                subtotal REAL NOT NULL,
                frete REAL NOT NULL,
                desconto REAL NOT NULL,
                total REAL NOT NULL,
                criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(cliente_id) REFERENCES clientes(id)
            );
        """)

    cursor = conn.cursor()

    # Migração segura: caso o banco já exista de uma versão anterior sem imagem_url ou imagem_emoji
    cursor.execute("PRAGMA table_info(cupcakes)")
    cols_cupcakes = [row["name"] for row in cursor.fetchall()]
    if "imagem_url" not in cols_cupcakes:
        cursor.execute("ALTER TABLE cupcakes ADD COLUMN imagem_url TEXT")
    if "imagem_emoji" not in cols_cupcakes:
        cursor.execute("ALTER TABLE cupcakes ADD COLUMN imagem_emoji TEXT")

    cursor.execute("PRAGMA table_info(clientes)")
    cols_clientes = [row["name"] for row in cursor.fetchall()]
    if "telefone" not in cols_clientes:
        cursor.execute("ALTER TABLE clientes ADD COLUMN telefone TEXT")
    if "rg" not in cols_clientes:
        cursor.execute("ALTER TABLE clientes ADD COLUMN rg TEXT")

    # Garante que o cliente padrão (id=1) exista para evitar erro de FOREIGN KEY nos pedidos
    cursor.execute("SELECT COUNT(*) FROM clientes WHERE id = 1")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT OR IGNORE INTO clientes (id, nome, email, senha, cpf, telefone) VALUES (1, 'Cliente Gourmet', 'cliente@cupcake.com', '123456', '000.000.000-00', '(41) 99999-9999')"
        )

    # Inserir ou atualizar os 6 cupcakes com suas respectivas imagens reais
    cursor.execute("SELECT COUNT(*) FROM cupcakes")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.executemany(
            "INSERT INTO cupcakes (id, nome, categoria, descricao, preco, imagem_emoji, imagem_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
            SEED_CUPCAKES
        )
    else:
        for cid, nome, cat, desc, preco, emoji, img_url in SEED_CUPCAKES:
            cursor.execute(
                "UPDATE cupcakes SET imagem_url = ?, imagem_emoji = ? WHERE id = ? AND (imagem_url IS NULL OR imagem_url = '')",
                (img_url, emoji, cid)
            )
            cursor.execute(
                "INSERT OR IGNORE INTO cupcakes (id, nome, categoria, descricao, preco, imagem_emoji, imagem_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (cid, nome, cat, desc, preco, emoji, img_url)
            )

    conn.commit()
    conn.close()
