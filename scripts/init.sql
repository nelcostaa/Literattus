-- ================================================================
-- Literattus Database Schema - Production Ready
-- Aligned with professor's PDF requirements (Projeto BD - Entrega 1)
-- ================================================================

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS literattus CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the database
USE literattus;

-- ================================================================
-- TABLE: usuarios (Users)
-- ================================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    REDACTED VARCHAR(255) NOT NULL COMMENT 'Hashed REDACTED with bcrypt',
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    avatar VARCHAR(500) NULL,
    bio TEXT NULL,
    phone VARCHAR(20) UNIQUE NULL,
    birthdate DATE NULL,
    authorization ENUM('LEITOR', 'ADMIN', 'MODERADOR', 'ADMIN_SISTEMA') NOT NULL DEFAULT 'LEITOR',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_active (is_active),
    INDEX idx_authorization (authorization)
) ENGINE=InnoDB COMMENT='User accounts and profiles';

-- ================================================================
-- TABLE: livros (Books)
-- Uses Google Books ID as PRIMARY KEY per requirements
-- ================================================================
CREATE TABLE IF NOT EXISTS books (
    id VARCHAR(12) PRIMARY KEY COMMENT 'Google Books API ID (max 12 chars)',
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    description TEXT NULL,
    cover_image VARCHAR(2048) NULL COMMENT 'URL to cover image',
    isbn VARCHAR(13) UNIQUE NULL COMMENT 'ISBN-13',
    published_date DATE NULL,
    page_count INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_title (title),
    INDEX idx_author (author),
    INDEX idx_isbn (isbn)
) ENGINE=InnoDB COMMENT='Book catalog with Google Books integration';

-- ================================================================
-- TABLE: clubes (Book Clubs)
-- ================================================================
CREATE TABLE IF NOT EXISTS clubs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT NULL,
    cover_image VARCHAR(2048) NULL,
    is_private BOOLEAN NOT NULL DEFAULT FALSE,
    created_by_id INT NOT NULL,
    max_members INT NOT NULL DEFAULT 50,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_name (name),
    INDEX idx_created_by (created_by_id),
    INDEX idx_private (is_private)
) ENGINE=InnoDB COMMENT='Book clubs';

-- ================================================================
-- TABLE: club_members (Club Memberships)
-- ================================================================
CREATE TABLE IF NOT EXISTS club_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    club_id INT NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'member' COMMENT 'member, admin, owner',
    joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE,
    UNIQUE KEY uq_user_club (user_id, club_id),
    INDEX idx_user (user_id),
    INDEX idx_club (club_id),
    INDEX idx_role (role)
) ENGINE=InnoDB COMMENT='Club membership with roles';

-- ================================================================
-- TABLE: club_books (Club Reading Lists)
-- NEW TABLE - Resolves "cannot know which books are in which club"
-- ================================================================
CREATE TABLE IF NOT EXISTS club_books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    club_id INT NOT NULL,
    book_id VARCHAR(12) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'planned' COMMENT 'planned, current, completed, voted',
    added_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME NULL,
    completed_at DATETIME NULL,
    FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    UNIQUE KEY uq_club_book (club_id, book_id),
    INDEX idx_club (club_id),
    INDEX idx_book (book_id),
    INDEX idx_status (status)
) ENGINE=InnoDB COMMENT='Books being read/discussed in each club';

-- ================================================================
-- TABLE: reading_progress (User Reading Progress)
-- ================================================================
CREATE TABLE IF NOT EXISTS reading_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id VARCHAR(12) NOT NULL,
    club_id INT NULL COMMENT 'Optional: for club reading challenges',
    status VARCHAR(50) NOT NULL DEFAULT 'not_started' COMMENT 'not_started, reading, completed, abandoned',
    current_page INT NOT NULL DEFAULT 0,
    progress_percentage DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    rating TINYINT NULL COMMENT 'User rating 1-5 stars',
    review TEXT NULL COMMENT 'User review',
    started_at DATETIME NULL,
    completed_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE SET NULL,
    UNIQUE KEY uq_user_book (user_id, book_id),
    INDEX idx_user (user_id),
    INDEX idx_book (book_id),
    INDEX idx_club (club_id),
    INDEX idx_status (status)
) ENGINE=InnoDB COMMENT='User reading progress and reviews';

-- ================================================================
-- TABLE: discussions (Discussion Topics)
-- UPDATED: Added book_id FK - Resolves "cannot know which book is being discussed"
-- ================================================================
CREATE TABLE IF NOT EXISTS discussions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    club_id INT NOT NULL,
    user_id INT NOT NULL,
    book_id VARCHAR(12) NOT NULL COMMENT 'Book being discussed',
    parent_id INT NULL COMMENT 'For nested replies',
    title VARCHAR(300) NULL COMMENT 'Only for top-level discussions',
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES discussions(id) ON DELETE CASCADE,
    INDEX idx_club (club_id),
    INDEX idx_user (user_id),
    INDEX idx_book (book_id),
    INDEX idx_parent (parent_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB COMMENT='Discussion topics and replies';

-- ================================================================
-- SAMPLE DATA (from PDF requirements)
-- ================================================================

-- Insert sample users (usuarios)
INSERT IGNORE INTO users (id, email, username, REDACTED, first_name, last_name, bio, birthdate, authorization) VALUES
(1, 'ana.silva@email.com', 'anasilva', '$2a$10$f/..hash..', 'Ana', 'Silva', 'Leitora ávida e fã de ficção científica.', '1990-05-15', 'ADMIN'),
(2, 'bruno.costa@email.com', 'brunocosta', '$2a$10$f/..hash..', 'Bruno', 'Costa', 'Apaixonado por clássicos da literatura.', '1988-11-20', 'LEITOR'),
(3, 'carla.mendes@email.com', 'carlamendes', '$2a$10$f/..hash..', 'Carla', 'Mendes', 'Explorando o mundo da fantasia.', '1995-02-10', 'LEITOR'),
(4, 'diogo.martins@email.com', 'diogomartins', '$2a$10$f/..hash..', 'Diogo', 'Martins', 'Interessado em não-ficção e história.', '1992-09-03', 'LEITOR'),
(5, 'elena.ferreira@email.com', 'elenaferreira', '$2a$10$f/..hash..', 'Elena', 'Ferreira', 'Amante de romances e poesia.', '1998-07-25', 'LEITOR'),
(6, 'fabio.gomes@email.com', 'fabiogomes', '$2a$10$f/..hash..', 'Fábio', 'Gomes', 'Devorador de livros de mistério e suspense.', '1985-12-30', 'LEITOR'),
(7, 'helena.alves@email.com', 'helenaalves', '$2a$10$f/..hash..', 'Helena', 'Alves', 'Aventureira literária.', '1991-04-12', 'LEITOR'),
(8, 'igor.santos@email.com', 'igorsantos', '$2a$10$f/..hash..', 'Igor', 'Santos', 'Foco em desenvolvimento pessoal e filosofia.', '1993-08-08', 'LEITOR'),
(9, 'joana.pereira@email.com', 'joanapereira', '$2a$10$f/..hash..', 'Joana', 'Pereira', 'Leitora de biografias e memórias.', '1989-06-18', 'LEITOR'),
(10, 'luis.oliveira@email.com', 'luisoliveira', '$2a$10$f/..hash..', 'Luís', 'Oliveira', 'Descobrindo novos autores.', '1997-01-22', 'LEITOR');

-- Insert sample books (livros) - using Google Books IDs as primary key
INSERT IGNORE INTO books (id, title, author, description, isbn, published_date, page_count) VALUES
('U799AY3yfqcC', 'O Hobbit', 'J.R.R. Tolkien', 'A história de como um Baggins teve uma aventura e se viu a fazer e a dizer coisas totalmente inesperadas.', '9780547928227', '1937-09-21', 320),
('kotPYEqx7kMC', '1984', 'George Orwell', 'Numa sociedade totalitária, Winston Smith arrisca a sua vida ao desafiar o poder omnipresente do Grande Irmão.', '9780451524935', '1949-06-08', 328),
('p1MULH7JsTQC', 'Duna', 'Frank Herbert', 'A história de Paul Atreides e a ambição da sua família para concretizar o sonho mais antigo da humanidade no planeta deserto de Arrakis.', '9780441013593', '1965-08-01', 412),
('s1gVAAAAYAAJ', 'Orgulho e Preconceito', 'Jane Austen', 'Um romance clássico sobre costumes, casamento e a complexidade das relações sociais na Inglaterra do século XIX.', '9780141439518', '1813-01-28', 279),
('PGR2AwAAQBAJ', 'O Sol é Para Todos', 'Harper Lee', 'Uma história sobre injustiça racial e a perda da inocência no sul dos Estados Unidos, contada através dos olhos de uma criança.', '9780061120084', '1960-07-11', 324),
('HestSXO362YC', 'O Grande Gatsby', 'F. Scott Fitzgerald', 'O conto do fabulosamente rico Jay Gatsby e do seu amor pela bela Daisy Buchanan, na Long Island da Era do Jazz.', '9780743273565', '1925-04-10', 180),
('pgPWOaOctq8C', 'Cem Anos de Solidão', 'Gabriel García Márquez', 'A ascensão e queda da mítica cidade de Macondo através da história da família Buendía.', '9780060883287', '1967-05-30', 417),
('wrOQLV6xB-wC', 'Harry Potter e a Pedra Filosofal', 'J.K. Rowling', 'Um jovem rapaz com um grande destino prova o seu valor enquanto frequenta a Escola de Magia e Bruxaria de Hogwarts.', '9780590353427', '1997-06-26', 309),
('j--EMdEfmbkC', 'À Espera no Centeio', 'J.D. Salinger', 'A história de Holden Caulfield, um adolescente que lida com a angústia e a alienação após ser expulso da escola.', '9780316769488', '1951-07-16', 224),
('yl4dILkcqm4C', 'O Senhor dos Anéis', 'J.R.R. Tolkien', 'A saga épica da demanda para destruir o Um Anel e derrotar o Senhor das Trevas, Sauron.', '9780618640157', '1954-07-29', 1178);

-- Insert sample clubs (clubes)
INSERT IGNORE INTO clubs (id, name, description, is_private, created_by_id) VALUES
(1, 'Clube da Ficção Científica', 'Explorando galáxias distantes e futuros alternativos, um livro de cada vez.', FALSE, 1),
(2, 'Clássicos para Sempre', 'Dedicado à leitura e discussão dos grandes clássicos da literatura mundial.', FALSE, 2),
(3, 'A Sociedade dos Leitores de Fantasia', 'Um refúgio para todos os que amam dragões, magia e mundos épicos.', TRUE, 3),
(4, 'Mentes Curiosas', 'Focado em livros de não-ficção, ciência, história e filosofia.', FALSE, 4),
(5, 'Páginas de Romance', 'Um clube para os românticos incuráveis.', FALSE, 5),
(6, 'Detetives Literários', 'Resolvemos os mistérios e suspenses mais intrigantes da literatura.', TRUE, 6),
(7, 'Aventura em Cada Página', 'Para quem ama uma boa história de ação e aventura.', FALSE, 1),
(8, 'Leituras Filosóficas', 'Discussões profundas sobre as grandes questões da vida através dos livros.', FALSE, 8),
(9, 'Biografias que Inspiram', 'Conhecendo a vida e o legado de grandes personalidades.', FALSE, 9),
(10, 'Novos Horizontes', 'Dedicado a descobrir e apoiar autores contemporâneos.', TRUE, 10);

-- Insert sample club members (clubes_membros)
INSERT IGNORE INTO club_members (user_id, club_id, role) VALUES
(1, 1, 'owner'),
(2, 1, 'member'),
(3, 1, 'member'),
(2, 2, 'owner'),
(5, 2, 'member'),
(3, 3, 'owner'),
(7, 3, 'member'),
(4, 4, 'owner'),
(8, 4, 'member'),
(5, 5, 'owner'),
(6, 6, 'owner'),
(1, 6, 'member'),
(1, 7, 'owner'),
(8, 8, 'owner'),
(9, 9, 'owner'),
(10, 10, 'owner');

-- Insert sample club books (NEW - resolves missing club-book relationship)
INSERT IGNORE INTO club_books (club_id, book_id, status) VALUES
(1, 'p1MULH7JsTQC', 'current'),  -- Ficção Científica reading Duna
(1, 'kotPYEqx7kMC', 'completed'), -- Already read 1984
(2, 's1gVAAAAYAAJ', 'current'),  -- Clássicos reading Orgulho e Preconceito
(3, 'wrOQLV6xB-wC', 'current'),  -- Fantasia reading Harry Potter
(3, 'yl4dILkcqm4C', 'planned'),  -- Planning to read Senhor dos Anéis
(7, 'U799AY3yfqcC', 'current');  -- Aventura reading O Hobbit

-- Insert sample reading progress (progressos_leitura)
INSERT IGNORE INTO reading_progress (user_id, book_id, status, rating) VALUES
(1, 'p1MULH7JsTQC', 'completed', 5),
(1, 'U799AY3yfqcC', 'reading', NULL),
(2, 's1gVAAAAYAAJ', 'completed', 5),
(2, 'PGR2AwAAQBAJ', 'completed', 4),
(3, 'wrOQLV6xB-wC', 'reading', NULL),
(3, 'yl4dILkcqm4C', 'not_started', NULL),
(4, 'kotPYEqx7kMC', 'completed', 5),
(5, 's1gVAAAAYAAJ', 'not_started', NULL),
(6, 'j--EMdEfmbkC', 'completed', 3),
(7, 'U799AY3yfqcC', 'completed', 5),
(8, 'pgPWOaOctq8C', 'reading', NULL),
(9, 'PGR2AwAAQBAJ', 'not_started', NULL),
(10, 'HestSXO362YC', 'completed', 4),
(1, 'kotPYEqx7kMC', 'not_started', NULL),
(2, 'p1MULH7JsTQC', 'not_started', NULL);

-- Insert sample discussions (topicos_discussao) - NOW with book_id
INSERT IGNORE INTO discussions (title, content, user_id, club_id, book_id) VALUES
('A complexidade moral de Paul Atreides', 'O que acharam do arco de transformação do Paul no primeiro livro de Duna? Ele é um herói ou um anti-herói?', 1, 1, 'p1MULH7JsTQC'),
('O simbolismo do "Big Brother"', 'Para além da vigilância, que outros simbolismos vocês veem na figura do Grande Irmão em 1984?', 4, 1, 'kotPYEqx7kMC'),
('A crítica social em Orgulho e Preconceito', 'A escrita de Jane Austen ainda é relevante para discutir as pressões sociais sobre as mulheres hoje?', 2, 2, 's1gVAAAAYAAJ'),
('O Hobbit vs O Senhor dos Anéis', 'Qual dos dois preferem e porquê? O tom mais leve de O Hobbit ou a escala épica de O Senhor dos Anéis?', 7, 7, 'U799AY3yfqcC'),
('A coragem de Atticus Finch', 'Discutam a cena do julgamento em "O Sol é Para Todos". É uma das personagens mais íntegras da literatura?', 2, 2, 'PGR2AwAAQBAJ'),
('O sistema de magia em Harry Potter', 'Quais são as vossas regras de magia preferidas e quais acham menos consistentes?', 3, 3, 'wrOQLV6xB-wC'),
('O final de Cem Anos de Solidão', 'Fiquei impressionado com o final. Como interpretaram a última profecia?', 8, 8, 'pgPWOaOctq8C'),
('A "falsidade" do mundo adulto em À Espera no Centeio', 'Acham que a visão do Holden é ingénua ou precisa?', 6, 6, 'j--EMdEfmbkC'),
('O sonho americano em O Grande Gatsby', 'Gatsby alcançou o sonho americano ou foi destruído por ele?', 10, 10, 'HestSXO362YC'),
('A jornada de Bilbo', 'Qual foi o momento mais importante para o crescimento de Bilbo como personagem em O Hobbit?', 1, 7, 'U799AY3yfqcC');

-- ================================================================
-- VERIFICATION QUERIES (from PDF requirements)
-- ================================================================

-- Show all tables
SHOW TABLES;

-- Show table structures
DESCRIBE users;
DESCRIBE books;
DESCRIBE clubs;
DESCRIBE club_members;
DESCRIBE club_books;
DESCRIBE reading_progress;
DESCRIBE discussions;
