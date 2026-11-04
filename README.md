# Chatbot para o Ensino de Programação em Python

<br>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React">
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/FAISS-00599C?style=for-the-badge&logoColor=white" alt="FAISS">
  <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
</p>

## Sobre o projeto

Este projeto foi desenvolvido como parte de um Trabalho de Conclusão de Curso (TCC) de Bacharelado em Sistemas de Informação da UniRios, intitulado **"Adaptação contextual de respostas baseada em análise de sentimento em um chatbot voltado ao ensino de programação em Python: uma avaliação da qualidade conversacional"**.

A pesquisa investiga os efeitos da adaptação contextual de respostas, baseada em análise de sentimento, sobre a qualidade conversacional de um chatbot destinado ao ensino de programação em Python. Para isso, propõe-se um sistema conversacional híbrido, fundamentado em regras e técnicas de recuperação de informações, capaz de responder a dúvidas relacionadas aos conceitos básicos da linguagem.

Diferentemente de sistemas baseados exclusivamente na geração de texto, o chatbot utiliza um banco de respostas previamente estruturado, com o objetivo de fornecer respostas fundamentadas em conteúdos selecionados e reduzir a ocorrência de informações não verificáveis.

O sistema permite comparar duas condições de interação:

- **Versão A - Modo base:** utiliza mecanismos de recuperação e reordenação de respostas candidatas.
- **Versão B - Modo adaptativo:** utiliza os mesmos mecanismos da versão base, acrescentando uma apresentação contextual orientada pela análise de sentimento da mensagem do usuário.

A adaptação atua na forma de apresentação da resposta, sem modificar a seleção do conteúdo técnico recuperado.

## Objetivo

O objetivo da pesquisa foi analisar os efeitos da adaptação contextual de respostas baseada em análise de sentimento sobre a qualidade conversacional de um chatbot voltado ao ensino de programação em Python.

## Funcionalidades

- Interface web para interação com o chatbot.
- Operação entre as versões base e adaptativa do chatbot.
- Recuperação de respostas relacionadas aos conceitos básicos de Python.
- Processamento e normalização das mensagens enviadas pelos usuários.
- Identificação de perguntas fora do escopo do sistema.
- Recuperação de respostas candidatas por meio de busca vetorial.
- Reordenação das respostas recuperadas por mecanismos de reranking.
- Análise de sentimento das mensagens na versão adaptativa.
- Adaptação contextual da apresentação das respostas.
- Registro das sessões e interações em banco de dados PostgreSQL.
- Apresentação de respostas com exemplos de código e referências à documentação oficial do Python.
- Encerramento de sessões e apresentação de informações sobre sua duração.

## Interface do sistema

As capturas de tela a seguir apresentam os principais elementos da interface e o funcionamento do chatbot, contemplando as duas condições de interação avaliadas no estudo: **Versão A (modo base)** e **Versão B (modo adaptativo)**.

### Tela inicial
<br>

<p align="center">
<img src="https://github.com/user-attachments/assets/97242b30-e0ed-43b1-b9fc-2fdddf42d7a5" alt="Tela inicial do chatbot na versão A" width="850">
</p>

<p align="center">
  <strong>Versão A - Modo base</strong>
</p>

<p align="center">
<img src="https://github.com/user-attachments/assets/5d845689-6a7c-4cd8-9ba1-acae0aed235d" alt="Tela inicial do chatbot na versão B" width="850">
</p>

<p align="center">
  <strong>Versão B - Modo adaptativo</strong>
</p>

### Interação com o chatbot
<br>

<p align="center">
<img src="https://github.com/user-attachments/assets/6aa81501-3e28-40e0-9dda-03e550d50e3b" alt="Interação com o chatbot na versão A" width="850">
</p>

<p align="center">
  <strong>Versão A - Modo base</strong>
</p>

<p align="center">
<img src="https://github.com/user-attachments/assets/3c5c9378-8b00-41fc-af67-39817253cad9" alt="Interação com o chatbot na versão B" width="850">
</p>

<p align="center">
  <strong>Versão B - Modo adaptativo</strong>
</p>

### Apresentação das respostas
<br>

<p align="center">
<img src="https://github.com/user-attachments/assets/084e312e-3c73-4b58-81f9-cbf06aaaaa6f" alt="Resposta apresentada pelo chatbot na versão A" width="850">
</p>

<p align="center">
  <strong>Versão A - Modo base</strong>
</p>

<p align="center">
<img src="https://github.com/user-attachments/assets/ab3fc3a1-1823-4032-a938-f320ed89c232" alt="Resposta apresentada pelo chatbot na versão B" width="850">
</p>

<p align="center">
  <strong>Versão B - Modo adaptativo</strong>
</p>

### Encerramento da sessão
<br>

<p align="center">
<img src="https://github.com/user-attachments/assets/3eb3bb7e-a5bd-44a5-87f8-086cfc2e5a51" alt="Encerramento da sessão na versão A" width="850">
</p>

<p align="center">
  <strong>Versão A - Modo base</strong>
</p>

<p align="center">
<img src="https://github.com/user-attachments/assets/da832f4a-f5d7-4e22-aff6-07353de4c00f" alt="Encerramento da sessão na versão B" width="850">
</p>

<p align="center">
  <strong>Versão B - Modo adaptativo</strong>
</p>

## Arquitetura e tecnologias

O projeto está organizado em três componentes principais: frontend, backend e armazenamento de dados.

| Componente                 | Tecnologias                   | Responsabilidade                                              |
| -------------------------- | ----------------------------- | ------------------------------------------------------------- |
| Frontend                   | React, Vite e JavaScript      | Interface e interação com o usuário.                          |
| Backend                    | Python e FastAPI              | Processamento das mensagens e disponibilização da API.        |
| Recuperação de informações | Sentence Transformers e FAISS | Representação vetorial e recuperação de respostas candidatas. |
| Análise de sentimento      | Transformers e XLM-RoBERTa    | Classificação das mensagens na versão adaptativa.             |
| Banco de dados             | PostgreSQL e Psycopg          | Persistência das sessões e interações.                        |

### Frontend

Responsável pela interface de interação com o usuário e pela comunicação com a API do chatbot.

Principais tecnologias e bibliotecas:

- **React:** construção da interface.
- **Vite:** ambiente de desenvolvimento e ferramenta de build.
- **JavaScript:** implementação da lógica da aplicação.
- **Axios:** comunicação HTTP com o backend.
- **React Markdown:** renderização de respostas em Markdown.

### Backend

Responsável pelo processamento das mensagens, gerenciamento das sessões, recuperação de respostas e aplicação da adaptação contextual.

Principais tecnologias e bibliotecas:

- **Python:** linguagem principal do backend.
- **FastAPI:** construção da API REST.
- **Uvicorn:** servidor ASGI.
- **Sentence Transformers:** geração de representações vetoriais.
- **FAISS:** recuperação de respostas por similaridade vetorial.
- **Rank BM25:** suporte à recuperação e ordenação lexical.
- **Transformers:** utilização de modelos pré-treinados.
- **Psycopg:** comunicação com o banco de dados PostgreSQL.
- **Python-dotenv:** carregamento de variáveis de ambiente.

### Banco de dados

O PostgreSQL é utilizado para armazenar informações relacionadas às sessões e às interações realizadas durante o uso do chatbot.
Esse armazenamento permite registrar informações necessárias ao gerenciamento das sessões e à posterior análise dos dados coletados.

### Fluxo de processamento

De maneira geral, o processamento de uma mensagem segue as seguintes etapas:

1. Recebimento da mensagem enviada pelo usuário.
2. Aplicação de regras de processamento e verificação de escopo.
3. Normalização da pergunta.
4. Recuperação de respostas candidatas utilizando busca vetorial.
5. Reordenação das respostas recuperadas.
6. Seleção da resposta mais adequada.
7. Aplicação da apresentação contextual, quando utilizada a versão adaptativa.
8. Retorno da resposta ao frontend.
9. Registro da interação no banco de dados.

Na versão adaptativa, a análise de sentimento orienta a apresentação contextual da resposta, preservando o conteúdo técnico selecionado pelo mecanismo de recuperação.

## Modelos e mecanismos utilizados

### Recuperação de respostas

O sistema utiliza representações vetoriais para identificar perguntas semanticamente semelhantes às mensagens enviadas pelos usuários.
O modelo de embeddings utilizado é:
`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

A busca vetorial é realizada por meio do FAISS, permitindo recuperar respostas candidatas com base na similaridade entre as representações das perguntas.
O processo também utiliza mecanismos de reranking para refinar a ordenação dos resultados recuperados.

### Análise de sentimento

Na versão adaptativa, é utilizado o modelo:
`cardiffnlp/twitter-xlm-roberta-base-sentiment`

O modelo classifica as mensagens em três categorias:

- Positivo.
- Neutro.
- Negativo.

A classificação é utilizada como referência para as regras de adaptação contextual, responsáveis por ajustar a apresentação da resposta ao contexto identificado na mensagem.
É importante destacar que a classificação representa uma estimativa produzida pelo modelo, não uma confirmação do estado emocional real do usuário.

## Estrutura do projeto

A organização principal do repositório está distribuída da seguinte maneira:

```text
TCC_Chatbot/
│
├── backend/
│   ├── requirements.txt
│   └── src/
│       ├── api/
│       ├── database/
│       ├── models/
│       │   ├── embeddings/
│       │   ├── sentiment/
│       │   └── translation/
│       ├── modes/
│       ├── preprocessing/
│       ├── reranking/
│       ├── retrieval/
│       ├── rules/
│       └── session/
│
├── data/
│   └── analysis/
│       ├── metrics/
│       ├── preparation/
│       ├── raw/
│       └── statistics/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── services/
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── notebooks/
│   ├── 01_filtragem_datasets.ipynb
│   ├── 02_limpeza_padronizacao_datasets.ipynb
│   ├── 03_criacao_dataset.ipynb
│   ├── 04_curadoria_datasets.ipynb
│   ├── 05_concatenacao_datasets.ipynb
│   ├── 06_geracao_embeddings.ipynb
│   ├── 07_banco_PostgreSQL.ipynb
│   └── 08_FAISS.ipynb
│
└── .gitignore
```

**Observação:** arquivos e diretórios gerados durante o processamento dos dados, como determinados arquivos `.parquet` e índices `.index`, não são necessariamente versionados no repositório, conforme as regras do `.gitignore`.

## Requisitos

Para executar o projeto localmente, são necessários:

- Python instalado.
- Node.js e npm.
- PostgreSQL.
- Git.
- Arquivos de dados e recursos necessários ao mecanismo de recuperação.
- Conexão com a internet para o eventual download de modelos pré-treinados.

## Instalação e execução

As instruções a seguir consideram a execução local do projeto, a partir do diretório raiz do repositório.

### 1. Clonar o repositório

```bash
git clone https://github.com/Vinilves/TCC_Chatbot.git
```

Acessar o diretório:

```bash
cd TCC_Chatbot
```

### 2. Configurar o backend

Criar um ambiente virtual Python:

```bash
python -m venv .venv
```

Ativar o ambiente virtual no Windows:

```bash
.venv\Scripts\activate
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

Instalar as dependências:

```bash
pip install -r backend/requirements.txt
```

### 3. Configurar as variáveis de ambiente

O backend utiliza a variável `DATABASE_URL` para estabelecer a conexão com o PostgreSQL.

Crie um arquivo `.env` dentro do diretório `backend/`:

```text
backend/
└── .env
```

Adicione a string de conexão do banco de dados:

```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco
```

Substitua os valores de exemplo pelas credenciais e informações correspondentes à sua instalação do PostgreSQL.

**Importante:** não compartilhe ou versione arquivos `.env` contendo credenciais reais.

### 4. Executar o backend

A partir do diretório raiz do projeto, execute:

```bash
uvicorn backend.src.api.app:app --reload
```

A API estará disponível em:

```text
http://127.0.0.1:8000
```

A documentação interativa da API pode ser acessada em:

```text
http://127.0.0.1:8000/docs
```

### 5. Configurar o frontend

Em outro terminal, acesse o diretório do frontend:

```bash
cd frontend
```

Instale as dependências:

```bash
npm install
```

### 6. Executar o frontend

Inicie o servidor de desenvolvimento:

```bash
npm run dev
```

Por padrão, a interface estará disponível em:

```text
http://localhost:5173
```

Com o backend e o frontend em execução, a interface poderá realizar as requisições à API local.

**Atenção:** a execução completa também depende da configuração do PostgreSQL e da disponibilidade dos arquivos de dados, embeddings e índices necessários à recuperação das respostas. Esses recursos devem ser preparados conforme o fluxo de processamento documentado nos notebooks do projeto.

## API

A comunicação entre frontend e backend é realizada por meio de uma API REST desenvolvida com FastAPI.

Entre as principais rotas disponíveis estão:

| Método | Endpoint                         | Descrição                                 |
| ------ | -------------------------------- | ----------------------------------------- |
| `GET`  | `/api/health`                    | Verifica a disponibilidade da API.        |
| `POST` | `/api/sessions`                  | Inicia uma sessão de interação.           |
| `POST` | `/api/chat/messages`             | Processa uma mensagem enviada ao chatbot. |
| `POST` | `/api/sessions/{session_id}/end` | Encerra uma sessão.                       |

A documentação completa dos endpoints pode ser consultada por meio do Swagger UI, disponibilizado pelo FastAPI em `/docs`.

## Processamento e preparação dos dados

O projeto também contempla notebooks destinados à preparação dos dados utilizados na construção do banco de respostas candidatas.

Esses notebooks organizam etapas como:

- Filtragem de conjuntos de dados.
- Limpeza e padronização.
- Construção e curadoria do conjunto de dados.
- Concatenação das fontes selecionadas.
- Geração de embeddings.
- Preparação do banco de dados PostgreSQL.
- Construção do índice de busca vetorial FAISS.

Os notebooks estão disponíveis no diretório `notebooks/`.

## Avaliação experimental

A avaliação do chatbot foi conduzida por meio de um estudo experimental, com comparação entre duas condições de interação: modo base (A) e modo adaptativo (B).

Participaram do estudo **20 participantes**, cada um utilizando ambas as versões do sistema, totalizando **114 interações**, distribuídas igualmente entre as condições.

A avaliação combinou duas abordagens complementares:

- **Métricas automáticas:** BERTScore F1, similaridade por cosseno, TTR, Distinct-2 e Distinct-3, utilizadas para analisar aspectos semânticos e de diversidade lexical das respostas.
- **Questionário de percepção:** instrumento composto por cinco itens em escala Likert, respondidos separadamente para as versões A e B, com o objetivo de avaliar a percepção dos participantes sobre a qualidade das interações.

Os resultados completos, incluindo as análises estatísticas, interpretações e discussões, são apresentados no Trabalho de Conclusão de Curso que originou este projeto.

## Autor

**Vinícius Alves Ferreira dos Santos**

Bacharelado em Sistemas de Informação - UniRios.

Trabalho de Conclusão de Curso orientado pelo **Prof. Esp. José Anchieta dos Santos Júnior**.

## Licença

Este projeto foi desenvolvido para fins acadêmicos e de pesquisa.
