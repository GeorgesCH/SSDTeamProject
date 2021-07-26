"""Module containing functions for encrypting/decrypting data.

Functions:
    encrypt_medical_record -- encrypts a given medical record using the user key.
    decrypt_medical_record -- decrypts a number of posts using the key.
    encrypted_post -- encrypts a post using the recipient's key.
    decrypt_post -- decrypts a number of posts using the key.
"""

from cryptography.fernet import Fernet
from healthapp.models import User


def encrypt_medical_record(new_entry, user_key):
    """Encrypts a record using the given key.

    Args:
        new_entry -- the new record entry that is to be encrypted.
        user_key -- the key of the user that the record is associated with.
    """

    # encodes the new record entry as a byte string as required by Fernet.
    encoded_data = new_entry.encode()

    # encrypts the record with the user's key, and decodes the encrypted data
    # to a utf-8 string to be passed into the database.
    encrypted_data = Fernet(user_key.encode()).encrypt(encoded_data).decode('utf-8')
    return encrypted_data


def decrypt_medical_record(encrypted_posts, key):
    """Decrypts records using the given key.

    Args:
         encrypted_posts -- posts to be decrypted.
         key -- encryption key associated with the records.
    """

    decrypted_posts = []    # empty list for decrypted posts the be appended to.

    for post in encrypted_posts:
        encrypted_data = post.record.encode()   # encodes post as a byte string required by Fernet.

        # decrypts the data using fernet and the user's key, and decodes it to a utf-8 string.
        decrypted_data = Fernet(key.encode()).decrypt(encrypted_data).decode('utf-8')

        # writes the decrypted record to a dictionary, along with other record
        # info from the database.
        decrypted_posts.append({'id': post.id,
                                'author': post.author.email,
                                'date_posted': post.date_posted.strftime('%Y-%m-%d'),
                                'record': decrypted_data})

    return decrypted_posts


def encrypt_post(post, recipient):
    """Encrypts a user post using the recipient's key.

    Args:
        post -- The post to be encrypted.
        recipient -- the recipient of the post
    """

    # gets the recipient's key form the database.
    encryption_key = User.query.filter_by(email=recipient).first().key
    # encodes post as a byte string.
    encoded_data = post.encode()
    # encrypts post using the key and decodes it to utf-8 string to pass into the database.
    encrypted_post = Fernet(encryption_key.encode()).encrypt(encoded_data).decode('utf-8')

    return encrypted_post


def decrypt_post(encrypted_posts, key):
    """Decrypts posts using the given key.

    Args:
          encrypted_posts -- the posts to be decrypted.
          key -- recipient key associated with the encrypted posts.
    """

    decrypted_posts = []    # empty list for decrypted post to be appended to.

    for post in encrypted_posts:
        encrypted_data = post.content.encode()  # encodes post to a byte string.
        # decrypts post using the passed in key and decodes it to a utf-8 string.
        decrypted_data = Fernet(key.encode()).decrypt(encrypted_data).decode('utf-8')

        # writes decrypted post to a dictionary along with appropriate post data from the database.
        decrypted_posts.append({'id': post.id,
                                'author': post.author.email,
                                'recipient': post.recipient,
                                'date_posted': post.date_posted.strftime('%Y-%m-%d'),
                                'title': post.title,
                                'content': decrypted_data})

    return decrypted_posts
