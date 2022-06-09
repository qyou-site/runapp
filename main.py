from app import create_app, create_database
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DB_NAME = "database.db"
app = create_app(DB_NAME,db)
create_database(app,db)

if __name__ == '__main__':
    app.run(debug=False)