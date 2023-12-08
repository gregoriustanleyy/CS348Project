from flask import Flask, request, render_template, jsonify, send_from_directory, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from os.path import isfile, join
from datetime import timedelta
import sqlite3

app = Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///artnet_db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Define ORM model
db = SQLAlchemy(app)

class Artwork(db.Model):
    __tablename__ = 'artworks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    listed = db.Column(db.Boolean, default=True, nullable=False)

def get_db_connection():
    db_path = os.path.join(app.instance_path, 'artnet_db.sqlite3')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

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
    required_fields = ['artworkImage', 'artworkTitle', 'artworkArtist', 'artworkPrice']
    missing_fields = [field for field in required_fields if field not in request.form and field not in request.files]
    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

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
            print(f"Artwork ID {new_artwork.id} uploaded successfully!") 
            return jsonify({"message": "Artwork uploaded successfully!", "id": new_artwork.id})
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"An error occurred while uploading artwork: {e}")
            return jsonify({"error": "An error occurred while uploading artwork."}), 500
    else:
        return jsonify({"error": "Invalid form data."}), 400
    
@app.route('/get_artworks', methods=['GET'])
def get_artworks():
    try:
        artworks = Artwork.query.all()
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
    
@app.route('/edit_artwork', methods=['POST'])
def edit_artwork():
    artwork_id = request.form.get('artwork_id')
    new_artist = request.form.get('new_artist')
    new_price = request.form.get('new_price')

    try:
        artwork = Artwork.query.get(artwork_id)
        if artwork:
            artwork.artist = new_artist if new_artist else artwork.artist
            artwork.price = float(new_price) if new_price else artwork.price
            db.session.commit()
            return redirect(url_for('index', edit='success'))
        else:
            return redirect(url_for('index', edit='error'))
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('index', edit='error'))

@app.route('/statistics_content')
def statistics_content():
    conn = get_db_connection()
    avg_price = conn.execute('SELECT AVG(price) as avg_price FROM artworks').fetchone()['avg_price']
    total_artworks = conn.execute('SELECT COUNT(*) as total_artworks FROM artworks').fetchone()['total_artworks']
    avg_price_listed = conn.execute('SELECT listed, AVG(price) AS average_price FROM artworks GROUP BY listed').fetchall()
    artworks_by_artist = conn.execute('SELECT artist, COUNT(*) as artwork_count FROM artworks GROUP BY artist').fetchall()
    expensive_artworks = conn.execute('SELECT title, price FROM artworks WHERE price > 2000').fetchall()
    top_artists_by_avg_price = conn.execute('SELECT artist, AVG(price) as avg_price FROM artworks GROUP BY artist ORDER BY avg_price DESC LIMIT 5').fetchall()
    common_price_points = conn.execute('SELECT price, COUNT(*) as frequency FROM artworks GROUP BY price ORDER BY frequency DESC LIMIT 5').fetchall()
    listed_percentage = conn.execute("""
        SELECT 
            listed, 
            ROUND((COUNT(*) * 100.0) / (SELECT COUNT(*) FROM artworks), 2) as percentage 
        FROM artworks 
        GROUP BY listed
    """).fetchall()
    avg_price_by_range = conn.execute("""
        SELECT 
            CASE 
                WHEN price < 500 THEN 'Under $500'
                WHEN price BETWEEN 500 AND 1000 THEN '$500 - $1000'
                WHEN price BETWEEN 1001 AND 2000 THEN '$1001 - $2000'
                ELSE 'Above $2000'
            END AS price_range,
            AVG(price) AS avg_price
        FROM artworks
        GROUP BY price_range
    """).fetchall()
    price_ranges = conn.execute("""
        SELECT 
            CASE 
                WHEN price < 500 THEN 'Under $500'
                WHEN price BETWEEN 500 AND 1000 THEN '$500 - $1000'
                WHEN price BETWEEN 1001 AND 2000 THEN '$1001 - $2000'
                ELSE 'Above $2000'
            END AS price_range,
            COUNT(*) AS count
        FROM artworks
        GROUP BY price_range
    """).fetchall()
    conn.close()

    statistics_html = (
        f"<div><h2>Statistics</h2>"
        f"<p>Average Price: {avg_price}</p>"
        f"<p>Total Artworks: {total_artworks}</p>"
        "<h3>Price Range Distribution:</h3><ul>" +
        "".join([f"<li>{range['price_range']}: {range['count']} artworks</li>" for range in price_ranges]) +
        "</ul>"
        "<h3>Average Price (Listed vs. Not Listed):</h3><ul>" +
        "".join([f"<li>{'Listed' if item['listed'] else 'Not Listed'}: ${item['average_price']:.2f}</li>" for item in avg_price_listed]) +
        "</ul>"
        "<h3>Percentage of Artworks Listed vs. Not Listed:</h3><ul>" +
        "".join([f"<li>{'Listed' if item['listed'] == 1 else 'Not Listed'}: {item['percentage']}%</li>" for item in listed_percentage]) +
        "</ul>"
        "<h3>Number of Artworks by Each Artist:</h3><ul>" +
        "".join([f"<li>{artist_info['artist']}: {artist_info['artwork_count']} artworks</li>" for artist_info in artworks_by_artist]) +
        "</ul>"
        "<h3>Artworks Priced Above $2000:</h3><ul>" +
        "".join([f"<li>{artwork['title']} - ${artwork['price']}</li>" for artwork in expensive_artworks]) +
        "</ul>"
        "<h3>Top Artists by Average Price:</h3><ul>" +
        "".join([f"<li>{artist['artist']}: Average price ${artist['avg_price']:.2f}</li>" for artist in top_artists_by_avg_price]) +
        "</ul>"
        "<h3>Most Common Artwork Price Points:</h3><ul>" +
        "".join([f"<li>${price_point['price']}: {price_point['frequency']} times</li>" for price_point in common_price_points]) +
        "</ul>"
        "<h3>Average Price in Each Price Range:</h3><ul>" +
        "".join([f"<li>{range_info['price_range']}: Average price ${range_info['avg_price']:.2f}</li>" for range_info in avg_price_by_range]) +
        "</ul>"
        "<div style='margin-bottom: 30px;'></div></div>"
    )
    return jsonify({'htmlContent': statistics_html})

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)
