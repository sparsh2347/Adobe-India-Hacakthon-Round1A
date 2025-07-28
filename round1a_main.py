import pdfplumber
import json
import os
from collections import defaultdict

# ----------- Group characters into words and lines -----------

def extract_clean_lines(page, x_tolerance=1.5, y_tolerance=3):
    chars = page.chars
    lines = defaultdict(list)

    for c in chars:
        key = round(c["top"] / y_tolerance) * y_tolerance
        lines[key].append(c)

    grouped_lines = []
    for _, line_chars in lines.items():
        line_chars = sorted(line_chars, key=lambda c: c["x0"])
        words = []
        current_word = [line_chars[0]]
        for prev, curr in zip(line_chars, line_chars[1:]):
            gap = curr["x0"] - prev["x1"]
            if gap <= x_tolerance:
                current_word.append(curr)
            else:
                words.append(current_word)
                current_word = [curr]
        words.append(current_word)

        line_words = []
        for word_chars in words:
            word_text = ''.join(c['text'] for c in word_chars)
            word_bbox = [
                word_chars[0]['x0'],
                min(c['top'] for c in word_chars),
                word_chars[-1]['x1'],
                max(c['bottom'] for c in word_chars)
            ]
            word_font = word_chars[0]['fontname']
            word_size = word_chars[0]['size']
            line_words.append({
                'text': word_text,
                'bbox': word_bbox,
                'fontname': word_font,
                'size': word_size
            })

        grouped_lines.append(line_words)

    return grouped_lines

def detect_font_properties(fontname):
    fontname = fontname.lower()
    is_bold = "bold" in fontname or "black" in fontname
    is_underlined = "underline" in fontname  # Some fonts may include this info
    weight = "bold" if "bold" in fontname else (
        "black" if "black" in fontname else (
            "light" if "light" in fontname else "normal"
        )
    )
    return is_bold, is_underlined, weight
def detect_alignment(x0, x_center, page_width):
    if 0.4 * page_width <= x_center <= 0.6 * page_width:
        return "center"
    elif x0 <= 0.05 * page_width:
        return "justified"  # near-left, full width
    elif x0 >= 0.1 * page_width:
        return "indented"
    else:
        return "left"

# ----------- Heading Level Heuristic -----------
def get_heading_level(font_size,base_size,max_font_size, is_bold, is_underlined, font_weight, alignment, top, page_height,x0,x1,page_width):
    score = 0

    # Special override rule: max font + center or padded = title
    left_padding = x0 >= 0.05 * page_width
    right_padding = x1 <= 0.95 * page_width
    top_padding = top >= 0.05 * page_height
    bottom_padding = top <= 0.95 * page_height

    if font_size == max_font_size and (alignment == "center" or (left_padding and right_padding and top_padding and bottom_padding)):
        return "title"

    # Font size weighting
    if font_size >= base_size + 8:
        score += 4
    elif font_size >= base_size + 5:
        score += 3
    elif font_size >= base_size + 3:
        score += 2
    elif font_size >= base_size + 1:
        score += 1

    # Bold text or heavy font weight
    if is_bold or font_weight in ("bold", "black", "heavy"):
        score += 1

    # Underlined text often indicates heading or section divider
    if is_underlined:
        score += 1

    # Alignment clues
    if alignment == "center":
        score += 1
    elif alignment == "left" and top <= 0.2 * page_height:
        score += 1  # Left-top alignment

    # Top-of-page likely to be title or heading
    if top <= 0.15 * page_height:
        score += 1

    # Final decision
    if score >= 5:
        return "title"
    elif score >= 4:
        return "h1"
    elif score >= 3:
        return "h2"
    elif score >= 2:
        return "h3"
    else:
        return "paragraph"

# ----------- Main Parsing Function -----------

def parse_layout(pdf_path):
    result = { "pages": [] }

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            page_width = page.width
            page_height = page.height

            lines = extract_clean_lines(page)
            font_sizes = [w['size'] for line in lines for w in line if w['size'] > 0]
            base_font_size = min(font_sizes) if font_sizes else 10
            max_font_size = max(font_sizes) if font_sizes else 10

            structure = []

            for line_words in lines:
                text = ' '.join(w['text'] for w in line_words)
                font_size = max(w['size'] for w in line_words)
                x0 = min(w['bbox'][0] for w in line_words)
                x1 = max(w['bbox'][2] for w in line_words)
                top = min(w['bbox'][1] for w in line_words)
                bottom = max(w['bbox'][3] for w in line_words)
                x_center = (x0 + x1) / 2

                is_bold, is_underlined, font_weight = detect_font_properties(" ".join(w["fontname"] for w in line_words))
                alignment = detect_alignment(x0, x_center, page_width)
                heading_level = get_heading_level(font_size, base_font_size,max_font_size, is_bold, is_underlined, font_weight, alignment, top, page_height,x0,x1,page_width)

                structure.append({
                    "type": heading_level,
                    "text": text,
                    "bbox": [x0, top, x1, bottom],
                    "font_size": font_size,
                    "bold": is_bold,
                    "underline": is_underlined,
                    "font_weight": font_weight,
                    "fontnames": list(set(w["fontname"] for w in line_words)),
                    "alignment": alignment
                    # "debug_score": score  # Uncomment to debug score values
                })


            # Add tables
            for table in page.extract_tables():
                structure.append({
                    "type": "table",
                    "content": table,
                    "bbox": [0, 0, 0, 0]
                })

            # Add images
            for img in page.images:
                structure.append({
                    "type": "image",
                    "bbox": [img["x0"], img["top"], img["x1"], img["bottom"]]
                })

            result["pages"].append({
                "page_number": i,
                "structure": structure
            })

    return result

# ----------- Batch Processor -----------

def process_folder(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".pdf"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename.replace(".pdf", ".json"))

            print(f"📄 Processing {filename}...")
            layout = parse_layout(input_path)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(layout, f, indent=2, ensure_ascii=False)

            print(f"✅ Saved to {output_path}")

# ----------- CLI Entry -----------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Batch PDF Layout Parser")
    parser.add_argument("input_folder", help="Folder containing PDF files")
    parser.add_argument("output_folder", help="Folder to save JSON outputs")
    args = parser.parse_args()

    process_folder(args.input_folder, args.output_folder)
