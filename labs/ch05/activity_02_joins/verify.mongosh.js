db = db.getSiblingDB("college_ch05");
db.orders.aggregate([{$group:{_id:"$status",average:{$avg:"$total"}}}]);
