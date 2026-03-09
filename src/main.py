import argparse
import sys
import os

# Ensure the root project directory is in the Python path so "src." imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from src.api.services.inference import InferencePipeline
from src.utils.logger import get_logger
import uvicorn

logger = get_logger(__name__)

def run_server(port=5000):
    logger.info(f"Starting LexiScan2 API Server on port {port}...")
    import webbrowser
    import threading
    import time

    def open_browser():
        time.sleep(3) # Wait a few seconds for the server to spin up completely
        webbrowser.open(f"http://127.0.0.1:{port}/docs")

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=port, reload=False)

def run_cli_inference(file_path):
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return

    pipeline = InferencePipeline()
    is_pdf = file_path.lower().endswith(".pdf")
    logger.info(f"Running inference pipeline on {'PDF' if is_pdf else 'Image'}: {file_path}")
    
    result = pipeline.process_file(file_path, is_pdf=is_pdf)
    
    if result["status"] == "success":
        logger.info("\n--- EXTRACTION COMPLETE ---")
        print(f"File: {file_path}")
        
        entities = result.get("entities", [])
        if entities:
            print(f"\nFound {len(entities)} Entities:\n")
            for ent in entities:
                display_val = ent.get("standardized_value", ent['text'])
                print(f"[{ent['label']:<15}] => {display_val}")
        else:
            print("\nNo entities extracted.")
        print("-" * 50)
    else:
        logger.error(f"Failed to process file: {result.get('message')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LexiScan2 - Automated Legal Entity Extractor")
    parser.add_argument("--server", action="store_true", help="Start the FastAPI backend server")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the server on (default: 5000)")
    parser.add_argument("--file", type=str, help="Process a specific document file via CLI")

    args = parser.parse_args()

    if args.server:
        run_server(port=args.port)
    elif args.file:
        run_cli_inference(args.file)
    else:
        parser.print_help()
