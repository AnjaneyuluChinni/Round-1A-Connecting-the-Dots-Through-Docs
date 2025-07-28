# PDF Outline Extractor - Adobe Hackathon Solution

## 🎯 Overview

This solution extracts structured outlines from PDF documents, identifying titles and hierarchical headings (H1, H2, H3) with their corresponding page numbers. It's designed for the Adobe Hackathon Round 1A challenge.

## 🚀 Approach

### Multi-Factor Heading Detection
Our solution combines multiple techniques for robust heading detection:

1. **Font Size Analysis**: Dynamically determines font size thresholds based on document characteristics
2. **Pattern Recognition**: Uses regex patterns to identify common heading formats
3. **Contextual Analysis**: Considers page position, text length, and formatting
4. **Hierarchical Classification**: Intelligently assigns heading levels based on multiple factors

### Key Features

- **Dynamic Threshold Detection**: Automatically adapts to different document styles
- **Pattern-Based Recognition**: Handles various heading formats (numbered, titled, etc.)
- **Multilingual Support**: Works with different languages including Japanese
- **Robust Error Handling**: Gracefully handles malformed or complex PDFs
- **Performance Optimized**: Processes 50-page PDFs in under 10 seconds

## 🛠 Technical Implementation

### Libraries Used
- **PyMuPDF (fitz)**: Primary PDF processing library for text extraction and formatting analysis
- **Python Standard Library**: For file handling, JSON processing, and regex operations

### Algorithm Workflow

1. **Text Extraction**: Extract all text with font size and position metadata
2. **Font Analysis**: Determine document-specific font size thresholds
3. **Title Detection**: Identify document title from first page using largest font
4. **Heading Classification**: Apply multi-factor analysis to classify heading levels
5. **Structure Generation**: Create hierarchical JSON output

### Heading Detection Strategies

```python
# Font-based detection
if font_size >= h1_threshold: return "H1"

# Pattern-based detection  
if re.match(r'^\d+\.\d+\.\d+', text): return "H3"
if re.match(r'^\d+\.\d+', text): return "H2"
if re.match(r'^\d+\.', text): return "H1"

# Format-based detection
if text.isupper() and len(text.split()) <= 5: return "H1"
```

## 🏗 Build & Run Instructions

### Building the Docker Image
```bash
docker build --platform linux/amd64 -t pdf-extractor:v1.0 .
```

### Running the Container
```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  pdf-extractor:v1.0
```

## 📁 Project Structure

```
├── pdf_extractor.py    # Main extraction logic
├── Dockerfile         # Container configuration
├── requirements.txt   # Python dependencies
└── README.md         # This documentation
```

## 📊 Performance Characteristics

- **Execution Time**: < 10 seconds for 50-page PDFs
- **Model Size**: < 200MB (uses lightweight PyMuPDF)
- **Memory Usage**: Optimized for 16GB RAM systems
- **CPU Architecture**: AMD64 (x86_64) compatible
- **Network**: Fully offline operation

## 🎯 Scoring Optimization

### Heading Detection Accuracy (25 points)
- Multi-factor detection algorithm maximizes both precision and recall
- Handles edge cases like inconsistent font sizes and unusual formatting
- Dynamic threshold adaptation improves accuracy across document types

### Performance (10 points)
- Lightweight PyMuPDF library ensures fast processing
- Optimized algorithms stay well under time limits
- Minimal memory footprint

### Multilingual Support (10 points bonus)
- Unicode-aware text processing
- Pattern recognition works across languages
- Tested with Japanese and other non-Latin scripts

## 🔧 Advanced Features

### Smart Title Detection
- Analyzes first page for largest font elements
- Filters out page numbers and headers
- Cleans and formats title text

### Hierarchical Structure Preservation
- Maintains proper H1 > H2 > H3 relationships
- Handles complex document structures
- Preserves page number associations

### Error Resilience
- Graceful handling of corrupted PDFs
- Fallback mechanisms for edge cases
- Comprehensive logging for debugging

## 🧪 Testing Strategy

The solution is designed to handle:
- Academic papers with numbered sections
- Business documents with mixed formatting
- Technical manuals with complex hierarchies
- Multilingual documents
- PDFs with inconsistent styling

## 💡 Future Enhancements

For Round 1B and beyond, this modular architecture enables:
- Semantic analysis integration
- Table of contents extraction
- Cross-reference detection
- Advanced formatting recognition

## 🏆 Competitive Advantages

1. **Robustness**: Handles diverse PDF formats and styles
2. **Performance**: Optimized for speed and memory efficiency
3. **Accuracy**: Multi-factor detection maximizes precision/recall
4. **Scalability**: Modular design supports future enhancements
5. **Reliability**: Comprehensive error handling and logging

---

*Built for Adobe Hackathon 2025 - Connecting the Dots Through Docs*