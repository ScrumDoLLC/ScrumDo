from favorites.models import Favorite
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def add(request, favorite_type, favorite_id):    
    Favorite.setFavorite( int(favorite_type), favorite_id, request.user, True)
    return HttpResponse("OK")
    
@login_required
def remove(request, favorite_type, favorite_id):
    Favorite.setFavorite( int(favorite_type), favorite_id, request.user, False)
    return HttpResponse("OK")    