from app import app, db, Post, Page

def migrate_to_pages():
    with app.app_context():
        # Create Page table
        db.create_all()
        
        # Check if index page already exists
        if not Page.query.filter_by(slug='index').first():
            # Get all the index posts
            index_posts = Post.query.filter(Post.slug.in_([
                "sura-ibrahim-14",
                "sura-al-hijr-15",
                "an-nahl-16",
                "al-kahf-18",
                "maryam-19"
            ])).all()
            
            # Sort them
            slug_order = {
                "sura-ibrahim-14": 0,
                "sura-al-hijr-15": 1,
                "an-nahl-16": 2,
                "al-kahf-18": 3,
                "maryam-19": 4
            }
            index_posts.sort(key=lambda p: slug_order.get(p.slug, 999))
            
            # Combine into single page content
            content_parts = []
            for post in index_posts:
                content_parts.append(f"## {post.title}\n\n{post.content}\n")
            
            combined_content = "\n".join(content_parts)
            
            # Create index page
            index_page = Page(
                title="জান্নাতের বর্ননা",
                slug="index",
                content=combined_content
            )
            db.session.add(index_page)
            db.session.commit()
            print("Index page created successfully!")
        else:
            print("Index page already exists, skipping...")

if __name__ == "__main__":
    migrate_to_pages()
