from database import add_movie, remove_movie, movies

def add_new_movie(kod, path):
    add_movie(kod, path)
    return f"{kod} kodi bilan kino qo'shildi."

def delete_movie(kod):
    if kod in movies:
        remove_movie(kod)
        return f"{kod} kodi bilan kino o'chirildi."
    return "Bunday kino topilmadi."