from dotenv import load_dotenv, find_dotenv
import os
import pyodbc
from faker import Faker

# Get ROOT_DIR
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)) )

# Take environment variables from .env.
load_dotenv(ROOT_DIR+'/.env', override=True)

# Connect to the SQL Server database
conn = pyodbc.connect(os.getenv("CONNECTION_STRING")  )

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# create sample datbase tables
products = """IF OBJECT_ID(N'dbo.products', N'U') IS NULL
    CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    product_description TEXT,
    product_price DECIMAL(10, 2),
    product_category VARCHAR(50),
    in_stock BIT
);"""

sellers = """IF OBJECT_ID(N'dbo.sellers', N'U') IS NULL
    CREATE TABLE sellers (
    seller_id INT PRIMARY KEY,
    seller_name VARCHAR(100),
    seller_email VARCHAR(100),
    seller_contact_number VARCHAR(15),
    seller_address TEXT
);"""

sales_transaction = """IF OBJECT_ID(N'dbo.sales_transaction', N'U') IS NULL
    CREATE TABLE sales_transaction (
    transaction_id INT PRIMARY KEY,
    product_id INT,
    seller_id INT,
    quantity INT,
    transaction_date DATE,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
);"""

cursor.execute(products)
cursor.execute(sellers)
cursor.execute(sales_transaction)



# Clean up the database tables
cursor.execute("DELETE FROM sales_transaction")
cursor.execute("DELETE FROM products")
cursor.execute("DELETE FROM sellers")

# Create Faker object
fake = Faker()

# Insert Products
cursor.execute("INSERT INTO products (product_id, product_name, product_description, product_price, product_category, in_stock) VALUES (?, ?, ?, ?, ?, ?)", 
               1, 'Apple iPhone 13', 'Latest model of iPhone with A15 Bionic chip', 999.99, 'Electronics', 1)

cursor.execute("INSERT INTO products (product_id, product_name, product_description, product_price, product_category, in_stock) VALUES (?, ?, ?, ?, ?, ?)", 
               2, 'Nike Air Force 1', 'Classic Nike sneakers in white', 90.00, 'Footwear', 1)

cursor.execute("INSERT INTO products (product_id, product_name, product_description, product_price, product_category, in_stock) VALUES (?, ?, ?, ?, ?, ?)", 
               3, 'The Alchemist', 'A novel by Paulo Coelho', 10.99, 'Books', 1)


# Insert Sellers
cursor.execute("INSERT INTO sellers (seller_id, seller_name, seller_email, seller_contact_number, seller_address) VALUES (?, ?, ?, ?, ?)",
               1, 'John Doe', 'johndoe@example.com', '1234567890', '123 Main St, Anytown, USA')

cursor.execute("INSERT INTO sellers (seller_id, seller_name, seller_email, seller_contact_number, seller_address) VALUES (?, ?, ?, ?, ?)",
               2, 'Jane Smith', 'janesmith@example.com', '0987654321', '456 High St, Sometown, USA')

cursor.execute("INSERT INTO sellers (seller_id, seller_name, seller_email, seller_contact_number, seller_address) VALUES (?, ?, ?, ?, ?)",
               3, 'Bob Johnson', 'bobjohnson@example.com', '1122334455', '789 Low St, Othertown, USA')

# Populate sales_transaction table with faker data
for i in range(100):
    # Generate fake data
    transaction_id = i+1
    product_id = fake.random_int(min=1, max=3)
    seller_id = fake.random_int(min=1, max=3)
    quantity = fake.random_int(min=1, max=10)
    transaction_date = fake.date_between(start_date='-1y', end_date='today')

    cursor.execute("INSERT INTO sales_transaction (transaction_id, product_id, seller_id, quantity, transaction_date) VALUES (?, ?, ?, ?, ?)", 
                   transaction_id, product_id, seller_id, quantity, transaction_date)  

# Commit the changes and close the connection
conn.commit()
conn.close()