CREATE TABLE IF NOT EXISTS users (
    username TEXT UNIQUE NOT NULL,
    name TEXT,
    password TEXT NOT NULL,
    email TEXT,
    bio TEXT,
    isAdmin TEXT,
    CONSTRAINT username_unique UNIQUE (username)
);

CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    section_id INTEGER NOT NULL,
    description TEXT,
    copies INTEGER NOT NULL,
    CONSTRAINT section_fk FOREIGN KEY (section_id) REFERENCES sections(id)
);

CREATE TABLE IF NOT EXISTS sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    CONSTRAINT name_unique UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS borrows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    book_id INTEGER NOT NULL,
    borrow_date TEXT NOT NULL,
    return_date TEXT NOT NULL,
    status INTEGER NOT NULL,
    CONSTRAINT user_fk FOREIGN KEY (username) REFERENCES users(username),
    CONSTRAINT book_fk FOREIGN KEY (book_id) REFERENCES books(id)
);
