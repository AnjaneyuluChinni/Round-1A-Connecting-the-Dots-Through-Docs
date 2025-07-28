#!/usr/bin/env python3
"""
PDF Outline Extractor for Adobe Hackathon
Extracts hierarchical structure (title, H1, H2, H3) from PDF documents
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import fitz  # PyMuPDF
from collections import Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFOutlineExtractor:
    def __init__(self):
        self.heading_patterns = [
            # Common heading patterns
            r'^(\d+\.?\s+[A-Z][^.!?]*?)$',  # "1. Introduction" or "1 Introduction"
            r'^([A-Z][A-Z\s]{2,}[A-Z])$',   # ALL CAPS headings
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*):?\s*$',  # Title Case headings
            r'^(Chapter\s+\d+[:\s]+[^.!?]*?)$',  # Chapter headings
            r'^(Section\s+\d+[:\s]+[^.!?]*?)$',  # Section headings
            r'^(\d+\.\d+\.?\s+[A-Z][^.!?]*?)$',  # "1.1 Subsection"
            r'^(\d+\.\d+\.\d+\.?\s+[A-Z][^.!?]*?)$',  # "1.1.1 Subsubsection"
        ]
        
        # Font size thresholds (will be determined dynamically)
        self.font_thresholds = {}
        
    def extract_text_with_formatting(self, pdf_path: str) -> List[Dict]:
        """Extract text with font size and position information"""
        doc = fitz.open(pdf_path)
        formatted_text = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")
            
            for block in blocks["blocks"]:
                if "lines" not in block:
                    continue
                    
                for line in block["lines"]:
                    line_text = ""
                    font_sizes = []
                    
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            line_text += text + " "
                            font_sizes.append(span["size"])
                    
                    line_text = line_text.strip()
                    if line_text and font_sizes:
                        avg_font_size = sum(font_sizes) / len(font_sizes)
                        formatted_text.append({
                            "text": line_text,
                            "font_size": avg_font_size,
                            "page": page_num + 1,
                            "bbox": line["bbox"]
                        })
        
        doc.close()
        return formatted_text
    
    def determine_font_thresholds(self, formatted_text: List[Dict]) -> Dict[str, float]:
        """Dynamically determine font size thresholds for different heading levels"""
        font_sizes = [item["font_size"] for item in formatted_text]
        font_counter = Counter(font_sizes)
        
        # Sort font sizes in descending order
        unique_sizes = sorted(font_counter.keys(), reverse=True)
        
        if len(unique_sizes) < 2:
            return {"title": max(unique_sizes), "h1": max(unique_sizes), "h2": max(unique_sizes), "h3": max(unique_sizes)}
        
        # Determine thresholds based on distribution
        title_threshold = unique_sizes[0]  # Largest font
        h1_threshold = unique_sizes[1] if len(unique_sizes) > 1 else unique_sizes[0]
        h2_threshold = unique_sizes[2] if len(unique_sizes) > 2 else h1_threshold
        h3_threshold = unique_sizes[3] if len(unique_sizes) > 3 else h2_threshold
        
        return {
            "title": title_threshold,
            "h1": h1_threshold,
            "h2": h2_threshold,
            "h3": h3_threshold
        }
    
    def is_heading_by_pattern(self, text: str) -> bool:
        """Check if text matches common heading patterns"""
        text = text.strip()
        if len(text) < 3 or len(text) > 200:  # Reasonable heading length
            return False
            
        for pattern in self.heading_patterns:
            if re.match(pattern, text):
                return True
        return False
    
    def classify_heading_level(self, text: str, font_size: float, page: int) -> Optional[str]:
        """Classify heading level based on multiple factors"""
        text = text.strip()
        
        # Check if it's a potential heading
        if not self.is_heading_by_pattern(text):
            # Additional checks for headings without patterns
            if not (text[0].isupper() and len(text.split()) <= 10):
                return None
        
        # Determine level based on font size and content patterns
        if font_size >= self.font_thresholds["title"] and page == 1:
            return "title"
        elif font_size >= self.font_thresholds["h1"]:
            return "H1"
        elif font_size >= self.font_thresholds["h2"]:
            return "H2"
        elif font_size >= self.font_thresholds["h3"]:
            return "H3"
        
        # Pattern-based classification
        if re.match(r'^\d+\.\d+\.\d+', text):
            return "H3"
        elif re.match(r'^\d+\.\d+', text):
            return "H2"
        elif re.match(r'^\d+\.', text):
            return "H1"
        elif text.isupper() and len(text.split()) <= 5:
            return "H1"
        
        return None
    
    def extract_title(self, formatted_text: List[Dict]) -> str:
        """Extract document title from the first page"""
        first_page_text = [item for item in formatted_text if item["page"] == 1]
        
        if not first_page_text:
            return "Untitled Document"
        
        # Look for the largest font size on first page
        max_font_size = max(item["font_size"] for item in first_page_text)
        title_candidates = [
            item for item in first_page_text 
            if item["font_size"] == max_font_size and len(item["text"]) > 3
        ]
        
        if title_candidates:
            # Take the first substantial text with maximum font size
            title = title_candidates[0]["text"]
            # Clean up title
            title = re.sub(r'^\d+\.?\s*', '', title)  # Remove leading numbers
            return title.strip()
        
        # Fallback: look for text that looks like a title
        for item in first_page_text[:10]:  # Check first 10 lines
            text = item["text"].strip()
            if (len(text) > 5 and len(text) < 100 and 
                not text.startswith(('Page', 'Chapter', 'Section')) and
                not re.match(r'^\d+$', text)):
                return text
        
        return "Untitled Document"
    
    def extract_outline(self, pdf_path: str) -> Dict:
        """Extract complete outline from PDF"""
        logger.info(f"Processing PDF: {pdf_path}")
        
        # Extract formatted text
        formatted_text = self.extract_text_with_formatting(pdf_path)
        
        if not formatted_text:
            return {"title": "Empty Document", "outline": []}
        
        # Determine font thresholds
        self.font_thresholds = self.determine_font_thresholds(formatted_text)
        logger.info(f"Font thresholds: {self.font_thresholds}")
        
        # Extract title
        title = self.extract_title(formatted_text)
        
        # Extract headings
        outline = []
        seen_headings = set()  # Avoid duplicates
        
        for item in formatted_text:
            level = self.classify_heading_level(item["text"], item["font_size"], item["page"])
            
            if level and level != "title":
                heading_text = item["text"].strip()
                # Clean up heading text
                heading_text = re.sub(r'\s+', ' ', heading_text)
                
                # Avoid duplicates and very short headings
                if heading_text not in seen_headings and len(heading_text) > 2:
                    outline.append({
                        "level": level,
                        "text": heading_text,
                        "page": item["page"]
                    })
                    seen_headings.add(heading_text)
        
        # Sort by page number
        outline.sort(key=lambda x: x["page"])
        
        logger.info(f"Extracted title: {title}")
        logger.info(f"Extracted {len(outline)} headings")
        
        return {
            "title": title,
            "outline": outline
        }

def process_single_pdf(input_path: str, output_path: str):
    """Process a single PDF file"""
    try:
        extractor = PDFOutlineExtractor()
        result = extractor.extract_outline(input_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully processed {input_path} -> {output_path}")
        
    except Exception as e:
        logger.error(f"Error processing {input_path}: {str(e)}")
        # Create empty result on error
        error_result = {"title": "Error Processing Document", "outline": []}
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(error_result, f, indent=2)

def main():
    """Main function to process all PDFs in input directory"""
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("No PDF files found in input directory")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    for pdf_file in pdf_files:
        output_file = output_dir / f"{pdf_file.stem}.json"
        process_single_pdf(str(pdf_file), str(output_file))
    
    logger.info("Processing complete!")

if __name__ == "__main__":
    main()