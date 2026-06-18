import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import random
current_month = 1

app = Flask(__name__)

# ensure database folder exists
if not os.path.exists("database"):
    os.makedirs("database")

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'database', 'committee.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- DATABASE MODEL ----------------
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    monthly_amount = db.Column(db.Integer, default=10000)
    has_received = db.Column(db.Boolean, default=False)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    month = db.Column(db.Integer)
    amount = db.Column(db.Integer)
    status = db.Column(db.String(20))  # Paid / Unpaid

class Winner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    month = db.Column(db.Integer)
    amount = db.Column(db.Integer)

# ---------------- ROUTES ----------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/members')
def members():
    all_members = Member.query.all()
    return render_template('members.html', members=all_members)

@app.route('/add-member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']

        new_member = Member(name=name, phone=phone)
        db.session.add(new_member)
        db.session.commit()

        return redirect('/members')

    return render_template('add_member.html')

@app.route('/delete-member/<int:id>')
def delete_member(id):
    member = Member.query.get(id)
    if member:
        db.session.delete(member)
        db.session.commit()
    return redirect('/members')

@app.route('/payments')
def payments():
    members = Member.query.all()
    return render_template('payments.html', members=members)



@app.route('/draw-winner')
def draw_winner():
    global current_month

    # check if already winner exists for this month
    existing_winner = Winner.query.filter_by(month=current_month).first()

    if existing_winner:
        return redirect('/winners')

    available_members = Member.query.filter_by(has_received=False).all()

    if not available_members:
        return "No members available"

    winner = random.choice(available_members)

    # mark as received
    winner.has_received = True

    # save winner
    new_winner = Winner(
        member_id=winner.id,
        month=current_month,
        amount=100000
    )

    db.session.add(new_winner)
    db.session.commit()

    # move to next month ONLY after success
    current_month += 1

    return redirect('/winners')

@app.route('/winners')
def winners():
    data = Winner.query.all()
    return render_template('winners.html', winners=data)

# ---------------- RUN APP ----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)