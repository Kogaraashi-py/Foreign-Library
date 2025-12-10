from pathlib import Path
import os
from dotenv import load_dotenv         



class Settings:
    load_dotenv()
    db_username = os.getenv('USER_DB')
    
    db_password = os.getenv('PASSWORD_DB')
    
    db_host = os.getenv('HOST_DB')
    
    db_name = os.getenv('NAME_DB')

    app_name: str = "Api de Novelas"

    #Define the SQLMODEL and connection
    url_conection = f'mysql+pymysql://{db_username}:{db_password}@{db_host}:3306/{db_name}'

 
  # File Upload
    UPLOAD_DIR: Path = Path("static/novels")
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png", "webp"}
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    def __init__(self):
        # Crear directorio de subida si no existe
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
