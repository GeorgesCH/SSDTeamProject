"""Module containing functions for downloading data

Functions:
    download_record -- downloads specified records of a user.
"""

import csv
from pathlib import Path
from flask_login import current_user
from flask import send_file
from healthapp.encryption import decrypt_post, decrypt_medical_record
from healthapp.models import User, Post, Weight, BloodPressure
from healthapp import db


def download_record(user_email, record_type):
    """Downloads data of the given user and record.

    Args:
        user_email -- the email of the user whose data is to be downloaded.
        record_type - the type of record to be downloaded.
    """
    path = Path(__file__).parent / "../ExportedData.csv"   # path csv is temporarily saved to.
    user = User.query.filter_by(email=user_email).first()   # user that owns the record

    if record_type == 'Posts':
        # pulls all post between the specified user and the current user from the database.
        encrypted_posts = db.session.query(Post) \
            .where(((Post.user_id == user.id) & (Post.recipient == current_user.email))
                   | ((Post.user_id == current_user.id) & (Post.recipient == user.email))) \
            .order_by(Post.date_posted.desc()).all()

        posts = []  # empty list that decrypted posts are appended to.

        for post in encrypted_posts:
            post_list = [post]  # decrypt_posts() requires a list as an argument.

            if post_list[0].recipient == current_user.email:
                # if current user is post recipient then their key is used to decrypt.
                posts.append(decrypt_post(post_list, current_user.key)[0])

            if post_list[0].recipient == user.email:
                # if specified user is post recipient then their key is used to decrypt.
                posts.append(decrypt_post(post_list, user.key)[0])

        with open(path, 'w') as csvfile:
            # writes the decrypted posts to the csv at the path.
            # field names are column names.
            writer = csv.DictWriter(
                csvfile,
                fieldnames=['id', 'author', 'recipient', 'date_posted', 'title', 'content']
            )

            writer.writeheader()

            for post in posts:
                writer.writerow(post)

    elif record_type == 'Blood Pressure':
        # pulls all blood pressure records for the given user from the database.
        encrypted_bp = BloodPressure.query.filter_by(user_id=user.id).all()

        # decrypts records using the specified user's key
        posts = decrypt_medical_record(encrypted_bp, user.key)

        with open(path, 'w') as csvfile:
            # writes the decrypted posts to the csv at the path.
            # field names are column names.
            writer = csv.DictWriter(csvfile, fieldnames=['id', 'author', 'date_posted', 'record'])
            writer.writeheader()
            for post in posts:
                writer.writerow(post)

    elif record_type == 'Weight':
        # pulls all weight records for the given user from the database.
        encrypted_weight = Weight.query.filter_by(user_id=user.id).all()

        # decrypts records using the specified user's key
        posts = decrypt_medical_record(encrypted_weight, user.key)

        with open(path, 'w') as csvfile:
            # writes the decrypted posts to the csv at the path.
            # field names are column names.
            writer = csv.DictWriter(csvfile, fieldnames=['id', 'author', 'date_posted', 'record'])
            writer.writeheader()
            for post in posts:
                writer.writerow(post)

    return send_file(path, as_attachment=True)  # sends csv file to be downloaded.
