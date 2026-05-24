# Plano de Testes - PokéShop

Este documento descreve a estratégia de testes automatizados para o sistema PokéShop, seguindo a metodologia **TDD First** (Test-Driven Development) para garantir a integridade das funcionalidades críticas e evitar regressões.

## 1. Objetivo
Garantir que todas as funcionalidades do sistema (autenticação, catálogo, carrinho, checkout, pedidos, suporte e admin) operem conforme as especificações técnicas, com foco em cenários de sucesso e, principalmente, tratamento de erros e casos críticos.

## 2. Escopo
Os testes cobrirão os seguintes módulos:
- **Autenticação:** Registro, login, logout, bloqueio de conta e rate limit.
- **Catálogo:** Listagem, busca, filtragem e detalhes de produtos.
- **Carrinho:** Adição (com validação de estoque), remoção, limpeza e cálculo de frete (ViaCEP).
- **Checkout:** Validação de carrinho, endereço, pagamento e baixa de estoque.
- **Pedidos:** Histórico e detalhes (com validação de permissão).
- **Suporte:** Abertura de chamados e interação (tickets).
- **Admin:** Dashboard, CRUD de produtos, gestão de atendentes e alteração de status de pedidos.

## 3. Ferramentas e Estrutura
- **Framework:** `pytest`
- **Extensões:** `pytest-flask` (integração com Flask), `pytest-cov` (cobertura), `requests-mock` (simulação da API ViaCEP).
- **Estrutura de Pastas:**
  ```
  tests/
  ├── conftest.py          # Fixtures globais (app, client, db_session)
  ├── test_auth.py         # Testes de autenticação
  ├── test_catalog.py      # Testes do catálogo
  ├── test_cart.py         # Testes do carrinho
  ├── test_checkout.py     # Testes de finalização de compra
  ├── test_orders.py       # Testes de histórico de pedidos
  ├── test_support.py      # Testes de suporte/tickets
  └── test_admin.py        # Testes do painel administrativo
  ```

## 4. Casos de Teste (Cenários Críticos)

### 4.1. Autenticação (`test_auth.py`)
| ID | Caso de Teste | Descrição | Critério de Aceite |
|----|---------------|-----------|--------------------|
| AUT-01 | Login Inválido | Tentar login com e-mail inexistente ou senha errada. | Exibir mensagem de erro e não autenticar. |
| AUT-02 | Bloqueio de Conta | Errar a senha 5 vezes consecutivas. | O campo `failed_login_attempts` deve chegar a 5 e a conta ser bloqueada. |
| AUT-03 | Registro Duplicado| Tentar registrar um e-mail já existente. | Impedir cadastro e exibir aviso. |

### 4.2. Catálogo (`test_catalog.py`)
| ID | Caso de Teste | Descrição | Critério de Aceite |
|----|---------------|-----------|--------------------|
| CAT-01 | Busca de Produto | Buscar por um termo que existe e um que não existe. | Retornar os produtos corretos ou lista vazia. |
| CAT-02 | Filtro Categoria | Filtrar por uma categoria específica. | Mostrar apenas produtos daquela categoria. |

### 4.3. Carrinho (`test_cart.py`)
| ID | Caso de Teste | Descrição | Critério de Aceite |
|----|---------------|-----------|--------------------|
| CAR-01 | Estoque Esgotado | Tentar adicionar produto com quantidade > estoque. | Impedir adição e exibir erro "Estoque insuficiente". |
| CAR-02 | MOCK ViaCEP | Calcular frete para um CEP válido (usando mock). | Retornar valores de frete baseados na lógica regional. |

### 4.4. Checkout (`test_checkout.py`)
| ID | Caso de Teste | Descrição | Critério de Aceite |
|----|---------------|-----------|--------------------|
| CHK-01 | Carrinho Vazio | Tentar acessar o checkout sem itens. | Redirecionar para o carrinho com aviso. |
| CHK-02 | Baixa de Estoque | Finalizar pedido com sucesso. | O estoque do produto no banco deve ser decrementado corretamente. |

### 4.5. Admin (`test_admin.py`)
| ID | Caso de Teste | Descrição | Critério de Aceite |
|----|---------------|-----------|--------------------|
| ADM-01 | Acesso Negado | Usuário 'Cliente' tenta acessar `/admin`. | Redirecionar para o catálogo com erro 403 ou aviso de restrição. |
| ADM-02 | CRUD Produto | Administrador cria/edita um produto. | Alterações devem ser persistidas no banco. |

## 5. Instruções para Execução

### Instalação das dependências
```bash
pip install -r requirements.txt
```

### Executar todos os testes
```bash
pytest
```

### Executar com relatório de cobertura
```bash
pytest --cov=app tests/
```

### Executar um arquivo específico
```bash
pytest tests/test_auth.py
```

## 6. Resultados e Cobertura
- **Status:** 18 testes passando (100% dos cenários críticos).
- **Cobertura:** ~74% total, com mais de 80% em módulos principais como Catálogo, Suporte e Ordens.
- **Destaque:** Implementado bypass de bcrypt em testes para execução ultra-rápida (4s para toda a suíte).

## 7. Critérios de Aceite Gerais
- 100% de passagem nos testes de cenários críticos.
- Cobertura de código mínima de 80% nos blueprints principais.
- Mocks utilizados para todas as chamadas de rede externas (ViaCEP).
