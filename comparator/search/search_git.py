from github import Github
import validators

from svn.remote import RemoteClient

ACCESS_TOKEN = ''

g = Github(ACCESS_TOKEN)


def download_folder(url):
    if not validators.url(url):
        print('Invalid url')
        return

    if 'tree/master' in url:
        url = url.replace('tree/master', 'trunk')

    r = RemoteClient(url)
    r.export('output')


def search_github(name_lib):
    query = '+'.join(name_lib) + '+in:readme+in:description'
    result = g.search_repositories(query, 'stars', 'desc')
    # print(f'Found {result.totalCount} repo(s)')

    for repo in result:
        download_folder(repo.clone_url)
        break


def entry_point(name_lib: str):
    search_github(name_lib)
