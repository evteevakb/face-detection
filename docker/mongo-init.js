db = db.getSiblingDB(process.env.DATABASE_NAME);
db.createCollection(process.env.COLLECTION_NAME);
