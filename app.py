from flask import Flask, send_file, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
import logging
basedir = os.path.abspath(os.path.dirname(__file__))

log_file = os.path.join(basedir, 'trackgmailserver.log')
logging.basicConfig(
    filename=log_file,
    level = logging.INFO,
    format = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
# handler.setLevel(logging.INFO)
# formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
# handler.setFormatter(formatter)



app = Flask(__name__)
# app.logger.addHandler(handler)


app.logger.info('Flask app started')
print('Flask app started')

CORS(app)


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
    app.logger.info('Home page accessed')
    return 'Home, hello world!'





@app.route('/images', methods=['POST'])
# @cross_origin(origin='https://mail.google.com')
def add_new_image():
    data = request.json
    if not data or not data.get('image_key'):
        app.logger.error('Invalid input data')
        return jsonify({'error' : 'Invalid input data'}), 400
    
    image_key = int(data.get('image_key'))
    if ImageKey.query.filter_by(image_key = image_key).first():
        app.logger.error('Image index already exists')
        return jsonify({'error': 'Image index already exists'}), 409

    image = ImageKey(image_key = image_key, visits = 0)
    db.session.add(image)
    db.session.commit()
    app.logger.info('Image Index added successfully')
    return jsonify({'success' : 'Image Index added successfully'}), 201






@app.route('/images/<int:image_key>')
# @cross_origin(origin='https://mail.google.com')
def download_image(image_key):
    """
    Download image from the specified path and serve it to the user
    """
    # Check if key exists
    key_called = ImageKey.query.filter_by(image_key = image_key).first()
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