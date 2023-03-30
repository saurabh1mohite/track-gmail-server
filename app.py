from flask import Flask, send_file, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import os
from flask import Flask
from flask_cors import CORS
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
CORS(app)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'imagekey.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(app)


class ImageKey(db.Model):
    image_key = db.Column(db.Integer, primary_key=True)
    visits = db.Column(db.Integer)

    def __repr__(self):
        return f'Image key - {self.image_key}; Visits - {self.visits}'



@app.route('/')
def helloWorld():
    return 'Hello world!'

@app.route('/images', methods=['POST'])
def add_new_image():
    data = request.json
    if not data or not data.get('image_key') or not isinstance(data.get('image_key'), int):
        return jsonify({'error' : 'Invalid input data'}), 400
    
    if ImageKey.query.filter_by(image_key = data['image_key']).first():
        return jsonify({'error': 'Image index already exists'}), 409

    image = ImageKey(image_key = data['image_key'], visits = 0)
    db.session.add(image)
    db.session.commit()
    response = make_response(jsonify({'success' : 'Image Index added successfully'}), 201)
    response.headers['Access-Control-Allow-Origin'] = 'https://mail.google.com'
    return response

@app.route('/images/<int:image_key>')
def download_image(image_key):
    """
    Download image from the specified path and serve it to the user
    """
    # Check if key exists
    key_called = ImageKey.query.filter_by(image_key = image_key).first()
    app.logger.info("Key searched in database")
    if key_called:
        app.logger.info(f"Accessed key - {key_called}")
        if key_called.visits < 2:
            key_called.visits += 1
            db.session.commit()
        else:
            db.session.delete(key_called)
            db.session.commit()
    else:
        app.logger.info("No key found")
    # Serve file to the user
    return send_file('images/tree.jpg', as_attachment=True)       


if __name__ == '__main__':
    app.run(debug = True)
