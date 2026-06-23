import os

from utils.pdf_loader import load_pdf
from utils.vector_store import store_document

folder_path = "data"

for file in os.listdir(folder_path):

    if file.endswith(".pdf"):

        pdf_path = os.path.join(folder_path, file)

        print(f"Processing {file}...")

        text = load_pdf(pdf_path)

        source_name = file.replace(".pdf", "")

        store_document(
            text,
            source_name
        )

print("All documents stored successfully!")