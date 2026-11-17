# Atelier do Cupcake - Projeto Integrador Transdisciplinar em Engenharia de Software II

Aplicacao web full-stack desenvolvida no padrao arquitetural **MVC (Model-View-Controller)** com **Python (Flask)** e banco de dados relacional **SQLite**.

## Estrutura de Diretorios (Padrao MVC)
```text
atelier-cupcake-pit2/
├── app.py                     # Ponto de entrada da aplicacao Flask
├── requirements.txt           # Dependencias do projeto
├── models/
│   ├── database.py            # Conexao SQLite e inicializacao do schema
│   └── entities.py            # Regras de negocio e persistencia (Model)
├── controllers/
│   └── routes.py              # Rotas web e endpoints REST (Controller)
├── templates/
│   └── index.html             # Interface do usuario responsiva (View)
├── database/
│   ├── schema.sql             # Projeto Fisico do Banco de Dados (DDL + Seed)
│   └── DICIONARIO_DADOS.md    # Dicionario de Dados completo
└── tests/
    └── test_app.py            # Testes unitarios automatizados com Pytest
```

## Como Executar Localmente
1. Instale as dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Inicie o servidor:
   ```bash
   python app.py
   ```
3. Acesse no navegador: `http://127.0.0.1:5000`

## Como Executar os Testes Unitarios (Pytest)
```bash
pytest -v
```
