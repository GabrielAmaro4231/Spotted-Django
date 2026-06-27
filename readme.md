Membros: Gabriel Amaro;
Vídeo Apresentação: https://www.youtube.com/watch?v=334MMan5_sQ;

# Spotted API

Backend da aplicação **Spotted**.

O Spotted é uma plataforma de registro de avistamentos de aeronaves desenvolvida para permitir que usuários registrem, organizem e acompanhem aeronaves observadas de maneira simples e moderna.

Este repositório contém a API responsável pela autenticação, persistência de dados, regras de negócio e comunicação com o aplicativo iOS.

---

# Sobre o Projeto

O objetivo do Spotted é funcionar como uma espécie de logbook digital para entusiastas da aviação.

Através do aplicativo, o usuário pode registrar informações sobre aeronaves avistadas, como:
- matrícula
- localização
- data e horário
- observações
- informações adicionais da aeronave

O backend foi desenvolvido seguindo uma arquitetura REST, permitindo que o aplicativo mobile se comunique de forma simples, segura e organizada com a API.

---

# Objetivos do Backend

O backend foi projetado com foco em:
- simplicidade
- organização
- escalabilidade futura
- legibilidade do código
- facilidade de manutenção
- separação clara de responsabilidades

O projeto evita complexidade desnecessária e prioriza uma base sólida para evolução futura.

---

# Tecnologias Utilizadas

## Backend
- Python
- Django
- Django REST Framework

## Banco de Dados
- SQLite (ambiente de desenvolvimento)

## Autenticação
- Token Authentication do Django REST Framework

## Outros
- django-filter
- Middleware customizado para logging de requisições

---

# Arquitetura

A API segue uma arquitetura baseada em aplicações separadas por responsabilidade.

Exemplo:

```text
spotted_api/
├── users/
├── posts/
├── core/
└── spotted_api/
```

---

# Aplicações

## users
Responsável por:
- autenticação
- gerenciamento de usuários
- login
- logout
- perfil do usuário

## posts
- Responsável pelos registros de avistamentos realizados pelos usuários.

## core
- Responsável por funcionalidades compartilhadas da aplicação, como middlewares e configurações centrais.

---

# Sistema de Autenticação

A autenticação é realizada utilizando o sistema de Token Authentication do Django REST Framework.
Após o login, o usuário recebe um token que deve ser enviado nas próximas requisições autenticadas.

Exemplo:
```http
Authorization: Token <token>
```

O sistema foi escolhido por sua simplicidade e facilidade de integração com aplicações mobile.

## Atualização de Perfil

O endpoint `POST /api/users/register/` cria um usuário com `email`, `name`, `password` e, opcionalmente, `profile_image_url` e `show_handle_on_leaderboard`. O campo `handle` é gerado automaticamente a partir do nome do usuário com números aleatórios.

O endpoint `GET /api/users/profile/` retorna os dados completos do usuário autenticado:
- id
- email
- name
- handle
- profile_image_url
- show_handle_on_leaderboard

O endpoint `PUT/PATCH /api/users/me/` permite atualizar o email, nome, link da imagem de perfil, preferência de exibição do handle na leaderboard e/ou senha do usuário autenticado.

Para alterar a senha, a requisição deve enviar a senha atual no campo `current_password` e a nova senha no campo `password`.

Exemplo:
```json
{
  "current_password": "SenhaAtual1",
  "password": "MinhaNovaSenha1"
}
```

Após a alteração de senha, o token atual é invalidado. O usuário deve realizar login novamente para receber um novo token.

No endpoint `GET /api/posts/leaderboard/`, o usuário atual aparece como `@handle` quando autenticado. Outros usuários só aparecem como `@handle` quando `show_handle_on_leaderboard` estiver marcado; caso contrário, continuam anônimos.

---

# Sistema de Logging

A API possui um sistema centralizado de logging de requisições implementado através de middleware customizado.
Os logs incluem informações como:
- método HTTP
- endpoint acessado
- parâmetros da requisição
- status da resposta
- duração da requisição
- identificador do usuário autenticado

Informações sensíveis como senhas e tokens são automaticamente ocultadas antes de serem registradas.

Os logs são armazenados em arquivos rotativos para evitar crescimento excessivo do armazenamento.
