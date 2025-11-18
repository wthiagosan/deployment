# 📦 API RESTful CRUD de Produtos
## Serviço de Gerenciamento de Estoque e Catálogo

Esta API foi desenvolvida para oferecer um conjunto completo de operações **CRUD (Create, Read, Update, Delete)** sobre a entidade `Produto`. Construída para ser rápida, assíncrona e facilmente portável através de contêineres Docker.

---

## 🛠️ Stack Tecnológica

| Componente | Tecnologia | Detalhe |
| :--- | :--- | :--- |
| **Linguagem** | Python 3.11 | |
| **Framework** | **FastAPI** | Framework assíncrono para alto desempenho (ASGI). |
| **Banco de Dados** | **MongoDB** (Async driver `motor`) | Banco de dados NoSQL para persistência de dados. |
| **Servidor** | **Uvicorn** | Servidor ASGI utilizado para rodar a aplicação. |
| **Conteinerização** | **Docker** | Uso de contêiner para garantir ambiente de execução consistente. |

---

## ⚙️ Configuração Local

Para rodar o projeto localmente, você precisará ter o Docker instalado e configurar as variáveis de ambiente.

### 1. Pré-requisitos
* Docker
* String de Conexão com o MongoDB (Local ou Atlas).

### 2. Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto, baseado no [.env.example], e preencha-o. Este arquivo é crucial para a API conectar ao banco de dados e aplicar a segurança.

| Variável | Descrição | Exemplo |
| :--- | :--- | :--- |
| `MONGO_URL` | URL de conexão com o cluster MongoDB. | `mongodb+srv://<user>:<password>@<cluster-url>/` |
| `DATABASE_NAME` | Nome do banco de dados a ser utilizado. | `lightsail_db` |
| `API_TOKEN` | Token de autenticação para operações protegidas. | `ChaveSecretaDoProjeto2025!XYZ123` |

### 3. Execução com Docker

Utilize o Docker para construir a imagem e iniciar o contêiner:

```bash
# 1. Construir a imagem
docker build -t api-produtos .

# 2. Rodar o container injetando as variáveis do arquivo .env
# A API estará acessível em http://localhost:8000
docker run -d -p 8000:8000 --env-file .env --name produtos-api api-produtos
