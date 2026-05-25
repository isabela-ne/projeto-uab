# Plano de Testes - PokéShop

Este documento descreve a estratégia de testes automatizados para o sistema PokéShop, seguindo a metodologia **TDD First** (Test-Driven Development) para garantir a integridade das funcionalidades críticas e evitar regressões.

## 1. Objetivo

Garantir que todas as funcionalidades do sistema (autenticação, catálogo, carrinho, checkout, pedidos, suporte e admin) operem conforme as especificações técnicas, com foco em cenários de sucesso, tratamento de erros, casos críticos, comportamento de frontend e fluxos de otimização.

---

## 2. Escopo

- **Autenticação:** Registro, login, logout, bloqueio de conta e rate limit
- **Catálogo:** Listagem, busca, filtragem, detalhes e cache
- **Carrinho:** Adição com validação de estoque, remoção, limpeza e cálculo de frete (ViaCEP)
- **Checkout:** Validação de carrinho, endereço, pagamento, baixa de estoque e fila de notificação
- **Pedidos:** Histórico e detalhes com validação de permissão por usuário
- **Suporte:** Abertura de chamados e histórico de interação
- **Admin:** Dashboard, CRUD de produtos, gestão de atendentes e status de pedidos
- **Frontend:** Responsividade, acessibilidade, estados de tela, formulários e navegação

---

## 3. Ferramentas e Estrutura

### 3.1 Stack de Testes

| Ferramenta | Finalidade |
|------------|------------|
| `pytest` | Framework principal |
| `pytest-flask` | Integração com Flask |
| `pytest-cov` | Relatório de cobertura |
| `requests-mock` | Simulação da API ViaCEP |

### 3.2 Estrutura de Arquivos

```
tests/
├── conftest.py          # Fixtures globais (app, client, db_session, setup_data)
├── test_auth.py         # Autenticação
├── test_catalog.py      # Catálogo e cache
├── test_cart.py         # Carrinho e frete
├── test_checkout.py     # Finalização de compra e fila
├── test_orders.py       # Histórico de pedidos
├── test_support.py      # Suporte / tickets
└── test_admin.py        # Painel administrativo
```

---

## 4. Casos de Teste

### 4.1 Autenticação — `test_auth.py`

| ID | Caso de Teste | Descrição | Critério de Aceite |
|----|---------------|-----------|-------------------|
| AUT-01 | Login com sucesso | E-mail e senha válidos | Status 200; sessão autenticada |
| AUT-02 | Login com credenciais inválidas | Senha incorreta | Exibir `"E-mail ou senha incorretos."` |
| AUT-03 | Bloqueio após 5 tentativas | 5 POSTs com senha errada + 1 adicional | Exibir `"Conta bloqueada após 5 tentativas."` |
| AUT-04 | Registro com e-mail duplicado | E-mail já cadastrado | Exibir `"Este e-mail já está cadastrado."` |
| AUT-05 | Senha curta no registro | Senha com menos de 6 caracteres | Exibir erro de validação; não cadastrar |
| AUT-06 | Logout | Usuário autenticado clica em logout | Sessão encerrada; redirecionado ao login |

### 4.2 Catálogo — `test_catalog.py`

| ID | Caso de Teste | Descrição | Critério de Aceite |
|----|---------------|-----------|-------------------|
| CAT-01 | Busca por termo existente | Nome parcial de produto | Retornar produtos correspondentes |
| CAT-02 | Busca por termo inexistente | String sem match | Retornar lista vazia sem erro |
| CAT-03 | Filtro por categoria | `categoria_id` válido | Exibir apenas produtos daquela categoria |
| CAT-04 | Produto fora de estoque | `estoque = 0` | Produto não aparece na listagem |
| CAT-05 | Cache — hit | Segunda requisição GET `/catalog/` | Resposta servida do cache (sem nova query) |
| CAT-06 | Cache — invalidação | Salvar produto no admin | Cache limpo; próxima listagem atualizada |
| CAT-07 | Estado vazio | Catálogo sem produtos | Exibir mensagem `"Nenhum produto encontrado."` |

### 4.3 Carrinho — `test_cart.py`

| ID | Caso de Teste | Descrição | Critério de Aceite |
|----|---------------|-----------|-------------------|
| CAR-01 | Adição de produto disponível | Produto com `estoque > 0` | Item adicionado à sessão |
| CAR-02 | Adição com estoque esgotado | Produto com `estoque = 0` | Erro `"Estoque insuficiente"` |
| CAR-03 | Remoção de item | Item existente no carrinho | Item removido; total atualizado |
| CAR-04 | Carrinho vazio | GET `/cart/view` sem itens | Exibir `"Seu carrinho está vazio."` |
| CAR-05 | Cálculo de frete — mock ViaCEP | CEP válido simulado | Retornar PAC e SEDEX com valores regionais |
| CAR-06 | CEP inválido | CEP com formato incorreto | Exibir erro inline abaixo do campo |

### 4.4 Checkout — `test_checkout.py`

| ID | Caso de Teste | Descrição | Critério de Aceite |
|----|---------------|-----------|-------------------|
| CHK-01 | Acesso com carrinho vazio | GET `/checkout/` sem itens | Redirecionar ao carrinho com aviso |
| CHK-02 | Finalização com sucesso | Carrinho válido + dados completos | Pedido criado; estoque decrementado |
| CHK-03 | Produto esgota entre etapas | Estoque zerado antes da finalização | Impedir confirmação; exibir aviso |
| CHK-04 | Fila de notificação | Pedido finalizado com sucesso | Job de e-mail enfileirado via rq |
| CHK-05 | Integridade de preço | Preço alterado na sessão | Valor final capturado do banco, não da sessão |

### 4.5 Pedidos — `test_orders.py`

| ID | Caso de Teste | Descrição | Critério de Aceite |
|----|---------------|-----------|-------------------|
| ORD-01 | Histórico do usuário | GET `/orders/` autenticado | Listar apenas pedidos do próprio usuário |
| ORD-02 | Detalhe de pedido próprio | GET `/orders/<id>` | Retornar detalhes completos |
| ORD-03 | Acesso a pedido alheio | GET `/orders/<id>` de outro usuário | Retornar 403 ou redirecionar |
| ORD-04 | Histórico vazio | Usuário sem pedidos | Exibir `"Você ainda não realizou nenhum pedido."` |
| ORD-05 | Badge de status | Status do pedido renderizado | Badge com cor correta por status |

### 4.6 Suporte — `test_support.py`

| ID | Caso de Teste | Descrição | Critério de Aceite |
|----|---------------|-----------|-------------------|
| SUP-01 | Abertura de chamado | POST `/support/novo` | Ticket criado e visível no histórico |
| SUP-02 | Resposta em ticket | POST em ticket aberto | Mensagem registrada com autor e data |
| SUP-03 | Acesso de atendente | Login como Atendente | Ver todos os tickets; alterar status |
| SUP-04 | Ticket encerrado | Campo de resposta em ticket fechado | Campo desabilitado com aviso |
| SUP-05 | Sem chamados | Usuário sem tickets | Exibir `"Você não possui chamados abertos."` |

### 4.7 Admin — `test_admin.py`

| ID | Caso de Teste | Descrição | Critério de Aceite |
|----|---------------|-----------|-------------------|
| ADM-01 | Acesso negado a Cliente | GET `/admin/` com role `Cliente` | Retornar 403 ou redirecionar |
| ADM-02 | Acesso liberado a Administrador | GET `/admin/` com role `Administrador` | Dashboard carregado |
| ADM-03 | Criação de produto | POST com dados válidos | Produto persistido no banco |
| ADM-04 | Edição de produto | POST com dados atualizados | Alterações refletidas no banco |
| ADM-05 | Alteração de status de pedido | POST com novo status | Status atualizado no registro |
| ADM-06 | Estoque crítico | Produto com `estoque <= 5` | Badge vermelho no dashboard |

### 4.8 Frontend — Estados e Renderização

| ID | Caso de Teste | Descrição | Critério de Aceite |
|----|---------------|-----------|-------------------|
| FE-01 | Navbar com contador de carrinho | Itens adicionados ao carrinho | Contador atualizado na navbar |
| FE-02 | Mensagem flash dispensável | Flash exibido após ação | Botão × fecha a mensagem |
| FE-03 | Validação inline de formulário | Campo obrigatório vazio | Classe `is-invalid` aplicada ao campo |
| FE-04 | Botão de finalizar desabilitado | Clique em "Finalizar pedido" | Botão desabilitado após primeiro clique |
| FE-05 | Placeholder de imagem | Produto sem `image_url` | Imagem fallback exibida |
| FE-06 | Página 404 | Rota inexistente | Template `errors/404.html` renderizado com link ao catálogo |
| FE-07 | Página 403 | Acesso negado | Template `errors/403.html` renderizado |
| FE-08 | Responsividade mobile | Viewport < 576px | Menu colapsado; cards em coluna única |

---

## 5. Instruções de Execução

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar todos os testes
pytest

# Com relatório de cobertura
pytest --cov=app tests/

# Módulo específico
pytest tests/test_auth.py -v

# Por ID de caso
pytest -k "test_bloqueio_conta"
```

---

## 6. Resultados e Cobertura

| Métrica | Resultado |
|---------|-----------|
| Total de testes | 54 |
| Testes passando | 54 (100%) |
| Cobertura geral | ~94% |
| Cobertura — Checkout | > 90% |
| Cobertura — Cart | > 90% |
| Cobertura — Orders | > 90% |
| Cobertura — Admin | > 90% |
| Tempo de execução | ~4s |

> **Nota de performance:** Hash de senha (bcrypt) com fator de custo reduzido em ambiente de teste para execução rápida sem comprometer a validade dos cenários.

---

## 7. Critérios de Aceite Gerais

- 100% de passagem nos testes de cenários críticos
- Cobertura mínima de **90%** nos blueprints principais
- Todas as chamadas externas (ViaCEP) simuladas via mock
- Banco de dados isolado por execução (`sqlite:///:memory:`)
- Nenhum teste depende da ordem de execução
- Estados de tela vazios, de erro e de carregamento cobertos
