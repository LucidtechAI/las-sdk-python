import requests


class Receipt:
    def __init__(self, url=None, filename=None, fp=None, content=None):
        if not fp and not url and not filename and not content:
            raise Exception('fp, url, filename or content must be provided')

        if url:
            self.content = requests.get(url).content
        elif filename:
            with open(filename, 'rb') as fp:
                self.content = fp.read()
        elif fp:
            self.content = fp.read()
        else:
            self.content = content
