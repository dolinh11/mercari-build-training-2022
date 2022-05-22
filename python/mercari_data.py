import sqlite3

conn = sqlite3.connect('items.db')
c = conn.cursor()

#Create table
c.execute("""CREATE TABLE IF NOT EXISTS items (
    name TEXT,
    category TEXT
)""")

#Insert Data
lst_item = [('jacket', 'fashion'), ('rice', 'food')]
c.executemany('INSERT INTO items (name, category) VALUES (?, ?)', lst_item)

#Add image
c.execute("""ALTER TABLE items ADD image TEXT""")

#New table for category
c.execute("ALTER TABLE items DROP COLUMN category")
c.execute("""CREATE TABLE categories (
    id INTEGER,
    name TEXT
)""")
c.execute("ALTER TABLE items ADD COLUMN category_id INTEGER REFERENCES categories(id)")

conn.commit()
conn.close() 