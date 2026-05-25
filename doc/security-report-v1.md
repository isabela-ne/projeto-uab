# Relatório de Inspeção de Segurança — PokéShop
**Nível:** Superficial  
**Arquivos inspecionados:**
- `app/blueprints/auth/routes.py`
- `app/blueprints/checkout/routes.py`
- `app/__init__.py`
- `app/extensions.py`
- `.env.example`

**Projeto:** PokéShop — IFTO/UAB  
**Data:** Maio 2026

---

## Resumo Executivo

| Severidade | Quantidade |
|------------|------------|
| 🔴 Crítica | 2 |
| 🟠 Alta | 3 |
| 🟡 Média | 4 |
| 🔵 Baixa | 2 |
| **Total** | **11** |

---

## 5 Ações Mais Urgentes

1. **[CRÍTICA]** Fixar `SECRET_KEY` com fallback `'dev'` em produção — qualquer sessão pode ser forjada.
2. **[CRÍTICA]** Validar e sanitizar o parâmetro `next` no login para evitar Open Redirect.
3. **[ALTA]** Rate limiting em memória se perde ao reiniciar o servidor — substituir por solução persistente.
4. **[ALTA]** Ausência de cabeçalhos de segurança HTTP (CSP, X-Frame-Options, HSTS).
5. **[ALTA]** CEP e campos de endereço sem validação de formato no backend.

---

## Vulnerabilidades Encontradas

---

### VUL-01 — Secret Key com valor padrão inseguro
**Severidade:** 🔴 Crítica  
**OWASP:** A02 — Security Misconfiguration  
**CWE:** CWE-521

**Localização:** `app/__init__.py`, linha 9

**Descrição:** A `SECRET_KEY` usa `'dev'` como fallback caso a variável de ambiente não esteja definida. Em produção, isso permite que um atacante forge cookies de sessão e tokens CSRF.

**Evidência:**
```python
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
```

**Impacto:** Comprometimento total de sessões de usuários e tokens CSRF.

**Recomendação:**
```python
secret = os.getenv('SECRET_KEY')
if not secret:
    raise RuntimeError("SECRET_KEY não definida. Configure a variável de ambiente.")
app.config['SECRET_KEY'] = secret
```

---

### VUL-02 — Open Redirect via parâmetro `next`
**Severidade:** 🔴 Crítica  
**OWASP:** A01 — Broken Access Control  
**CWE:** CWE-601

**Localização:** `app/blueprints/auth/routes.py`, linha 41

**Descrição:** O parâmetro `next` recebido via query string é usado diretamente no redirecionamento sem validação. Um atacante pode criar um link como `/auth/login?next=https://site-malicioso.com` para redirecionar a vítima após o login.

**Evidência:**
```python
next_page = request.args.get('next')
return redirect(next_page or url_for('catalog.index'))
```

**Impacto:** Phishing, roubo de credenciais pós-autenticação.

**Recomendação:**
```python
from urllib.parse import urlparse, urljoin

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

next_page = request.args.get('next')
if next_page and not is_safe_url(next_page):
    next_page = None
return redirect(next_page or url_for('catalog.index'))
```

---

### VUL-03 — Rate limiting em memória sem persistência
**Severidade:** 🟠 Alta  
**OWASP:** A07 — Authentication Failures  
**CWE:** CWE-307

**Localização:** `app/blueprints/auth/routes.py`, linhas 13–19

**Descrição:** O dicionário `_tentativas` é armazenado em memória do processo. Ao reiniciar o servidor (deploy, crash), o histórico de tentativas é perdido, zerando o rate limit e permitindo ataques de força bruta.

**Evidência:**
```python
_tentativas = defaultdict(list)

def checar_rate_limit(ip):
    agora = time.time()
    _tentativas[ip] = [t for t in _tentativas[ip] if agora - t < 300]
    if len(_tentativas[ip]) >= 10:
        return False
    _tentativas[ip].append(agora)
    return True
```

**Impacto:** Bypass de proteção contra força bruta após reinicialização.

**Recomendação:** Usar Flask-Limiter com backend Redis ou SQLite para persistência:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(get_remote_address, app=app, default_limits=["10 per 5 minutes"])

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per 5 minutes")
def login():
    ...
```

---

### VUL-04 — Ausência de cabeçalhos de segurança HTTP
**Severidade:** 🟠 Alta  
**OWASP:** A02 — Security Misconfiguration  
**CWE:** CWE-16

**Localização:** `app/__init__.py` — nenhum middleware de cabeçalhos configurado

**Descrição:** A aplicação não define cabeçalhos HTTP de segurança essenciais, deixando o navegador sem proteções contra XSS, clickjacking e sniffing de conteúdo.

**Cabeçalhos ausentes:**
- `Content-Security-Policy`
- `X-Frame-Options`
- `X-Content-Type-Options`
- `Strict-Transport-Security`
- `Referrer-Policy`

**Impacto:** Exposição a ataques XSS, clickjacking e MIME sniffing.

**Recomendação:** Instalar e configurar Flask-Talisman:
```python
from flask_talisman import Talisman

Talisman(app, content_security_policy={
    'default-src': "'self'",
    'script-src': ["'self'", 'cdn.jsdelivr.net'],
    'style-src': ["'self'", 'cdn.jsdelivr.net'],
})
```

---

### VUL-05 — Campos de endereço e CEP sem validação de formato
**Severidade:** 🟠 Alta  
**OWASP:** A05 — Injection  
**CWE:** CWE-20

**Localização:** `app/blueprints/checkout/routes.py`, linhas 28–45

**Descrição:** Os campos `cep`, `estado`, `rua`, `cidade` e demais campos de endereço são verificados apenas quanto à presença (`not all([...])`), sem validação de formato. Isso permite entradas malformadas ou potencialmente maliciosas.

**Evidência:**
```python
if not all([rua, numero, bairro, cidade, estado, cep, pagamento]):
    flash('Preencha todos os campos.', 'danger')
```

**Impacto:** Dados corrompidos no banco; possível injeção em integrações externas.

**Recomendação:**
```python
import re

if not re.fullmatch(r'\d{5}-?\d{3}', cep):
    flash('CEP inválido.', 'danger')
    return redirect(url_for('checkout.index'))

if not re.fullmatch(r'[A-Za-z]{2}', estado):
    flash('Estado inválido.', 'danger')
    return redirect(url_for('checkout.index'))
```

---

### VUL-06 — Ausência de validação de e-mail no registro
**Severidade:** 🟡 Média  
**OWASP:** A05 — Injection  
**CWE:** CWE-20

**Localização:** `app/blueprints/auth/routes.py`, linhas 50–62

**Descrição:** O campo `email` no registro é aceito sem validação de formato. Qualquer string é aceita como e-mail válido.

**Evidência:**
```python
email = request.form.get('email', '').strip()
# Nenhuma validação de formato de e-mail
if User.query.filter_by(email=email).first():
```

**Recomendação:**
```python
import re
EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
if not EMAIL_RE.match(email):
    flash('E-mail inválido.', 'warning')
    return render_template('auth/register.html')
```

---

### VUL-07 — `DATABASE_URL` com fallback para SQLite sem aviso
**Severidade:** 🟡 Média  
**OWASP:** A02 — Security Misconfiguration  
**CWE:** CWE-547

**Localização:** `app/__init__.py`, linha 10

**Descrição:** Se `DATABASE_URL` não for definida, a aplicação silenciosamente usa SQLite local. Em produção, isso pode expor dados em arquivo acessível no sistema de arquivos.

**Evidência:**
```python
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///pokeshop.db')
```

**Recomendação:** Logar aviso explícito em ambiente não-development:
```python
db_url = os.getenv('DATABASE_URL', 'sqlite:///pokeshop.db')
if 'sqlite' in db_url and os.getenv('FLASK_ENV') == 'production':
    import warnings
    warnings.warn("SQLite em produção não é recomendado.")
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
```

---

### VUL-08 — Ausência de logging de eventos de segurança
**Severidade:** 🟡 Média  
**OWASP:** A09 — Security Logging and Alerting Failures  
**CWE:** CWE-778

**Localização:** `app/blueprints/auth/routes.py` — geral

**Descrição:** Eventos críticos como login com falha, bloqueio de conta e tentativas de acesso não autorizado não são registrados em log. Isso impede auditoria e detecção de ataques.

**Recomendação:**
```python
import logging
logger = logging.getLogger(__name__)

# Em caso de falha de login:
logger.warning(f"Falha de login para {email} — IP {ip}")

# Em caso de bloqueio:
logger.warning(f"Conta bloqueada: {email} após 5 tentativas — IP {ip}")
```

---

### VUL-09 — Nome de usuário aceito sem limite de tamanho
**Severidade:** 🟡 Média  
**OWASP:** A05 — Injection  
**CWE:** CWE-20

**Localização:** `app/blueprints/auth/routes.py`, linha 52

**Descrição:** O campo `nome` no registro não tem validação de tamanho máximo no backend, apesar do modelo `User` definir `String(120)`. Entradas muito longas podem causar erros inesperados.

**Recomendação:**
```python
if len(nome) > 120:
    flash('Nome muito longo (máximo 120 caracteres).', 'warning')
    return render_template('auth/register.html')
```

---

### VUL-10 — `login_manager` sem configuração de `session_protection`
**Severidade:** 🔵 Baixa  
**OWASP:** A07 — Authentication Failures  
**CWE:** CWE-613

**Localização:** `app/extensions.py`

**Descrição:** Flask-Login tem proteção de sessão configurável (`basic` ou `strong`). Sem configuração explícita, o padrão é `basic`, que não invalida a sessão em mudança de IP ou User-Agent.

**Recomendação:**
```python
login_manager.session_protection = "strong"
```

---

### VUL-11 — Ausência de atributos `Secure` e `HttpOnly` explícitos nos cookies
**Severidade:** 🔵 Baixa  
**OWASP:** A02 — Security Misconfiguration  
**CWE:** CWE-614

**Localização:** `app/__init__.py`

**Descrição:** Os cookies de sessão não têm `Secure` e `HttpOnly` configurados explicitamente via `app.config`.

**Recomendação:**
```python
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True   # apenas em produção com HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
```

---

## Próximos Passos

Este foi o nível **superficial** da inspeção. As próximas etapas devem cobrir:

- **Nível moderado:** `app/blueprints/admin/routes.py`, `app/blueprints/cart/routes.py`, `app/models/`, templates Jinja2
- **Nível profundo:** análise de queries SQLAlchemy, lógica de autorização por role, validação de uploads de imagem, integração ViaCEP

---

*Inspeção realizada com base no OWASP Top 10 e boas práticas de desenvolvimento seguro.*
