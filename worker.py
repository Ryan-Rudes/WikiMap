from termcolor import colored
from bs4 import BeautifulSoup
import urllib
import random
import string
import re

letters = string.ascii_letters

class Worker:
    def __init__(self):
        self.renew_user_agent()

    def request(self, url, max_retries=10, save_errors=False, filepath='', verbose=False):
        while True:
            try:
                resp = urllib.request.urlopen(url)
                return resp
            except KeyboardInterrupt:
                return
            except:
                self.renew_user_agent()
            """
            except HTTPError as e:
                if e.code == 429:
                    self.renew_user_agent()
                else:
                    if verbose:
                        print ('Failed to request %s: %s' % (url, str(e)))

                    if save_errors:
                        with open(filepath, 'a') as f:
                            f.write(url[30:] + '\n')
                    return
            except Exception as e:
                if verbose:
                    print ('Failed to request %s: %s' % (url, str(e)))

                if save_errors:
                    with open(filepath, 'a') as f:
                        f.write(url[30:] + '\n')
                return
            """

    def fetch(self, path, max_retries=10, save_errors=False, filepath='', verbose=False):
        link = 'https://en.wikipedia.org/wiki/' + path
        resp = self.request(link, max_retries = max_retries, save_errors = save_errors, filepath = filepath, verbose = verbose)
        if not resp is None:
            html = resp.read()
            soup = BeautifulSoup(html, features = 'html.parser')
            urls = soup.find_all('a', attrs = {'href': re.compile('^/wiki/(?!Wikipedia:|Help:|Special:|Portal:|Talk:|Category:|File:|Wayback_Machine|Main_Page)')})
            href = set(item['href'][6:] for item in urls)
            try:
                page = soup.find('h1', class_ = 'firstHeading', id = 'firstHeading').text
            except Exception as e:
                print (colored(f"""
                Failed to parse title from HTML content:
                    - URL: {link}
                    - ERR: {str(e)}
                """.strip()))
                return (None, None), False
            return (href, page), True
        return (None, None), False

    def renew_user_agent(self):
        opener = urllib.request.build_opener()
        user_agent = generate_random_user_agent()
        opener.addheaders = [('User-agent', user_agent)]
        urllib.request.install_opener(opener)

def generate_random_user_agent():
    return ''.join(random.choice(letters) for i in range(random.randint(8, 15)))
