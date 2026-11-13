import requests
from pypdf import PdfReader
from io import BytesIO

url = "https://www.gtbit.ac.in/assets/pdf/academic-calender-25-26.pdf"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=60)
reader = PdfReader(BytesIO(response.content))

print("TOTAL PAGES:", len(reader.pages))

for i, page in enumerate(reader.pages, start=1):
    print(f"\nPAGE {i}")
    print("Extracted text:", len(page.extract_text() or ""))

    resources = page.get("/Resources")

    if resources:
        xobjects = resources.get("/XObject")

        if xobjects:
            xobjects = xobjects.get_object()
            print("Images found:", len(xobjects))
        else:
            print("Images found: 0")
    else:
        print("No resources found")
