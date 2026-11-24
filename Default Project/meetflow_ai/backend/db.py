from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os
DB_URL=os.getenv('DATABASE_URL','sqlite:///./meetflow.db')
engine=create_engine(DB_URL,connect_args={'check_same_thread':False} if DB_URL.startswith('sqlite') else {})
Session=sessionmaker(bind=engine,autoflush=False,autocommit=False)
Base.metadata.create_all(engine)
def get_db():
    db=Session()
    try: yield db
    finally: db.close()
