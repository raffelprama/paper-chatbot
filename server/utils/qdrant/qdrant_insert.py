import os
import glob
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI
from server.service.qdrant_svc import qdrant_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qdrant_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
collection_name = os.environ.get("COLLECTION_NAME")

OPENAI_API_KEY = "sk-G1_wkZ37sEmY4eqnGdcNig"
EMBEDDING_MODEL = "baai/bge-multilingual-gemma2"

openai_client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://dekallm.cloudeka.ai/v1")

def create_embedding(text: str) -> List[float]:
    """Create embedding using OpenAI API"""
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error creating embedding: {e}")
        return []

def load_pdf_documents(pdf_path: str) -> List[Dict[str, Any]]:
    """Load and process PDF documents from directory or single file"""
    documents = []
    
    if not os.path.exists(pdf_path):
        logger.error(f"Path not found: {pdf_path}")
        return documents
    
    # Get PDF files
    if os.path.isfile(pdf_path):
        pdf_files = [pdf_path]
        logger.info(f"Processing single PDF: {os.path.basename(pdf_path)}")
    elif os.path.isdir(pdf_path):
        pdf_files = glob.glob(os.path.join(pdf_path, "*.pdf"))
        if not pdf_files:
            logger.error(f"No PDF files found in directory: {pdf_path}")
            return documents
        logger.info(f"Found {len(pdf_files)} PDF files to process")
    else:
        logger.error(f"Invalid path: {pdf_path}")
        return documents
    
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
    )
    
    for pdf_file in pdf_files:
        try:
            logger.info(f"Processing: {os.path.basename(pdf_file)}")
            
            # Load and split PDF
            loader = PyPDFLoader(pdf_file)
            pages = loader.load()
            chunks = text_splitter.split_documents(pages)
            
            # Create document data
            for i, chunk in enumerate(chunks):
                documents.append({
                    "content": chunk.page_content,
                    "metadata": {
                        "source": pdf_file,
                        "filename": os.path.basename(pdf_file),
                        "page": chunk.metadata.get("page", i),
                        "chunk_id": i
                    }
                })
            
            logger.info(f"Processed {len(chunks)} chunks from {os.path.basename(pdf_file)}")
            
        except Exception as e:
            logger.error(f"Error processing {pdf_file}: {e}")
            continue
    
    return documents

def ensure_qdrant_collection():
    """Ensure Qdrant collection exists, create if not"""
    try:
        # Check if collection exists
        try:
            qdrant_client.get_collection(collection_name)
            logger.info(f"Collection {collection_name} already exists")
        except:
            # Create collection if it doesn't exist
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=3584,  # bge-multilingual-gemma2 dimension
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {collection_name}")
        
    except Exception as e:
        logger.error(f"Error with collection: {e}")
        raise

def insert_documents_to_qdrant(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Insert documents into Qdrant with embeddings"""
    points = []
    successful_inserts = 0
    failed_inserts = 0
    
    logger.info(f"Processing {len(documents)} document chunks...")
    
    for i, doc in enumerate(documents):
        try:
            content = doc["content"]
            metadata = doc["metadata"]
            
            # Create embedding
            embedding = create_embedding(content)
            if not embedding:
                logger.error(f"Failed to create embedding for chunk {i+1}")
                failed_inserts += 1
                continue
            
            # Create point for Qdrant
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "content": content,
                    "filename": metadata["filename"],
                    "source": metadata["source"],
                    "page": metadata["page"],
                    "chunk_id": metadata["chunk_id"],
                    "metadata": {
                        "inserted_at": datetime.now().isoformat(),
                        "collection": collection_name
                    }
                }
            ))
            successful_inserts += 1
            
        except Exception as e:
            logger.error(f"Error processing chunk {i+1}: {e}")
            failed_inserts += 1
    
    # Insert points in batches
    if points:
        try:
            logger.info(f"Inserting {len(points)} points into Qdrant...")
            batch_size = 10
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                qdrant_client.upsert(
                    collection_name=collection_name,
                    points=batch
                )
                logger.info(f"Inserted batch {i//batch_size + 1}/{(len(points) + batch_size - 1)//batch_size}")
            
            # Get collection info
            collection_info = qdrant_client.get_collection(collection_name)
            logger.info(f"Successfully inserted {successful_inserts} chunks. Collection now has {collection_info.points_count} points")
            
            return {
                "points_inserted": successful_inserts,
                "points_failed": failed_inserts,
                "total_points": collection_info.points_count
            }
            
        except Exception as e:
            logger.error(f"Error inserting points to Qdrant: {e}")
            raise
    else:
        logger.warning("No points to insert!")
        return {
            "points_inserted": 0,
            "points_failed": failed_inserts,
            "total_points": 0
        }

def process_pdfs_to_qdrant(pdf_path: str, collection_name: str = None) -> Dict[str, Any]:
    """
    Process PDFs and insert into Qdrant
    
    Args:
        pdf_path: Path to PDF file or directory containing PDFs (required)
        collection_name: Name of the Qdrant collection (optional)
    
    Returns:
        Dictionary with processing results
    """
    if not pdf_path:
        raise ValueError("PDF path is required")
    
    logger.info(f"Starting PDF to Qdrant insertion process")
    logger.info(f"PDF Path: {pdf_path}")
    logger.info(f"Collection: {collection_name}")
    
    result = {
        "success": False,
        "message": "",
        "documents_processed": 0,
        "chunks_created": 0,
        "points_inserted": 0,
        "errors": []
    }
    
    try:
        # Ensure Qdrant collection exists
        ensure_qdrant_collection()
        
        # Load PDF documents
        documents = load_pdf_documents(pdf_path)
        
        if not documents:
            error_msg = "No documents to process"
            logger.error(error_msg)
            result["message"] = error_msg
            return result
        
        result["documents_processed"] = len(set(doc["metadata"]["filename"] for doc in documents))
        result["chunks_created"] = len(documents)
        
        # Insert documents into Qdrant
        insert_result = insert_documents_to_qdrant(documents)
        result["points_inserted"] = insert_result.get("points_inserted", 0)
        
        result["success"] = True
        result["message"] = f"Successfully processed {result['documents_processed']} documents with {result['chunks_created']} chunks"
        
        logger.info("PDF insertion process completed successfully")
        
    except Exception as e:
        error_msg = f"Error during processing: {str(e)}"
        logger.error(error_msg)
        result["message"] = error_msg
        result["errors"].append(error_msg)
    
    return result

def insert_collection(path:str):
    """Main function for command line usage"""
    pdf_path = f"{path}"
    
    result = process_pdfs_to_qdrant(pdf_path)
    
    if result["success"]:
        logger.info(f"SUCCESS: {result['message']}")
    else:
        logger.error(f"FAILED: {result['message']}")

if __name__ == "__main__":
    data = insert_collection("/mnt/d/user/Downloads/__administartion/Arcfusion/task/resource/papers")
    # data = insert_collection("/mnt/c/Users/raffe/OneDrive/Documents/JURNAL/agroeconomic/")
    logging.info(data)