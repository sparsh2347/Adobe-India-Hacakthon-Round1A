# 🧠 PDF Layout Structure Extractor

This project extracts structured layout information (titles, headings, paragraphs, tables, images) from PDF documents using rule-based heuristics and `pdfplumber`.

It outputs a clean **JSON structure** of each page's content, including the detected semantic types like `title`, `h1`, `h2`, `h3`, and `paragraph`.

---

## 🚀 Features

- ✅ Extracts clean line-wise content grouped into words using spatial positions  
- ✅ Detects headings and semantic structure using font size, boldness, alignment, and position  
- ✅ Identifies and includes tables and images  
- ✅ Outputs each PDF as a structured JSON with layout info  
- ✅ Batch processes all PDFs in a folder  
- ✅ Comes with Docker support for reproducible deployment  

---

## 📁 Project Structure

```text
Adobe-India-Hackathon-Round1A
├── round1a_main.py # Main script to process PDFs
├── requirements.txt # Python dependencies
├── Dockerfile # Containerization setup
├── input/ # Folder to place PDF files
└── output/ # Folder to receive JSON outputs
```
---

## 🛠 Approach

### 1. **Layout Detection with `pdfplumber`**
- Characters are grouped into words and lines using XY positions (`x_tolerance` & `y_tolerance`).
- Each line's font size, boldness, alignment (center, left, indented), and position (top of page) is analyzed.

### 2. **Heading & Paragraph Classification**
We apply rule-based scoring to classify text blocks as:
- `title` – large, bold, centered, and top-aligned
- `h1`, `h2`, `h3` – varying font sizes and formatting
- `paragraph` – regular-sized left-aligned text

### 3. **Tables and Images**
- Tables are extracted using `page.extract_tables()`
- Images are included via bounding box coordinates

---
## 🧩 Installation Guide

### 🔧 Local Installation (without Docker)

Make sure you have **Python 3.8+** installed (or use a virtual environment).

---

#### 1. Clone the Repository
```bash
git clone https://github.com/sparsh2347/Adobe-India-Hackathon-Round1A
cd Adobe-India-Hackathon-Round1A
```
#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
#### 3. Run the script
```bash
python round1a_main.py input output
```

## Docker Installation

### Prerequisites

Make sure **Docker is installed and running** on your machine:

- 🔗 [Download Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac)
- 🐧 On Linux, install via your package manager:
  ```bash
  sudo apt install docker.io
  ```
  
- You can verify your Docker installation using:
 ```bash
    docker --version
 ```

### Pull Prebuilt Docker Image
You can use our prebuilt image directly from Docker Hub:

```bash
docker pull cocane/adobe-round-1
```

### Run with docker

```bash
docker run cocane/adobe-round-1
```

**📂 Note:**
Place your PDFs and input.json inside the input/Collection X/ folder.
The generated output.json will be saved inside the corresponding output/ folder.

## 📦 Dependencies

### ✅ Minimal Required (in `requirements.txt`)
```txt
pdfplumber==0.10.2
pdfminer.six==20221105
Pillow==11.1.0
```

## 🔧 System Dependencies (handled via Docker)

The `Dockerfile` automatically installs essential system libraries:

- `poppler-utils` – for PDF parsing  
- `ghostscript`, `libjpeg`, `libpng`, `freetype`, etc. – for image processing  
- `ffmpeg`, `curl`, `tcl/tk`, and more – for rich compatibility across visual and document formats  
- `libgl1`, `libtiff-dev`, `libopenjp2-7` – for broader support in image decoding  

💡 All dependencies are handled within Docker, so no system-level setup is needed if you use the containerized version.

---

## 📈 Sample Output Format (per page)

```json
{
  "page_number": 1,
  "structure": [
    {
      "type": "title",
      "text": "Financial Statement 2024",
      "bbox": [50.0, 70.0, 520.0, 100.0],
      "font_size": 24,
      "bold": true,
      "alignment": "center"
    },
    {
      "type": "paragraph",
      "text": "This report contains information...",
      "bbox": [40.0, 120.0, 500.0, 140.0],
      "font_size": 11
    }
  ]
}
```
Each page in the output JSON includes a list of detected content blocks with rich metadata:

- **type** — semantic classification (`title`, `h1`, `h2`, `paragraph`, etc.)
- **text** — extracted text content from the block
- **bbox** — bounding box coordinates in `[x0, y0, x1, y1]` format
- **font_size** — numerical font size of the block
- **bold** — whether the text is bold (`true`/`false`)
- **alignment** — alignment hint (e.g., `left`, `center`, `right`, `indented`)

## Team details
**Team Name: Pixels** <br>
**Team Leader: Sparsh Sinha**<br>
**Team Members: Rahul Naksar,Ayush Kumar**
