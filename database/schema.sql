CREATE DATABASE devsecops_db;

CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'apppassword';

GRANT ALL PRIVILEGES ON devsecops_db.* TO 'appuser'@'localhost';

USE devsecops_db;

CREATE TABLE contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

