-- Initialize Literattus Database Schema
-- This script runs automatically when MySQL container starts

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS literattus CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the database
USE literattus;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    REDACTED VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    avatar VARCHAR(500),
    bio TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_active (is_active)
);

-- Create books table
CREATE TABLE IF NOT EXISTS books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    google_books_id VARCHAR(50) UNIQUE,
    title VARCHAR(500) NOT NULL,
    authors TEXT,
    description TEXT,
    isbn VARCHAR(20),
    page_count INT,
    published_date DATE,
    categories TEXT,
    language VARCHAR(10) DEFAULT 'en',
    cover_image_url VARCHAR(1000),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_google_id (google_books_id),
    INDEX idx_title (title(100)),
    INDEX idx_isbn (isbn)
);

-- Create clubs table
CREATE TABLE IF NOT EXISTS clubs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created_by_id INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    max_members INT DEFAULT 50,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_created_by (created_by_id),
    INDEX idx_active (is_active)
);

-- Create club_members table
CREATE TABLE IF NOT EXISTS club_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    club_id INT NOT NULL,
    user_id INT NOT NULL,
    role ENUM('member', 'admin', 'moderator') DEFAULT 'member',
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_membership (club_id, user_id),
    INDEX idx_club (club_id),
    INDEX idx_user (user_id)
);

-- Create reading_progress table
CREATE TABLE IF NOT EXISTS reading_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    status ENUM('want_to_read', 'currently_reading', 'completed', 'abandoned') DEFAULT 'want_to_read',
    current_page INT DEFAULT 0,
    total_pages INT,
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    started_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_book (user_id, book_id),
    INDEX idx_user (user_id),
    INDEX idx_book (book_id),
    INDEX idx_status (status)
);

-- Create discussions table
CREATE TABLE IF NOT EXISTS discussions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    club_id INT NOT NULL,
    user_id INT NOT NULL,
    book_id INT,
    title VARCHAR(300) NOT NULL,
    content TEXT NOT NULL,
    is_pinned BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE SET NULL,
    INDEX idx_club (club_id),
    INDEX idx_user (user_id),
    INDEX idx_book (book_id),
    INDEX idx_pinned (is_pinned),
    INDEX idx_created (created_at)
);

-- Insert sample data for testing
INSERT IGNORE INTO users (email, REDACTED, first_name, last_name) VALUES
('admin@literattus.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Qz8K2', 'Admin', 'User'),
('test@literattus.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Qz8K2', 'Test', 'User');

INSERT IGNORE INTO books (title, authors, description, isbn) VALUES
('The Great Gatsby', 'F. Scott Fitzgerald', 'A classic American novel about the Jazz Age', '9780743273565'),
('To Kill a Mockingbird', 'Harper Lee', 'A story of racial injustice and childhood innocence', '9780061120084');

INSERT IGNORE INTO clubs (name, description, created_by_id) VALUES
('Classic Literature Club', 'A club for discussing classic literature', 1),
('Modern Fiction Club', 'A club for contemporary fiction discussions', 2);

-- Show tables created
SHOW TABLES;
