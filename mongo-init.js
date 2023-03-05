db = db.getSiblingDB('face_detection');
db.createCollection('images');
db.createCollection('results');