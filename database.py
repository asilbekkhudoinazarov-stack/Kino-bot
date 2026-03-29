users = {}  # {user_id: {"kod": "", "movies_seen": []}}
movies = {}  # {"KINO1": "movies/example.txt", "KINO2": "movies/example2.txt"}

def add_user(user_id):
    if user_id not in users:
        users[user_id] = {"kod": "", "movies_seen": []}

def add_movie(kod, path):
    movies[kod] = path

def remove_movie(kod):
    if kod in movies:
        del movies[kod]