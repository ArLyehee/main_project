# from fastapi import FastAPI, Request, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
# from pydantic import BaseModel
# from sqlalchemy import create_engine, Column, Integer, String, Boolean
# from sqlalchemy.orm import declarative_base, sessionmaker
# import os
# import io
# import zipfile

# # FastAPI 앱 초기화
# app = FastAPI()

# # CORS 설정
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # SQLAlchemy 설정
# DATABASE_URL = 'oracle+cx_oracle://admin:1234@localhost:1521/xe'

# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(bind=engine)
# Base = declarative_base()

# # ---------------------------
# # DB 모델 정의
# # ---------------------------
# class File(Base):
#     __tablename__ = 'files'

#     id = Column(Integer, primary_key=True, index=True)
#     filename = Column(String(255), nullable=False)
#     relative_path = Column(String(500), nullable=False, unique=True)
#     full_path = Column(String(1000), nullable=False)
#     category = Column(String(100), nullable=False)
#     downloaded = Column(Boolean, default=False)

# Base.metadata.create_all(bind=engine)

# # ---------------------------
# # 데모 사용자 정보
# # ---------------------------
# USERS = {
#     1: {'username': 'demo', 'base_path': r'C:\Users\4Class_18\Desktop\main_project\testsample'}
# }

# def get_user():
#     return USERS[1]

# # ---------------------------
# # 요청 모델
# # ---------------------------
# class BasePathRequest(BaseModel):
#     base_path: str

# class DownloadedFilesRequest(BaseModel):
#     downloaded_files: list[str]

# # ---------------------------
# # API: GET /api/user/path
# # ---------------------------
# @app.get("/api/user/path")
# def get_user_path():
#     user = get_user()
#     return {"base_path": user.get("base_path")}

# # ---------------------------
# # API: POST /api/user/path
# # ---------------------------
# @app.post("/api/user/path")
# def set_user_path(req: BasePathRequest):
#     base_path = req.base_path
#     if not os.path.isdir(base_path):
#         raise HTTPException(status_code=400, detail="경로가 존재하지 않습니다.")
#     user = get_user()
#     user["base_path"] = base_path
#     return {"ok": True}

# # ---------------------------
# # API: POST /api/scan
# # ---------------------------
# @app.post("/api/scan")
# def scan():
#     user = get_user()
#     base = user["base_path"]
#     grouped_docs = {}
#     session = SessionLocal()

#     for root, _, files in os.walk(base):
#         for fname in files:
#             if fname.startswith('.'):
#                 continue
#             full_path = os.path.join(root, fname)
#             rel_path = os.path.relpath(full_path, base)
#             parts = rel_path.replace("\\", "/").split("/")
#             category = parts[0] or "기타"
#             filename = parts[-1]

#             # 중복 확인
#             if not session.query(File).filter_by(relative_path=rel_path).first():
#                 file_entry = File(
#                     filename=filename,
#                     relative_path=rel_path,
#                     full_path=full_path,
#                     category=category
#                 )
#                 session.add(file_entry)
#                 session.commit()

#             if category not in grouped_docs:
#                 grouped_docs[category] = []
#             grouped_docs[category].append({
#                 "filename": filename,
#                 "relative_path": rel_path,
#                 "full_path": full_path
#             })

#     # 제한 출력
#     MAX_DISPLAY = 5
#     for cat, files in grouped_docs.items():
#         if len(files) > MAX_DISPLAY:
#             grouped_docs[cat] = files[:MAX_DISPLAY] + [{"filename": f"...외 {len(files) - MAX_DISPLAY}개 생략...", "relative_path": "", "full_path": ""}]

#     session.close()
#     return {"groupedDocuments": grouped_docs}

# # ---------------------------
# # API: POST /api/download-new-zip
# # ---------------------------
# @app.post("/api/download-new-zip")
# def download_new_zip(req: DownloadedFilesRequest):
#     downloaded_files = req.downloaded_files
#     session = SessionLocal()

#     mem_zip = io.BytesIO()
#     with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
#         files_to_download = session.query(File).filter(~File.relative_path.in_(downloaded_files)).all()
#         for f in files_to_download:
#             if os.path.exists(f.full_path):
#                 zf.write(f.full_path, arcname=f.relative_path)
#                 f.downloaded = True
#                 session.commit()

#     mem_zip.seek(0)
#     session.close()

#     return StreamingResponse(mem_zip, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=new_documents.zip"})

# # ---------------------------
# # API: POST /api/download-all
# # ---------------------------
# @app.post("/api/download-all")
# def download_all():
#     user = get_user()
#     session = SessionLocal()

#     mem_zip = io.BytesIO()
#     with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
#         for f in session.query(File).all():
#             if os.path.exists(f.full_path):
#                 zf.write(f.full_path, arcname=f.relative_path)
#                 f.downloaded = True
#                 session.commit()

#     mem_zip.seek(0)
#     session.close()

#     return StreamingResponse(mem_zip, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=all_documents.zip"})
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
import io
import zipfile
import zipstream
from fastapi.responses import StreamingResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데모 사용자 정보
USERS = {
    1: {'username': 'demo', 'base_path': r'C:\Users\4Class_18\Desktop\main_project\testsample'}
}

def get_user():
    return USERS[1]

class BasePathRequest(BaseModel):
    base_path: str

class DownloadedFilesRequest(BaseModel):
    downloaded_files: list[str]

# 메모리 임시 저장소 (DB 대신)
temp_files = []

@app.get("/api/user/path")
def get_user_path():
    user = get_user()
    return {"base_path": user.get("base_path")}

@app.post("/api/user/path")
def set_user_path(req: BasePathRequest):
    base_path = req.base_path
    if not os.path.isdir(base_path):
        raise HTTPException(status_code=400, detail="경로가 존재하지 않습니다.")
    user = get_user()
    user["base_path"] = base_path
    # 임시 저장소 초기화 (경로 바뀌면 리셋)
    global temp_files
    temp_files = []
    return {"ok": True}

@app.post("/api/scan")
def scan():
    user = get_user()
    base = user["base_path"]
    grouped_docs = {}

    global temp_files

    for root, _, files in os.walk(base):
        for fname in files:
            if fname.startswith('.'):
                continue
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, base).replace("\\", "/")
            parts = rel_path.split("/")
            category = parts[0] or "기타"
            filename = parts[-1]

            # 중복 체크: temp_files 내에 없으면 추가
            if not any(f['relative_path'] == rel_path for f in temp_files):
                temp_files.append({
                    "filename": filename,
                    "relative_path": rel_path,
                    "full_path": full_path,
                    "category": category,
                    "downloaded": False
                })

            if category not in grouped_docs:
                grouped_docs[category] = []
            grouped_docs[category].append({
                "filename": filename,
                "relative_path": rel_path,
                "full_path": full_path
            })

    # 출력 제한
    MAX_DISPLAY = 5
    for cat, files in grouped_docs.items():
        if len(files) > MAX_DISPLAY:
            grouped_docs[cat] = files[:MAX_DISPLAY] + [{"filename": f"...외 {len(files) - MAX_DISPLAY}개 생략...", "relative_path": "", "full_path": ""}]

    return {"groupedDocuments": grouped_docs}

@app.post("/api/download-new-zip")
def download_new_zip(req: DownloadedFilesRequest):
    selected_files = req.downloaded_files  # 선택된 파일 목록

    global temp_files

    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for f in temp_files:
            if f['relative_path'] in selected_files:
                if os.path.exists(f['full_path']):
                    zf.write(f['full_path'], arcname=f['relative_path'])
                    f['downloaded'] = True  # 선택된 파일만 다운로드로 표시

    mem_zip.seek(0)
    return StreamingResponse(
        mem_zip,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=selected_documents.zip"}
    )

@app.post("/api/download-all")
def download_all():
    global temp_files
    zs = zipstream.ZipFile(mode='w', compression=zipstream.ZIP_DEFLATED)
    
    for f in temp_files:
        if os.path.exists(f['full_path']):
            zs.write(f['full_path'], arcname=f['relative_path'])
            f['downloaded'] = True

    headers = {"Content-Disposition": "attachment; filename=all_documents.zip"}
    return StreamingResponse(zs, media_type="application/zip", headers=headers)