import requests
from healthapp.restapi.tests.rebuild_db import rebuild_db


def user_get_test(BASE, admin_token, astro_token, medic_token):

    print('All user request:')

    print(
        requests.get(BASE + '/api/user', {'email': 'all', 'token': admin_token}).json()
    )

    print('\nSpecific user:')

    print(
        requests.get(BASE + '/api/user', {'email': 'astro@email.com', 'token': admin_token}).json()
    )

    print('\nNon admin:')

    print(
        requests.get(BASE + '/api/user', {'email': 'astro@email.com', 'token': medic_token}).json()
    )

    print('\nBad email:')

    print(
        requests.get(BASE + '/api/user', {'email': '@email.com', 'token': admin_token}).json()
    )


def user_put_test(BASE, admin_token, astro_token, medic_token):

    print('Register new user:')
    print(
        requests.put(BASE + '/api/user', {'email': 'new@email.com',
                                          'first_name': 'New',
                                          'last_name': 'Username',
                                          'role': 'Astronaut',
                                          'password': 'newpassword',
                                          'token': admin_token}).json()
    )

    print('Non Admin:')
    print(
        requests.put(BASE + '/api/user', {'email': 'new@email.com',
                                          'first_name': 'New',
                                          'last_name': 'Username',
                                          'role': 'Astronaut',
                                          'password': 'newpassword',
                                          'token': medic_token}).json()
    )

    print('Email already in use:')
    print(
        requests.put(BASE + '/api/user', {'email': 'doc@email.com',
                                          'first_name': 'New',
                                          'last_name': 'Username',
                                          'role': 'Astronaut',
                                          'password': 'newpassword',
                                          'token': admin_token}).json()
    )

    print('Bad role:')
    print(
        requests.put(BASE + '/api/user', {'email': 'new_2@email.com',
                                          'first_name': 'New',
                                          'last_name': 'Username',
                                          'role': 'Astro',
                                          'password': 'newpassword',
                                          'token': admin_token}).json()
    )

    print('Missing args:')
    print(
        requests.put(BASE + '/api/user').json()
    )


def user_patch_test(BASE, admin_token, astro_token, medic_token):

    print('Update info:')
    print(
        requests.patch(BASE + '/api/user', {'email': 'astro@email.com',
                                            'first_name': 'New',
                                            'token': admin_token}).json()
    )

    print('\nBad role:')
    print(
        requests.patch(BASE + '/api/user', {'email': 'astro@email.com',
                                            'role': 'badrole',
                                            'token': admin_token}).json()
    )

    print('\nBad user:')
    print(
        requests.patch(BASE + '/api/user', {'email': '@email.com',
                                            'first_name': 'New',
                                            'token': admin_token}).json()
    )

    print('\nNot admin:')
    print(
        requests.patch(BASE + '/api/user', {'email': '@email.com',
                                            'first_name': 'New',
                                            'token': medic_token}).json()
    )

    print('\nMissing args:')
    print(
        requests.patch(BASE + '/api/user').json()
    )


def user_delete_test(BASE, admin_token, astro_token, medic_token):
    print('Deleted user:')
    print(
        requests.delete(BASE + '/api/user',
                        data={'email': 'astro@email.com', 'token': admin_token}).json()
    )

    print('\nGet for deleted user:')
    print(
        requests.get(BASE + '/api/user', {'email': 'astro@email.com', 'token': admin_token}).json()
    )

    rebuild_db()

    print('\nNot admin:')
    print(
        requests.delete(BASE + '/api/user',
                        data={'email': 'astro@email.com', 'token': medic_token}).json()
    )

    print('\nNot admin but current user:')
    print(
        requests.delete(BASE + '/api/user',
                        data={'email': 'astro@email.com', 'token': astro_token}).json()
    )

    print('\nGet for deleted user:')
    print(
        requests.get(BASE + '/api/user', {'email': 'astro@email.com', 'token': admin_token}).json()
    )

    print('\nDeleted user invalidated token:')
    print(
        requests.get(BASE + '/api/user', {'email': 'astro@email.com', 'token': astro_token}).json()
    )

    rebuild_db()


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

    user_get_test(BASE, admin_token, astro_token, medic_token)
    user_put_test(BASE, admin_token, astro_token, medic_token)
    user_patch_test(BASE, admin_token, astro_token, medic_token)
    user_delete_test(BASE, admin_token, astro_token, medic_token)