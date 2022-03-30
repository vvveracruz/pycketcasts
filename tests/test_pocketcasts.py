from _secrets import user, password
import pycketcasts

def test():
    assert user=='login@vgg.cz'

def test_api():
    assert type(pycketcasts.PocketCast(user, password)) == pycketcasts.pocketcasts.PocketCast
