from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt, mongo
from app.models import User
from app.forms import RegistrationForm, LoginForm
from datetime import datetime
import logging

# Setup logging
logger = logging.getLogger(__name__)

def register_routes(app):
    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            try:
                existing_user = User.query.filter_by(email=form.email.data).first()
                if existing_user:
                    flash('Email already registered. Please use a different email.', 'danger')
                    return render_template('register.html', form=form)

                hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                user = User(
                    username=form.username.data,
                    email=form.email.data,
                    password=hashed_password
                )
                db.session.add(user)
                db.session.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred. Please try again.', 'danger')
                logger.error(f'Registration error: {str(e)}')
        
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                flash('Login successful!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'danger')
        
        return render_template('login.html', form=form)

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/add_patient', methods=['GET', 'POST'])
    @login_required
    def add_patient():
        if request.method == 'POST':
            try:
                print("Received form data:", request.form)
                
                patient_data = {
                    'patient_id': request.form.get('patient_id'),
                    'name': request.form.get('name'),
                    'gender': request.form.get('gender'),
                    'age': int(request.form.get('age')),
                    'hypertension': int(request.form.get('hypertension')),
                    'ever_married': request.form.get('ever_married'),
                    'work_type': request.form.get('work_type'),
                    'residence_type': request.form.get('residence_type'),
                    'avg_glucose_level': float(request.form.get('avg_glucose_level')),
                    'bmi': float(request.form.get('bmi')),
                    'smoking_status': request.form.get('smoking_status'),
                    'stroke': int(request.form.get('stroke')),
                    'user_id': str(current_user.id),
                    'created_at': datetime.utcnow()
                }
                
                print("Processed patient data:", patient_data)
                
                result = mongo.db.patients.insert_one(patient_data)
                print("Data saved with ID:", result.inserted_id)
                
                flash('Patient data stored successfully!', 'success')
                return redirect(url_for('dashboard'))

            except Exception as e:
                print(f"Error storing patient data: {str(e)}")
                flash('An error occurred while storing patient data. Please try again.', 'danger')
                return redirect(url_for('add_patient'))

        return render_template('add_patient.html')

    @app.route('/view_patients')
    @login_required
    def view_patients():
        patient_id = request.args.get('patient_id', '')
        searched = bool(patient_id)
        patient = None

        if patient_id:
            try:
                # Search for patient in MongoDB
                patient = mongo.db.patients.find_one({
                    'patient_id': patient_id,
                    'user_id': str(current_user.id)
                })
                print(f"Found patient: {patient}")
            except Exception as e:
                print(f"Error searching for patient: {str(e)}")
                flash('Error searching for patient.', 'danger')

        return render_template('view_patients.html', 
                             patient=patient, 
                             searched=searched)

    @app.route('/edit_patient/<patient_id>', methods=['GET', 'POST'])
    @login_required
    def edit_patient(patient_id):
        try:
            # Find the patient
            patient = mongo.db.patients.find_one({
                'patient_id': patient_id,
                'user_id': str(current_user.id)
            })
            
            if not patient:
                flash('Patient not found.', 'danger')
                return redirect(url_for('view_patients'))

            if request.method == 'POST':
                try:
                    # Prepare updated data
                    updated_data = {
                        'name': request.form.get('name'),
                        'gender': request.form.get('gender'),
                        'age': int(request.form.get('age')),
                        'hypertension': int(request.form.get('hypertension')),
                        'ever_married': request.form.get('ever_married'),
                        'work_type': request.form.get('work_type'),
                        'residence_type': request.form.get('residence_type'),
                        'avg_glucose_level': float(request.form.get('avg_glucose_level')),
                        'bmi': float(request.form.get('bmi')),
                        'smoking_status': request.form.get('smoking_status'),
                        'stroke': int(request.form.get('stroke'))
                    }

                    print(f"Updating patient {patient_id} with data:", updated_data)

                    # Update in MongoDB
                    result = mongo.db.patients.update_one(
                        {'patient_id': patient_id, 'user_id': str(current_user.id)},
                        {'$set': updated_data}
                    )

                    if result.modified_count > 0:
                        flash('Patient data updated successfully!', 'success')
                    else:
                        flash('No changes made to patient data.', 'info')

                    return redirect(url_for('view_patients', patient_id=patient_id))

                except ValueError as ve:
                    flash(f'Invalid input: Please check numeric fields.', 'danger')
                    return render_template('edit_patient.html', patient=patient)
                except Exception as e:
                    print(f"Error updating patient: {str(e)}")
                    flash('Error updating patient data.', 'danger')
                    return render_template('edit_patient.html', patient=patient)

            return render_template('edit_patient.html', patient=patient)

        except Exception as e:
            print(f"Error in edit_patient route: {str(e)}")
            flash('Error accessing patient data.', 'danger')
            return redirect(url_for('view_patients'))

    @app.route('/delete_patient/<patient_id>')
    @login_required
    def delete_patient(patient_id):
        try:
            result = mongo.db.patients.delete_one({
                'patient_id': patient_id,
                'user_id': str(current_user.id)
            })
            
            if result.deleted_count:
                flash('Patient record deleted successfully.', 'success')
            else:
                flash('Patient not found.', 'danger')
        except Exception as e:
            flash('Error deleting patient record.', 'danger')
        
        return redirect(url_for('view_patients'))

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('home'))

    return app