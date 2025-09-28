import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'https://book-recommendation-app-8.onrender.com';


function App() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [newUserName, setNewUserName] = useState('');
  const [books, setBooks] = useState([]);
  const [readBooks, setReadBooks] = useState([]);
  const [userStats, setUserStats] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [activeTab, setActiveTab] = useState('library');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Mark as read form state
  const [markReadForm, setMarkReadForm] = useState({
    bookId: '',
    rating: 5
  });

  // Book form state
  const [bookForm, setBookForm] = useState({
    title: '',
    author: '',
    genre: '',
    cover_url: '',
    rating: 0
  });

  // Fetch users on component mount
  useEffect(() => {
    fetchUsers();
  }, []);

  // Fetch user data when selected user changes
  useEffect(() => {
    if (selectedUser) {
      fetchUserBooks();
      fetchReadBooks();
      fetchUserStats();
      fetchRecommendations();
    }
  }, [selectedUser]);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/users/`);
      setUsers(response.data);
    } catch (error) {
      setError('Failed to fetch users');
    }
  };

  const fetchUserBooks = async () => {
    if (!selectedUser) return;
    
    try {
      setLoading(true);
      console.log('Fetching books for user:', selectedUser);
      const response = await axios.get(`${API_BASE_URL}/users/${selectedUser}/books`);
      console.log('Fetched books:', response.data);
      setBooks(response.data);
    } catch (error) {
      console.error('Error fetching user books:', error);
      setError(`Failed to fetch user books: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchReadBooks = async () => {
    if (!selectedUser) return;
    
    try {
      const response = await axios.get(`${API_BASE_URL}/users/${selectedUser}/read-books`);
      console.log('Fetched read books:', response.data);
      setReadBooks(response.data);
    } catch (error) {
      console.error('Error fetching read books:', error);
      setError(`Failed to fetch read books: ${error.response?.data?.detail || error.message}`);
    }
  };

  const fetchUserStats = async () => {
    if (!selectedUser) return;
    
    try {
      const response = await axios.get(`${API_BASE_URL}/users/${selectedUser}/stats`);
      setUserStats(response.data);
    } catch (error) {
      setError('Failed to fetch user statistics');
    }
  };

  const fetchRecommendations = async () => {
    if (!selectedUser) return;
    
    try {
      const response = await axios.get(`${API_BASE_URL}/users/${selectedUser}/recommendations`);
      setRecommendations(response.data);
    } catch (error) {
      setError('Failed to fetch recommendations');
    }
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    if (!newUserName.trim()) {
      setError('Please enter a user name');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE_URL}/users/`, {
        name: newUserName.trim()
      });
      
      setUsers([...users, response.data]);
      setNewUserName('');
      setSuccess(`User "${response.data.name}" added successfully!`);
      setError('');
    } catch (error) {
      if (error.response?.status === 400) {
        setError('User already exists');
      } else {
        setError('Failed to add user');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAddBook = async (e) => {
    e.preventDefault();
    
    // Check if user is selected
    if (!selectedUser) {
      setError('Please select a user or add a new user before adding books');
      return;
    }

    if (!bookForm.title.trim() || !bookForm.author.trim() || !bookForm.genre.trim()) {
      setError('Please fill in all required fields (Title, Author, Genre)');
      return;
    }

    try {
      setLoading(true);
      console.log('Adding book with data:', bookForm);
      console.log('User ID:', selectedUser);
      
      const response = await axios.post(`${API_BASE_URL}/books/?user_id=${selectedUser}`, {
        ...bookForm
      });
      
      console.log('Book added successfully:', response.data);
      setBooks([...books, response.data]);
      setBookForm({ title: '', author: '', genre: '', cover_url: '', rating: 0 });
      setSuccess(`Book "${response.data.title}" added successfully!`);
      setError('');
      
      // Refresh user stats and recommendations
      fetchUserStats();
      fetchRecommendations();
    } catch (error) {
      console.error('Error adding book:', error);
      console.error('Error response:', error.response?.data);
      setError(`Failed to add book: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (e) => {
    e.preventDefault();
    
    if (!markReadForm.bookId) {
      setError('Please select a book to mark as read');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.put(`${API_BASE_URL}/books/${markReadForm.bookId}/mark-read?rating=${markReadForm.rating}`);
      
      setSuccess(response.data.message);
      setError('');
      setMarkReadForm({ bookId: '', rating: 5 });
      
      // Refresh all data
      fetchUserBooks();
      fetchReadBooks();
      fetchUserStats();
      fetchRecommendations();
    } catch (error) {
      console.error('Error marking book as read:', error);
      setError(`Failed to mark book as read: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleUserSelect = (e) => {
    setSelectedUser(e.target.value);
    setError('');
    setSuccess('');
  };

  const clearMessages = () => {
    setError('');
    setSuccess('');
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="container">
          <div className="header-content">
            <div className="header-icon">
              📚
            </div>
            <h1>Personalized Book Recommendations</h1>
          </div>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          {/* User Management Section */}
          <section className="user-section">
            <div className="card">
              <h2>User Management</h2>
              
              <div className="user-controls">
                <div className="form-group">
                  <label className="form-label">Select User:</label>
                  <select 
                    className="form-select" 
                    value={selectedUser} 
                    onChange={handleUserSelect}
                  >
                    <option value="">--Choose User--</option>
                    {users.map(user => (
                      <option key={user.id} value={user.id}>
                        {user.name}
                      </option>
                    ))}
                  </select>
                </div>

                <form onSubmit={handleAddUser} className="add-user-form">
                  <div className="form-group">
                    <label className="form-label">New user name:</label>
                    <div className="input-group">
                      <input
                        type="text"
                        className="form-input"
                        value={newUserName}
                        onChange={(e) => setNewUserName(e.target.value)}
                        placeholder="Enter new user name"
                      />
                      <button 
                        type="submit" 
                        className="btn btn-success"
                        disabled={loading}
                      >
                        {loading ? <span className="spinner"></span> : 'Add User'}
                      </button>
                    </div>
                  </div>
                </form>
              </div>
            </div>
          </section>

          {/* Book Management Section */}
          <section className="book-section">
            <div className="card">
              <h2>Add New Book</h2>
              
              <form onSubmit={handleAddBook} className="book-form">
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Book Title *</label>
                    <input
                      type="text"
                      className="form-input"
                      value={bookForm.title}
                      onChange={(e) => setBookForm({...bookForm, title: e.target.value})}
                      placeholder="Enter book title"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Author *</label>
                    <input
                      type="text"
                      className="form-input"
                      value={bookForm.author}
                      onChange={(e) => setBookForm({...bookForm, author: e.target.value})}
                      placeholder="Enter author name"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Genre *</label>
                    <input
                      type="text"
                      className="form-input"
                      value={bookForm.genre}
                      onChange={(e) => setBookForm({...bookForm, genre: e.target.value})}
                      placeholder="Enter genre"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Cover URL</label>
                    <input
                      type="url"
                      className="form-input"
                      value={bookForm.cover_url}
                      onChange={(e) => setBookForm({...bookForm, cover_url: e.target.value})}
                      placeholder="Enter cover image URL (optional)"
                    />
                  </div>

                </div>

                <button 
                  type="submit" 
                  className="add-book-button"
                  disabled={loading}
                >
                  {loading ? <span className="spinner"></span> : 'Add Book'}
                </button>
              </form>
            </div>
          </section>

          {/* Messages */}
          {error && (
            <div className="alert alert-error" onClick={clearMessages}>
              {error}
            </div>
          )}
          
          {success && (
            <div className="alert alert-success" onClick={clearMessages}>
              {success}
            </div>
          )}

          {/* User Stats */}
          {userStats && (
            <section className="stats-section">
              <div className="stats-card">
                <h3 className="stats-title">Reading Statistics for {userStats.user.name}</h3>
                <div className="stats-grid">
                  <div className="stat-item">
                    <div className="stat-number">{userStats.total_books}</div>
                    <div className="stat-label">Books Read</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-number">{userStats.favorite_genre}</div>
                    <div className="stat-label">Favorite Genre</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-number">{Object.keys(userStats.genre_counts).length}</div>
                    <div className="stat-label">Genres Explored</div>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Mark as Read Section */}
          {selectedUser && books.length > 0 && (
            <section className="mark-read-section">
              <div className="card">
                <h2>Mark Book as Read</h2>
                <form onSubmit={handleMarkAsRead} className="mark-read-form">
                  <div className="form-row">
                    <div className="form-group">
                      <label className="form-label">Choose Book:</label>
                      <select
                        className="form-select"
                        value={markReadForm.bookId}
                        onChange={(e) => setMarkReadForm({...markReadForm, bookId: e.target.value})}
                      >
                        <option value="">--Choose Book--</option>
                        {books.filter(book => book.is_read === 0).map(book => (
                          <option key={book.id} value={book.id}>
                            {book.title} by {book.author}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="form-group">
                      <label className="form-label">Rate:</label>
                      <select
                        className="form-select"
                        value={markReadForm.rating}
                        onChange={(e) => setMarkReadForm({...markReadForm, rating: parseInt(e.target.value)})}
                      >
                        <option value={5}>⭐⭐⭐⭐⭐ (5 stars)</option>
                        <option value={4}>⭐⭐⭐⭐ (4 stars)</option>
                        <option value={3}>⭐⭐⭐ (3 stars)</option>
                        <option value={2}>⭐⭐ (2 stars)</option>
                        <option value={1}>⭐ (1 star)</option>
                      </select>
                    </div>
                  </div>
                  <button 
                    type="submit" 
                    className="btn btn-success"
                    disabled={loading}
                  >
                    {loading ? <span className="spinner"></span> : 'Mark as Read'}
                  </button>
                </form>
              </div>
            </section>
          )}

          {/* Tabs */}
          {selectedUser && (
            <section className="tabs-section">
              <div className="tabs">
                <button 
                  className={`tab ${activeTab === 'library' ? 'active' : ''} tab-button`}
                  onClick={() => setActiveTab('library')}
                >
                  My Library
                </button>
                <button 
                  className={`tab ${activeTab === 'read' ? 'active' : ''} tab-button`}
                  onClick={() => setActiveTab('read')}
                >
                  Read Books
                </button>
                <button 
                  className={`tab ${activeTab === 'recommendations' ? 'active' : ''} tab-button`}
                  onClick={() => setActiveTab('recommendations')}
                >
                  Recommended Books
                </button>
              </div>

              {/* My Library Tab */}
              {activeTab === 'library' && (
                <div className="tab-content">
                  <h3>My Library - All Books</h3>
                  
                  {loading ? (
                    <div className="loading">
                      <span className="spinner"></span>
                      Loading books...
                    </div>
                  ) : books.length > 0 ? (
                    <div className="grid grid-3">
                      {books.map(book => (
                        <div key={book.id} className="book-card">
                          <img 
                            src={book.cover_url || ''} 
                            alt={book.title}
                            className="book-cover"
                            loading="lazy"
                            onLoad={(e) => {
                              e.target.style.opacity = '1';
                            }}
                            onError={(e) => {
                              e.target.style.display = 'none';
                            }}
                            style={{ opacity: 0, transition: 'opacity 0.3s ease' }}
                          />
                          <div className="book-card-content">
                            <h4 className="book-title">{book.title}</h4>
                            <p className="book-author">by {book.author}</p>
                            <div className="book-status">
                              {book.is_read === 1 ? (
                                <span className="status-read">✅ Read</span>
                              ) : (
                                <span className="status-unread">📖 Unread</span>
                              )}
                            </div>
                            {book.is_read === 1 && (
                              <div className="book-rating">
                                <span className="rating-stars">
                                  {'⭐'.repeat(book.rating)}
                                  <span className="rating-text">({book.rating}/5)</span>
                                </span>
                              </div>
                            )}
                            <span className="book-genre">{book.genre}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-state">
                      <div className="empty-state-icon">📚</div>
                      <h4 className="empty-state-title">No books in library yet</h4>
                      <p className="empty-state-description">
                        Add books to your library to start building your collection.
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Read Books Tab */}
              {activeTab === 'read' && (
                <div className="tab-content">
                  <h3>Books Read by {users.find(u => u.id === parseInt(selectedUser))?.name}</h3>
                  
                  {loading ? (
                    <div className="loading">
                      <span className="spinner"></span>
                      Loading books...
                    </div>
                  ) : readBooks.length > 0 ? (
                    <div className="grid grid-3">
                      {readBooks.map(book => (
                        <div key={book.id} className="book-card">
                          <img 
                            src={book.cover_url || ''} 
                            alt={book.title}
                            className="book-cover"
                            loading="lazy"
                            onLoad={(e) => {
                              e.target.style.opacity = '1';
                            }}
                            onError={(e) => {
                              e.target.style.display = 'none';
                            }}
                            style={{ opacity: 0, transition: 'opacity 0.3s ease' }}
                          />
                          <div className="book-card-content">
                            <h4 className="book-title">{book.title}</h4>
                            <p className="book-author">by {book.author}</p>
                            <div className="book-rating">
                              <span className="rating-stars">
                                {'⭐'.repeat(book.rating)}
                                <span className="rating-text">({book.rating}/5)</span>
                              </span>
                            </div>
                            <span className="book-genre">{book.genre}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-state">
                      <div className="empty-state-icon">📖</div>
                      <h4 className="empty-state-title">No books read yet</h4>
                      <p className="empty-state-description">
                        Mark books as read to see your reading history and get personalized recommendations.
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Recommendations Tab */}
              {activeTab === 'recommendations' && (
                <div className="tab-content">
                  <h3>Recommended Books for {users.find(u => u.id === parseInt(selectedUser))?.name}</h3>
                  
                  {recommendations ? (
                    <div>
                      <div className="alert alert-info">
                        <strong>Recommendation:</strong> {recommendations.recommended_genre} - {recommendations.reason}
                      </div>
                      
                      {recommendations.suggested_books.length > 0 ? (
                        <div className="grid grid-3">
                          {recommendations.suggested_books.map(book => (
                            <div key={book.id} className="book-card">
                              <img 
                                src={book.cover_url || ''} 
                                alt={book.title}
                                className="book-cover"
                                loading="lazy"
                                onLoad={(e) => {
                                  e.target.style.opacity = '1';
                                }}
                                onError={(e) => {
                                  e.target.style.display = 'none';
                                }}
                                style={{ opacity: 0, transition: 'opacity 0.3s ease' }}
                              />
                              <div className="book-card-content">
                                <h4 className="book-title">{book.title}</h4>
                                <p className="book-author">by {book.author}</p>
                                <div className="book-rating">
                                  {book.rating > 0 ? (
                                    <span className="rating-stars">
                                      {'⭐'.repeat(book.rating)}
                                      <span className="rating-text">({book.rating}/5)</span>
                                    </span>
                                  ) : (
                                    <span className="no-rating">No rating</span>
                                  )}
                                </div>
                                <span className="book-genre">{book.genre}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="empty-state">
                          <div className="empty-state-icon">🔍</div>
                          <h4 className="empty-state-title">No recommendations available</h4>
                          <p className="empty-state-description">
                            Add more books to get better recommendations based on your reading preferences.
                          </p>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="loading">
                      <span className="spinner"></span>
                      Loading recommendations...
                    </div>
                  )}
                </div>
              )}
            </section>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
