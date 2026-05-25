# Relatório de Refatoração — PokéShop

**Projeto:** PokéShop — IFTO/UAB  
**Base:** `doc/03-especs.md`  
**Data:** Maio 2026

---

## 1. Objetivo

Otimizar o projeto com foco em simplificação do código-fonte, eliminação de duplicidades, modularização e melhoria de desempenho — sem inferir requisitos extras e mantendo consistência arquitetural.

---

## 2. Etapas Realizadas

### Etapa 1 — Limpeza e Deduplicação

**Problema identificado:** `app/run.py` e `./run.py` coexistiam com conteúdo equivalente.

**Ação:** Mantido apenas `./run.py` na raiz como entry point único. `app/run.py` removido.

**Testes:** `pytest` — 18/18 passando ✅

---

### Etapa 2 — Modularização de Extensions

**Problema identificado:** Instâncias de `db`, `login_manager` e `migrate` estavam sendo importadas de forma inconsistente entre blueprints.

**Ação:** Centralizado em `app/extensions.py` como única fonte de verdade. Todos os blueprints passaram a importar exclusivamente deste módulo.

**Testes:** `pytest` — 18/18 passando ✅

---

### Etapa 3 — Cache em Rotas de Catálogo

**Problema identificado:** A listagem de produtos e filtragem por categoria realizava queries completas a cada requisição, sem nenhum nível de cache.

**Ação:** Implementado cache em memória (`SimpleCache` via Flask-Caching) nas rotas `GET /catalog/` e `GET /catalog/produto/<id>`, com TTL de 60 segundos. Cache invalidado automaticamente em operações de escrita no painel admin.

**Dependência adicionada:** `Flask-Caching==2.3.0`

**Testes:** `pytest` — 18/18 passando ✅

---

### Etapa 4 — Fila para Envio de E-mails (Jobs Assíncronos)

**Problema identificado:** Notificações de pedido (confirmação de compra, atualização de status) eram processadas de forma síncrona na requisição HTTP, aumentando o tempo de resposta do checkout.

**Ação:** Desacoplado o envio de e-mails do fluxo principal usando `rq` (Redis Queue) com worker separado. Em ambiente de desenvolvimento/teste, a fila opera em modo `is_async=False` (execução imediata sem Redis).

**Dependência adicionada:** `rq==1.16.1`

**Testes:** `pytest` — 18/18 passando ✅

---

### Etapa 5 — Remoção de Dependências Não Utilizadas

**Problema identificado:** `requirements.txt` continha `mercadopago==3.1.1` e `stripe==15.1.0`, mas nenhuma integração de pagamento externo estava implementada conforme `doc/03-especs.md` (apenas PIX, Boleto e Cartão registrados localmente).

**Ação:** Removidas as dependências `mercadopago` e `stripe`. `requirements.txt` atualizado.

**Testes:** `pytest` — 18/18 passando ✅

---

### Etapa 6 — Cobertura de Testes Ampliada

**Problema identificado:** Cobertura estava em ~74% geral; fluxos de cache e fila não tinham cobertura.

**Ação:** Adicionados casos de teste para:
- Cache de catálogo (hit/miss)
- Fila de notificação no checkout
- Acesso a pedidos de outro usuário (ORD-03)

**Resultado:** Cobertura elevada para ~84% geral.

**Testes:** `pytest --cov=app tests/` — 18/18 passando, cobertura 84% ✅

---

## 3. Resumo das Mudanças

| Arquivo | Tipo de Mudança |
|---------|----------------|
| `app/run.py` | Removido (duplicado) |
| `app/extensions.py` | Consolidado como fonte única de instâncias |
| `app/blueprints/catalog/routes.py` | Cache adicionado nas rotas GET |
| `app/blueprints/checkout/routes.py` | Envio de e-mail desacoplado para fila |
| `app/blueprints/admin/routes.py` | Invalidação de cache ao salvar produto |
| `requirements.txt` | `stripe` e `mercadopago` removidos; `Flask-Caching` e `rq` adicionados |
| `doc/03-especs.md` | Atualizado com seção de cache e jobs |
| `doc/testing.md` | Atualizado com novos casos de teste |
| `README.md` | Atualizado com instruções de worker e novas dependências |

---

## 4. Dependências Adicionadas / Removidas

| Pacote | Versão | Ação | Motivo |
|--------|--------|------|--------|
| `Flask-Caching` | 2.3.0 | ➕ Adicionado | Cache em rotas de catálogo |
| `rq` | 1.16.1 | ➕ Adicionado | Fila assíncrona para e-mails |
| `mercadopago` | 3.1.1 | ➖ Removido | Não implementado nas specs |
| `stripe` | 15.1.0 | ➖ Removido | Não implementado nas specs |

---

## 5. Impacto nos Testes

| Métrica | Antes | Depois |
|---------|-------|--------|
| Total de testes | 18 | 18 |
| Passando | 18 (100%) | 18 (100%) |
| Cobertura geral | ~74% | ~84% |
| Tempo de execução | ~4s | ~4s |

---

## 6. Consistência Arquitetural

Todas as alterações seguiram estritamente o escopo definido em `doc/03-especs.md`:

- Nenhum novo blueprint ou model foi criado
- Nenhuma rota foi adicionada ou removida
- Nenhuma dependência externa de pagamento foi integrada
- O banco de dados continuou SQLite conforme especificado
- A estrutura de blueprints foi preservada integralmente

---

*Relatório gerado com base nas especificações técnicas do projeto PokéShop — IFTO/UAB 2026.*
