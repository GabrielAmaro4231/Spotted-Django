Membro: Gabriel Amaro  
Vídeo de apresentação: https://www.youtube.com/watch?v=334MMan5_sQ

# Spotted API

Backend da aplicação **Spotted**, um logbook digital para registro de avistamentos de aeronaves.

A API foi criada para atender um aplicativo iOS/mobile, oferecendo autenticação, gerenciamento de perfil, upload automático de avatar, cadastro de avistamentos e ranking público anonimizado.

---

## Sobre o projeto

O Spotted é uma plataforma de registro de avistamentos de aeronaves desenvolvida para permitir que usuários registrem, organizem e acompanhem aeronaves observadas de maneira simples e moderna.

A proposta do app é funcionar como um logbook digital para entusiastas da aviação. Em vez de manter anotações soltas, o usuário pode criar um histórico próprio de aeronaves avistadas, com dados básicos do avistamento e localização.

Na versão atual do backend, cada avistamento registra:

- matrícula da aeronave;
- modelo da aeronave, quando informado;
- companhia aérea, quando informada;
- latitude e longitude;
- data e horário de criação.

Este repositório contém a API responsável pela autenticação, persistência de dados, regras de acesso, gerenciamento de perfil, imagens de avatar e comunicação com o aplicativo mobile.

---

## Objetivos do backend

O backend foi projetado com foco em:

- simplicidade;
- organização;
- legibilidade do código;
- facilidade de manutenção;
- separação clara de responsabilidades;
- uma base sólida para evoluções futuras.

O projeto evita complexidade desnecessária e segue uma arquitetura REST para que o app mobile consiga consumir os recursos de forma previsível e segura.

---

## Tecnologias

- Python
- Django 6.0.6
- Django REST Framework
- DRF Token Authentication
- django-filter
- SQLite para desenvolvimento local
- boto3 para upload de imagens de perfil no S3
- python-dotenv para configurações locais por `.env`

---

## Estrutura

```text
spotted_api/
├── core/          # código compartilhado, incluindo middleware de logging
├── posts/         # avistamentos, filtros, permissões e leaderboard
├── users/         # usuário customizado, auth, perfil, avatar e S3
├── spotted_api/   # settings, URLs e entrypoints do projeto Django
├── manage.py
├── requirements.txt
└── readme.md
```

### Responsabilidades das aplicações

- `users`: cadastro, login, logout, perfil, geração de handle, preferências de leaderboard e avatar de perfil.
- `posts`: registros de avistamentos, filtros, ordenação, permissões de dono e leaderboard.
- `core`: código compartilhado, atualmente com o middleware de logging de requisições.
- `spotted_api`: configurações centrais do Django, URLs raiz e entrypoints ASGI/WSGI.

---

## Como rodar localmente

Crie e ative o ambiente virtual, caso ainda não exista:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Rode as migrações:

```bash
.venv/bin/python manage.py migrate
```

Execute as verificações do Django:

```bash
.venv/bin/python manage.py check
```

Inicie o servidor local:

```bash
.venv/bin/python manage.py runserver
```

Rotas principais:

- `/admin/`
- `/api/users/`
- `/api/posts/`

---

## Autenticação

A API usa Token Authentication do Django REST Framework.

Depois do login, envie o token nas rotas autenticadas:

```http
Authorization: Token <token>
```

Por padrão, as rotas exigem usuário autenticado. Endpoints públicos usam permissão explícita.

---

## Usuários e perfil

O projeto usa um modelo de usuário customizado:

- `id` UUID
- `email` como campo de login
- `name`
- `handle` gerado automaticamente
- `profile_image_url`
- `show_handle_on_leaderboard`
- flags de permissão do Django: `is_active`, `is_staff`, `is_superuser`

Endpoints:

| Método | Rota | Descrição |
| --- | --- | --- |
| `POST` | `/api/users/register/` | Cria usuário com `email`, `name`, `password` e opcionalmente `show_handle_on_leaderboard`. |
| `POST` | `/api/users/login/` | Autentica com `email` e `password`, retornando um token. |
| `GET` | `/api/users/me/` | Retorna o perfil do usuário autenticado. |
| `PUT/PATCH` | `/api/users/me/` | Atualiza `email`, `name`, `show_handle_on_leaderboard` e/ou senha. |
| `GET` | `/api/users/profile/` | Retorna os dados completos do perfil autenticado. |
| `POST` | `/api/users/logout/` | Remove o token atual. |

Campos retornados no perfil:

- `id`
- `email`
- `name`
- `handle`
- `profile_image_url`
- `show_handle_on_leaderboard`

### Senha

Para alterar a senha, envie a senha atual e a nova senha:

```json
{
  "current_password": "SenhaAtual1",
  "password": "MinhaNovaSenha1"
}
```

Após uma troca de senha, o token atual é invalidado e o usuário precisa fazer login novamente.

### Avatar de perfil

`profile_image_url` é somente leitura para o cliente.

No cadastro, a API:

1. gera um hash SHA256 do email normalizado;
2. tenta baixar a imagem do Gravatar;
3. se não houver Gravatar, gera uma imagem pelo UI Avatars;
4. envia a imagem para o S3;
5. salva a URL pública no campo `profile_image_url`.

Quando o email é alterado, a API repete esse fluxo com o novo email.

Alterações de perfil são registradas em `UserProfileChangeLog`. A criação salva um snapshot dos campos públicos do perfil, e atualizações registram apenas campos alterados. Senhas não são armazenadas no histórico; a troca de senha é marcada apenas como alteração realizada.

---

## Configuração de S3

As configurações podem ficar no arquivo `.env`, usando `.env.example` como base, ou em variáveis de ambiente do processo.

Variáveis usadas pelo projeto:

```env
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=
AWS_S3_PROFILE_AVATAR_PREFIX=
```

Também há suporte no código para configurações opcionais como `AWS_SESSION_TOKEN`, `AWS_S3_CUSTOM_DOMAIN`, `AWS_S3_ENDPOINT_URL` e `AWS_S3_OBJECT_ACL`, úteis em cenários com credenciais temporárias, CloudFront/domínio próprio, endpoints compatíveis com S3 ou buckets que exigem ACL explícita.

Se `AWS_STORAGE_BUCKET_NAME` não estiver configurado ou se o upload falhar, a API mantém o usuário sem avatar salvo em `profile_image_url` e continua funcionando.

---

## Avistamentos

Os avistamentos são representados pelo modelo `Post`.

Campos:

- `id` UUID
- `user`
- `airplane_registration`
- `airplane_model`
- `airline`
- `latitude`
- `longitude`
- `created_at`

`airplane_model` e `airline` são opcionais. `created_at` é gerado automaticamente. Latitude deve estar entre `-90` e `90`; longitude entre `-180` e `180`.

Endpoints sob `/api/posts/`:

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/api/posts/` | Lista os avistamentos do usuário autenticado. |
| `POST` | `/api/posts/` | Cria um avistamento para o usuário autenticado. |
| `GET` | `/api/posts/<id>/` | Retorna um avistamento do usuário autenticado. |
| `PUT/PATCH` | `/api/posts/<id>/` | Atualiza um avistamento do usuário autenticado. |
| `DELETE` | `/api/posts/<id>/` | Remove um avistamento do usuário autenticado. |
| `GET` | `/api/posts/leaderboard/` | Retorna o ranking público por quantidade de avistamentos. |

Posts são privados por padrão. A listagem, consulta, edição e exclusão ficam sempre limitadas ao usuário autenticado.

### Filtros e ordenação

Filtros de posts:

- `airplane_registration`
- `airplane_model`
- `airline`
- `created_after`
- `created_before`

Os filtros de texto usam busca case-insensitive parcial.

Ordenação de posts:

- `ordering=created_at`
- `ordering=-created_at`
- `ordering=airplane_registration`
- `ordering=-airplane_registration`

A ordenação padrão é por `created_at` mais recente primeiro.

### Leaderboard

O endpoint `/api/posts/leaderboard/` agrega a quantidade de posts por usuário.

Ele não expõe emails nem IDs de usuários. O nome exibido segue esta regra:

- o usuário autenticado aparece como `@handle`;
- outros usuários aparecem como `@handle` apenas se `show_handle_on_leaderboard` estiver ativo;
- caso contrário, aparecem como `Anonymous User <posição>`.

Ordenação da leaderboard:

- `ordering=desc`
- `ordering=asc`

---

## Logging

O middleware `RequestLoggingMiddleware` registra metadados de requisições e respostas em `logs/requests.log` com rotação de arquivo.

Dados registrados:

- método HTTP
- path
- query params
- corpo da requisição
- corpo da resposta
- status code
- duração
- ID do usuário autenticado, quando houver

Campos sensíveis são mascarados automaticamente, incluindo senhas, tokens, autorização, cookies, secrets, API keys e JWTs.
