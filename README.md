# 📚 Personalized Book Recommendation System

A modern web application that provides personalized book recommendations based on user reading habits and genre preferences. Built with FastAPI, React, and SQLite.

## ✨ Features

- **User Management**: Add and select multiple users
- **Book Management**: Add books with title, author, genre, and cover image
- **Smart Recommendations**: AI-powered recommendations based on reading patterns
- **Genre Analysis**: Automatic analysis of user's favorite genres
- **Professional UI**: Modern, responsive design with great UX
- **Data Persistence**: SQLite database for reliable data storage

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation & Setup

1. **Clone or download the project**
   ```bash
   cd book-recommendation
   ```

2. **Start the Backend (FastAPI)**
   ```bash
   # Windows
   python start_backend.py
   
   # Linux/Mac
   python3 start_backend.py
   ```
   The backend will be available at `http://localhost:8000`

3. **Start the Frontend (React)**
   ```bash
   # Windows
   start_frontend.bat
   
   # Linux/Mac
   chmod +x start_frontend.sh
   ./start_frontend.sh
   ```
   The frontend will be available at `http://localhost:3000`

## 🏗️ Architecture

### Backend (FastAPI + SQLite)
- **Database**: SQLite with SQLAlchemy ORM
- **API**: RESTful API with FastAPI
- **Features**:
  - User management (CRUD operations)
  - Book management with user association
  - Genre analysis and statistics
  - Smart recommendation algorithm
  - CORS enabled for frontend integration

### Frontend (React)
- **Framework**: React 18 with modern hooks
- **Styling**: Custom CSS with professional design
- **Features**:
  - User selection and creation
  - Book addition with validation
  - Tabbed interface for read books and recommendations
  - Real-time statistics display
  - Responsive design for all devices

## 📊 How It Works

1. **User Creation**: Users can add their name to the system
2. **Book Addition**: Users can add books they've read (only when a user is selected)
3. **Genre Analysis**: The system analyzes reading patterns to identify favorite genres
4. **Recommendations**: Based on genre preferences, the system suggests new books
5. **Statistics**: Users can view their reading statistics and genre breakdown

## 🎯 Key Features

### User Validation
- Users must select an existing user or create a new one before adding books
- Alert messages guide users through the process
- Prevents orphaned book entries

### Smart Recommendations
- Analyzes user's reading history
- Identifies most-read genres
- Suggests books from preferred genres
- Falls back to popular books if no history exists

### Professional UI/UX
- Clean, modern design
- Responsive layout for all devices
- Loading states and error handling
- Intuitive navigation with tabs
- Visual feedback for all actions

## 🛠️ API Endpoints

### Users
- `GET /users/` - Get all users
- `POST /users/` - Create new user
- `GET /users/{user_id}` - Get specific user
- `GET /users/{user_id}/stats` - Get user statistics

### Books
- `GET /books/` - Get all books
- `POST /books/` - Add new book
- `GET /users/{user_id}/books` - Get user's books
- `GET /users/{user_id}/recommendations` - Get recommendations

## 📱 Screenshots

The application features:
- **Header**: Clean title with book icon
- **User Management**: Dropdown selection and new user creation
- **Book Form**: Input fields for title, author, genre, and cover URL
- **Statistics**: Visual display of reading habits
- **Tabs**: Switch between "Read Books" and "Recommended Books"
- **Book Cards**: Beautiful display of book information with covers

## 🔧 Development

### Backend Development
```bash
cd backend
pip install -r ../requirements.txt
python main.py
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### Database
The SQLite database is automatically created in the backend directory. It includes:
- `users` table: User information
- `books` table: Book information with user relationships

## 🎨 Customization

### Adding New Genres
The system automatically detects and works with any genre you add. No configuration needed!

### Styling
- Modify `frontend/src/index.css` for global styles
- Modify `frontend/src/App.css` for component-specific styles
- All styles are responsive and professional

### Recommendation Algorithm
The recommendation system can be enhanced by modifying the logic in `backend/main.py` in the `get_recommendations` endpoint.

## 🚀 Deployment

### Backend Deployment
1. Install dependencies: `pip install -r requirements.txt`
2. Run with production server: `uvicorn main:app --host 0.0.0.0 --port 8000`

### Frontend Deployment
1. Build the app: `npm run build`
2. Serve the `build` folder with any static file server

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions, please create an issue in the repository.

---

**Happy Reading! 📖✨**
