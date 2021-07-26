import requests
from healthapp.restapi.tests.rebuild_db import rebuild_db

def login_test():

    rebuild_db()

    BASE = 'http://127.0.0.1:5000/'

    print('Successful Logins and tokens')

    admin_token = requests.post(BASE + '/api/login',
                                {'email': 'admin@email.com',
                                 'password': 'password'}).\
                                json()['token']

    print('admin: ' + admin_token)

    astro_token = requests.post(BASE + '/api/login',
                                {'email': 'astro@email.com',
                                 'password': 'testing'}).\
                                json()['token']

    print('astro: ' + astro_token)

    medic_token = requests.post(BASE + '/api/login',
                                {'email': 'doc@email.com',
                                 'password': 'test123'}). \
                                json()['token']

    print('medic: ' + medic_token)

    print('\n Login errors')

    bad_email = requests.post(BASE + '/api/login',
                                {'email': '@email.com',
                                 'password': 'password'}). \
                                json()

    print(bad_email)

    bad_pw = requests.post(BASE + '/api/login',
                              {'email': 'admin@email.com',
                               'password': 'passwd'}). \
                                json()

    print(bad_pw)

    print('\n Missing args')

    missing_email = requests.post(BASE + '/api/login').json()

    print(missing_email)

    missing_pw = requests.post(BASE + '/api/login', {'email': 'email'}).json()

    print(missing_pw)

    print('\nBad token:')
    print(
        requests.get(BASE + '/api/user', {'email': 'astro@email.com',
                                            'token': 'token123'}).json()
    )

if __name__ == '__main__':
    login_test()