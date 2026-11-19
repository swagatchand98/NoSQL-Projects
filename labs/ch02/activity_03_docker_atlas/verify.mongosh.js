db = db.getSiblingDB("college_ch02");
db.books.find({year:{$lt:2010}});
