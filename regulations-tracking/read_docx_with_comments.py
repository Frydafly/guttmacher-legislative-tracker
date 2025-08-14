#!/usr/bin/env python3
"""Extract text and comments from a Word document"""

from docx import Document
from zipfile import ZipFile
from lxml import etree
import sys

def extract_comments_from_docx(docx_path):
    """Extract comments from a .docx file"""
    comments = []
    
    # Open the docx file as a zip archive
    with ZipFile(docx_path, 'r') as docx_zip:
        # Check if comments file exists
        if 'word/comments.xml' in docx_zip.namelist():
            # Parse the comments XML
            comments_xml = docx_zip.read('word/comments.xml')
            root = etree.fromstring(comments_xml)
            
            # Define the namespace
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            # Extract all comments
            for comment in root.xpath('//w:comment', namespaces=ns):
                comment_id = comment.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
                author = comment.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author', 'Unknown')
                date = comment.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}date', '')
                
                # Extract comment text
                comment_text = []
                for paragraph in comment.xpath('.//w:p', namespaces=ns):
                    para_text = ''
                    for text_node in paragraph.xpath('.//w:t', namespaces=ns):
                        if text_node.text:
                            para_text += text_node.text
                    if para_text:
                        comment_text.append(para_text)
                
                if comment_text:
                    comments.append({
                        'id': comment_id,
                        'author': author,
                        'date': date[:10] if date else '',  # Just the date part
                        'text': '\n'.join(comment_text)
                    })
    
    return comments

def read_docx_with_comments(docx_path):
    """Read document text and comments from a .docx file"""
    
    # Read the main document text
    doc = Document(docx_path)
    
    print("=" * 80)
    print("DOCUMENT CONTENT")
    print("=" * 80)
    
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            print(paragraph.text)
    
    # Extract comments
    comments = extract_comments_from_docx(docx_path)
    
    if comments:
        print("\n" + "=" * 80)
        print(f"COMMENTS ({len(comments)} total)")
        print("=" * 80)
        
        for i, comment in enumerate(comments, 1):
            print(f"\nComment #{i}")
            print(f"Author: {comment['author']}")
            if comment['date']:
                print(f"Date: {comment['date']}")
            print(f"Text: {comment['text']}")
            print("-" * 40)
    else:
        print("\n" + "=" * 80)
        print("NO COMMENTS FOUND")
        print("=" * 80)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        docx_path = sys.argv[1]
    else:
        docx_path = "/Users/frydaguedes/Downloads/Regulations Tracking Proposal.docx"
    
    try:
        read_docx_with_comments(docx_path)
    except Exception as e:
        print(f"Error reading document: {e}")