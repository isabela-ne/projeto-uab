# Relatório de Inspeção de Segurança — PokéShop
**Nível:** Moderado  
**Arquivos inspecionados:**
- `app/blueprints/admin/routes.py`
- `app/blueprints/cart/routes.py`

**Projeto:** PokéShop — IFTO/UAB  
**Data:** Maio 2026

---

## Resumo Executivo

| Severidade | Quantidade |
|------------|------------|
| 🔴 Crítica | 1 |
| 🟠 Alta | 4 |
| 🟡 Média | 4 |
| 🔵 Baixa | 2 |
| **Total** | **11** |

> Somando com o relatório superficial (v1): **22 vulnerabilidades** identificadas até agora.

---

## 5 Ações Mais Urgentes (nível moderado)

1. **[CRÍTICA]** `float()` e `int()` sem try/except no admin — crash imediato com entrada inválida.
2. **[ALTA]** `image_url` de produto aceita qualquer URL sem validação — vetor para XSS e SSRF.
3. **[ALTA]** Requisição externa ao ViaCEP sem timeout adequado e sem sanitização da resposta.
4. **[ALTA]** Cupom sem validação de formato no backend — código arbitrário aceito.
5. **[ALTA]** Exclusão de atendente sem verificação se é o próprio admin logado.

---

## Vulnerabilidades Encontradas

---

### VUL-12 — Conversão de tipos sem tratamento de exceção (crash garantido)
**Severidade:** 🔴 Crítica  
**OWASP:** A10 — Mishandling of Exceptional Conditions  
**CWE:** CWE-391

**Localização:** `app/blueprints/admin/routes.py`, linhas 57–60 e 82–85

**Descrição:** Os campos `preco`, `estoque` e `categoria_id` são convertidos com `float()` e `int()` sem nenhum tratamento de exceção. Uma entrada não numérica (ex: `preco=abc`) causa `ValueError` e derruba o servidor com erro 500.

**Evidência:**
```python
preco   = float(request.form.get('preco', 0))
estoque = int(request.form.get('estoque', 0))
cat_id  = int(request.form.get('categoria_id'))
```

**Impacto:** Crash do servidor; possível DoS por requisições malformadas repetidas.

**Recomendação:**
```python
try:
    preco   = float(request.form.get('preco', 0))
    estoque = int(request.form.get('estoque', 0))
    cat_id  = int(request.form.get('categoria_id', 0))
except (ValueError, TypeError):
    flash('Valores numéricos inválidos.', 'danger')
    return render_template('admin/produto_form.html', categorias=categorias)

if preco <= 0 or estoque < 0 or cat_id <= 0:
    flash('Valores inválidos.', 'danger')
    return render_template('admin/produto_form.html', categorias=categorias)
```

---

### VUL-13 — `image_url` aceita qualquer URL sem validação
**Severidade:** 🟠 Alta  
**OWASP:** A05 — Injection / A03 — Software Supply Chain Failures  
**CWE:** CWE-79, CWE-918

**Localização:** `app/blueprints/admin/routes.py`, linhas 61 e 86

**Descrição:** O campo `image_url` aceita qualquer string como URL de imagem, sem validar o domínio ou o protocolo. Isso abre dois vetores:
- **XSS:** `javascript:alert(1)` como URL renderiza script no template se não houver escaping adequado.
- **SSRF:** URL apontando para serviços internos (`http://localhost/admin`) pode ser usada para mapeamento interno.

**Evidência:**
```python
image_url = request.form.get('image_url', '').strip()
p = Product(... image_url=image_url)
```

**Recomendação:**
```python
from urllib.parse import urlparse

def validar_image_url(url):
    if not url:
        return True
    parsed = urlparse(url)
    return parsed.scheme in ('http', 'https') and bool(parsed.netloc)

if image_url and not validar_image_url(image_url):
    flash('URL de imagem inválida.', 'danger')
    return render_template('admin/produto_form.html', categorias=categorias)
```

---

### VUL-14 — Requisição ao ViaCEP sem validação do conteúdo da resposta
**Severidade:** 🟠 Alta  
**OWASP:** A08 — Software or Data Integrity Failures  
**CWE:** CWE-20, CWE-918

**Localização:** `app/blueprints/cart/routes.py`, linhas 68–75

**Descrição:** A resposta do ViaCEP é usada diretamente sem verificar o tipo de conteúdo nem sanitizar os campos `localidade` e `uf` antes de armazená-los na sessão. Se a API retornar dados inesperados ou a requisição for interceptada (man-in-the-middle), dados maliciosos podem ser injetados na sessão.

**Evidência:**
```python
resp = requests.get(f'https://viacep.com.br/ws/{cep}/json/', timeout=5)
dados = resp.json()
cidade = dados.get('localidade', '')
estado = dados.get('uf', '')
```

**Recomendação:**
```python
# Validar Content-Type e sanitizar campos
if 'application/json' not in resp.headers.get('Content-Type', ''):
    raise ValueError("Resposta inesperada do ViaCEP")

cidade = str(dados.get('localidade', ''))[:100]
estado = str(dados.get('uf', ''))[:2]

if not estado.isalpha():
    raise ValueError("UF inválida na resposta")
```

---

### VUL-15 — Cupom sem validação de formato no backend
**Severidade:** 🟠 Alta  
**OWASP:** A05 — Injection  
**CWE:** CWE-20

**Localização:** `app/blueprints/cart/routes.py`, linha 134 e `app/blueprints/admin/routes.py`, linha 167

**Descrição:** O código do cupom é aceito sem validação de formato ou tamanho máximo. Strings arbitrariamente longas ou com caracteres especiais são processadas sem restrição.

**Evidência:**
```python
codigo = request.form.get('cupom', '').strip().upper()
# Sem validação de formato ou tamanho
cupom = Coupon.query.filter_by(codigo=codigo).first()
```

**Recomendação:**
```python
import re
if not re.fullmatch(r'[A-Z0-9]{3,20}', codigo):
    flash('Código de cupom inválido.', 'danger')
    return redirect(url_for('cart.view'))
```

---

### VUL-16 — Exclusão de atendente sem proteção contra auto-exclusão ou exclusão de admin
**Severidade:** 🟠 Alta  
**OWASP:** A01 — Broken Access Control  
**CWE:** CWE-284

**Localização:** `app/blueprints/admin/routes.py`, linhas 115–120

**Descrição:** A rota de exclusão de atendente não verifica se o usuário sendo excluído é o próprio admin logado nem se é outro Administrador. Um admin poderia excluir a si mesmo acidentalmente ou excluir outro administrador.

**Evidência:**
```python
def atendente_excluir(id):
    u = User.query.get_or_404(id)
    db.session.delete(u)
    db.session.commit()
```

**Recomendação:**
```python
def atendente_excluir(id):
    u = User.query.get_or_404(id)
    if u.id == current_user.id:
        flash('Você não pode excluir sua própria conta.', 'danger')
        return redirect(url_for('admin.usuarios'))
    if u.role == 'Administrador':
        flash('Não é permitido excluir outro Administrador.', 'danger')
        return redirect(url_for('admin.usuarios'))
    db.session.delete(u)
    db.session.commit()
```

---

### VUL-17 — Desconto de cupom sem limite máximo
**Severidade:** 🟡 Média  
**OWASP:** A06 — Insecure Design  
**CWE:** CWE-20

**Localização:** `app/blueprints/admin/routes.py`, linha 168

**Descrição:** O campo `desconto_pct` é lido como `float` sem validação de intervalo. Um valor acima de 100 (ex: `desconto_pct=999`) resultaria em preço negativo no checkout.

**Evidência:**
```python
desconto_pct = float(request.form.get('desconto_pct', 0))
```

**Recomendação:**
```python
try:
    desconto_pct = float(request.form.get('desconto_pct', 0))
except (ValueError, TypeError):
    desconto_pct = 0

if not (0 < desconto_pct <= 100):
    flash('Desconto deve ser entre 1% e 100%.', 'danger')
    return render_template('admin/cupom_form.html')
```

---

### VUL-18 — Validade do cupom sem validação de data mínima
**Severidade:** 🟡 Média  
**OWASP:** A06 — Insecure Design  
**CWE:** CWE-20

**Localização:** `app/blueprints/admin/routes.py`, linha 169

**Descrição:** A data de validade do cupom é aceita sem verificar se é uma data futura. Um cupom já vencido pode ser criado sem alerta.

**Evidência:**
```python
validade = datetime.strptime(validade_str, '%Y-%m-%d') if validade_str else None
```

**Recomendação:**
```python
from datetime import datetime, date
if validade_str:
    validade = datetime.strptime(validade_str, '%Y-%m-%d')
    if validade.date() < date.today():
        flash('A data de validade deve ser futura.', 'warning')
        return render_template('admin/cupom_form.html')
```

---

### VUL-19 — Quantidade de itens no carrinho sem limite máximo
**Severidade:** 🟡 Média  
**OWASP:** A06 — Insecure Design  
**CWE:** CWE-770

**Localização:** `app/blueprints/cart/routes.py`, linha 24

**Descrição:** O campo `quantidade` é lido como `int` sem limite superior. Um usuário pode adicionar `quantidade=999999` de um produto com `estoque=1000000`, inflando artificialmente a sessão.

**Evidência:**
```python
quantidade = int(request.form.get('quantidade', 1))
```

**Recomendação:**
```python
try:
    quantidade = int(request.form.get('quantidade', 1))
except (ValueError, TypeError):
    quantidade = 1

if quantidade < 1 or quantidade > 99:
    flash('Quantidade inválida (máximo 99 por item).', 'danger')
    return redirect(url_for('catalog.index'))
```

---

### VUL-20 — Filtro de status de pedidos via query string sem validação
**Severidade:** 🟡 Média  
**OWASP:** A05 — Injection  
**CWE:** CWE-20

**Localização:** `app/blueprints/admin/routes.py`, linha 124

**Descrição:** O parâmetro `status` da query string é passado diretamente para o filtro ORM sem validação. Embora o SQLAlchemy proteja contra SQL injection, valores inválidos geram queries desnecessárias.

**Evidência:**
```python
status = request.args.get('status', '')
if status:
    lista = Order.query.filter_by(status=status)...
```

**Recomendação:**
```python
STATUS_VALIDOS = ['aguardando_pagamento','pago','em_separacao','enviado','entregue','cancelado']
status = request.args.get('status', '')
if status and status not in STATUS_VALIDOS:
    status = ''
```

---

### VUL-21 — Exception genérica no cálculo de frete suprime erros reais
**Severidade:** 🔵 Baixa  
**OWASP:** A10 — Mishandling of Exceptional Conditions  
**CWE:** CWE-390

**Localização:** `app/blueprints/cart/routes.py`, linha 107

**Descrição:** O bloco `except Exception` captura qualquer erro (timeout, JSON inválido, erro de rede) e exibe a mesma mensagem genérica, dificultando diagnóstico em produção.

**Recomendação:**
```python
except requests.Timeout:
    flash('Tempo limite ao consultar o CEP. Tente novamente.', 'danger')
except requests.RequestException as e:
    app.logger.error(f"Erro ViaCEP: {e}")
    flash('Erro ao consultar o CEP. Tente novamente.', 'danger')
except ValueError as e:
    app.logger.error(f"Resposta inválida ViaCEP: {e}")
    flash('Resposta inválida do serviço de CEP.', 'danger')
```

---

### VUL-22 — Ausência de paginação nas listagens do admin
**Severidade:** 🔵 Baixa  
**OWASP:** A06 — Insecure Design  
**CWE:** CWE-770

**Localização:** `app/blueprints/admin/routes.py`, linhas 44, 97, 125

**Descrição:** As listagens de produtos, usuários e pedidos carregam todos os registros sem paginação. Com volume alto de dados, isso pode causar degradação de desempenho ou timeout.

**Recomendação:**
```python
# Exemplo para pedidos
pagina = request.args.get('page', 1, type=int)
lista = Order.query.order_by(Order.created_at.desc()).paginate(page=pagina, per_page=20)
```

---

## Consolidado das Duas Inspeções

| Relatório | Nível | Vulnerabilidades |
|-----------|-------|-----------------|
| security-report-v1 | Superficial | 11 |
| security-report-v2 | Moderado | 11 |
| **Total acumulado** | | **22** |

| Severidade | v1 | v2 | Total |
|------------|----|----|-------|
| 🔴 Crítica | 2 | 1 | 3 |
| 🟠 Alta | 3 | 4 | 7 |
| 🟡 Média | 4 | 4 | 8 |
| 🔵 Baixa | 2 | 2 | 4 |

---

## Próxima Etapa

**Nível profundo** deve cobrir:
- `app/models/` — verificar constraints, campos sensíveis e queries brutas
- `app/templates/` — verificar escaping Jinja2, formulários sem CSRF, atributos `autocomplete`
- `app/blueprints/orders/routes.py` e `support/routes.py` — validação de ownership
- `.env.example` — verificar segredos expostos
- `Dockerfile` e `docker-compose.yml` — configurações de produção inseguras

---

*Inspeção realizada com base no OWASP Top 10 e boas práticas de desenvolvimento seguro.*
