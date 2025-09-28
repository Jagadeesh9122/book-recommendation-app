from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from collections import Counter
import os

# Database setup
DATABASE_URL = "sqlite:///./book_recommendations.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
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
    rating = Column(Integer, default=0)  # Rating from 1-5
    is_read = Column(Integer, default=0)  # 0 = not read, 1 = read
    user = relationship("User", back_populates="books")

# Create tables
Base.metadata.create_all(bind=engine)

# Add rating and is_read columns if they don't exist (for existing databases)
def add_missing_columns():
    try:
        with engine.connect() as conn:
            # Check if rating column exists
            result = conn.execute(text("PRAGMA table_info(books)"))
            columns = [row[1] for row in result]
            
            if 'rating' not in columns:
                # Add rating column
                conn.execute(text("ALTER TABLE books ADD COLUMN rating INTEGER DEFAULT 0"))
                conn.commit()
                print("✅ Added rating column to existing database")
            
            if 'is_read' not in columns:
                # Add is_read column
                conn.execute(text("ALTER TABLE books ADD COLUMN is_read INTEGER DEFAULT 0"))
                conn.commit()
                print("✅ Added is_read column to existing database")
    except Exception as e:
        print(f"Database migration note: {e}")

# Run migration
add_missing_columns()

# Pydantic models
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

# FastAPI app
app = FastAPI(title="Book Recommendation System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Book Recommendation System API"}

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
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
    users = db.query(User).all()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/books/", response_model=BookResponse)
async def create_book(book: BookCreate, user_id: int, db: Session = Depends(get_db)):
    try:
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate rating
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
            is_read=0  # New books are not read by default
        )
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book
    except Exception as e:
        db.rollback()
        print(f"Error creating book: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create book: {str(e)}")

@app.get("/users/{user_id}/books", response_model=List[BookResponse])
async def get_user_books(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        books = db.query(Book).filter(Book.user_id == user_id).all()
        return books
    except Exception as e:
        print(f"Error fetching user books: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch books: {str(e)}")

@app.get("/users/{user_id}/read-books", response_model=List[BookResponse])
async def get_user_read_books(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        read_books = db.query(Book).filter(Book.user_id == user_id, Book.is_read == 1).all()
        return read_books
    except Exception as e:
        print(f"Error fetching read books: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch read books: {str(e)}")

@app.put("/books/{book_id}/mark-read")
async def mark_book_as_read(book_id: int, rating: int, db: Session = Depends(get_db)):
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Validate rating
        if rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        book.is_read = 1
        book.rating = rating
        db.commit()
        
        return {"message": f"Book '{book.title}' marked as read with rating {rating}"}
    except Exception as e:
        db.rollback()
        print(f"Error marking book as read: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to mark book as read: {str(e)}")

@app.get("/users/{user_id}/stats", response_model=UserStatsResponse)
async def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Only count read books for statistics
    read_books = db.query(Book).filter(Book.user_id == user_id, Book.is_read == 1).all()
    
    if not read_books:
        return UserStatsResponse(
            user=user,
            total_books=0,
            favorite_genre="No books read yet",
            genre_counts={},
            books=[]
        )
    
    # Analyze genre preferences from read books only
    genres = [book.genre for book in read_books]
    genre_counts = dict(Counter(genres))
    favorite_genre = max(genre_counts, key=genre_counts.get)
    
    return UserStatsResponse(
        user=user,
        total_books=len(read_books),
        favorite_genre=favorite_genre,
        genre_counts=genre_counts,
        books=read_books
    )

@app.get("/users/{user_id}/recommendations", response_model=RecommendationResponse)
async def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Step 1: Identify books already read by the user
    user_read_books = db.query(Book).filter(Book.user_id == user_id, Book.is_read == 1).all()
    user_book_titles = {book.title.lower() for book in user_read_books}
    
    if not user_read_books:
        # If no books, recommend popular genres
        all_books = db.query(Book).all()
        if all_books:
            all_genres = [book.genre for book in all_books]
            genre_counts = dict(Counter(all_genres))
            recommended_genre = max(genre_counts, key=genre_counts.get)
            suggested_books = db.query(Book).filter(Book.genre == recommended_genre).limit(5).all()
            
            return RecommendationResponse(
                recommended_genre=recommended_genre,
                reason="Based on popular genres in our database",
                suggested_books=suggested_books
            )
        else:
            return RecommendationResponse(
                recommended_genre="Fiction",
                reason="No books in database yet",
                suggested_books=[]
            )
    
    # Step 2: Determine the user's favorite genre from past reads
    user_genres = [book.genre for book in user_read_books]
    genre_counts = dict(Counter(user_genres))
    favorite_genre = max(genre_counts, key=genre_counts.get)
    
    # Step 3: Suggest books in favorite genre the user hasn't read yet
    content_based_books = db.query(Book).filter(
        Book.genre == favorite_genre,
        Book.user_id != user_id,  # Books from other users
        ~Book.title.in_(user_book_titles)
    ).all()
    
    # Step 4: Recommend books read by similar users (collaborative filtering)
    collaborative_books = []
    
    # Find users with similar reading patterns
    all_users = db.query(User).filter(User.id != user_id).all()
    similar_users = []
    
    for other_user in all_users:
        other_user_books = db.query(Book).filter(Book.user_id == other_user.id).all()
        if not other_user_books:
            continue
            
        # Calculate similarity based on genre overlap
        other_genres = [book.genre for book in other_user_books]
        other_genre_counts = dict(Counter(other_genres))
        
        # Calculate Jaccard similarity for genres
        user_genre_set = set(genre_counts.keys())
        other_genre_set = set(other_genre_counts.keys())
        
        if user_genre_set and other_genre_set:
            intersection = user_genre_set.intersection(other_genre_set)
            union = user_genre_set.union(other_genre_set)
            similarity = len(intersection) / len(union) if union else 0
            
            if similarity > 0.3:  # Threshold for similarity
                similar_users.append((other_user.id, similarity))
    
    # Get highly-rated books from similar users
    for similar_user_id, similarity in similar_users:
        similar_user_books = db.query(Book).filter(
            Book.user_id == similar_user_id,
            Book.rating >= 4,  # Only highly-rated books
            ~Book.title.in_(user_book_titles)
        ).all()
        collaborative_books.extend(similar_user_books)
    
    # Step 5: Merge results, remove duplicates, and return a list with cover images and ratings
    all_suggested_books = []
    
    # Add content-based recommendations (weighted by genre preference)
    for book in content_based_books:
        all_suggested_books.append((book, 1.0))  # Base weight for content-based
    
    # Add collaborative recommendations (weighted by similarity)
    for book in collaborative_books:
        # Find the similarity score for this book's user
        book_user_similarity = next((sim for uid, sim in similar_users if uid == book.user_id), 0.5)
        all_suggested_books.append((book, book_user_similarity))
    
    # Remove duplicates and sort by weight
    seen_books = set()
    unique_books = []
    
    for book, weight in all_suggested_books:
        if book.id not in seen_books:
            seen_books.add(book.id)
            unique_books.append((book, weight))
    
    # Sort by weight (similarity + content preference) and rating
    unique_books.sort(key=lambda x: (x[1], x[0].rating), reverse=True)
    
    # Take top 5 recommendations
    final_books = [book for book, weight in unique_books[:5]]
    
    # If not enough recommendations, add popular books from other genres
    if len(final_books) < 5:
        remaining_books = db.query(Book).filter(
            Book.user_id != user_id,
            ~Book.title.in_(user_book_titles),
            ~Book.id.in_([book.id for book in final_books])
        ).order_by(Book.rating.desc()).limit(5 - len(final_books)).all()
        final_books.extend(remaining_books)
    
    return RecommendationResponse(
        recommended_genre=favorite_genre,
        reason=f"Based on your preference for {favorite_genre} books and similar users' recommendations",
        suggested_books=final_books
    )

@app.get("/books/", response_model=List[BookResponse])
async def get_all_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    return books

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
