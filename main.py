from app import create_app, create_database,db
from flask_sqlalchemy import SQLAlchemy

DB_NAME = "database.db"
app = create_app(DB_NAME,db)
create_database(app,db)

if __name__ == '__main__':
    app.run(debug=False)