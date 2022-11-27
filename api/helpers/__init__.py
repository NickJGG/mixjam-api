def add_saved_status_to_collection(spotify_client, collection, ids, type):
    like_checks = spotify_client.check_if_saved({
        "type": type,
        "ids": ",".join(ids)
    }).json()

    for index, like_check in enumerate(like_checks):
        if len(collection) > index:
            collection[index]["is_liked"] = like_check
    
    return collection