-- Projeto Fisico do Banco de Dados - Atelier do Cupcake (PIT II)
-- SGBD: SQLite 3 (Compativel com SQL padrao / MySQL / PostgreSQL)

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    cpf TEXT,
    rg TEXT,
    telefone TEXT,
    tentativas_falhas INTEGER DEFAULT 0,
    bloqueado INTEGER DEFAULT 0,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS enderecos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    apelido TEXT DEFAULT 'Principal',
    rua TEXT NOT NULL,
    numero TEXT NOT NULL,
    complemento TEXT,
    bairro TEXT NOT NULL,
    cep TEXT NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cupcakes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    categoria TEXT NOT NULL CHECK (categoria IN ('Tradicionais', 'Especiais', 'Veganos')),
    descricao TEXT NOT NULL,
    preco REAL NOT NULL CHECK (preco >= 0),
    imagem_emoji TEXT DEFAULT '🧁',
    disponivel INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    cliente_id INTEGER NOT NULL,
    endereco_entrega TEXT NOT NULL,
    forma_pagamento TEXT NOT NULL CHECK (forma_pagamento IN ('PIX', 'Cartao de Credito', 'Dinheiro')),
    subtotal REAL NOT NULL,
    desconto REAL DEFAULT 0,
    frete REAL DEFAULT 0,
    total REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pedido Recebido',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE TABLE IF NOT EXISTS itens_pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL,
    cupcake_id INTEGER NOT NULL,
    nome_produto TEXT NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario REAL NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
    FOREIGN KEY (cupcake_id) REFERENCES cupcakes(id)
);

INSERT OR IGNORE INTO clientes (id, nome, email, senha, cpf, rg, telefone)
VALUES (1, 'Cliente Demonstracao', 'cliente@cupcake.com', '123456', '123.456.789-00', '12.345.678-9', '(41) 99999-0000');

INSERT OR IGNORE INTO enderecos (id, cliente_id, apelido, rua, numero, bairro, cep)
VALUES (1, 1, 'Casa', 'Rua das Flores', '420', 'Batel', '80420-000');

INSERT OR IGNORE INTO cupcakes (id, nome, categoria, descricao, preco, imagem_emoji) VALUES
(1, 'Red Velvet Classico', 'Tradicionais', 'Massa aveludada de cacau suave com cobertura cremosa de cream cheese.', 14.90, '🧁'),
(2, 'Belga Trufado 70%', 'Especiais', 'Chocolate belga intenso recheado com ganache meio amargo e raspas.', 16.50, '🍫'),
(3, 'Pistache Siciliano', 'Especiais', 'Massa de baunilha bourbon com creme artesanal de pistache torrado.', 18.90, '🌿'),
(4, 'Ninho com Nutella', 'Tradicionais', 'Massa fofinha de leite Ninho com coracao cremoso de creme de avela.', 15.90, '🤎'),
(5, 'Limao Siciliano & Merengue', 'Tradicionais', 'Curd citrico de limao siciliano finalizado com merengue macaricado.', 14.50, '🍋'),
(6, 'Cacau Vegano & Frutas Vermelhas', 'Veganos', '100% vegetal, sem lactose, com geleia artesanal de framboesa e morango.', 16.00, '🍓');
