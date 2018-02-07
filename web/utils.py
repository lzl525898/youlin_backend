import os
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
try:
    from PIL import Image, ImageOps
except ImportError:
    import Image, ImageOps
try:
    from django.views.decorators.csrf import csrf_exempt
except ImportError:
# monkey patch this with a dummy decorator which just returns the same function
# (for compatability with pre-1.1 Djangos)
    def csrf_exempt(fn):
        return fn
THUMBNAIL_SIZE = (75, 75)

def exists(name):
    """
    Determines wether or not a file exists on the target storage system.
    """
    return os.path.exists(name)

def get_available_name(name):
    """
    Returns a filename that's free on the target storage system, and
    available for new content to be written to.
    """
    dir_name, file_name = os.path.split(name)
    file_root, file_ext = os.path.splitext(file_name)
    # If the filename already exists, keep adding an underscore (before the
    # file extension, if one exists) to the filename until the generated
    # filename doesn't exist.
    while exists(name):
        file_root += '_'
        # file_ext includes the dot.
        name = os.path.join(dir_name, file_root + file_ext)
    return name

def get_thumb_filename(filename):
    """
    Generate thumb filename by adding _thumb to end of filename before . (if present)
    """
    try:
        dot_index = filename.rindex('.')
    except ValueError: # filename has no dot
        return '%s_thumb' % filename
    else:
        return '%s_thumb%s' % (filename[:dot_index], filename[dot_index:])
    
def create_thumbnail(filename):
    image = Image.open(filename)
    # Convert to RGB if necessary
    # Thanks to Limodou on DjangoSnippets.org
    # http://www.djangosnippets.org/snippets/20/
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')
    # scale and crop to thumbnail
    imagefit = ImageOps.fit(image, THUMBNAIL_SIZE, Image.ANTIALIAS)
    imagefit.save(get_thumb_filename(filename))
    
def get_media_url(path):
    """
    Determine system file's media url.
    """
    upload_url = getattr(settings, "CKEDITOR_UPLOAD_PREFIX", None)
    if upload_url:
        url = upload_url + os.path.basename(path)
    else:
        url = settings.MEDIA_URL + path.split(settings.MEDIA_ROOT)[1]
    return url