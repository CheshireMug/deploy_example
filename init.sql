CREATE TABLE IF NOT EXISTS users (
    id INTEGER primary key generated always as identity,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);