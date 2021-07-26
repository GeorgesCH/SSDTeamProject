import requests
from healthapp.restapi.tests.rebuild_db import rebuild_db


def post_get_test(BASE, admin_token, astro_token, medic_token):
    print('All posts to current user:')
    print(
        requests.get(BASE + '/api/post', {'email': 'all', 'token': astro_token}).json()
    )

    print('\nPosts between current user and other:')
    print(
        requests.get(BASE + '/api/post', {'email': 'admin@email.com', 'token': astro_token}).json()
    )

    print('\nBad email:')
    print(
        requests.get(BASE + '/api/post', {'email': 'an@email.com', 'token': astro_token}).json()
    )


def post_put_test(BASE, admin_token, astro_token, medic_token):
    print('New post:')
    print(
        requests.put(BASE + '/api/post', {'email': 'admin@email.com',
                                          'content': 'new post 123 test test test',
                                          'title': 'API test post',
                                          'token': astro_token}).json()
    )

    print('\nGet to show new post in database:')
    print(
        requests.get(BASE + '/api/post', {'email': 'all', 'token': astro_token}).json()
    )

    print('\nBad email:')
    print(
        requests.put(BASE + '/api/post', {'email': '@email.com',
                                          'content': 'new post 123 test test test',
                                          'title': 'API test post',
                                          'token': astro_token}).json()
    )


if __name__ == '__main__':
    rebuild_db()

    BASE = 'http://127.0.0.1:5000/'

    admin_token = requests.post(BASE + '/api/login',
                                {'email': 'admin@email.com',
                                 'password': 'password'}). \
        json()['token']

    astro_token = requests.post(BASE + '/api/login',
                                {'email': 'astro@email.com',
                                 'password': 'testing'}). \
        json()['token']

    medic_token = requests.post(BASE + '/api/login',
                                {'email': 'doc@email.com',
                                 'password': 'test123'}). \
        json()['token']

    #post_get_test(BASE, admin_token, astro_token, medic_token)
    post_put_test(BASE, admin_token, astro_token, medic_token)
