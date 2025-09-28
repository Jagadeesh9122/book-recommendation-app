#!/usr/bin/env python3
"""
Database reset script for Book Recommendation System
This will delete the existing database and create a fresh one with the new schema
"""

import os
import sqlite3

def reset_database():
    """Reset the database to fix schema issues"""
    db_path = "backend/book_recommendations.db"
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✅ Removed existing database: {db_path}")
    
    # Create new database with proper schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR UNIQUE NOT NULL
        )
    ''')
    
    # Create books table with rating column
    cursor.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR NOT NULL,
            author VARCHAR NOT NULL,
            genre VARCHAR NOT NULL,
            cover_url VARCHAR,
            user_id INTEGER NOT NULL,
            rating INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX ix_users_id ON users (id)')
    cursor.execute('CREATE INDEX ix_users_name ON users (name)')
    cursor.execute('CREATE INDEX ix_books_id ON books (id)')
    cursor.execute('CREATE INDEX ix_books_title ON books (title)')
    cursor.execute('CREATE INDEX ix_books_genre ON books (genre)')
    cursor.execute('CREATE INDEX ix_books_user_id ON books (user_id)')
    
    conn.commit()
    conn.close()
    
    print("✅ Created fresh database with new schema")
    print("✅ All tables and indexes created successfully")
    print("✅ Rating column included in books table")

if __name__ == "__main__":
    print("🔄 Resetting Book Recommendation Database...")
    print("=" * 50)
    reset_database()
    print("=" * 50)
    print("🎉 Database reset complete!")
    print("You can now start the backend server.")
