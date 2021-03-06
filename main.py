from flask import Flask, render_template, request, redirect, url_for
from datetime import timedelta

from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from models import db, Student, Exercise, Routine, Selected
from sqlalchemy.exc import IntegrityError

''' Begin boilerplate code '''

login_manager = LoginManager()
@login_manager.user_loader
def load_user(student_id):
	return Student.query.get(student_id)


def create_app():
	app = Flask(__name__, template_folder="templates")
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	app.config['SECRET_KEY'] = "MYSECRET"
	login_manager.init_app(app)
	db.init_app(app)
	return app


app = create_app()

app.app_context().push()
''' End Boilerplate Code '''


@app.route("/")
def home():
	return render_template("home.html")


@app.route("/signup")
def signupPage():
	return render_template("signup.html")


@app.route("/signup", methods=(['POST']))
def signup():
	if request.method == 'POST':
		userData = request.form.to_dict()
		print(userData)
		if userData:
			newUser = Student(studentId=userData["studentid"], email=userData["email"])  # to create a Student object
			newUser.set_password(userData['pass'])  # to set the password
			try:
				db.session.add(newUser)
				db.session.commit()
				return render_template('login.html'), 201
			except IntegrityError:
				db.session.rollback()
				return "Looks like you already signed up", 400
		return 'Nothing submitted', 400
	return


@app.route("/login", methods=(['GET', 'POST']))
def login():
	if request.method == 'GET':
		return render_template('login.html')

	elif request.method == 'POST':
		userData = request.form.to_dict()
		username = userData['studentid']
		password = userData['pass']
		student = Student.query.filter_by(studentId=username).first()
		if student and student.check_password(password):
			time = timedelta(hours=1)
			login_user(student, False, time)
			return workouts(), 200
		if student is None:
			return render_template("signup.html"), 401
		return "Invalid login", 401


@login_manager.unauthorized_handler
def unauthorized():
	return render_template('login.html')


@app.route("/oops")
def error():
	return render_template("error.html")


@app.route("/workouts", methods=(['GET']))
@login_required
def workouts():
	asgs = Exercise.query.all()
	report = ""
	return render_template("workouts.html", message=report, exerciselist=asgs)


@app.route("/workouts", methods=(['POST']))
@login_required
def search():
	if request.method == 'POST':
		entry = request.form.to_dict()
		key = entry['keyword']
		print(key)
		searchk = "%{}%".format(key)
		asgs = Exercise.query.filter(Exercise.exerciseName.like(searchk)).all()
		if asgs:
			report = ""
			return render_template("workouts.html", message=report, exerciselist=asgs)
		else:
			report = "No exercises found."
			return render_template("workouts.html", message=report, exerciselist=asgs)
	return error(), 400


@app.route("/routine", methods=(['GET']))
@login_required
def routine():
	asgs = Exercise.query.all()
	return render_template("routine.html", exerciselist=asgs)


@app.route('/routine', methods=['POST'])
@login_required
def create_my_routine():
	data = request.form.to_dict()
	print(data)
	rec = Routine(routineName=data["routineName"], userid=current_user.id)
	try:
		db.session.add(rec)
		num = db.session.flush()
		db.session.commit()
		add_exercises(num, data)
		return routine(), 201
	except IntegrityError:
		db.session.rollback()
		return "Routine already exists", 400


def add_exercises(rid, data):
	for key in data:
		if key == "exercise":
			print(data[key])
			name = str(data[key])
			reps = data["reps"]
			print(reps)
			sets = data["sets"]
			print(sets)
			newSet = Selected(rid=rid, reps=reps, sets=sets, ename=name)
			try:
				db.session.add(newSet)
				db.session.commit()
			except IntegrityError:
				db.session.rollback()
	return



@app.route("/aboutus")
def aboutus():
	return render_template("aboutus.html")


@app.route("/logout", methods=(['GET']))
@login_required
def logout():
	logout_user()
	return render_template("home.html")