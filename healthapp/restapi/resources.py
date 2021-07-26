"""
Module containing the rest api resources.

Classes:
    LoginApi -- allows login
    UserApi -- allows viewing, editing, adding, and deleting users.
    RecordApi -- allows viewing and adding medical records.
    PostApi -- allows viewing and sending posts.

Functions:
    check_token -- checks if json web token is valid.
    check_user_role -- checks the current user's role.
"""

from datetime import datetime, timedelta
import jwt
from flask import jsonify
from flask_restful import Resource, abort, fields, marshal_with
from cryptography.fernet import Fernet
from healthapp import app, db, bcrypt, api
from healthapp.models import User, Post, BloodPressure, Weight, delete_user_from_db
from healthapp.encryption import encrypt_post, encrypt_medical_record, \
    decrypt_medical_record, decrypt_post

from healthapp.restapi.parsers import user_get_args, user_delete_args,\
        user_put_args, user_patch_args, login_args, record_get_args,\
        record_put_args, post_get_args, post_put_args

# structure for how User objects are returned using the @marshall_with decorator.
user_fields = {'email': fields.String, 'first_name': fields.String,
               'last_name': fields.String, 'role': fields.String}


def check_token(token):
    """
    Takes a json web token and checks its validity. If it is valid then is returns the
    current logged in user. If it is invalid then an access denied error is returned.

    Args:
        token -- the json web token to be checked.
    """
    # try to decode the token if it is valid.
    try:
        # decodes the token and extracts the data stored in it.
        data = jwt.decode(token, app.config['SECRET_KEY'], 'HS256')

        # finds the current user's information in the database.
        current_user = User.query.filter_by(email=data['email']).first()

        # returns current_user if user is found in the database.
        if current_user:
            return current_user

        abort(403, message='Invalid token. Please login.')

    # if an error occurs when decoding the token, or the token is expired,
    # then the below access denied error is sent along with the message.
    except (jwt.exceptions.DecodeError, jwt.exceptions.ExpiredSignatureError):
        return abort(403, message='Invalid token. Please login.')


def check_user_role(current_user, role):
    """
    Checks the current user's role. If it is not the same as the role passed in
    then an access denied error is returned.

    Args:
        current_user -- the current user who's role is to be checked.
        role -- the role to check against.
    """
    # if roles don't match return the below error.
    if current_user.role != role:
        abort(403, message='Access denied. Invalid user role.')


class LoginApi(Resource):
    """
    Allows the user to log in.
    """
    def post(self):
        """
        Logs a user in using the email and password sent with the request.
        """
        # Parses the sent arguments using login arguments parser.
        args = login_args.parse_args()
        # looks for user with the received email address in the database.
        user = User.query.filter_by(email=args['email']).first()

        # checks that the user is in the database and the password is correct.
        if user and bcrypt.check_password_hash(user.password, args['password']):
            # generates a new json web token with the user email
            # and expiry time stored in it.
            # 'exp' is the expiry time: login time + an amount of time.
            token = jwt.encode({'email': user.email,
                                'exp': datetime.utcnow() + timedelta(minutes=10)},
                               app.config['SECRET_KEY'], algorithm='HS256')

            # returns the web token.
            return {'token': token}

        #returns error message if log in fails.
        return {'message': 'Login error. Check username and password.'}


# adds the LoginApi resource to the api.
api.add_resource(LoginApi, '/api/login')


class UserApi(Resource):
    """
    Allows the registered users to be viewed, users to be added,
    user info to be updated, and a user to be deleted.
    """
    def __init__(self):
        # list of available user roles.
        self.user_roles = ['Admin', 'Astronaut', 'Medic']

    @marshal_with(user_fields)
    def get(self):
        """
        Gets a  user, or a list of all users in the database if the current user is an admin.
        """
        # Parses the arguments passed in the request.
        args = user_get_args.parse_args()

        # checks the token sent with the request.
        current_user = check_token(args['token'])
        # checks the user is an admin
        check_user_role(current_user, 'Admin')

        # if all is passed as the email argument then a list of all users is returned.
        if args['email'] == 'all':
            users = User.query.all()
            return users


        # looks for the user with the passed in email in the database
        user = User.query.filter_by(email=args['email']).first()

        # if the no user is found then a not found error is returned.
        if not user:
            abort(404, message="Could not find user")

        # returns the user info.
        return user

    @marshal_with(user_fields)
    def put(self):
        """
        Allows an admin to register a new user.
        """
        # Parses the arguments passed in the request.
        args = user_put_args.parse_args()

        # checks the token sent with the request.
        current_user = check_token(args['token'])
        # checks the user is an admin
        check_user_role(current_user, 'Admin')

        # looks for a user with the passed in email in the database.
        user = User.query.filter_by(email=args['email']).first()

        # if a user with the email already exists then the below error is returned.
        if user:
            abort(409, message=f"User with the email {args['email']} already exists")

        # if the passed in user role isn't in the list of valid roles then
        # the below error is returned.
        if args['role'] not in self.user_roles:
            abort(403, message=f'User role must be in {self.user_roles}.')

        # the passed in password is hashed and decoded to a utf-8 string
        # to be stored in the database.
        hashed_pw = bcrypt.generate_password_hash(args['password']).decode('utf-8')

        # a new User object containing the relevant user information.
        new_user = User(email=args['email'],
                        first_name=args['first_name'],
                        last_name=args['last_name'],
                        role=args['role'],
                        password=hashed_pw,
                        key=Fernet.generate_key().decode('utf-8'))

        # adds the new user to the database and commits the change.
        db.session.add(new_user)
        db.session.commit()

        # returns the new user info.
        return new_user, 201

    @marshal_with(user_fields)
    def patch(self):
        """
        Allows user info to be updated.
        """
        # Parses the arguments passed in the request.
        args = user_patch_args.parse_args()

        # checks the token sent with the request.
        current_user = check_token(args['token'])
        # checks the user is an admin
        check_user_role(current_user, 'Admin')

        # looks for a user with the passed in email in the database.
        user = User.query.filter_by(email=args['email']).first()

        # if the user is not in the database then returns a not found error
        if not user:
            abort(404, message="User does not exist, cannot update.")

        # if a value is passed in for any of the below arguments,
        # then the new info is updated in the database.
        if args['new_email']:
            user.email = args['new_email']

        if args['first_name']:
            user.first_name = args['first_name']

        if args['last_name']:
            user.last_name = args['last_name']

        if args['role']:
            # checks if the new user role is valid.
            if args['role'] not in self.user_roles:
                abort(403, message=f'User role must in {self.user_roles}.')

            user.role = args['role']

        if args['password']:
            # hashes new password
            hashed_pw = bcrypt.generate_password_hash(args['password']).decode('utf-8')
            user.password = hashed_pw

        # commits the changes to the database.
        db.session.commit()

        # returns the user with updated info.
        return user

    def delete(self):
        """
        Allows a user to be deleted.
        """
        # Parses the arguments passed in the request.
        args = user_delete_args.parse_args()

        # checks the token sent with the request.
        current_user = check_token(args['token'])

        # if the email argument is the current user's email then
        # the user is deleted and the below message is returned.
        if current_user.email == args['email']:
            delete_user_from_db(current_user.email)

        else:
            # checks the user is an admin.
            check_user_role(current_user, 'Admin')

            # looks for a user with the passed in email in the database.
            user = User.query.filter_by(email=args['email']).first()

            # if the user is not in the database then returns a not found error.
            if not user:
                abort(404, message="User does not exist, cannot be deleted.")

            # deletes the all information associated with the passed in email from the database.
            delete_user_from_db(args['email'])

        return {'message': f'User {args["email"]} deleted'}


# adds the UserApi resource to the api.
api.add_resource(UserApi, '/api/user')


class RecordApi(Resource):
    """
    Allows user medical records to be viewed and added.
    """
    def __init__(self):
        # valid record types.
        self.record_types = ['blood_pressure', 'weight']

    def get(self, record_type):
        """
        Allows users to view the records of different users, depending on their role.
        """
        # Parses the arguments passed in the request.
        args = record_get_args.parse_args()
        # checks the token sent with the request.
        current_user = check_token(args['token'])

        if record_type == 'blood_pressure':

            if current_user.email == args['email']:
                # if the current user is requesting their own records then they are decrypted
                # and returned as json.
                encrypted_bp = BloodPressure.query.filter_by(user_id=current_user.id).order_by(
                    BloodPressure.date_posted.desc()).all()

                posts = decrypt_medical_record(encrypted_bp, current_user.key)

                return jsonify(posts)

            if current_user.role in ['Admin', 'Medic']:
                # if the current user is an admin or medic then the requested
                # records are decrypted and returned as json.

                user = User.query.filter_by(email=args['email']).first()

                if not user or user.role != 'Astronaut':
                    return abort(404, message='User not found or not an astronaut.')

                encrypted_bp = BloodPressure.query.filter_by(user_id=user.id).order_by(
                    BloodPressure.date_posted.desc()).all()

                posts = decrypt_medical_record(encrypted_bp,
                                               User.query.filter_by(email=args['email']).\
                                               first().key)

                return jsonify(posts)

        if record_type == 'weight':

            if current_user.email == args['email']:
                # if the current user is requesting their own records then they are decrypted
                # and returned as json.
                encrypted_weight = Weight.query.filter_by(user_id=current_user.id).order_by(
                    Weight.date_posted.desc()).all()

                posts = decrypt_medical_record(encrypted_weight, current_user.key)

                return jsonify(posts)

            if current_user.role in ['Admin', 'Medic']:
                # if the current user is an admin or medic then the requested
                # records are decrypted and returned as json.

                user = User.query.filter_by(email=args['email']).first()

                if not user or user.role != 'Astronaut':
                    return abort(404, message='User not found or not an astronaut.')

                encrypted_weight = Weight.query.filter_by(user_id=user.id).order_by(
                    Weight.date_posted.desc()).all()

                posts = decrypt_medical_record(encrypted_weight,
                                               User.query.filter_by(email=args['email']).\
                                               first().key)

                return jsonify(posts)

        # access denied error
        return abort(403, message='Access denied. Check token or request records')

    def put(self, record_type):
        """
        Allows astronauts to add new medical records to the database.
        """
        # Parses the arguments passed in the request.
        args = record_put_args.parse_args()
        # checks the token sent with the request.
        current_user = check_token(args['token'])
        # checks the current user is an astronaut.
        check_user_role(current_user, 'Astronaut')

        if record_type == 'blood_pressure':
            # new blood pressure is encrypted using the current user's key
            encrypted_blood_pressure = encrypt_medical_record(args['record'], current_user.key)

            # new blood pressure object is added to the database and the change is committed.
            bp = BloodPressure(record=encrypted_blood_pressure, user_id=current_user.id)
            db.session.add(bp)
            db.session.commit()

            # returns success message.
            return {'message': 'Blood pressure record added.'}

        if record_type == 'weight':
            # new weight is encrypted using the current user's key
            encrypted_weight = encrypt_medical_record(args['record'], current_user.key)

            # new weight object is added to the database and the change is committed.
            weight = Weight(record=encrypted_weight, user_id=current_user.id)
            db.session.add(weight)
            db.session.commit()

            # returns success message.
            return {'message': 'Weight record added.'}

        # record type error message.
        return {'message': f'record_type must be in {self.record_types}.'}


# adds the RecordApi resource to the api.
api.add_resource(RecordApi, '/api/record/<string:record_type>')


class PostApi(Resource):
    """
    Allows user to view and send posts to other users.
    """
    def get(self):
        """
        Allows users to view their sent and received messages.
        """
        # Parses the arguments passed in the request.
        args = post_get_args.parse_args()
        # checks the token sent with the request.
        current_user = check_token(args['token'])

        if args['email'] == 'all':
            # decrypts all conversations involving the current user if
            # the email argument passed in is 'all'

            # pulls all posts involving the current user from the database.
            encrypted_posts = db.session.query(Post) \
                .where((Post.recipient == current_user.email) | (Post.user_id == current_user.id)) \
                .order_by(Post.date_posted.desc()).all()

            posts = []		# empty list for decrypted posts to be appended to.

            for post in encrypted_posts:
                post_list = [post]    # decrypt_post() takes a list as an arg.

                # decrypts the posts using the appropriate key.
                if post_list[0].recipient == current_user.email:
                    posts.append(decrypt_post(post_list, current_user.key)[0])

                else:
                    user = User.query.filter_by(email=post.recipient).first()
                    posts.append(decrypt_post(post_list, user.key)[0])

            # returns the posts as json.
            return jsonify(posts)

        # looks for a user with the passed in email address in the database.
        user = User.query.filter_by(email=args['email']).first()

        if not user:
            return abort(404, message='User not found.')

        # finds all posts between the current user and the user passed in.
        encrypted_posts = db.session.query(Post) \
            .where(((Post.user_id == user.id) & (Post.recipient == current_user.email))
                   | ((Post.user_id == current_user.id) & (Post.recipient == user.email))) \
            .order_by(Post.date_posted.desc()).all()

        posts = []		# empty list for decrypted posts to be appended to.

        for post in encrypted_posts:
            post_list = [post]		# decrypt_post() takes a list as an arg.

            # decrypts the posts using the appropriate key.
            if post_list[0].recipient == current_user.email:
                posts.append(decrypt_post(post_list, current_user.key)[0])

            if post_list[0].recipient == user.email:
                posts.append(decrypt_post(post_list, user.key)[0])

        # returns the posts as json.
        return jsonify(posts)

    def put(self):
        """
        Allows users to send private posts to other users.
        """
        # Parses the arguments passed in the request.
        args = post_put_args.parse_args()
        # checks the token sent with the request.
        current_user = check_token(args['token'])

        # looks for a user with the passed in email address in the database.
        user = User.query.filter_by(email=args['email']).first()

        # if the user is not in the database then returns a not found error.
        if not user:
            return abort(404, message='Recipient not found')

        else:
            # encrypts the content passed in the request.
            encrypted_content = encrypt_post(args['content'], args['email'])

            # new post object containing the pass in data.
            post = Post(recipient=args['email'],
                        title=args['title'],
                        content=encrypted_content,
                        user_id=current_user.id)

            # new post added to the database and the change is committed.
            db.session.add(post)
            db.session.commit()

            # returns success message.
            return {'message': f'Post sent to {args["email"]}.'}


# adds the PostApi resource to the api.
api.add_resource(PostApi, '/api/post')
