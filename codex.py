#main code file -Bi
import fitz
import json
import argparse
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
#pymupdf/fitz
def extract_text_blocks(pdf_path):
    doc = fitz.open(pdf_path)
    blocks = []
    for page_num, page in enumerate(doc):
        for block in page.get_text("dict")["blocks"]:
            if block["type"] == 0:  # text block
                for line in block["lines"]:
                    line_text = " ".join([span["text"] for span in line["spans"]]).strip()
                    if not line_text:
                        continue
                    font_sizes = [span["size"] for span in line["spans"]]
                    font_names = [span["font"] for span in line["spans"]]
                    is_bold = any("Bold" in fn for fn in font_names)
                    avg_font = sum(font_sizes) / len(font_sizes)
                    blocks.append({
                        "text": line_text,
                        "font_size": avg_font,
                        "bold": int(is_bold),
                        "y": line["bbox"][1],
                        "page": page_num
                    })
    return blocks

#title detection
def detect_title(blocks):
    page0_blocks = [b for b in blocks if b["page"] == 0]
    sorted_blocks = sorted(page0_blocks, key=lambda b: (-b["font_size"], b["y"]))
    return sorted_blocks[0]["text"] if sorted_blocks else None

#ML model
def prepare_features(blocks):
    return np.array([[b["font_size"], b["bold"], b["y"]] for b in blocks])

def train_heading_model(blocks, labels):
    X = prepare_features(blocks)
    le = LabelEncoder()
    y = le.fit_transform(labels)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    return clf, le

def predict_headings(clf, le, blocks):
    X = prepare_features(blocks)
    preds = clf.predict(X)
    labels = le.inverse_transform(preds)
    for i, label in enumerate(labels):
        blocks[i]["heading"] = label
    return blocks

#outline
def build_outline(blocks):
    level_map = {"H1": 1, "H2": 2, "H3": 3}
    outline = []
    for block in blocks:
        level = level_map.get(block.get("heading"))
        if level:
            outline.append({
                "title": block["text"],
                "level": f"H{level}",
                "page": block["page"]
            })
    return outline

#JSON
def export_json(pdf_path, title, outline, output_path):
    data = {
        "file": os.path.basename(pdf_path),
        "title": title,
        "outline": outline
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

#Batch pipeline
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_csv", default="training_labels.csv")
    parser.add_argument("--input_dir", default="input")
    parser.add_argument("--output_dir", default="output")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    df = pd.read_csv(args.train_csv)
    blocks = df.to_dict(orient="records")
    labels = df["label"].tolist()
    clf, le = train_heading_model(blocks, labels)

    for filename in os.listdir(args.input_dir):
        if filename.endswith(".pdf"):
            input_path = os.path.join(args.input_dir, filename)
            output_path = os.path.join(args.output_dir, filename.replace(".pdf", ".json"))
            test_blocks = extract_text_blocks(input_path)
            title = detect_title(test_blocks)
            labeled_blocks = predict_headings(clf, le, test_blocks)
            outline = build_outline(labeled_blocks)
            export_json(input_path, title, outline, output_path)
