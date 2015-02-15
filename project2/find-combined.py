# Find combined number of users making up 1% of all contributions.

def print_combined_users(db):
    contributions = db.openstreet.aggregate([
    {"$group":{"_id": "$created.user","count":{"$sum": 1}}},
    {"$sort": {"count": 1}}])['result']

    total = db.openstreet.count() / 100
    total_calc = 0
    comb_users = 0
    for c in contributions:
        total_calc += c['count']
        comb_users += 1
        if total_calc >= total:
            break

    percentage = round(float(comb_users) / float(len(contributions)) * 100, 2)
    print "Combined number of users making up only 1% ({0}) of posts: {1} ({2}% of all users)".format(total, comb_users, percentage)

def get_db():
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.project2
    return db

def test():
    db = get_db()
    print_combined_users(db)

if __name__ == "__main__":
    test()