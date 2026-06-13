import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
WDI_PATH = "cleaned_data/wdi_cleaned.csv"
NEWS_PATH = "cleaned_data/news_cleaned.csv"
CHROMA_PATH = "chroma_db"

def load_wdi_data():
    """
    Loads the cleaned WDI data into a Pandas DataFrame.
    Returns:
        pd.DataFrame: DataFrame containing WDI data.
    """
    if not os.path.exists(WDI_PATH):
        raise FileNotFoundError(f"WDI file not found at {WDI_PATH}")
    
    df = pd.read_csv(WDI_PATH)
    print(f"Loaded {len(df)} WDI records.")
    return df

def create_news_vector_store():
    """
    Loads cleaned news data, creates document objects, and initializes/updates the ChromaDB vector store.
    """
    if not os.path.exists(NEWS_PATH):
        raise FileNotFoundError(f"News file not found at {NEWS_PATH}")

    print("Loading news data...")
    df = pd.read_csv(NEWS_PATH)
    
    # Take top 2000 rows for initial verification and development
    # (Assuming user wants quick feedback loops before full scale)
    print("Sampling top 50 news events for verification (Free Tier Limit)...")
    df = df.head(50)
    
    # Create a comprehensive text representation for embedding
    # We combine actors, event codes, and location to give the model context.
    df['page_content'] = (
        "Event: " + df['EventCode'].astype(str) + 
        " | Actors: " + df['Actor1Name'].fillna('') + ", " + df['Actor2Name'].fillna('') +
        " | Location: " + df['ActionGeo_FullName'].fillna('') +
        " | Source: " + df['SOURCEURL'].fillna('')
    )
    
    # Clean up NaN in metadata columns
    df['Year'] = df['Year'].fillna(0).astype(int)
    df['ActionGeo_CountryCode'] = df['ActionGeo_CountryCode'].fillna('Unknown')

    # Load into LangChain Documents
    loader = DataFrameLoader(df, page_content_column="page_content")
    documents = loader.load()

    # Add extra metadata explicitly if needed (DataFrameLoader does most of it)
    # Ensure Year is an integer for filtering
    for doc in documents:
        doc.metadata['year'] = int(doc.metadata['Year'])
        doc.metadata['country_code'] = doc.metadata['ActionGeo_CountryCode']
        # Remove raw dataframe columns from metadata to save space.

    print(f"Created {len(documents)} documents. Initializing Vector Store...")

    # Initialize Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    # Create/Update ChromaDB
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    
    print(f"Vector Store successfully created at {CHROMA_PATH}")
    return vectorstore

if __name__ == "__main__":
    # Test the functions
    try:
        wdi_df = load_wdi_data()
        vector_store = create_news_vector_store()
    except Exception as e:
        print(f"Error: {e}")
