# Finding out percentage of contributions of top 10 users:
db.openstreet.aggregate([
    {"$group":{"_id": "$created.user","count":{"$sum": 1}}},
    {"$project": { "_id": "$_id", "count": "$count",
    "contribution_percentage": {"$divide": ["$count",db.openstreet.count()]} }},
    {"$sort": {"count": -1}}, {"$limit":10}, 
    {"$group": {"_id": null, "total": {"$sum": "$contribution_percentage"}}}])

# Finding out combined number of users making up only 1% of posts:
db.openstreet.aggregate([
    {"$group":{"_id": "$created.user","count":{"$sum": 1}}},
    {"$match": {"count": {"&lte": db.openstreet.count()/100}}},
    {"$group": {"_id": null, "total": {"$sum": 1}}}
])

# Most favourite cuisine
db.openstreet.aggregate([
{"$match": {"amenity":{"$exists":1}, "amenity":"restaurant"}},
{"$group":{"_id":"$cuisine", "count":{"$sum":1}}},
{"$sort":{"count":1}},
{"$limit":2}])

# Top 1 contributing user
db.openstreet.aggregate([
    {"$group":{"_id": "$created.user","count":{"$sum": 1}}},
    {"$sort": {"count": -1}}, {"$limit":1}])


# 5 Most recorded amenities
db.openstreet.aggregate([
    {"$match": {"amenity": {"$exists": 1}}},
    {"$group": {
        "_id": "$amenity",
        "count": {"$sum": 1}
    }},
    {"$sort": {"count": -1}},
    {"$limit": 5}
])

# Top 5 natural attractions
db.openstreet.aggregate([{"$match": {"natural": {"$exists": 1, "$ne": "tree"}}},
{"$group": {"_id": "$natural", "count": {"$sum": 1}}},
{"$sort": {"count": -1}}, {"$limit": 5}])

# Top 5 tourism-related places
db.openstreet.aggregate([{"$match": {"tourism": {"$exists": 1}}}, {"$group": {"_id": "$tourism", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 5}])

# Find out who created tree nodes
db.openstreet.find({"natural": "tree"})
db.openstreet.find({"natural": "tree", "created.user": "okas95"}).count()
db.openstreet.find({"$near": {"$geometry": {"type": "Point", "coordinates": [-8.6576948, 115.2102476]}, "$maxDistance": 10}})