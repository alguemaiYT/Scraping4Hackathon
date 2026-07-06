# Scraping4Hackathon — Coletor e API de Dados Acadêmicos (UNESP Sorocaba)

Este repositório contém o sistema completo de coleta de dados acadêmicos em tempo real, persistência e API REST desenvolvido para alimentar o banco de dados da **MINA (Assistente Virtual)**. O sistema foi concebido para coletar programaticamente dados do Portal da UNESP Sorocaba (Jornal, horários e locais) e expô-los através de uma API ágil de alto desempenho.

---

## 🛠️ Recursos e Tecnologias

* **Coletor Assíncrono (Collector):** Robô de raspagem assíncrono desenvolvido com `aiohttp` e `Playwright` para navegar, coletar e formatar notícias, eventos e grades horárias sem sobrecarregar o portal.
* **Persistência de Dados (Database):** Armazenamento estruturado usando **PostgreSQL** com ORM SQLAlchemy para logs e histórico.
* **API de Alto Desempenho (API):** Desenvolvida em **FastAPI**, fornecendo rotas rápidas e documentação interativa (Swagger UI) para consumo da Mina.
* **RAG & Agent (IA):** Agente inteligente construído com **LangChain** para busca semântica em linguagem natural sobre o mural de notícias raspado.
* **Cache em Memória (Redis):** Cache temporário para reduzir latência de requisições concorrentes.
* **Dashboard Web:** Interface interativa básica para monitoramento das tabelas e do status do coletor.
* **Dockerizado:** Orquestração completa usando `docker-compose` para fácil implantação e portabilidade.

---

## 📂 Estrutura do Repositório

```
Scraping4Hackathon/
├── collector/          # Robôs de coleta assíncrona (scraping/APIs)
│   ├── base.py           # Interface base para coletores
│   ├── open_meteo.py     # Coletor de testes e clima
│   ├── university_api.py # Conexão direta com APIs internas
│   └── scheduler.py      # Agendador de raspagem periódica
├── database/           # Modelos de banco de dados (PostgreSQL + SQLAlchemy)
├── api/                # Rotas FastAPI e lógica de respostas
├── agent/              # Busca semântica e RAG com LangChain
├── frontend/           # Painel de controle web para monitoramento
├── docker/             # Dockerfiles de infraestrutura
├── config/             # Configurações dinâmicas via Pydantic Settings
├── shared/             # Gerenciamento de Cache Redis e logs
├── tests/              # Testes unitários com pytest
└── docker-compose.yml  # Orquestração do banco, redis, API e coletor
```

---

## 🚀 Instalação e Execução

### 1. Requisitos Mínimos
* Linux (Ubuntu 20.04+ / Debian) ou macOS/Windows com suporte a Docker.
* Docker e Docker Compose v2 instalados.
* Python 3.12 (opcional para desenvolvimento local).

### 2. Configurar Variáveis de Ambiente
Copie o arquivo `.env.example` e crie a sua configuração:
```bash
cp .env.example .env
```

### 3. Subir com Docker Compose
O comando abaixo baixa as imagens, compila e inicia todos os serviços (PostgreSQL, Redis, Coletor e API FastAPI):
```bash
docker compose up -d --build
```

### 4. Verificar Status
```bash
docker compose logs -f api
docker compose logs -f collector
```

---

## 🔗 Endpoints Principais da API

Após inicializado, a API estará acessível em `http://localhost:8000`.

| Rota | Método | Descrição |
| :--- | :--- | :--- |
| `/status` | `GET` | Status de integridade do coletor, PostgreSQL e Redis |
| `/dados-atuais` | `GET` | Últimos dados e notícias acadêmicas raspadas |
| `/historico` | `GET` | Histórico paginado dos dados coletados |
| `/agente/perguntar` | `POST` | Pergunta ao agente de IA RAG sobre as notícias da UNESP |

---

## 🤝 Integração com o Projeto MINA
A assistente virtual **MINA** faz requisições periódicas para o endpoint `/dados-atuais` desta API e sincroniza os dados recebidos com o banco de dados SQLite interno local da TV Box/Orange Pi, mantendo a assistente atualizada mesmo rodando de forma 100% offline posterior.
