import requests
from healthapp.restapi.tests.rebuild_db import rebuild_db


def record_get_test(BASE, admin_token, astro_token, medic_token):
    print('Blood pressure for current user:')
    print(
        requests.get(BASE + '/api/record/blood_pressure', {'email': 'astro@email.com', 'token': astro_token}).json()
    )

    print('\nBlood pressure admin:')
    print(
        requests.get(BASE + '/api/record/blood_pressure', {'email': 'astro@email.com', 'token': admin_token}).json()
    )

    print('\nBlood pressure medic:')
    print(
        requests.get(BASE + '/api/record/blood_pressure', {'email': 'astro@email.com', 'token': medic_token}).json()
    )

    print('\nWeight for current user:')
    print(
        requests.get(BASE + '/api/record/weight', {'email': 'astro@email.com', 'token': astro_token}).json()
    )

    print('\nWeight admin:')
    print(
        requests.get(BASE + '/api/record/weight', {'email': 'astro@email.com', 'token': admin_token}).json()
    )

    print('\nWeight medic:')
    print(
        requests.get(BASE + '/api/record/weight', {'email': 'astro@email.com', 'token': medic_token}).json()
    )

    print('\nInvalid user:')
    print(
        requests.get(BASE + '/api/record/blood_pressure', {'email': 'admin@email.com', 'token': astro_token}).json()
    )

    print('\nBad email:')
    print(
        requests.get(BASE + '/api/record/blood_pressure', {'email': '@email.com', 'token': admin_token}).json()
    )

    print('\nBad record:')
    print(
        requests.get(BASE + '/api/record/blood', {'email': 'astro@email.com', 'token': medic_token}).json()
    )


def record_put_test(BASE, admin_token, astro_token, medic_token):
    print('Blood pressure new post:')
    print(
        requests.put(BASE + '/api/record/blood_pressure', {'record': '123/456mmhg', 'token': astro_token}).json()
    )

    print('\nBlood pressure get showing new entry:')
    print(
        requests.get(BASE + '/api/record/blood_pressure', {'email': 'astro@email.com', 'token': astro_token}).json()
    )

    print('\nWeight new post:')
    print(
        requests.put(BASE + '/api/record/weight', {'record': '50kg', 'token': astro_token}).json()
    )

    print('\nWeight get showing new entry:')
    print(
        requests.get(BASE + '/api/record/weight', {'email': 'astro@email.com', 'token': astro_token}).json()
    )

    print('\nNot astronaut:')
    print(
        requests.put(BASE + '/api/record/blood_pressure', {'record': '123/456mmhg', 'token': admin_token}).json()
    )

    print('\nBad record type:')
    print(
        requests.put(BASE + '/api/record/blood', {'record': '123/456mmhg', 'token': astro_token}).json()
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

    record_get_test(BASE, admin_token, astro_token, medic_token)
    record_put_test(BASE, admin_token, astro_token, medic_token)
