import re, os, shutil, time, random, functools, datetime

import jwt
import uuid
from werkzeug import security
from werkzeug.utils import secure_filename

import config as cfg
from config import Config



def generate_id(s, salt, iterations=None, keylen=None):
    """
    Generate a random string (0-9, a-f) of length keylen*2.

    Arguments are self explanatory. Check werkzeug.security.pbkdf2_hex module
    for more info.
    """
    s, salt = str(s), bytes(salt)

    kwargs = {"iterations": iterations or 150000, "keylen": keylen or 4}
    return security.pbkdf2_hex(s, salt, **kwargs)


# permit thrumph omit
def loop_till_allowed(permit, omit):
    def loop_till_allowed_(func):
        @functools.wraps(func)
        def run(*args, **kwargs):
            val = func(*args, **kwargs)
            if val in permit:
                return val

            while val in omit:
                val = func(*args, **kwargs)
                if val in permit:
                    break
            return val
        return run
    return loop_till_allowed_


def generate_slug(s, ext=None, ext_len=2, salt=4):
    """
    Generate a slug from s. If ext, append a randomly generated string (using
    generate_id) of length ext_len*2 to it.
    """
    s = str(s)
    if ext:
        s += " " + generate_id(ext, salt, keylen=ext_len)
    return re.sub('[^\w]+', '-', s).lower()


def clean_path(url, short_url, include=True, plus_dir=True, ignore=[]):
    """
    Removes a file or a folder.

    url : The path to be removed. Ensure it ends with a "/" if its a folder.
    short_url : Used for logging purposes.
    include : Wether to remove the folder if url is a folder. If False, the folder
        contents are removed, but it is not included.
    plus_dir : Wether to remove any folder in url. If False, sub-folders in url
        are ignored and not removed.
    ignore : A list of sub-url, relative to url, to ignore (not remove).
    """
    if os.path.isfile(url):
        print("REMOVING FILE {}:".format(short_url), end=" ", flush=True)
        os.remove(url)
        print("DONE", flush=True)

    elif os.path.isdir(url):
        if include:
            print("REMOVING FOLDER '{}':".format(short_url), end=" ", flush=True)
            shutil.rmtree(url)
            return 

        print("REMOVING FILES IN FOLDER '{}':".format(short_url), end=" ", flush=True)
        for _sub_url in os.listdir(url):
            if _sub_url not in ignore:
                sub_url = "{}/{}".format(url.rstrip("/"), _sub_url.rstrip("/"))
                if os.path.isfile(sub_url):
                    os.remove(sub_url)
                elif plus_dir:
                    shutil.rmtree(sub_url+"/")
            else:
                continue
        else:
            print("REMOVING FILES IN FOLDER '{}':".format(url), end=" ", flush=True)
        print("DONE", flush=True)

    else:
        print("FILE '{}': NOT FOUND".format(url), flush=True)


def navigate_url(request):
    """
    Help views navigate between pages.
    
    returns prev, next.

    prev: Suggestion where a view should redirect to if it encounters any problem.
        Gotten from the query string.
    next: The current view's url. Tells the next page where to goto as above.
    """
    prev = request.args.get("next")
    _next = request.path
    return prev, _next


def encode_token(data, exp=None):
    """
    Encodes data into a token where it can later be retrieved.
    """
    try:
        payload = {
            "iat": datetime.datetime.utcnow(),
            "sub": data}
        if exp and isinstance(exp, datetime.datetime):
            payload["exp"] = exp
        return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
    except Exception as e:
        return e


def decode_token(token):
    """
    Retrieves the data encoded in token.
    """
    try:
        payload = jwt.decode(token, Config.SECRET_KEY)
        return True, payload["sub"]
    except jwt.ExpiredSignatureError:
        return False, "Signature expired. Generate a new one."
    except jwt.InvalidTokenError:
        return False, "Invalid token. Try again."
    except Exception as e:
        return False, "Something went wrong. Try again later."

