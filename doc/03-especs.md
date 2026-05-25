# Especificações Técnicas e Funcionais - PokéShop

Este documento descreve as especificações técnicas e funcionais do sistema PokéShop, uma plataforma de e-commerce voltada para produtos do universo Pokémon.

## 1. Descrição Geral
O PokéShop é uma aplicação web desenvolvida em Python com o framework Flask. O sistema gerencia o ciclo completo de venda, desde a navegação no catálogo até a finalização do pedido e suporte pós-venda.

### Tecnologias Utilizadas
- **Linguagem:** Python 3.x
- **Framework Web:** Flask
- **ORM:** SQLAlchemy
- **Banco de Dados:** SQLite (padrão de desenvolvimento)
- **Migrações:** Flask-Migrate (Alembic)
- **Autenticação:** Flask-Login
- **Segurança:** Flask-WTF (CSRF), bcrypt (hashing de senhas)
- **Integrações:** ViaCEP (Cálculo de frete)
- **Cache:** Flask-Caching (SimpleCache, TTL 60s)
- **Jobs:** rq (fila assíncrona para notificações)
- **Frontend:** Bootstrap 5, Jinja2

---

## 2. Funcionalidades Implementadas

### 2.1. Autenticação e Usuários (`auth`)
- **Cadastro:** Registro de novos clientes com validação de senha (mínimo 6 caracteres).
- **Login:** Autenticação com proteção contra força bruta (bloqueio após 5 tentativas) e rate limiting por IP.
- **Logout:** Encerramento seguro da sessão.
- **Perfis de Acesso:** Cliente (padrão), Atendente e Administrador.

### 2.2. Catálogo de Produtos (`catalog`)
- **Listagem:** Exibição de produtos disponíveis em estoque.
- **Filtros:** Busca por nome e filtragem por categoria.
- **Detalhes:** Visualização completa do produto com sugestão de itens relacionados da mesma categoria.
- **Cache:** Respostas GET em `/catalog/` e `/catalog/produto/<id>` cacheadas por 60 segundos. Cache invalidado em operações de escrita no admin.

### 2.3. Carrinho de Compras (`cart`)
- **Gestão de Itens:** Adicionar, remover e limpar o carrinho (armazenado em sessão).
- **Cálculo de Frete:** Integração com ViaCEP para busca de endereço e cálculo de valores/prazos com base na região do CEP.
- **Seleção de Frete:** Opções de PAC e SEDEX com atualização automática do total.

### 2.4. Checkout (`checkout`)
- **Validação:** Verificação dupla de estoque (ao entrar no checkout e ao finalizar).
- **Endereçamento:** Coleta de dados de entrega.
- **Pagamento:** Suporte a Cartão de Crédito, PIX e Boleto.
- **Finalização:** Criação do pedido, registro dos itens e baixa automática no estoque.
- **Notificação:** Envio de e-mail de confirmação via fila assíncrona (rq).

### 2.5. Pedidos (`orders`)
- **Histórico:** Visualização da lista de pedidos realizados pelo cliente.
- **Detalhe do Pedido:** Informações completas sobre status, itens, preços e endereço de entrega.

### 2.6. Suporte ao Cliente (`support`)
- **Tickets (Chamados):** Sistema de abertura de chamados para dúvidas ou problemas.
- **Mensagens:** Histórico de interação entre cliente e suporte.
- **Gestão:** Atendentes e Administradores podem visualizar todos os tickets e alterar seus status.

### 2.7. Painel Administrativo (`admin`)
- **Dashboard:** Visão geral com métricas (Receita total, total de pedidos, usuários, produtos com estoque crítico).
- **Gestão de Produtos:** CRUD completo de produtos (incluindo controle de estoque e imagens).
- **Gestão de Equipe:** Cadastro e remoção de Atendentes.
- **Gestão de Pedidos:** Acompanhamento de todos os pedidos e alteração manual de status de entrega.
- **Relatórios:** Dados consolidados sobre vendas e inventário.

---

## 3. Regras de Negócio Identificadas

### Segurança
- **Rate Limit:** Máximo de 10 tentativas de login por IP a cada 5 minutos.
- **Bloqueio de Conta:** Usuários são bloqueados após 5 falhas consecutivas de senha.
- **Proteção de Acesso:** Rotas de administração exigem perfil 'Administrador'. Usuários comuns só acessam seus próprios pedidos e tickets.

### Vendas e Estoque
- **Disponibilidade:** Apenas produtos com estoque > 0 são exibidos no catálogo.
- **Reserva de Estoque:** O estoque só é decrementado no momento da confirmação do pedido (Checkout Finalizar).
- **Integridade de Preço:** O preço final do pedido é capturado diretamente do banco de dados no momento da finalização, ignorando valores potencialmente alterados na sessão.

### Logística (Frete)
- **Cálculo Regional:** O valor e o prazo do frete são determinados pelo primeiro dígito do CEP:
    - `0, 1`: São Paulo (Mais barato/rápido).
    - `2, 3`: RJ, ES, MG.
    - `4, 5, 6, 7`: Outras regiões.
    - `8, 9`: Sul e demais.

---

## 4. Modelo de Dados

### User
- `id`: Inteiro, PK
- `nome`: String(120)
- `email`: String(120), Único
- `password_hash`: String(255)
- `role`: String(20) (Cliente, Atendente, Administrador)
- `failed_login_attempts`: Inteiro
- `ativo`: Booleano

### Product
- `id`: Inteiro, PK
- `nome`: String(200)
- `descricao`: Texto
- `preco`: Float
- `image_url`: String(500)
- `estoque`: Inteiro
- `categoria_id`: FK(Category)

### Category
- `id`: Inteiro, PK
- `nome`: String(100), Único

### Order
- `id`: Inteiro, PK
- `user_id`: FK(User)
- `status`: String(30) (aguardando_pagamento, pago, em_separacao, enviado, entregue, cancelado)
- `payment_method`: String(20)
- `total`: Float
- `endereco_*`: Campos de endereço (rua, numero, bairro, cidade, estado, cep)
- `created_at`: DateTime

### OrderItem
- `id`: Inteiro, PK
- `order_id`: FK(Order)
- `product_id`: FK(Product)
- `quantity`: Inteiro
- `unit_price`: Float

### Ticket & TicketMessage
- `Ticket`: Gerencia o assunto e status do chamado.
- `TicketMessage`: Armazena as mensagens individuais, autor e data.

---

## 5. Rotas Disponíveis

| Blueprint | Rota | Método | Descrição |
|-----------|------|--------|-----------|
| **Auth** | `/auth/login` | GET, POST | Autenticação de usuário |
| | `/auth/register` | GET, POST | Cadastro de novos clientes |
| | `/auth/logout` | GET | Encerramento de sessão |
| **Catalog**| `/catalog/` | GET | Listagem e busca de produtos |
| | `/catalog/produto/<id>` | GET | Detalhes do produto |
| **Cart** | `/cart/view` | GET | Visualização do carrinho |
| | `/cart/add/<id>` | POST | Adicionar item ao carrinho |
| | `/cart/remove/<pid>`| POST | Remover item do carrinho |
| | `/cart/frete` | POST | Calcular frete via ViaCEP |
| **Checkout**| `/checkout/` | GET, POST| Tela de endereço e pagamento |
| | `/checkout/finalizar`| POST | Processamento do pedido |
| **Orders** | `/orders/` | GET | Histórico de pedidos do usuário |
| | `/orders/<id>` | GET | Detalhe de um pedido específico |
| **Support**| `/support/` | GET | Lista de chamados |
| | `/support/novo` | GET, POST | Abertura de novo chamado |
| **Admin** | `/admin/` | GET | Dashboard administrativo |
| | `/admin/produtos` | GET, POST | Gestão de inventário |
| | `/admin/pedidos` | GET | Gestão de vendas e status |
| | `/admin/usuarios` | GET | Gestão de equipe de atendimento |

---

## 6. Especificações de Frontend

### 6.1. Design System

- **Framework CSS:** Bootstrap 5
- **Tipografia:** padrão Bootstrap; hierarquia `h1 > h2 > h3` respeitada por página
- **Cores:** paleta consistente com tema Pokémon; botões de ação primária em destaque
- **Ícones:** Bootstrap Icons ou equivalente já presente no projeto
- **Imagens de produto:** proporção 1:1, fallback com placeholder quando `image_url` ausente

### 6.2. Responsividade

Todas as páginas devem funcionar nos seguintes breakpoints Bootstrap:

| Breakpoint | Largura | Comportamento |
|------------|---------|---------------|
| Mobile | < 576px | Menu colapsado, cards em coluna única, formulários em bloco |
| Tablet | 576–991px | Grid de 2 colunas para produtos |
| Desktop | ≥ 992px | Grid de 3–4 colunas para produtos, sidebar visível |

### 6.3. Acessibilidade

- Todos os `<img>` devem ter atributo `alt` descritivo
- Todos os campos de formulário devem ter `<label>` associado via `for`/`id`
- Botões de ação devem ter texto visível ou `aria-label`
- Contraste mínimo de 4.5:1 entre texto e fundo
- Navegação por teclado funcional em formulários e menus
- Foco visível (`outline`) nunca removido via CSS sem substituto

### 6.4. Estados de Tela

#### Catálogo
- **Carregando:** spinner Bootstrap centralizado enquanto a listagem carrega
- **Vazio:** mensagem `"Nenhum produto encontrado."` quando busca não retorna resultados
- **Erro:** mensagem genérica `"Erro ao carregar produtos. Tente novamente."` em caso de falha

#### Carrinho
- **Vazio:** mensagem `"Seu carrinho está vazio."` com link para o catálogo
- **Frete não calculado:** total exibido sem frete até CEP ser informado
- **Calculando frete:** botão desabilitado com spinner enquanto requisição ViaCEP está em andamento
- **CEP inválido:** mensagem de erro inline abaixo do campo

#### Checkout
- **Campos obrigatórios:** validação HTML5 + feedback visual Bootstrap (`is-invalid`) antes do envio
- **Processando pedido:** botão "Finalizar" desabilitado após primeiro clique para evitar duplo envio
- **Sucesso:** redirecionamento para página de detalhe do pedido com mensagem flash de confirmação

#### Pedidos
- **Histórico vazio:** mensagem `"Você ainda não realizou nenhum pedido."` com link para o catálogo
- **Status:** badge colorido por status (aguardando = amarelo, pago = azul, enviado = verde, cancelado = vermelho)

#### Suporte
- **Sem chamados:** mensagem `"Você não possui chamados abertos."` com link para abrir novo
- **Ticket fechado:** campo de resposta desabilitado com aviso `"Este chamado está encerrado."`

#### Admin
- **Estoque crítico:** produtos com `estoque <= 5` destacados com badge vermelho no dashboard e na listagem
- **Ação destrutiva:** confirmação via modal Bootstrap antes de remover atendente ou produto

### 6.5. Formulários

- Feedback de erro exibido inline abaixo do campo afetado (classe `invalid-feedback` do Bootstrap)
- Mensagens flash exibidas no topo da página, dispensáveis pelo usuário (botão ×)
- Campos de senha com opção de revelar/ocultar (toggle de visibilidade)
- CEP com máscara `#####-###` e auto-preenchimento de endereço via ViaCEP após digitação

### 6.6. Navegação

- Navbar fixa no topo com links para: Catálogo, Carrinho (com contador de itens), Login/Logout, Admin (se Administrador)
- Breadcrumb nas páginas de detalhe de produto e detalhe de pedido
- Redirecionamento pós-login para a página de origem (parâmetro `next`)
- Páginas de erro 403 e 404 com layout padrão do projeto e link de retorno ao catálogo

### 6.7. Integração Frontend/Backend

- Respostas de erro do backend mapeadas para mensagens amigáveis na interface
- Frete calculado via POST assíncrono (fetch/AJAX) sem recarregar a página
- Formulário de login desabilitado durante requisição para evitar múltiplos envios
- Invalidação de cache do catálogo refletida imediatamente após salvar produto no admin

---

## 7. Otimizações Implementadas

- **Cache:** rotas GET do catálogo com TTL de 60 segundos via Flask-Caching
- **Fila assíncrona:** envio de e-mail de confirmação de pedido via rq, desacoplado do fluxo HTTP
- **Entry point único:** `app/run.py` removido; apenas `./run.py` na raiz
- **Extensions centralizadas:** `app/extensions.py` como fonte única de `db`, `login_manager`, `cache`
- **Dependências limpas:** `stripe` e `mercadopago` removidos (não implementados)
