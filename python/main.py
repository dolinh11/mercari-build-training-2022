import os
import logging
import pathlib
import hashlib
import sqlite3
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import UploadFile

import mercari_data

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "image"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

#Some function to work with database
# Get all items
def show_all():
    conn = sqlite3.connect('items.db')
    c = conn.cursor()
    
    c.execute("""SELECT items.id, items.name, categories.name, items.image
		FROM items INNER JOIN categories
		ON items.category_id = categories.id
	""")
    item = [dict((c.description[i][0], value)
                  for i, value in enumerate(row)) for row in c.fetchall()]
    conn.close()
    return {f"items:{item}"}

# Insert item
def insert_one(name, category_id, image):
	conn = sqlite3.connect('items.db')
	c = conn.cursor()

	c.execute('INSERT INTO items (name, category_id, image) VALUES (?, ?, ?)', (name, category_id, image))

	conn.commit()
	conn.close()

	return {'message': f'item received: {name}'}

# Search by a keyword
def search(keyword: str):

    conn = sqlite3.connect('mercari.sqlite3')
    c = conn.cursor()
    # Inner JOIN is advised by yuting0203 and reference to LingYi0612
    c.execute("""SELECT items.name,category.name as category,items.image
        FROM  items INNER JOIN category
        ON items.category_id =category.id
        WHERE items.name LIKE '%keyword%'""")
    
    name = [dict((c.description[i][0], value)
                  for i, value in enumerate(row)) for row in c.fetchall()]

    c.execute("""SELECT items.name,category.name as category,items.image
        FROM  items INNER JOIN category
        ON items.category_id =category.id
        WHERE category LIKE '%keyword%'""")

    category = [dict((c.description[i][0], value)
                  for i, value in enumerate(row)) for row in c.fetchall()]
    return (f"items:{name+category}")

# Get an item by id
def get_id(id):
	conn = sqlite3.connect('items.db')
	c = conn.cursor()

	c.execute(f"""SELECT items.id, items.name, categories.name, items.image
		FROM items INNER JOIN categories
		ON items.category_id = categories.id 
		WHERE items.id={id}
	""")
	item = c.fetchone()

	conn.close()

	return {'id': item[0], 'name': item[1], 'category': item[2], 'image': item[3]} 

#Function for image
def hash_img(image):
    image = hashlib.sha256(image.strip('jpg').encode('utf-8')).hexdigest() + '.jpg'
    return image


@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.get("/items")
def items():
    return show_all()

@app.post("/items")
def add_item(name: str = Form(...), category: str = Form(...), image: str = Form(...)):
    conn = sqlite3.connect('items.db')
    c = conn.cursor()

    c.execute("""SELECT * from category WHERE name == (?)""",[category])
    data = c.fetchone()
    if(categoryData == None):
        c.execute("""INSERT INTO category VALUES (?,?)""",(None,category))
        c.execute("""SELECT * from category WHERE name == (?)""",[category])
        data = c.fetchone()

    c.execute("""INSERT INTO items VALUES (?,?,?,?)""",(None,name,data[0],hash_img(image)))
    conn.commit()
    conn.close()

@app.get("/items/{item_id}")
def get_item(item_id):
    return get_id(item_id)

@app.get("/image/{items_image}")
async def get_image(items_image):
    # Create image path
    image = images / items_image

    if not items_image.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)
