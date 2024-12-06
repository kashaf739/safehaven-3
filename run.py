from app import create_app, db

app = create_app()

# Create the tables inside the app context
with app.app_context():
    db.create_all()  # Creates all tables based on your models

if __name__ == "__main__":
    app.run(debug=True)
