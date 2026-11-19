db = db.getSiblingDB("college_ch04");
db.inventory.find({tags:{$all:["mechanical","wireless"]}}).sort({name:1,sku:1});
