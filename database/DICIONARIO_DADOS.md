# Dicionario de Dados - Atelier do Cupcake (PIT II)

**SGBD:** SQLite 3  
**Padrao Arquitetural:** MVC (Model-View-Controller)  

## 1. Tabela `clientes`
| Campo | Tipo | Restricao | Nulo? | Descricao |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK, AUTOINCREMENT | Nao | Identificador unico do cliente |
| `nome` | TEXT | NOT NULL | Nao | Nome completo do cliente |
| `email` | TEXT | UNIQUE, NOT NULL | Nao | E-mail de login do cliente |
| `senha` | TEXT | NOT NULL | Nao | Senha de acesso |
| `cpf` | TEXT | Opcional | Sim | Cadastro de Pessoa Fisica |
| `rg` | TEXT | Opcional | Sim | Registro Geral do cliente |
| `telefone` | TEXT | Opcional | Sim | Telefone/WhatsApp de contato |
| `tentativas_falhas` | INTEGER | DEFAULT 0 | Nao | Contador de tentativas invalidas de login |
| `bloqueado` | INTEGER | DEFAULT 0 | Nao | Flag booleana (0 = ativo, 1 = bloqueado apos 3 falhas) |
| `criado_em` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Nao | Data e hora do cadastro |

## 2. Tabela `enderecos`
| Campo | Tipo | Restricao | Nulo? | Descricao |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK, AUTOINCREMENT | Nao | Identificador unico do endereco |
| `cliente_id` | INTEGER | FK -> `clientes(id)` | Nao | Referencia ao cliente proprietario |
| `apelido` | TEXT | DEFAULT 'Principal' | Nao | Identificacao (ex: Casa, Trabalho) |
| `rua` | TEXT | NOT NULL | Nao | Logradouro de entrega |
| `numero` | TEXT | NOT NULL | Nao | Numero do imovel |
| `complemento` | TEXT | Opcional | Sim | Apartamento ou ponto de referencia |
| `bairro` | TEXT | NOT NULL | Nao | Bairro de entrega |
| `cep` | TEXT | NOT NULL | Nao | Codigo de Enderecamento Postal |

## 3. Tabela `cupcakes`
| Campo | Tipo | Restricao | Nulo? | Descricao |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK, AUTOINCREMENT | Nao | Identificador unico do produto |
| `nome` | TEXT | NOT NULL | Nao | Nome comercial do cupcake |
| `categoria` | TEXT | CHECK IN ('Tradicionais','Especiais','Veganos') | Nao | Categoria para filtro na vitrine |
| `descricao` | TEXT | NOT NULL | Nao | Ingredientes e descricao detalhada |
| `preco` | REAL | CHECK (preco >= 0) | Nao | Valor unitario em Reais (R$) |
| `imagem_emoji` | TEXT | DEFAULT '🧁' | Nao | Icone representativo do produto |
| `disponivel` | INTEGER | DEFAULT 1 | Nao | Status de exibicao na vitrine (1 = ativo, 0 = inativo) |

## 4. Tabela `pedidos`
| Campo | Tipo | Restricao | Nulo? | Descricao |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK, AUTOINCREMENT | Nao | Identificador interno do pedido |
| `codigo` | TEXT | UNIQUE, NOT NULL | Nao | Codigo publico rastreavel (ex: `#PED-1042`) |
| `cliente_id` | INTEGER | FK -> `clientes(id)` | Nao | Cliente que realizou a compra |
| `endereco_entrega` | TEXT | NOT NULL | Nao | Endereco completo selecionado |
| `forma_pagamento` | TEXT | CHECK IN ('PIX','Cartao de Credito','Dinheiro') | Nao | Meio de pagamento escolhido |
| `subtotal` | REAL | NOT NULL | Nao | Soma dos itens antes de frete/desconto |
| `desconto` | REAL | DEFAULT 0 | Nao | Valor abatido por cupom promocional |
| `frete` | REAL | DEFAULT 0 | Nao | Valor da taxa de entrega |
| `total` | REAL | NOT NULL | Nao | Valor final cobrado do cliente |
| `status` | TEXT | DEFAULT 'Pedido Recebido' | Nao | Situacao atual do pedido |
| `criado_em` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Nao | Data e hora da compra |

## 5. Tabela `itens_pedido`
| Campo | Tipo | Restricao | Nulo? | Descricao |
| :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK, AUTOINCREMENT | Nao | Identificador unico do item |
| `pedido_id` | INTEGER | FK -> `pedidos(id)` | Nao | Pedido ao qual o item pertence |
| `cupcake_id` | INTEGER | FK -> `cupcakes(id)` | Nao | Produto comprado |
| `nome_produto` | TEXT | NOT NULL | Nao | Nome do produto no momento da compra |
| `quantidade` | INTEGER | CHECK (quantidade > 0) | Nao | Quantidade adquirida |
| `preco_unitario` | REAL | NOT NULL | Nao | Preco unitario praticado na compra |
