CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    login VARCHAR(20) NOT NULL UNIQUE,
    hashed_password VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tokens(
    id SERIAL PRIMARY KEY,
    value UUID NOT NULL UNIQUE DEFAULT uuid_generate_v4(),
    expires TIMESTAMP NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS salary(
    id SERIAL PRIMARY KEY,
    value INTEGER NOT NULL DEFAULT 0,
    target_date DATE NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
