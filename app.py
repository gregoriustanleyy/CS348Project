from flask import Flask, request, render_template, jsonify, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from os.path import isfile, join
from datetime import timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///artnet_db.sqlite3'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Define ORM model
db = SQLAlchemy(app)

class Artwork(db.Model):
    __tablename__ = 'artworks'  # Ensure the table name is correct
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    listed = db.Column(db.Boolean, default=True, nullable=False)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return upload_artwork()
    else:
        image_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if isfile(join(app.config['UPLOAD_FOLDER'], f))]
        return render_template('index.html', images=image_files)

@app.route('/upload_artwork', methods=['POST'])
def upload_artwork():
    print('Form data:', request.form)
    print('File data:', request.files)
    # Check if all required form fields are present
    required_fields = ['artworkImage', 'artworkTitle', 'artworkArtist', 'artworkPrice']
    missing_fields = [field for field in required_fields if field not in request.form and field not in request.files]
    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    # Extract the uploaded file, title, artist, and price
    image = request.files.get('artworkImage')
    title = request.form.get('artworkTitle')
    artist = request.form.get('artworkArtist')
    price = request.form.get('artworkPrice')

    if image and allowed_file(image.filename) and title and artist and price:
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        image_url = url_for('uploaded_file', filename=filename, _external=True)

        try:
            price = float(price)
            new_artwork = Artwork(title=title, artist=artist, price=price, image_url=image_url)
            db.session.add(new_artwork)
            db.session.commit()
            print(f"Artwork ID {new_artwork.id} uploaded successfully!")  # Log the new artwork ID
            return jsonify({"message": "Artwork uploaded successfully!", "id": new_artwork.id})
        except Exception as e:
            db.session.rollback()  # Rollback in case of exception
            app.logger.error(f"An error occurred while uploading artwork: {e}")
            return jsonify({"error": "An error occurred while uploading artwork."}), 500
    else:
        return jsonify({"error": "Invalid form data."}), 400
    
@app.route('/get_artworks', methods=['GET'])
def get_artworks():
    try:
        artworks = Artwork.query.all()  # Use SQLAlchemy ORM to fetch all artwork records
        artworks_list = [{"id": artwork.id, "title": artwork.title, "artist": artwork.artist, "price": artwork.price, "image_url": artwork.image_url} for artwork in artworks]
        print(artworks_list)
        return jsonify(artworks_list)
    except Exception as e:
        app.logger.error(f"An error occurred while retrieving artworks: {e}")
        return jsonify({"error": "An error occurred while retrieving artworks."}), 500
    
@app.route('/delete_artwork/<int:artwork_id>', methods=['DELETE'])
def delete_artwork(artwork_id):
    try:
        artwork = Artwork.query.get(artwork_id)
        db.session.delete(artwork)
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)
