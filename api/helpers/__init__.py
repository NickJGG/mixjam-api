from api.models import PartyInvite, Artist
from api.serializers import PartyInviteSerializer

def add_saved_status_to_collection(spotify_client, collection, type):
    ids = list(map(lambda item: item.get("id", ""), collection))

    like_checks = spotify_client.check_if_saved({
        "type": type,
        "ids": ",".join(ids)
    })

    for index, like_check in enumerate(like_checks):
        if len(collection) > index:
            collection[index]["is_liked"] = like_check
    
    return collection

def add_artists_to_collection(spotify_client, collection):
    collection, artist_ids = add_artists(collection)

    if len(artist_ids) > 0:
        resp = spotify_client.get_artists({
            "ids": artist_ids
        })

        for artist in resp.get("artists"):
            spotify_id = artist.get("id")
            name = artist.get("name")
            images = artist.get("images")
            image_url = images[0]["url"] if len(images) > 0 else ""

            Artist.objects.create(spotify_id=spotify_id, name=name, image_url=image_url)
    
        collection, artist_ids = add_artists(collection)

    return collection

def add_artists(collection):
    artist_ids = []

    for item_index, item in enumerate(collection):
        artists = item.get("artists")

        if len(artists) == 0:
            continue

        artist_index = 0
        artist = artists[artist_index]

        # for artist_index, artist in enumerate(artists):
        if "images" in artist:
            continue

        artist_id = artist["id"]
        artist_obj = Artist.objects.filter(spotify_id=artist_id)

        if artist_obj.exists():
            artist_obj = artist_obj[0]

            collection[item_index]["artists"][artist_index]["images"] = [
                {
                    "url": artist_obj.image_url,
                }
            ]
        else:
            artist_ids.append(artist_id)
    
    return collection, artist_ids

def get_notifications(user):
    party_invites = PartyInvite.objects.filter(notification__receiver=user)
    serialized_invites = PartyInviteSerializer(party_invites, many=True).data

    return serialized_invites
