from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL, Regexp
from dotenv import load_dotenv
import datetime
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
Bootstrap5(app)


# Database
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Add form
class AddCafeForm(FlaskForm):
    name = StringField(label='Cafe name', validators=[DataRequired()])
    location = StringField(label='Location', validators=[DataRequired()])
    map_url = StringField(label="Location link", validators=[DataRequired(), URL(message="Invalid URL"),
                                                             Regexp("^https",
                                                                    message="URL must begin with https")])
    img_url = StringField(label="Image link", validators=[DataRequired(), URL(message="Invalid URL"),
                                                          Regexp("^https", message="URL must begin with https")])
    has_sockets = SelectField(
        label="Sockets",
        choices=[('0', 'No'), ('1', 'Yes')],
        validators=[DataRequired()]
    )
    has_toilet = SelectField(
        label="Toilets",
        choices=[('0', 'No'), ('1', 'Yes')],
        validators=[DataRequired()]
    )
    has_wifi = SelectField(
        label="WiFi",
        choices=[('0', 'No'), ('1', 'Yes')],
        validators=[DataRequired()]
    )
    can_take_calls = SelectField(
        label="Take calls?",
        choices=[('0', 'No'), ('1', 'Yes')],
        validators=[DataRequired()]
    )
    seats = SelectField(
        label="Number of seats",
        choices=[('0', '0 - 10'),
                 ('1', '10 - 20'),
                 ('2', '20 - 30'),
                 ('3', '30 - 40'),
                 ('4', '40 - 50'),
                 ('5', '50 +')],
        validators=[DataRequired()]
    )
    coffee_price = StringField(label="Coffee price", validators=[DataRequired()])
    submit = SubmitField(label='Add Cafe')


# Create / configure Table here
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    has_sockets: Mapped[int] = mapped_column(Integer, nullable=False)
    has_toilet: Mapped[int] = mapped_column(Integer, nullable=False)
    has_wifi: Mapped[int] = mapped_column(Integer, nullable=False)
    can_take_calls: Mapped[int] = mapped_column(Integer, nullable=False)
    seats: Mapped[str] = mapped_column(String(50), nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(20), nullable=False)


# with app.app_context():
#     db.create_all()

@app.route('/')
def homepage():
    current_year = datetime.datetime.now().year
    return render_template('index.html', current_year=current_year)


@app.route("/about")
def about():
    current_year = datetime.datetime.now().year
    return render_template("about.html", current_year=current_year)


@app.route('/all-cafes')
def get_all_cafes():
    current_year = datetime.datetime.now().year

    admin_access = request.args.get('key') == SECRET_KEY
    all_cafes = db.session.execute(db.select(Cafe)).scalars().all()
    cafes = [cafe for cafe in all_cafes]
    return render_template('all_cafes.html', all_cafes=cafes, admin_access=admin_access, current_year=current_year)


@app.route('/cafe/<int:cafe_id>')
def show_cafe(cafe_id):
    current_year = datetime.datetime.now().year

    requested_cafe = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
    return render_template("cafe.html", cafe=requested_cafe, current_year=current_year)


@app.route('/add-cafe', methods=['GET', 'POST'])
def add_cafe():
    current_year = datetime.datetime.now().year

    form = AddCafeForm()

    if form.validate_on_submit() and request.method == "POST":
        new_cafe = Cafe(
            name=request.form.get('name'),
            map_url=request.form.get('map_url'),
            img_url=request.form.get('img_url'),
            location=request.form.get('location'),
            has_sockets=request.form.get('has_sockets'),
            has_toilet=request.form.get('has_toilet'),
            has_wifi=request.form.get('has_wifi'),
            can_take_calls=request.form.get('can_take_calls'),
            seats=request.form.get('seats'),
            coffee_price=request.form.get('coffee_price'),
        )
        db.session.add(new_cafe)
        db.session.commit()

        return redirect(url_for('get_all_cafes'))

    return render_template("add-cafe.html", form=form, current_year=current_year)


@app.route('/delete-cafe/<cafe_id>')
def delete_cafe(cafe_id):
    post_to_delete = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()

    db.session.delete(post_to_delete)
    db.session.commit()

    return redirect(url_for('get_all_cafes', cafe_id=post_to_delete.id))


if __name__ == "__main__":
    app.run(debug=True)
