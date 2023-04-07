from flask import Flask, send_file, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS, cross_origin
import logging
import sys

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.logger.addHandler(logging.StreamHandler(sys.stdout))

CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(basedir, 'imagekey.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class ImageKey(db.Model):
    image_key = db.Column(db.Integer, primary_key=True)
    visits = db.Column(db.Integer)

    def __repr__(self):
        return f'Image key - {self.image_key}; Visits - {self.visits}'

@app.route('/')
def helloWorld():
    return 'Home, hello world!'

@app.route('/images', methods=['POST'])
# @cross_origin(origin='https://mail.google.com')
def add_new_image():
    data = dict(request.json)
    if not data or not data['image_key'] or not isinstance(data['image_key'], int):
        return jsonify({'error' : 'Invalid input data'}), 400
    
    if ImageKey.query.filter_by(image_key = data['image_key']).first():
        return jsonify({'error': 'Image index already exists'}), 409

    image = ImageKey(image_key = data['image_key'], visits = 0)
    db.session.add(image)
    db.session.commit()
    return jsonify({'success' : 'Image Index added successfully'}), 201


@app.route('/images/<int:image_key>')
# @cross_origin(origin='https://mail.google.com')
def download_image(image_key):
    """
    Download image from the specified path and serve it to the user
    """
    # Check if key exists
    # key_called = ImageKey.query.filter_by(image_key = image_key).first()
    key_called = ImageKey.query.get(image_key)
    app.logger.info("Key searched in database")
    if key_called is not None:
        app.logger.info(f"Accessed key - {key_called}")
        key_called.visits += 1
        if key_called.visits >= 2:
            db.session.delete(key_called)
            db.session.commit()
        else:
            db.session.commit()    
    else:
        app.logger.info("No key found")
    # Serve file to the user
    return send_file('images/tree.jpg', as_attachment=True)

if __name__ == '__main__':
    app.run(debug = True)