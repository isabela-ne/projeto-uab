# Relatório de Inspeção de Segurança - v3

## 1. Resumo Executivo

Esta inspeção detalhada foi realizada seguindo as melhores práticas de desenvolvimento seguro e as diretrizes do OWASP Top 10. Foram identificadas vulnerabilidades que variam de severidade Baixa a Crítica.

### 1.1 Contagem de Achados por Severidade

| Severidade | Quantidade |
| :--- | :--- |
| 🔴 Crítica | 1 |
| 🟠 Alta | 1 |
| 🟡 Média | 3 |
| 🔵 Baixa | 3 |
| **Total** | **8** |

### 1.2 Top 5 Ações Mais Urgentes

1.  **Desabilitar o Modo Debug:** O modo debug está ativado no ponto de entrada da aplicação, o que pode expor segredos e permitir execução remota de código.
2.  **Remover Fallback de SECRET_KEY:** O uso de 'dev' como chave secreta padrão em código é um risco alto para a integridade das sessões e proteção CSRF.
3.  **Implementar Cabeçalhos de Segurança:** A aplicação carece de defesas básicas no nível do navegador (HSTS, CSP, etc.).
4.  **Corrigir Lógica de Autorização no Suporte:** Restringir o acesso a tickets de forma explícita para evitar bypass por novos papéis de usuário.
5.  **Configurar Usuário Não-Root no Docker:** Aumentar o isolamento do container para mitigar danos em caso de comprometimento.

---

## 2. Detalhamento das Vulnerabilidades

### VUL-22: Modo Debug Habilitado em Produção
*   **Localização:** `app/run.py`, linha 6 (função `__main__`)
*   **Descrição:** A aplicação está configurada para rodar com `debug=True`. Isso habilita o depurador interativo do Werkzeug, que permite a execução de código Python arbitrário no servidor caso um erro ocorra.
*   **Evidência:**
    ```python
    if __name__ == '__main__':
        app.run(debug=True, host='0.0.0.0', port=5000)
    ```
*   **Impacto Potencial:** Execução Remota de Código (RCE), exposição de código-fonte e variáveis de ambiente.
*   **Nível de Severidade:** 🔴 Crítica
*   **Recomendação:** Desabilitar o modo debug ou utilizá-lo apenas se uma variável de ambiente específica estiver presente.
    ```python
    app.run(debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true', host='0.0.0.0', port=5000)
    ```
*   **Referências:** OWASP A05:2021 - Security Misconfiguration, CWE-489.

### VUL-23: Fallback de SECRET_KEY Inseguro
*   **Localização:** `app/__init__.py`, linha 10 (função `create_app`)
*   **Descrição:** A `SECRET_KEY` possui um valor padrão 'dev'. Se a variável de ambiente não for configurada em produção, a aplicação usará uma chave conhecida, permitindo a falsificação de cookies de sessão e bypass de tokens CSRF.
*   **Evidência:**
    ```python
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    ```
*   **Impacto Potencial:** Sequestro de sessão, falsificação de requisições (CSRF), comprometimento da integridade dos dados.
*   **Nível de Severidade:** 🟠 Alta
*   **Recomendação:** Remova o valor padrão ou force a falha da aplicação caso a chave não esteja presente em ambientes que não sejam de desenvolvimento.
*   **Referências:** OWASP A02:2021 - Cryptographic Failures, CWE-330.

### VUL-24: Lógica de Autorização Permissiva na Rota de Suporte
*   **Localização:** `app/blueprints/support/routes.py`, linha 39 (função `detalhe`)
*   **Descrição:** A verificação de acesso usa uma lógica de exclusão baseada apenas no papel 'Cliente'. Se um usuário possuir um papel diferente (ex: 'Gerente', 'Visitante') que não esteja explicitamente listado como admin/atendente, ele poderá visualizar tickets de outros usuários.
*   **Evidência:**
    ```python
    if current_user.role == 'Cliente' and ticket.usuario_id != current_user.id:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('support.index'))
    ```
*   **Impacto Potencial:** Acesso não autorizado a dados sensíveis de suporte de outros usuários.
*   **Nível de Severidade:** 🟡 Média
*   **Recomendação:** Utilize uma lógica de "Permissão Mínima" ou "Allow-list".
    ```python
    if not (current_user.role in ['Administrador', 'Atendente'] or ticket.usuario_id == current_user.id):
        flash('Acesso negado.', 'danger')
        return redirect(url_for('support.index'))
    ```
*   **Referências:** OWASP A01:2021 - Broken Access Control, CWE-285.

### VUL-25: Ausência de Cabeçalhos de Segurança HTTP
*   **Localização:** `app/__init__.py`
*   **Descrição:** A aplicação não configura cabeçalhos de segurança fundamentais que instruem o navegador a mitigar ataques comuns.
*   **Evidência:** Ausência de middleware ou extensões como `Flask-Talisman`.
*   **Impacto Potencial:** Vulnerabilidade a Clickjacking, ataques de MIME-sniffing e falta de proteção contra interceptação (HSTS).
*   **Nível de Severidade:** 🟡 Média
*   **Recomendação:** Implementar cabeçalhos como `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options` e `Strict-Transport-Security`. Recomenda-se o uso do `Flask-Talisman`.
*   **Referências:** OWASP A05:2021 - Security Misconfiguration.

### VUL-26: Docker Container Executando como Usuário Root
*   **Localização:** `Dockerfile`
*   **Descrição:** O `Dockerfile` não define um usuário (`USER`), o que faz com que todos os processos dentro do container rodem com privilégios de root.
*   **Evidência:** Ausência da instrução `USER` e criação de usuário não-privilegiado.
*   **Impacto Potencial:** Em caso de comprometimento da aplicação (ex: RCE), o atacante terá privilégios totais dentro do container e maior facilidade para ataques de "escape" para o host.
*   **Nível de Severidade:** 🟡 Média
*   **Recomendação:** Criar um usuário sem privilégios no `Dockerfile` e utilizá-lo para rodar a aplicação.
    ```dockerfile
    RUN useradd -m myuser
    USER myuser
    ```
*   **Referências:** Melhores Práticas de Segurança em Docker.

### VUL-27: Falta de Validação de Status em Tickets
*   **Localização:** `app/blueprints/support/routes.py`, linhas 46-47 (função `detalhe`)
*   **Descrição:** O parâmetro `status` é aceito via formulário e atribuído diretamente ao modelo sem validação contra uma lista de estados permitidos.
*   **Evidência:**
    ```python
    novo_status = request.form.get('status')
    # ...
    if novo_status and current_user.role in ['Administrador', 'Atendente']:
        ticket.status = novo_status
    ```
*   **Impacto Potencial:** Corrupção de dados lógicos (status inválidos no banco de dados) e possível impacto em relatórios ou fluxos de trabalho automáticos.
*   **Nível de Severidade:** 🔵 Baixa
*   **Recomendação:** Validar se o `novo_status` pertence a uma lista pré-definida (ex: `['Aberto', 'Em Andamento', 'Encerrado', 'Reaberto']`).
*   **Referências:** OWASP A10:2021 - Mishandling of Exceptional Conditions.

### VUL-28: Política de Senhas Fraca
*   **Localização:** `app/blueprints/auth/routes.py`, linha 55 (função `register`)
*   **Descrição:** A aplicação exige apenas um comprimento mínimo de 6 caracteres para a senha, sem exigir complexidade (números, símbolos, maiúsculas).
*   **Evidência:**
    ```python
    if len(senha) < 6:
        flash('A senha deve ter pelo menos 6 caracteres.', 'warning')
    ```
*   **Impacto Potencial:** Suscetibilidade a ataques de força bruta e dicionário.
*   **Nível de Severidade:** 🔵 Baixa
*   **Recomendação:** Aumentar o mínimo para 8 ou 10 caracteres e implementar verificações de complexidade ou uso de bibliotecas como `zxcvbn`.
*   **Referências:** OWASP A07:2021 - Identification and Authentication Failures.

### VUL-29: Montagem de Volume com Código-Fonte em Docker Compose
*   **Localização:** `docker-compose.yml`, linha 7
*   **Descrição:** O arquivo de orquestração monta o diretório atual diretamente no container (`.:/app`). Embora útil em desenvolvimento, se esse arquivo for usado em produção, ele expõe o ambiente e permite modificações em tempo real no código que podem não ser auditadas.
*   **Evidência:**
    ```yaml
    volumes:
      - .:/app
    ```
*   **Impacto Potencial:** Exposição de arquivos sensíveis (.env, .git) para o container e riscos de integridade.
*   **Nível de Severidade:** 🔵 Baixa
*   **Recomendação:** Remover montagens de volume de código em arquivos destinados a ambientes de produção/homologação.
*   **Referências:** OWASP A03:2021 - Software and Data Integrity Failures.
