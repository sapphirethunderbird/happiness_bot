from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///happy_bot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    moments = db.relationship('HappyMoment', backref='user', lazy=True)

class HappyMoment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Initialize database
db.create_all()

# API endpoints
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists!"}), 400
    new_user = User(username=username)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User signed up successfully!"}), 201

@app.route('/submit', methods=['POST'])
def submit_moment():
    data = request.json
    username = data.get('username')
    content = data.get('content')
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found!"}), 404

    new_moment = HappyMoment(content=content, user=user)
    db.session.add(new_moment)
    db.session.commit()
    return jsonify({"message": "Happy moment submitted successfully!"}), 201

@app.route('/moments', methods=['GET'])
def get_moments():
    moments = HappyMoment.query.all()
    moment_list = [{"id": m.id, "content": m.content, "likes": m.likes, "username": m.user.username} for m in moments]
    return jsonify(moment_list), 200

@app.route('/like/<int:moment_id>', methods=['POST'])
def like_moment(moment_id):
    moment = HappyMoment.query.get(moment_id)
    if not moment:
        return jsonify({"message": "Moment not found!"}), 404
    moment.likes += 1
    db.session.commit()
    return jsonify({"message": "Moment liked!"}), 200

@app.route('/learn', methods=['GET'])
def learn_happy_triggers():
    moments = HappyMoment.query.order_by(HappyMoment.likes.desc()).limit(5).all()
    triggers = [{"content": m.content, "likes": m.likes} for m in moments]
    return jsonify({"happy_triggers": triggers}), 200

if __name__ == '__main__':
    app.run(debug=True)

