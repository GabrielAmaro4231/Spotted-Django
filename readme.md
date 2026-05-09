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