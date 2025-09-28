from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import List, Optional
from collections import Counter
import os


DATABASE_URL = "sqlite:///./book_recommendations.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    books = relationship("Book", back_populates="user")

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    genre = Column(String, index=True)
    cover_url = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer, default=0)
    is_read = Column(Integer, default=0)
    user = relationship("User", back_populates="books")


Base.metadata.create_all(bind=engine)


def add_missing_columns():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(books)"))
            columns = [row[1] for row in result]
            
            if 'rating' not in columns:
                conn.execute(text("ALTER TABLE books ADD COLUMN rating INTEGER DEFAULT 0"))
                conn.commit()
            
            if 'is_read' not in columns:
                conn.execute(text("ALTER TABLE books ADD COLUMN is_read INTEGER DEFAULT 0"))
                conn.commit()
    except Exception as e:
        print(f"Database migration note: {e}")

add_missing_columns()


class UserCreate(BaseModel):
    name: str

class UserResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class BookCreate(BaseModel):
    title: str
    author: str
    genre: str
    cover_url: Optional[str] = None
    rating: Optional[int] = 0

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    cover_url: Optional[str] = None
    user_id: int
    rating: int
    is_read: int
    
    class Config:
        from_attributes = True

class UserStatsResponse(BaseModel):
    user: UserResponse
    total_books: int
    favorite_genre: str
    genre_counts: dict
    books: List[BookResponse]

class RecommendationResponse(BaseModel):
    recommended_genre: str
    reason: str
    suggested_books: List[BookResponse]


app = FastAPI(title="Book Recommendation System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Book Recommendation System API"}

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.name == user.name).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    db_user = User(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/books/", response_model=BookResponse)
async def create_book(book: BookCreate, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    rating = book.rating or 0
    if rating < 0 or rating > 5:
        rating = 0
    db_book = Book(
        title=book.title,
        author=book.author,
        genre=book.genre,
        cover_url=book.cover_url,
        user_id=user_id,
        rating=rating,
        is_read=0
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/users/{user_id}/books", response_model=List[BookResponse])
async def get_user_books(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return db.query(Book).filter(Book.user_id == user_id).all()

@app.put("/books/{book_id}/mark-read")
async def mark_book_as_read(book_id: int, rating: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    book.is_read = 1
    book.rating = rating
    db.commit()
    return {"message": f"Book '{book.title}' marked as read with rating {rating}"}

@app.get("/users/{user_id}/stats", response_model=UserStatsResponse)
async def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    read_books = db.query(Book).filter(Book.user_id == user_id, Book.is_read == 1).all()
    if not read_books:
        return UserStatsResponse(user=user, total_books=0, favorite_genre="No books read yet", genre_counts={}, books=[])
    genres = [book.genre for book in read_books]
    genre_counts = dict(Counter(genres))
    favorite_genre = max(genre_counts, key=genre_counts.get)
    return UserStatsResponse(user=user, total_books=len(read_books), favorite_genre=favorite_genre, genre_counts=genre_counts, books=read_books)

@app.get("/users/{user_id}/recommendations", response_model=RecommendationResponse)
async def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_read_books = db.query(Book).filter(Book.user_id == user_id, Book.is_read == 1).all()
    user_book_titles = {book.title.lower() for book in user_read_books}
    if not user_read_books:
        all_books = db.query(Book).all()
        if all_books:
            all_genres = [book.genre for book in all_books]
            genre_counts = dict(Counter(all_genres))
            recommended_genre = max(genre_counts, key=genre_counts.get)
            suggested_books = db.query(Book).filter(Book.genre == recommended_genre).limit(5).all()
            return RecommendationResponse(recommended_genre=recommended_genre, reason="Based on popular genres", suggested_books=suggested_books)
        else:
            return RecommendationResponse(recommended_genre="Fiction", reason="No books in database yet", suggested_books=[])
    user_genres = [book.genre for book in user_read_books]
    genre_counts = dict(Counter(user_genres))
    favorite_genre = max(genre_counts, key=genre_counts.get)
    content_books = db.query(Book).filter(Book.genre == favorite_genre, Book.user_id != user_id, ~Book.title.in_(user_book_titles)).all()
    final_books = content_books[:5]  
    return RecommendationResponse(recommended_genre=favorite_genre, reason=f"Based on your preference for {favorite_genre}", suggested_books=final_books)

@app.get("/books/", response_model=List[BookResponse])
async def get_all_books(db: Session = Depends(get_db)):
    return db.query(Book).all()


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
