from langchain_community.document_loaders import PyPDFLoader

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts all text from a PDF using LangChain's PyPDFLoader."""
    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        return " ".join([d.page_content for d in docs])
    except Exception as e:
        print(f"[parsers] PDF parse error: {e}")
        return ""
