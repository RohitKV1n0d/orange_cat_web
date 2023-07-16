from app import db,app

def createDb(self):
    with app.app_context():
        db.create_all() 
        print("Database created")

createDb(self=None)