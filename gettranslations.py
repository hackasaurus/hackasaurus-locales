import os
import re
import urllib2
import zipfile
import StringIO
from distutils.dir_util import remove_tree

BASE_URL = "https://localize.mozilla.org/"
MINIMUM_COMPLETION = 20
ROOT = os.path.dirname(os.path.abspath(__file__))

def path(*a):
    return os.path.join(ROOT, *a)

def get_locale_zip(project, locale, base_url=BASE_URL):
    """
    Retrieves the ZIP containing the .po translations for the given
    locale of the given project and returns it as a file-like object.

    This requires the "Can download archives of translation projects"
    permission for the user "nobody" for the project.
    """
    
    zip_url = base_url + '%s/%s/export/zip' % (locale, project)
    return StringIO.StringIO(urllib2.urlopen(zip_url).read())

def get_available_locales(project, base_url=BASE_URL,
                          minimum_completion=MINIMUM_COMPLETION):
    """
    Returns a list of the available locales that the given project is
    available in.
    
    This requires the "Can view a translation project" permission
    for the user "nobody" for the project.
    
    A translation must be at least minimum_completion percent complete in
    order for it to be returned by this function.
    """

    lang_href = re.compile(r'.*"/(.*)/' + project + r'/".*')
    completion = re.compile(r'.*<div class="sortkey">([0-9]+)</div>.*')
    index_url = BASE_URL + 'projects/%s/' % project
    locales = []
    current_locale = None
    for line in urllib2.urlopen(index_url):
        match = lang_href.match(line)
        if match and match.group(1) not in ["templates", "projects"]:
            current_locale = match.group(1)
        elif current_locale:
            match = completion.match(line)
            if match:
                if int(match.group(1)) >= minimum_completion:
                    locales.append(current_locale)
                current_locale = None
    return locales

def download_available_locales(project, locale_dir):
    """
    Downloads and extracts all available locales of the given project
    into the given directory.
    
    Note that the given directory must exist, but individual
    locale-specific subdirectories will be created as needed.
    """

    for locale in get_available_locales(project):
        print "fetching locale %s" % locale
        locale_specific_dir = os.path.join(locale_dir, locale)
        if not os.path.exists(locale_specific_dir):
            os.mkdir(locale_specific_dir)
        zf = zipfile.ZipFile(get_locale_zip(project, locale))
        zf.extractall(locale_specific_dir)

if __name__ == '__main__':
    locale_dir = path('.')
    if not os.path.exists(locale_dir):
        os.mkdir(locale_dir)
    download_available_locales('hackasaurus', locale_dir)
