CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    price REAL NOT NULL CHECK (price >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)
);

INSERT OR IGNORE INTO items (id, name, price, stock)
VALUES
    (1, 'Rice 1kg', 60.00, 100),
    (2, 'Sugar 1kg', 45.00, 80),
    (3, 'Milk 1L', 30.00, 60),
    (4, 'Cooking Oil 1L', 140.00, 50),
    (5, 'Wheat Flour 1kg', 40.00, 70),
    (6, 'Bath Soap', 35.00, 100),
    (7, 'Biscuits', 20.00, 120),
    (8, 'Tea Powder 250g', 95.00, 40);
