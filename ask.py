import argparse
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from langchain_community.document_loaders import PyPDFDirectoryLoader
from localEmbedding import localEmbedding
import fitz  # PyMuPDF

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    response, sources = query_rag(query_text)
    for source in sources:
        pdfShow(source)


def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = localEmbedding()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model = Ollama(model="mistral")
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return response_text, sources


def pdfShow(inputPath):
    if inputPath is None:
        return

    # Split the path and page info
    inputPath = inputPath.split(':')[0]

    output_pdf = "output.pdf"

    # Open the PDF document
    doc = fitz.open(inputPath)
    output_doc = fitz.open()

    # Initialize a flag to check if any pages are added
    pages_added = False

    # Iterate through each page
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")

        # Check for the keywords in the page text
        if "Figure" in text or "Table" in text or "Image" in text:
            output_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
            pages_added = True

    # Save the result if any pages were added
    if pages_added:
        output_doc.save(output_pdf)
        print(f"Saved extracted pages to {output_pdf}")
    else:
        print("No pages with 'Figure', 'Table', or 'Image' found.")

    output_doc.close()
    doc.close()


if __name__ == "__main__":
    main()
    

# author: Umit-Yilmaz
