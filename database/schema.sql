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
