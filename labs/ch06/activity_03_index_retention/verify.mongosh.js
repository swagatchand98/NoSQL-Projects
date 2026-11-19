db = db.getSiblingDB("college_ch06");
db.products.find({category:"cat2"},{_id:0,category:1,price:1}).explain("executionStats");
