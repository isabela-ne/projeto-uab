# PokéShop — Loja Virtual Pokémon

> Projeto desenvolvido para a disciplina de Desenvolvimento Web — IFTO/UAB 2026

## Sobre o Projeto

A PokéShop é um e-commerce completo de produtos temáticos do universo Pokémon, desenvolvido com Flask (Python). O sistema permite que clientes naveguem pelo catálogo, adicionem produtos ao carrinho, calculem frete e realizem compras. Administradores gerenciam produtos, usuários e cupons de desconto pelo painel admin.

## Funcionalidades

- Cadastro e login de usuários com bloqueio após 5 tentativas
- Catálogo de produtos com busca, filtros e página de detalhe
- Carrinho de compras com cálculo de frete por CEP
- Cupons de desconto
- Avaliações de produtos com estrelas e comentários
- Sistema de suporte ao cliente (chamados)
- Painel administrativo completo
- Containerização com Docker

## Tecnologias

- Python 3.12
- Flask 3
- SQLAlchemy + SQLite
- Flask-Login, Flask-WTF, Flask-Migrate
- Bootstrap 5
- Docker

## Como Rodar

### Sem Docker

```bash
# 1. Clonar o repositório
git clone https://github.com/isabela-ne/projeto-uab.git
cd projeto-uab

# 2. Criar e ativar o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env

# 5. Rodar o seed inicial
python scripts/seed.py

# 6. Iniciar o servidor
python run.py
```

Acesse: http://localhost:5000

### Com Docker

```bash
docker-compose up --build
```

Acesse: http://localhost:5000

## Acesso Admin

| Campo | Valor |
|---|---|
| E-mail | admin@pokeshop.local |
| Senha | Admin@2026! |

## Cupons de Teste

| Cupom | Desconto |
|---|---|
| POKEMON10 | 10% OFF |
| POKEPARA20 | 20% OFF |

## Estrutura do Projeto
projeto-uab/
├── app/
│   ├── blueprints/     # Rotas por módulo
│   ├── models/         # Modelos do banco de dados
│   ├── templates/      # Templates HTML
│   └── static/         # Imagens e arquivos estáticos
├── scripts/
│   └── seed.py         # Dados iniciais
├── doc/
│   └── 03-especs.md    # Especificações do sistema
├── Dockerfile
├── docker-compose.yml
└── run.py

## Autor

Desenvolvido por Isabela Né — IFTO/UAB Campus Araguatins  
Disciplina: Desenvolvimento Web — 2026