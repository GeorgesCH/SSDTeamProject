from healthapp import db, bcrypt
from healthapp.models import User, Post, BloodPressure, Weight
from healthapp.encryption import encrypt_post, encrypt_medical_record
from cryptography.fernet import Fernet

def rebuild_db():
    db.drop_all()

    db.create_all()

    hashed_password_admin = bcrypt.generate_password_hash('password').decode('utf-8')
    user_admin = User(first_name='Test', last_name='Admin', email='admin@email.com',
                      password=hashed_password_admin, role='Admin',
                      key=Fernet.generate_key().decode('utf-8'))

    hashed_password_astro = bcrypt.generate_password_hash('testing').decode('utf-8')
    user_astro = User(first_name='Astro', last_name='Naut', email='astro@email.com',
                      password=hashed_password_astro, role='Astronaut',
                      key=Fernet.generate_key().decode('utf-8'))

    hashed_password_med = bcrypt.generate_password_hash('test123').decode('utf-8')
    user_med = User(first_name='Doctor', last_name='Zoidberg', email='doc@email.com',
                    password=hashed_password_med, role='Medic',
                    key=Fernet.generate_key().decode('utf-8'))

    post_2 = Post(title='Testing Testing', recipient='admin@email.com', content='', user_id=2)
    post_3 = Post(title='Test 123', recipient='admin@email.com', content='', user_id=3)
    post_4 = Post(title='This is a Test', recipient='astro@email.com', content='', user_id=1)
    post_6 = Post(title='To The Moon', recipient='astro@email.com', content='', user_id=3)
    post_7 = Post(title='Space Station 123', recipient='doc@email.com', content='', user_id=1)
    post_8 = Post(title='NASA NASA', recipient='doc@email.com', content='', user_id=2)

    bp_1 = BloodPressure(record='', user_id=2)
    bp_2 = BloodPressure(record='', user_id=2)
    bp_3 = BloodPressure(record='', user_id=2)

    weight_1 = Weight(record='70kg', user_id=2)
    weight_2 = Weight(record='71kg', user_id=2)
    weight_3 = Weight(record='69kg', user_id=2)

    posts = [post_2, post_3, post_4, post_6, post_7, post_8]

    records = [bp_1, bp_2, bp_3, weight_1, weight_2, weight_3]

    data = ['120/80mmHg', '118/84mmHg', '125/77mmHg', '70kg', '71kg', '69kg']

    db.session.add(user_admin)
    db.session.add(user_astro)
    db.session.add(user_med)

    for post in posts:
        post.content = encrypt_post('test test test post post post 123 abc', post.recipient)
        db.session.add(post)

    for i in range(6):
        records[i].record = encrypt_medical_record(data[i],
                                                   User.query.filter_by(id=records[i].user_id).first().key)
        db.session.add(records[i])

    db.session.commit()



if __name__ == "__main__":
    rebuild_db()
    print(User.query.all())
    print(Post.query.all())
    print(BloodPressure.query.all())
    print(Weight.query.all())
