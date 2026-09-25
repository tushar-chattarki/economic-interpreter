# 🌍 Economic Interpreter

> **Turning economic data into understandable stories using Retrieval-Augmented Generation (RAG).**

Economic Interpreter is a Generative AI application that connects **economic indicators** with **historical news events** to help explain *why* an economic metric changed.

Instead of looking at an isolated number such as GDP growth, inflation, or another World Development Indicator, the system combines the numerical trend with relevant historical events and uses an LLM to generate a simple, context-aware explanation.

The application provides an interactive **Streamlit dashboard** where users can select a country, economic indicator, and year, visualize its historical trend, and generate an AI-powered explanation for a particular change.

---

## ✨ Features

* 📊 **Interactive economic data visualization**

  * Explore World Bank World Development Indicators (WDI)
  * Select countries and economic indicators
  * View historical trends using interactive Plotly charts

* 📰 **Historical news retrieval**

  * Uses processed GDELT event/news data
  * Retrieves news relevant to the selected country and year

* 🔎 **Metadata-aware RAG retrieval**

  * Filters retrieved documents using **country code and year**
  * Performs semantic similarity search within the relevant subset

* 🧠 **AI-generated economic explanations**

  * Uses Google's **Gemini 2.5 Flash**
  * Combines economic data with retrieved news context
  * Produces explanations designed for a general audience

* 🛡️ **Grounded generation**

  * The LLM receives the actual economic change and retrieved historical context
  * The prompt instructs the model to avoid unsupported causal claims when relevant news evidence is unavailable

* ⚡ **Resilient API handling**

  * Includes retry logic with exponential backoff for rate-limit/API failures

---

## 🏗️ System Architecture

```text
                 ┌─────────────────────────┐
                 │   World Bank WDI Data   │
                 │  Economic Indicators    │
                 └────────────┬────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   Data Processing │
                    │     processor.py │
                    └────────┬─────────┘
                             │
                             │
                             │
       ┌─────────────────────┴─────────────────────┐
       │                                           │
       ▼                                           ▼
┌─────────────────┐                       ┌──────────────────┐
│ Economic Trends │                       │ GDELT News Data  │
│ Country / Year  │                       │ Historical Events│
└────────┬────────┘                       └────────┬─────────┘
         │                                         │
         │                                         ▼
         │                               ┌──────────────────┐
         │                               │ Gemini Embeddings│
         │                               └────────┬─────────┘
         │                                        │
         │                                        ▼
         │                               ┌──────────────────┐
         │                               │    ChromaDB      │
         │                               │   Vector Store   │
         │                               └────────┬─────────┘
         │                                        │
         └────────────────┐                       │
                          ▼                       ▼
                   ┌─────────────────────────────────┐
                   │       Retrieval Layer           │
                   │ Country + Year + Similarity     │
                   └────────────────┬────────────────┘
                                    │
                                    ▼
                          ┌────────────────────┐
                          │ Gemini 2.5 Flash   │
                          │ Generation Layer    │
                          └─────────┬──────────┘
                                    │
                                    ▼
                          ┌────────────────────┐
                          │ Streamlit Dashboard│
                          │ Economic Narrative │
                          └────────────────────┘
```

---

## 🔄 How It Works

### 1. Select an economic indicator

The user selects:

* Country
* Economic indicator
* Year

The application loads the corresponding WDI time series and calculates/displays the relevant year-over-year change.

### 2. Visualize the economic trend

The selected indicator is displayed as an interactive Plotly line chart, allowing the user to understand the broader trend before requesting an explanation.

### 3. Retrieve relevant historical events

When the user clicks **"Explain this Shift"**, the system constructs a retrieval query based on the selected country, year, and indicator.

The custom retriever first applies metadata filters for:

```text
Year
Country Code
```

Only documents satisfying those constraints are considered for semantic similarity retrieval.

### 4. Semantic retrieval with ChromaDB

Relevant GDELT-derived documents are stored in ChromaDB using Google's `gemini-embedding-001` embedding model.

The retriever returns the top relevant documents from the filtered dataset.

### 5. Generate the explanation

The retrieved news context and economic data are passed into a LangChain prompt.

The application uses:

```text
Gemini 2.5 Flash
```

to generate a human-readable explanation of the economic shift.

The prompt explicitly asks the model to distinguish between relevant evidence and situations where the available news does not provide a clear explanation.

---

## 🧠 RAG Pipeline

The core RAG pipeline consists of four stages:

### Retrieval

```text
User Selection
     ↓
Country + Year + Indicator
     ↓
Construct Retrieval Query
     ↓
Filter ChromaDB by Country + Year
     ↓
Semantic Similarity Search
     ↓
Top-k Relevant Documents
```

### Generation

```text
Economic Data
     +
Retrieved News Context
     ↓
Prompt Template
     ↓
Gemini 2.5 Flash
     ↓
Economic Explanation
```

The retriever currently returns up to **5 relevant documents** for the selected country and year.

---

## 🛠️ Tech Stack

| Category        | Technologies             |
| --------------- | ------------------------ |
| Language        | Python                   |
| Frontend        | Streamlit                |
| Data Processing | Pandas                   |
| Visualization   | Plotly                   |
| RAG Framework   | LangChain                |
| Vector Database | ChromaDB                 |
| Embeddings      | Google Gemini Embeddings |
| LLM             | Google Gemini 2.5 Flash  |
| Economic Data   | World Bank WDI           |
| News/Event Data | GDELT                    |
| Configuration   | python-dotenv            |

---

## 📁 Project Structure

```text
economic-interpreter/
│
├── app.py                     # Streamlit application
├── processor.py               # Data processing and vector-store creation
├── retriever_logic.py         # Custom ChromaDB retrieval logic
├── interpreter_chain.py        # LangChain + Gemini generation pipeline
│
├── preprocess_gdelt.py        # GDELT preprocessing
├── gen_ai_preprocessing.ipynb # Data preprocessing notebook
│
├── inspect_vectorstore.py     # Vector database inspection utility
├── debug_retrieval.py         # Retrieval debugging utility
├── debug_models.py            # Model debugging utility
│
├── DataSet/                   # Dataset files
├── cleaned_data/              # Processed datasets
├── chroma_db/                 # Persisted ChromaDB vector store
│
├── requirements.txt           # Python dependencies
├── project_context.md         # Detailed project architecture/context
├── run_app.bat                # Windows application launcher
└── .gitignore
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/tushar-chattarki/economic-interpreter.git
cd economic-interpreter
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key
```

The application uses the Google API for Gemini generation and embeddings.

**Never commit your API key to GitHub.**

---

## ▶️ Running the Application

Start the Streamlit application with:

```bash
streamlit run app.py
```

The application will open in your browser.

### Windows

You can also use:

```text
run_app.bat
```

---

## 📊 Example Workflow

Suppose the user selects:

```text
Country: Japan
Indicator: GDP Growth
Year: 2020
```

The application:

1. Loads the corresponding economic time series.
2. Displays the historical GDP trend.
3. Calculates the selected year's change.
4. Builds a context-specific retrieval query.
5. Filters the news vector store by Japan and 2020.
6. Retrieves the most relevant historical events.
7. Passes the economic change and retrieved context to Gemini.
8. Generates a human-readable explanation.

The goal is not to simply answer **"what happened?"**, but to provide useful historical context around **"what might explain this change?"**

---

## 🧩 Key Implementation Details

### Metadata-Constrained Retrieval

A key part of the system is the use of deterministic metadata filtering before semantic retrieval.

The retriever applies constraints such as:

```text
year = selected year
country_code = selected country
```

This reduces the chance of retrieving semantically similar but historically or geographically unrelated events.

### Gemini Embeddings

News/event documents are embedded using:

```text
gemini-embedding-001
```

and persisted in ChromaDB.

### Gemini Generation

The final narrative is generated using:

```text
gemini-2.5-flash
```

with a low temperature configuration to keep the generated explanations relatively consistent and grounded in the supplied context.

### Retry Handling

The generation pipeline includes retry logic with exponential backoff for temporary API/rate-limit failures.

---

## ⚠️ Current Limitations

* The project currently operates primarily as a **local application**.
* News retrieval depends on the available historical GDELT dataset.
* The quality of the generated explanation depends on the quality and coverage of the retrieved news context.
* The system identifies plausible relationships between economic changes and historical events; it should **not be interpreted as establishing definitive economic causality**.
* The current preprocessing/vectorization workflow contains development-oriented limitations and is not optimized for production-scale ingestion.
* A valid Google API key is required for Gemini embeddings and generation.

---

## 🚀 Future Improvements

Potential extensions include:

* 🔄 Real-time news ingestion
* 🤖 Multi-agent economic analysis
* 🔍 Multi-query retrieval and query expansion
* 🌐 Multilingual explanations
* ☁️ Cloud deployment
* 🐳 Docker-based deployment
* 📈 More advanced economic indicators and analytics
* 🧠 Improved retrieval and reranking
* 💬 Conversational follow-up questions
* 📚 Larger and continuously updated news corpora

---

## 🎯 Project Objective

Economic data is often easy to find but difficult to understand in context.

Economic Interpreter aims to bridge that gap by combining:

```text
Economic Data
      +
Historical Events
      +
Vector Retrieval
      +
Generative AI
      ↓
Understandable Economic Narratives
```

The project demonstrates how **Retrieval-Augmented Generation can be applied beyond conventional document question-answering**, using structured economic data and unstructured historical events to create contextual explanations.

---

## 👥 Project

This was developed as a **team project**.

Contributions include data processing, RAG pipeline development, retrieval logic, LLM integration, and Streamlit application development.

---

## 📄 License

This project currently does not specify an open-source license.

If you intend to distribute or reuse the project publicly, consider adding an appropriate license to the repository.
