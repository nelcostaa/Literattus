-- ================================================================
-- Literattus Database - Triggers and Stored Procedures
-- ================================================================
-- This file contains:
-- 1. Audit log table for tracking changes
-- 2. Trigger to log changes to reading_progress table
-- 3. Stored procedure to get user reading statistics
-- ================================================================

USE literattus;

-- ================================================================
-- 1. AUDIT LOG TABLE
-- ================================================================
-- Tracks all changes (INSERT, UPDATE, DELETE) to important tables
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(64) NOT NULL COMMENT 'Name of the table that was modified',
    record_id VARCHAR(255) NOT NULL COMMENT 'ID of the record (can be INT or VARCHAR)',
    action VARCHAR(10) NOT NULL COMMENT 'INSERT, UPDATE, or DELETE',
    old_values JSON NULL COMMENT 'Previous values (for UPDATE/DELETE)',
    new_values JSON NULL COMMENT 'New values (for INSERT/UPDATE)',
    changed_by INT NULL COMMENT 'User ID who made the change (if available)',
    changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'When the change occurred',
    INDEX idx_table_name (table_name),
    INDEX idx_record_id (record_id),
    INDEX idx_action (action),
    INDEX idx_changed_at (changed_at),
    INDEX idx_changed_by (changed_by)
) ENGINE=InnoDB COMMENT='Audit log for tracking all database changes';

-- ================================================================
-- 2. TRIGGER: Log Reading Progress Changes
-- ================================================================
-- Automatically logs all INSERT, UPDATE, and DELETE operations on reading_progress table

DELIMITER $$

-- Trigger for INSERT operations
DROP TRIGGER IF EXISTS trg_reading_progress_insert$$
CREATE TRIGGER trg_reading_progress_insert
AFTER INSERT ON reading_progress
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (
        table_name,
        record_id,
        action,
        new_values,
        changed_at
    ) VALUES (
        'reading_progress',
        NEW.id,
        'INSERT',
        JSON_OBJECT(
            'id', NEW.id,
            'user_id', NEW.user_id,
            'book_id', NEW.book_id,
            'club_id', NEW.club_id,
            'status', NEW.status,
            'current_page', NEW.current_page,
            'progress_percentage', NEW.progress_percentage,
            'rating', NEW.rating,
            'started_at', NEW.started_at,
            'completed_at', NEW.completed_at,
            'created_at', NEW.created_at,
            'updated_at', NEW.updated_at
        ),
        NOW()
    );
END$$

-- Trigger for UPDATE operations
DROP TRIGGER IF EXISTS trg_reading_progress_update$$
CREATE TRIGGER trg_reading_progress_update
AFTER UPDATE ON reading_progress
FOR EACH ROW
BEGIN
    -- Only log if something actually changed
    IF (OLD.status != NEW.status OR 
        OLD.current_page != NEW.current_page OR 
        OLD.progress_percentage != NEW.progress_percentage OR
        OLD.rating != NEW.rating OR
        (OLD.rating IS NULL AND NEW.rating IS NOT NULL) OR
        (OLD.rating IS NOT NULL AND NEW.rating IS NULL) OR
        OLD.review != NEW.review OR
        (OLD.review IS NULL AND NEW.review IS NOT NULL) OR
        (OLD.review IS NOT NULL AND NEW.review IS NULL) OR
        OLD.started_at != NEW.started_at OR
        (OLD.started_at IS NULL AND NEW.started_at IS NOT NULL) OR
        (OLD.started_at IS NOT NULL AND NEW.started_at IS NULL) OR
        OLD.completed_at != NEW.completed_at OR
        (OLD.completed_at IS NULL AND NEW.completed_at IS NOT NULL) OR
        (OLD.completed_at IS NOT NULL AND NEW.completed_at IS NULL)) THEN
        
        INSERT INTO audit_log (
            table_name,
            record_id,
            action,
            old_values,
            new_values,
            changed_at
        ) VALUES (
            'reading_progress',
            NEW.id,
            'UPDATE',
            JSON_OBJECT(
                'id', OLD.id,
                'user_id', OLD.user_id,
                'book_id', OLD.book_id,
                'status', OLD.status,
                'current_page', OLD.current_page,
                'progress_percentage', OLD.progress_percentage,
                'rating', OLD.rating,
                'started_at', OLD.started_at,
                'completed_at', OLD.completed_at
            ),
            JSON_OBJECT(
                'id', NEW.id,
                'user_id', NEW.user_id,
                'book_id', NEW.book_id,
                'status', NEW.status,
                'current_page', NEW.current_page,
                'progress_percentage', NEW.progress_percentage,
                'rating', NEW.rating,
                'started_at', NEW.started_at,
                'completed_at', NEW.completed_at
            ),
            NOW()
        );
    END IF;
END$$

-- Trigger for DELETE operations
DROP TRIGGER IF EXISTS trg_reading_progress_delete$$
CREATE TRIGGER trg_reading_progress_delete
AFTER DELETE ON reading_progress
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (
        table_name,
        record_id,
        action,
        old_values,
        changed_at
    ) VALUES (
        'reading_progress',
        OLD.id,
        'DELETE',
        JSON_OBJECT(
            'id', OLD.id,
            'user_id', OLD.user_id,
            'book_id', OLD.book_id,
            'club_id', OLD.club_id,
            'status', OLD.status,
            'current_page', OLD.current_page,
            'progress_percentage', OLD.progress_percentage,
            'rating', OLD.rating,
            'started_at', OLD.started_at,
            'completed_at', OLD.completed_at,
            'created_at', OLD.created_at,
            'updated_at', OLD.updated_at
        ),
        NOW()
    );
END$$

DELIMITER ;

-- ================================================================
-- 3. STORED PROCEDURE: Get User Reading Statistics
-- ================================================================
-- Returns comprehensive reading statistics for a specific user
-- Useful for dashboard displays and user profiles

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_get_user_reading_stats$$

CREATE PROCEDURE sp_get_user_reading_stats(
    IN p_user_id INT
)
BEGIN
    DECLARE v_total_books INT DEFAULT 0;
    DECLARE v_reading_count INT DEFAULT 0;
    DECLARE v_completed_count INT DEFAULT 0;
    DECLARE v_not_started_count INT DEFAULT 0;
    DECLARE v_abandoned_count INT DEFAULT 0;
    DECLARE v_total_pages_read INT DEFAULT 0;
    DECLARE v_avg_rating DECIMAL(3,2) DEFAULT 0;
    DECLARE v_total_reviews INT DEFAULT 0;
    
    -- Count books by status
    SELECT 
        COUNT(*) INTO v_total_books
    FROM reading_progress
    WHERE user_id = p_user_id;
    
    SELECT 
        COUNT(*) INTO v_reading_count
    FROM reading_progress
    WHERE user_id = p_user_id AND status = 'reading';
    
    SELECT 
        COUNT(*) INTO v_completed_count
    FROM reading_progress
    WHERE user_id = p_user_id AND status = 'completed';
    
    SELECT 
        COUNT(*) INTO v_not_started_count
    FROM reading_progress
    WHERE user_id = p_user_id AND status = 'not_started';
    
    SELECT 
        COUNT(*) INTO v_abandoned_count
    FROM reading_progress
    WHERE user_id = p_user_id AND status = 'abandoned';
    
    -- Calculate total pages read (sum of current_page for completed books)
    SELECT 
        COALESCE(SUM(rp.current_page), 0) INTO v_total_pages_read
    FROM reading_progress rp
    INNER JOIN books b ON rp.book_id = b.id
    WHERE rp.user_id = p_user_id 
    AND rp.status IN ('reading', 'completed')
    AND b.page_count IS NOT NULL;
    
    -- Calculate average rating
    SELECT 
        COALESCE(AVG(rating), 0) INTO v_avg_rating
    FROM reading_progress
    WHERE user_id = p_user_id 
    AND rating IS NOT NULL;
    
    -- Count reviews
    SELECT 
        COUNT(*) INTO v_total_reviews
    FROM reading_progress
    WHERE user_id = p_user_id 
    AND review IS NOT NULL 
    AND review != '';
    
    -- Return results as a single row
    SELECT 
        p_user_id AS user_id,
        v_total_books AS total_books,
        v_reading_count AS reading_count,
        v_completed_count AS completed_count,
        v_not_started_count AS not_started_count,
        v_abandoned_count AS abandoned_count,
        v_total_pages_read AS total_pages_read,
        ROUND(v_avg_rating, 2) AS average_rating,
        v_total_reviews AS total_reviews;
END$$

DELIMITER ;

-- ================================================================
-- VERIFICATION QUERIES
-- ================================================================

-- Show the audit log table structure
DESCRIBE audit_log;

-- Show all triggers
SHOW TRIGGERS WHERE `Table` = 'reading_progress';

-- Show the stored procedure
SHOW CREATE PROCEDURE sp_get_user_reading_stats;

-- Test the stored procedure (example with user_id = 1)
-- CALL sp_get_user_reading_stats(1);

-- View recent audit log entries
-- SELECT * FROM audit_log ORDER BY changed_at DESC LIMIT 10;

