# Document processing capabilities for various file formats
import os
import tempfile
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import PyPDF2
import docx2txt
from bs4 import BeautifulSoup
import re

@dataclass
class ProcessedDocument:
    filename: str
    content: str
    metadata: Dict[str, Any]
    chunks: List[str] = None
    
class DocumentProcessor:
    """Process various document formats and extract text content"""
    
    def __init__(self):
        self.supported_formats = {
            '.pdf': self._process_pdf,
            '.txt': self._process_txt,
            '.docx': self._process_docx,
            '.html': self._process_html,
            '.htm': self._process_html,
            '.md': self._process_markdown,
        }
    
    def process_file(self, file_path: str) -> ProcessedDocument:
        """Process a single file and extract content"""
        filename = os.path.basename(file_path)
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        try:
            content = self.supported_formats[file_ext](file_path)
            metadata = self._extract_metadata(file_path, content)
            chunks = self._chunk_content(content)
            
            return ProcessedDocument(
                filename=filename,
                content=content,
                metadata=metadata,
                chunks=chunks
            )
        except Exception as e:
            raise Exception(f"Error processing {filename}: {str(e)}")
    
    def process_uploaded_file(self, uploaded_file) -> ProcessedDocument:
        """Process file uploaded through Gradio"""
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name
            
            # Process the temporary file
            result = self.process_file(tmp_path)
            result.filename = uploaded_file.name
            
            # Clean up temporary file
            os.unlink(tmp_path)
            
            return result
        except Exception as e:
            raise Exception(f"Error processing uploaded file: {str(e)}")
    
    def _process_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            # Try PyPDF2 first
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return self._clean_text(text)
        except Exception as e:
            # Fallback: try pypdf
            try:
                import pypdf
                with open(file_path, 'rb') as file:
                    pdf_reader = pypdf.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return self._clean_text(text)
            except:
                raise Exception(f"Could not extract text from PDF: {str(e)}")
    
    def _process_txt(self, file_path: str) -> str:
        """Extract text from plain text file"""
        encodings = ['utf-8', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
        raise Exception("Could not decode text file with any supported encoding")
    
    def _process_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            text = docx2txt.process(file_path)
            return self._clean_text(text)
        except Exception as e:
            raise Exception(f"Could not extract text from DOCX: {str(e)}")
    
    def _process_html(self, file_path: str) -> str:
        """Extract text from HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                text = soup.get_text()
                return self._clean_text(text)
        except Exception as e:
            raise Exception(f"Could not extract text from HTML: {str(e)}")
    
    def _process_markdown(self, file_path: str) -> str:
        """Extract text from Markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # Remove markdown formatting (basic)
                content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)  # Headers
                content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Bold
                content = re.sub(r'\*(.*?)\*', r'\1', content)  # Italic
                content = re.sub(r'`(.*?)`', r'\1', content)  # Inline code
                content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)  # Links
                
                return self._clean_text(content)
        except Exception as e:
            raise Exception(f"Could not extract text from Markdown: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.,!?;:()\-\'"]+', '', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text
    
    def _extract_metadata(self, file_path: str, content: str) -> Dict[str, Any]:
        """Extract metadata from file"""
        stat = os.stat(file_path)
        return {
            'file_size': stat.st_size,
            'word_count': len(content.split()),
            'char_count': len(content),
            'file_type': os.path.splitext(file_path)[1].lower(),
            'processed_date': str(stat.st_mtime)
        }
    
    def _chunk_content(self, content: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split content into overlapping chunks for better retrieval"""
        if len(content) <= chunk_size:
            return [content]
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(content):
                # Look for sentence ending within the last 100 characters
                search_start = max(start, end - 100)
                sentence_end = content.rfind('.', search_start, end)
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(content):
                break
        
        return chunks

# Global instance
_document_processor = None

def get_document_processor() -> DocumentProcessor:
    """Get or create document processor instance"""
    global _document_processor
    if _document_processor is None:
        _document_processor = DocumentProcessor()
    return _document_processor

def process_document(file_path: str) -> ProcessedDocument:
    """Process a document file"""
    processor = get_document_processor()
    return processor.process_file(file_path)

def process_uploaded_document(uploaded_file) -> ProcessedDocument:
    """Process an uploaded document"""
    processor = get_document_processor()
    return processor.process_uploaded_file(uploaded_file)

# Test function
def test_document_processing():
    """Test document processing functionality"""
    # Create a test text file
    test_content = """
    This is a test document for the RAG system.
    It contains multiple sentences and paragraphs.
    
    The document processor should be able to extract this text
    and split it into appropriate chunks for vector storage.
    
    This is useful for testing the functionality before
    processing real documents.
    """
    
    test_file = "test_document.txt"
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    try:
        doc = process_document(test_file)
        print(f"Processed: {doc.filename}")
        print(f"Content length: {len(doc.content)} characters")
        print(f"Chunks: {len(doc.chunks)}")
        print(f"Metadata: {doc.metadata}")
        print(f"First chunk: {doc.chunks[0][:100]}...")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    test_document_processing()