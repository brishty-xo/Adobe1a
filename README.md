# Adobe India Hackathon: Challenge 1A

This repository focuses on solving the challenge 1A in said hackathon

## Objective

The main objective of the project was to extract the Document title, Heading structure (From H1 upto H3) from a given input file and output a JSON file representing said hierarchy. 
The constraints as suggested were to keep the model lightweight, offline, fast and dockerized.

## Architecture

The architecture overview can be given as:

```bash
PDF → [Extract Blocks] → [Font/Position Features] → [ML Model] → [Label H1/H2/...]
    → [Hierarchy Builder] → JSON Output
```

## Models/Libaries

* `PyMuPDF (fitz)` : Python Library focusing on pdf parsing and font extraction
* `scikit-learn` : Heading classification Model/ Random Forest Classifier
* `Pandas` : CSV and dataframe operations
* `numpy` : Library for Array and number operations
* `joblib` : To save/load model (optional)

## Approach

**1. Text Block Extraction:**
The PDF is parsed using PyMuPDF, extracting line-level text along with visual layout features such as font size, font style (e.g., bold), Y-position on the page, and page number. These features form the basis for heading classification.

**2. Title Detection (Heuristic):**
The document title is inferred from the first page by selecting the text block with the largest font size near the top. This simple heuristic reliably captures the main title without the need for model-based prediction.

**3. Heading Classification:**
A lightweight RandomForestClassifier is trained on labeled examples using layout features (font_size, bold, y). It classifies each line as Title, H1, H2, H3, or plain Text. The model is small, efficient, and suitable for offline use.

**4. Hierarchy Construction:**
Using predicted heading levels, a structured outline is built using a stack-based approach. Higher-level headings nest lower-level ones, forming a hierarchical JSON tree that mirrors the document’s logical structure.

**5. Offline Dockerized Execution:**
The entire pipeline, including model, code, and dependencies, is containerized in a Docker image using pre-downloaded wheels. It runs fully offline, meets the <200MB size constraint, and executes within 10 seconds for ~50-page PDFs.

## How to Build and Run

*For documentation purposes only*

These steps can be followed to build and run the solution completely offline using Docker:

1. To Load Docker Image (Offline)

Since working offline, first load the prebuilt image:

``` bash

docker load -i base.tar

```
This loads the Docker image containing all dependencies, wheels, and code.

2. Build the Docker Image

``` bash

docker build -t heading-extractor .

```

We have all .whl files in a wheels/ directory and the correct requirements.txt.


3. To Run the Container:

``` bash

docker run --rm -v "%cd%":/app heading-extractor \
  

```



## Expected Output Format
The output JSON includes:

The document title

A hierarchical outline of headings (H1, H2, etc.)

Example:

```json

{
  "file": "file01.pdf",
  "title": "Document Title",
  "outline": [
    {
      "title": "Introduction",
      "level": 1,
      "page": 0,
      "children": [
        {
          "title": "Background",
          "level": 2,
          "page": 0,
          "children": []
        }
      ]
    }
  ]
}
```
