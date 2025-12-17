from app import app, db, User, Post, Page, init_db
from populate_db import populate
from migrate_to_pages import migrate_to_pages

def setup():
    print("Starting database setup...")
    
    # 1. Create Tables and Admin User
    init_db()
    print("Tables created and Admin user checked/created.")
    
    # 2. Populate Posts
    populate()
    print("Posts populated.")
    
    # 3. Migrate to Pages (Create Index Page)
    migrate_to_pages()
    print("Index page created/migrated.")
    
    print("Database setup completed successfully!")

if __name__ == "__main__":
    setup()
