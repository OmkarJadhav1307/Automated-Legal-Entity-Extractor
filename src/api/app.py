import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.utils.logger import get_logger
from src.api.services.inference import InferencePipeline

logger = get_logger(__name__)

app = FastAPI(title="LexiScan API", description="Automated Legal Entity Extractor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the pipeline globally
pipeline = InferencePipeline()

temp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "temp"))
os.makedirs(temp_path, exist_ok=True)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "LexiScan API is running"}

@app.post("/extract")
async def extract_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
        
    file_path = os.path.join(temp_path, file.filename)
    
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        is_pdf = file.filename.lower().endswith(".pdf")
        
        # Run inference
        result = pipeline.process_file(file_path, is_pdf=is_pdf)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
            
        return result
        
    except Exception as e:
        logger.error(f"Endpoint /extract failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to remove temp file {file_path}: {str(e)}")

# CLI execution
if __name__ == "__main__":
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=5000, reload=True)
