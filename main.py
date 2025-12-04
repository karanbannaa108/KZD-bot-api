from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import subprocess
import tempfile
import shutil

from database import init_db, insert_log

app = FastAPI()
auth = HTTPBearer()

API_TOKEN = "API-SECRET-0566"  # token

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(auth)):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid Token")
    return True

class CodeInput(BaseModel):
    code: str

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def home():
    return {"message": "KZD Bot API Running ✔"}

@app.post("/run")
def run_code(data: CodeInput, valid=Depends(verify_token)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp:
            temp.write(data.code.encode())
            temp.flush()
            result = subprocess.run(
                ["python3", temp.name],
                capture_output=True,
                text=True,
                timeout=10
            )
        insert_log("run", data.code)
        return {"stdout": result.stdout, "stderr": result.stderr}
    except Exception as e:
        return {"error": str(e)}

@app.post("/upload")
async def upload(file: UploadFile = File(...), valid=Depends(verify_token)):
    save_path = f"uploads/{file.filename}"
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    insert_log("upload", file.filename)
    return {"status": "uploaded", "file": file.filename}

@app.post("/install")
def install_package(pkg: str, valid=Depends(verify_token)):
    try:
        result = subprocess.run(
            ["pip", "install", pkg],
            capture_output=True,
            text=True
        )
        insert_log("install", pkg)
        return {"stdout": result.stdout, "stderr": result.stderr}
    except Exception as e:
        return {"error": str(e)}

def bg_job(cmd):
    subprocess.run(cmd, shell=True)

@app.post("/background")
def background_task(cmd: str, tasks: BackgroundTasks, valid=Depends(verify_token)):
    tasks.add_task(bg_job, cmd)
    insert_log("background", cmd)
    return {"status": "background task started", "cmd": cmd}
