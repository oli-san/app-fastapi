from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


#configuracion de la base de datos PostgreSQL
#DATABASE_URL = "postgresql://postgres:root@localhost/crud_db"
DATABASE_URL = "postgresql://postgres:sanchez123@crud-db.cbway4c2ahkc.us-east-2.rds.amazonaws.com/crud_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#Modelo de la tabla 'books'
class Book(Base):
    __tablename__ = "books"  # Nombre de la tabla en la base de datos
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    published_year = Column(Integer) 
    
#Creacion de tablas
Base.metadata.create_all(bind = engine)


#Inicialización de FastAPI
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Cambia el dominio según sea necesario
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()
        
#Rutas de CRUD
@app.post("/books/", response_model=dict)
def create_book(book: dict, db: Session = Depends(get_db)):
    new_book = Book(**book)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return {"message": "Book created", "book": {"id": new_book.id, "title": new_book.title, "author": new_book.author, "published_year": new_book.published_year}}

@app.get("/books/{book_id}", response_model=dict)
def read_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"book": {"id": book.id, "title": book.title, "author": book.author, "published_year": book.published_year}}

@app.get("/books/", response_model=list)
def read_all_books(db: Session = Depends(get_db)):
    #Devuelve una lista con todos los libros existentes en la base de datos.
    books = db.query(Book).all()
    if not books:
        raise HTTPException(status_code=404, detail="No books found")
    return [{"id": book.id, "title": book.title, "author": book.author, "published_year": book.published_year} for book in books]

@app.put("/books/{book_id}", response_model=dict)
def update_book(book_id: int, updated_data: dict, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in updated_data.items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return {"message": "Book updated", "book": {"id": book.id, "title": book.title, "author": book.author, "published_year": book.published_year}}

@app.delete("/books/{book_id}", response_model=dict)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"message": "Book deleted"}