db = db.getSiblingDB("college_ch01");
db.products.aggregate([{$group:{_id:"$family",count:{$sum:1}}}]);
