from flask import Flask, render_template, flash
from flask import request, session, redirect
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import urllib3
import json
import datetime
import time
import requests
from flask import request, jsonify
import re
import math
import datetime
import random
import os






'''opening config file to access parameters'''
with open("config.json") as conf:
    params = json.load(conf)['params']


app = Flask(__name__)

# session kye for flash messages
app.secret_key = 'Session_key'  # secret key for session security


# For using zip in for in jinja2
app.jinja_env.filters['zip'] = zip

# Configuring database
app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
db = SQLAlchemy(app)



#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@host/database_name'





# Define relationships with other tables
class Forts(db.Model):
    fort_id = db.Column(db.Integer, primary_key=True)
    fort_name = db.Column(db.String(255))
    fort_district = db.Column(db.String(255))
    fort_latitude = db.Column(db.DOUBLE)
    fort_longitude = db.Column(db.DOUBLE)
    detail = db.Column(db.TEXT)

    def __repr__(self) -> str:
        return f"({self.fort_id},{self.fort_name},{self.fort_district},{self.fort_latitude},{self.fort_longitude},{self.detail})"


# Defining origin and destination table
class latitude_longitude(db.Model):
  plan_id = db.Column(db.Integer, primary_key=True)
  origin_latitude = db.Column(db.DECIMAL(11,8))
  origin_longitude = db.Column(db.DECIMAL(11,8))
  destination_latitude = db.Column(db.DECIMAL(11,8))
  destination_longitude = db.Column(db.DECIMAL(11,8))

  def __repr__(self) -> str:
      return f"({self.plan_id},{self.origin_latitude},{self.origin_longitude},{self.destination_latitude},{self.destination_longitude})"




class user_location(db.Model):
  u_id = db.Column(db.Integer, primary_key=True)
  user_latitude = db.Column(db.DECIMAL(11,8))
  user_longitude = db.Column(db.DECIMAL(11,8))

  def __repr__(self) -> str:
      return f"({self.u_id},{self.user_latitude},{self.user_longitude})"



class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(255))
    destination = db.Column(db.String(255))
    mode = db.Column(db.String(50))
    traffic_model = db.Column(db.String(50))
    departure_time = db.Column(db.String(50))

    def __repr__(self) -> str:
        return f"({self.id},{self.origin},{self.destination},{self.mode},{self.traffic_model},{self.departure_time})"


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_time = db.Column(db.DateTime)
    origin = db.Column(db.String(255))
    destination = db.Column(db.String(255))
    origin_addresses = db.Column(db.String(500))
    destination_addresses = db.Column(db.String(500))
    mode = db.Column(db.String(50))
    traffic_model = db.Column(db.String(50))
    departure_time = db.Column(db.String(50))
    distance_value = db.Column(db.Integer)
    distance_text = db.Column(db.String(50))
    duration_value = db.Column(db.Integer)
    duration_text = db.Column(db.String(50))
    duration_in_traffic_value = db.Column(db.Integer)
    duration_in_traffic_text = db.Column(db.String(50))

    def __repr__(self) -> str:
        return f"({self.id},{self.request_time},{self.origin},{self.destination},{self.origin_addresses},{self.destination_addresses},{self.mode},{self.traffic_model},{self.departure_time},{self.distance_value},{self.distance_text},{self.duration_value},{self.duration_text},{self.duration_in_traffic_value},{self.duration_in_traffic_text})"


class all_trips(db.Model):
    trip_id = db.Column(db.Integer, primary_key=True)
    trip_district = db.Column(db.String(255))
    forts_visited = db.Column(db.TEXT)
    required_time = db.Column(db.String(255))
    minimum_cost = db.Column(db.FLOAT)
    date = db.Column(db.Date)

    def __repr__(self) -> str:
        return f"({self.trip_id},{self.trip_district},{self.forts_visited},{self.required_time},{self.minimum_cost}, {self.date})"




class all_recommendations(db.Model):
    recommendation_id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer)
    trip_district = db.Column(db.String(255))
    forts_visited = db.Column(db.TEXT)
    required_time = db.Column(db.String(55))
    minimum_cost = db.Column(db.String(255))
    trip_title = db.Column(db.TEXT)
    trip_details = db.Column(db.TEXT)
    image_name = db.Column(db.TEXT)

    def __repr__(self) -> str:
        return f"({self.recommendation_id},{self.trip_id},{self.trip_district},{self.forts_visited},{self.required_time},{self.minimum_cost},{self.trip_title},{self.trip_details},{self.image_name})"



class user_feedback(db.Model):
    feedback_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.TEXT)
    email = db.Column(db.TEXT)
    subject = db.Column(db.TEXT)
    message = db.Column(db.TEXT)
    status = db.Column(db.TEXT)
    date = db.Column(db.Date)

    def __repr__(self) -> str:
        return f"({self.feedback_id},{self.name},{self.email},{self.subject},{self.message},{self.status},{self.date})"





@app.route("/admin", methods=['GET', 'POST'])     # main admin page
def admin():
    if 'user' in session and session['user'] == "admin":
        return redirect("/all_trips")

    if request.method == "POST":
        username = request.form['floatingInput']
        password = request.form['floatingPassword']

        if username == "admin" and password == "admin":
            session['user'] = username
            print(username, password)
            return redirect("/all_trips")
        else:
            flash('Invalid Username or Password')
            return render_template("admin/login.html", params=params)

    return render_template("admin/login.html", params=params)


@app.route("/logout")
def logout():
    session.pop('user', None)
    # return redirect(url_for('admin'))
    return redirect("/admin")




@app.route("/fort_management", methods=['GET', 'POST'])           # admin Fort management page
def adminfortmanagement():
    active2 = "active"
    if 'user' in session and session['user'] == "admin":
        return render_template("admin/fort_management.html", params=params, active2=active2)

    return redirect("/admin")



@app.route('/search', methods=['GET', 'POST'])
def search():
    active2 = "active"
    if request.method == 'POST':
        search_term = request.form['query']
        forts = Forts.query.filter(Forts.fort_name.like(f'%{search_term}%')).all()
        return render_template('admin/fort_management.html', forts=forts, params=params, active2=active2)
    else:
        return render_template('admin/fort_management.html', params=params, active2=active2)


@app.route('/fort_add', methods=['GET', 'POST'])
def fortadd():
    active2 = "active"
    if request.method == 'POST':
        f_id = request.form['fort_id']
        f_name = request.form['fort_name']
        f_district = request.form['fort_district']
        f_latitude = request.form['latitude']
        f_longitude = request.form['longitude']
        f_details = request.form['fort_details']

        # print(f_id)
        # print(f_name)

        if not f_latitude:
            f_latitude = 0
            f_longitude = 0
            print("not got")


        # Check if fort already exists
        forts = Forts.query.filter_by(fort_id=f_id).first()
        # db.session.commit()
        if forts:
            # flash('Fort data already exists !!!', 'error')
            flash('Fort data already exists !!  You should check if you are adding new fort data.')

        else:
            # Proceed with adding the Fort
            if f_name:
                new_fort = Forts(fort_name=f_name, fort_district=f_district, fort_latitude=f_latitude, fort_longitude=f_longitude, detail=f_details)
                db.session.add(new_fort)
                db.session.commit()
                # flash('Fort data added successfully', 'success')
                flash('Fort data added successfully')

            else:
                flash('Please Fill The Required Fields For Adding New Fort Data!!')

        return render_template('admin/fort_management.html', params=params, active2=active2)


@app.route('/fort_update', methods=['GET', 'POST'])
def fortupdate():
    active2 = "active"
    if request.method == 'POST':
        f_id = request.form['fort_id']
        f_name = request.form['fort_name']
        f_district = request.form['fort_district']
        f_latitude = request.form['latitude']
        f_longitude = request.form['longitude']
        f_details = request.form['fort_details']

        # if lat and long is none
        print(f_latitude)
        if f_latitude == "None" and f_longitude == "None":
            f_latitude = 0
            f_longitude = 0

        # Check if fort exists
        forts = Forts.query.filter_by(fort_id=f_id).first()
        # db.session.commit()
        if forts:
            # Proceed with updating the Fort
            forts.fort_name = f_name
            forts.fort_district = f_district
            forts.fort_latitude = f_latitude
            forts.fort_longitude = f_longitude
            forts.detail = f_details
            db.session.commit()
            flash('Fort data updated successfully')


        else:
            flash('Please Fill The Required Fields For Updating Fort Data!!')

        return render_template('admin/fort_management.html', params=params, active2=active2)


@app.route('/fort_delete', methods=['GET', 'POST'])
def fortdelete():
    active2 = "active"
    if request.method == 'POST':
        f_id = request.form['fort_id']

        forts = Forts.query.filter_by(fort_id=f_id).first()
        if forts:
            db.session.delete(forts)
            db.session.commit()
            flash('Fort data deleted successfully')

        else:
            flash('Please Check If You Have Selected Correct Row For Deleting Fort Data!!')

        return render_template('admin/fort_management.html', params=params, active2=active2)







@app.route("/all_trips", methods=['GET', 'POST'])               # admin all trips page
def adminalltrips():
    active3 = "active"
    planned_trips = all_trips.query.order_by(all_trips.date.desc()).all()
    db.session.commit()

    # Get the count of rows in the table
    row_count = all_trips.query.count()
    db.session.commit()
    # print(row_count)

    # Initialize lists to store unique values
    districts = []
    forts = []

    # Fetch records from the database
    records = all_trips.query.all()

    # Iterate through the records
    for record in records:
        # Check if the district is not already in the list
        if record.trip_district not in districts:
            districts.append(record.trip_district)
        # Check if the forts are not already in the list
        for fort in record.forts_visited.split(','):  # Assuming forts are comma-separated
            if fort.strip() not in forts:
                forts.append(fort.strip())

    # Print the unique values
    print("Districts:", districts)
    print("Forts:", forts)
    d_count = len(districts)
    f_count = len(forts)

    if 'user' in session and session['user'] == "admin":
        return render_template("admin/all_trips.html", params=params, active3=active3, planned_trips=planned_trips,
                               row_count=row_count, d_count=d_count, f_count=f_count)

    return redirect("/admin")

    # return render_template("admin/all_trips.html", params=params, active3=active3, planned_trips=planned_trips, row_count=row_count, d_count=d_count, f_count=f_count)





@app.route("/recommendation", methods=['GET', 'POST'])               # admin recommendation page
def adminrecommendation():
    active4 = "active"

    # for showing default table and count #
    planned_trips = all_trips.query.order_by(all_trips.date.desc()).all()
    db.session.commit()
    # print(f"lenghth of planned trips {len(planned_trips)}")
    r_count = len(planned_trips)

    #---------for showing options of districts -------------#
    districts = []

    records = all_trips.query.all()
    # Iterate through the records
    for record in records:
        # Check if the district is not already in the list
        if record.trip_district not in districts:
            districts.append(record.trip_district)
    db.session.commit()


    if 'user' in session and session['user'] == "admin":
        return render_template("admin/recommendation.html", params=params, active4=active4, planned_trips=planned_trips,
                               districts=districts, r_count=r_count)
    return redirect("/admin")

    # return render_template("admin/recommendation.html", params=params, active4=active4, planned_trips=planned_trips, districts=districts, r_count=r_count)





@app.route('/recommendationsearch', methods=['GET', 'POST'])
def recommendationsearch():
    active4 = "active"

    # ---------for showing options of districts -------------#
    districts = []

    records = all_trips.query.all()
    # Iterate through the records
    for record in records:
        # Check if the district is not already in the list
        if record.trip_district not in districts:
            districts.append(record.trip_district)
    db.session.commit()
    #--------------end-------------------------#

    if request.method == 'POST':
        search_term = request.form['query']
        sel_district = request.form['district']
        # print(search_term)
    #----------------For Filtering Search input for fort names---------------------------------------------------------#
        if search_term:
            r_s_forts = all_trips.query.filter(all_trips.forts_visited.like(f'%{search_term}%')).all()
            # db.session.commit()
            r_count = len(r_s_forts)
            if r_s_forts:
                return render_template('admin/recommendation.html', r_s_forts=r_s_forts, params=params, active4=active4,
                                       r_count=r_count, districts=districts)
            else:
                nodata = "nodata"
                return render_template('admin/recommendation.html', params=params, active4=active4, nodata=nodata, districts=districts)

    #----------------For Most viewed Button result------------------------------------------------------------------#
        elif sel_district:
            print(sel_district)
            fort_names = []
            fil = all_trips.query.filter_by(trip_district=sel_district).all()
            for fn in fil:
                fort_names.append(fn.forts_visited)
            db.session.commit()
            print(fort_names)

            #=============Most viewed recommendation logic ==========================================#
            from collections import Counter

            # Given list of strings
            # fort_names = ['Ghosale gad,Mangad Fort', 'Dronagiri Fort,Sudhagad,Lingana', 'Sarasgad,Lingana',
            #            'Sarasgad,Mangad Fort', 'Sarasgad,Sudhagad', 'Surgad,Sarasgad,Sudhagad',
            #            'Your Location,Sarasgad', 'Sarasgad,Sudhagad', 'Irshalgad,Sarasgad,Lingana',
            #            'Sarasgad,Sudhagad,Mangad Fort', 'Irshalgad,Sarasgad,Lingana']

            # Count the frequency of each fort mentioned in the strings
            fort_counts = Counter()
            for string in fort_names:
                forts = string.split(',')
                fort_counts.update(forts)

            # Sort the forts based on their frequency in descending order
            sorted_forts = sorted(fort_counts.items(), key=lambda x: x[1], reverse=True)

            # Calculate score for each string based on frequency of mentioned forts
            string_scores = []
            for string in fort_names:
                forts = string.split(',')
                score = sum(fort_counts[fort] for fort in forts)
                string_scores.append((string, score))

            # Sort the strings based on their score in descending order
            recommended_strings = [string for string, _ in sorted(string_scores, key=lambda x: x[1], reverse=True)]

            # adding in list without repeated values to access
            recommended_list = []

            # Print recommended strings
            for string in recommended_strings:
                if string not in recommended_list:
                    recommended_list.append(string)
                # print(string)

            most_v_recommendation = []
            # Getting table data from string
            for i in recommended_list:
                v_data = all_trips.query.filter_by(forts_visited=i).first()
                most_v_recommendation.append(v_data)
                db.session.commit()
                # print(i)

            #=================Logic end==================================================#

            # for counting rows
            r_count = len(fil)

            return render_template('admin/recommendation.html', params=params, active4=active4, r_count=r_count, most_v_recommendation=most_v_recommendation, districts=districts)




@app.route('/addonly', methods=['GET', 'POST'])
def recommaddonly():
    active4 = "active"

    #---------for showing default table and count-------#
    planned_trips = all_trips.query.order_by(all_trips.date.desc()).all()
    db.session.commit()
    # print(f"lenghth of planned trips {len(planned_trips)}")
    r_count = len(planned_trips)

    # ---------for showing options of districts -------------#
    districts = []

    records = all_trips.query.all()
    # Iterate through the records
    for record in records:
        # Check if the district is not already in the list
        if record.trip_district not in districts:
            districts.append(record.trip_district)
    db.session.commit()
    #--------------end--------------------------------#

    if request.method == 'POST':
        trip_id = request.form['trip_id']
        d_name = request.form['trip_district']
        f_names = request.form['forts_visited']
        req_time = request.form['required_time']
        m_cost = request.form['minimum_cost']
        t_title = request.form['trip_title']
        t_details = request.form['trip_details']

        upd_img = request.files['pic']


        print(trip_id)
        print(f_names)
        if d_name == "" or f_names == "":
            flash('Please select correct data from table!!')
            return render_template('admin/recommendation.html', params=params, active4=active4,
                                   planned_trips=planned_trips, districts=districts, r_count=r_count)

        if not trip_id:
            flash('Trip ID missing!! Go to your recommendations for custom recommendations!!')
            return render_template('admin/recommendation.html', params=params, active4=active4,
                                   planned_trips=planned_trips, districts=districts, r_count=r_count)

        get_table = all_recommendations.query.filter_by(trip_id=trip_id).first()
        db.session.commit()

        if get_table:
            flash('Trip is already present in recommendations!!')
            return render_template('admin/recommendation.html', params=params, active4=active4, planned_trips=planned_trips, districts=districts, r_count=r_count)

        else:
            # storing image in image folder
            if upd_img:
                # Path to the folder where you want to save the image
                folder_path = 'static/img/'
                # check if present
                file_path = os.path.join(folder_path, upd_img.filename)
                if not os.path.exists(file_path):
                    upd_img.save(file_path)
                    print("Image saved to folder")
                else:
                    print("Image File already exists in folder")
                    my_recommendations = all_recommendations.query.all()
                    db.session.commit()
                    r_count = len(my_recommendations)
                    flash('Image with same name exist!! Please change the Image name')

                    return render_template('admin/recommendation.html', params=params, active4=active4,
                                           my_recommendations=my_recommendations, districts=districts, r_count=r_count)


            fill = all_recommendations(trip_id=trip_id, trip_district=d_name, forts_visited=f_names,
                                       required_time=req_time, minimum_cost=m_cost, trip_title=t_title,
                                       trip_details=t_details, image_name=upd_img.filename)
            db.session.add(fill)
            db.session.commit()
            flash('Trip Added To Recommendations Successfully.... ')

            return render_template('admin/recommendation.html', params=params, active4=active4, planned_trips=planned_trips, districts=districts, r_count=r_count)


        # return f"({self.recommendations_id},{self.trip_id},{self.trip_district},{self.forts_visited},{self.required_time},{self.minimum_cost},{self.trip_title},{self.trip_details})"





@app.route("/myrecommendation", methods=['GET', 'POST'])
def myrecommendation():
    active4 = "active"

    # ---------for showing options of districts -------------#
    districts = []

    records = all_trips.query.all()
    # Iterate through the records
    for record in records:
        # Check if the district is not already in the list
        if record.trip_district not in districts:
            districts.append(record.trip_district)
    db.session.commit()
    # --------------end--------------------------------#


    my_recommendations = all_recommendations.query.all()
    db.session.commit()
    r_count = len(my_recommendations)


    return render_template('admin/recommendation.html', params=params, active4=active4, districts=districts, r_count=r_count, my_recommendations=my_recommendations)




@app.route('/recommadd', methods=['GET', 'POST'])
def recommadd():
    active4 = "active"

    # ---------for showing options of districts -------------#
    districts = []

    records = all_trips.query.all()
    # Iterate through the records
    for record in records:
        # Check if the district is not already in the list
        if record.trip_district not in districts:
            districts.append(record.trip_district)
    db.session.commit()
    #--------------end--------------------------------#

    if request.method == 'POST':
        recommendation_id = request.form['recommendation_id']
        trip_id = request.form['trip_id']
        d_name = request.form['trip_district']
        f_names = request.form['forts_visited']
        req_time = request.form['required_time']
        m_cost = request.form['minimum_cost']
        t_title = request.form['trip_title']
        t_details = request.form['trip_details']
        upd_img = request.files['pic']


        if d_name == "" or f_names == "":
            flash('Please select correct data from table!! \n or \n Fill the all required fields')
            my_recommendations = all_recommendations.query.all()
            db.session.commit()
            r_count = len(my_recommendations)
            return render_template('admin/recommendation.html', params=params, active4=active4, my_recommendations=my_recommendations, districts=districts, r_count=r_count)


        get_table = all_recommendations.query.filter_by(recommendation_id=recommendation_id).first()
        db.session.commit()


        if get_table:
            flash('Trip is already present in recommendations!!')

            my_recommendations = all_recommendations.query.all()
            db.session.commit()
            r_count = len(my_recommendations)
            return render_template('admin/recommendation.html', params=params, active4=active4, my_recommendations=my_recommendations, districts=districts, r_count=r_count)

        else:
            random_number = random.randint(2000, 4000)
            print(random_number)
            t_id_check = []
            chk = all_recommendations.query.all()
            for cid in chk:
                t_id_check.append(cid.trip_id)
            db.session.commit()


            if random_number in t_id_check:
                random_number = random.randint(4000, 5000)
                print(random_number)

                #Checking if fort is present
                # f_names = "raigad,manikgad fort, laubai"
                # Split the string into a list of fort names
                fort_names_list = f_names.split(',')
                # Iterate through the list and strip whitespace from each name
                fort_names_cleaned = [name.strip() for name in fort_names_list]
                print(fort_names_cleaned)
                for i in fort_names_cleaned:
                    print("got list")
                    check_fort = Forts.query.filter_by(fort_name=i).first()
                    if not check_fort:
                        db.session.commit()
                        flash('Please fill the appropriate forts names and check if they are present in the forts table')

                        my_recommendations = all_recommendations.query.all()
                        db.session.commit()
                        r_count = len(my_recommendations)

                        return render_template('admin/recommendation.html', params=params, active4=active4,
                                               my_recommendations=my_recommendations, districts=districts,
                                               r_count=r_count)

                # storing image in image folder
                if upd_img:
                    # Path to the folder where you want to save the image
                    folder_path = 'static/img/'
                    # check if present
                    file_path = os.path.join(folder_path, upd_img.filename)
                    if not os.path.exists(file_path):
                        upd_img.save(file_path)
                        print("Image saved to folder")
                    else:
                        print("Image File already exists in folder")
                        my_recommendations = all_recommendations.query.all()
                        db.session.commit()
                        r_count = len(my_recommendations)
                        flash('Image with same name exist!! Please change the Image name')

                        return render_template('admin/recommendation.html', params=params, active4=active4,
                                               my_recommendations=my_recommendations, districts=districts,
                                               r_count=r_count)


                # upload to data base
                fill = all_recommendations(trip_id=random_number, trip_district=d_name, forts_visited=f_names,
                                           required_time=req_time, minimum_cost=m_cost, trip_title=t_title,
                                           trip_details=t_details, image_name=upd_img.filename)
                db.session.add(fill)
                db.session.commit()
                flash('Trip Added To Recommendations Successfully.... ')


                my_recommendations = all_recommendations.query.all()
                db.session.commit()
                r_count = len(my_recommendations)

                return render_template('admin/recommendation.html', params=params, active4=active4,
                                       my_recommendations=my_recommendations, districts=districts, r_count=r_count)

            else:
                # Checking if fort is present
                # f_names = "raigad,manikgad fort, laubai"
                # Split the string into a list of fort names
                fort_names_list = f_names.split(',')
                # Iterate through the list and strip whitespace from each name
                fort_names_cleaned = [name.strip() for name in fort_names_list]
                print(fort_names_cleaned)
                for i in fort_names_cleaned:
                    print("got list")
                    check_fort = Forts.query.filter_by(fort_name=i).first()
                    if not check_fort:
                        db.session.commit()
                        flash(
                            'Please fill the appropriate forts names and check if they are present in the forts table')

                        my_recommendations = all_recommendations.query.all()
                        db.session.commit()
                        r_count = len(my_recommendations)

                        return render_template('admin/recommendation.html', params=params, active4=active4,
                                               my_recommendations=my_recommendations, districts=districts,
                                               r_count=r_count)

                fill = all_recommendations(trip_id=random_number, trip_district=d_name, forts_visited=f_names,
                                           required_time=req_time, minimum_cost=m_cost, trip_title=t_title,
                                           trip_details=t_details, image_name=upd_img.filename)
                db.session.add(fill)
                db.session.commit()
                flash('Trip Added To Recommendations Successfully.... ')

                # adding image to img folder
                if upd_img:
                    upd_img.save(f'static/img/{upd_img.filename}')
                    print("image created to folder")

                my_recommendations = all_recommendations.query.all()
                db.session.commit()
                r_count = len(my_recommendations)

                return render_template('admin/recommendation.html', params=params, active4=active4,
                                       my_recommendations=my_recommendations, districts=districts, r_count=r_count)








@app.route('/recommupdate', methods=['GET', 'POST'])
def recommupdate():
    active4 = "active"

    # ---------for showing options of districts -------------#
    districts = []

    records = all_trips.query.all()
    # Iterate through the records
    for record in records:
        # Check if the district is not already in the list
        if record.trip_district not in districts:
            districts.append(record.trip_district)
    db.session.commit()
    #--------------end--------------------------------#

    if request.method == 'POST':
        recommendation_id = request.form['recommendation_id']
        trip_id = request.form['trip_id']
        d_name = request.form['trip_district']
        f_names = request.form['forts_visited']
        req_time = request.form['required_time']
        m_cost = request.form['minimum_cost']
        t_title = request.form['trip_title']
        t_details = request.form['trip_details']

        upd_img = request.files['pic']

            # upd_img.save(f'static/img/{upd_img.filename}')
            # print("image created to folder")


        get_table = all_recommendations.query.filter_by(recommendation_id=recommendation_id).first()
        if get_table:
            get_table.trip_district = d_name
            get_table.forts_visited = f_names
            get_table.required_time = req_time
            get_table.minimum_cost = m_cost
            get_table.trip_title = t_title
            get_table.trip_details = t_details
            # storing image in image folder
            if upd_img:
                # Path to the folder where you want to save the image
                folder_path = 'static/img/'

                # Full path to the image file to delete it
                db_image = get_table.image_name
                if db_image:
                    file_path1 = os.path.join(folder_path, db_image)
                    if os.path.exists(file_path1):
                        # If the file exists, delete it
                        os.remove(file_path1)

                # check if present  and add or not add new image
                file_path = os.path.join(folder_path, upd_img.filename)
                if not os.path.exists(file_path):
                    upd_img.save(file_path)
                    print("Image saved to folder")

                    get_table.image_name = upd_img.filename

                else:
                    db.session.commit()
                    print("Image File already exists in folder")
                    my_recommendations = all_recommendations.query.all()
                    db.session.commit()
                    r_count = len(my_recommendations)
                    flash('Trip Recommendations Updated Successfully without Image.... ')
                    flash('Image with same name exist!! Please change the Image name and upload again')

                    return render_template('admin/recommendation.html', params=params, active4=active4,
                                           my_recommendations=my_recommendations, districts=districts, r_count=r_count)

        db.session.commit()

        my_recommendations = all_recommendations.query.all()
        db.session.commit()
        r_count = len(my_recommendations)
        flash('Trip Recommendations Updated Successfully.... ')

        return render_template('admin/recommendation.html', params=params, active4=active4, my_recommendations=my_recommendations, districts=districts, r_count=r_count)



@app.route('/recommdelete', methods=['GET', 'POST'])
def recommdelete():
    active4 = "active"

    # ---------for showing options of districts -------------#
    districts = []

    records = all_trips.query.all()
    # Iterate through the records
    for record in records:
        # Check if the district is not already in the list
        if record.trip_district not in districts:
            districts.append(record.trip_district)
    db.session.commit()
    #------------------end------------------------------#


    if request.method == 'POST':
        recommendation_id = request.form['recommendation_id']

        get_table = all_recommendations.query.filter_by(recommendation_id=recommendation_id).first()
        if get_table:

            # Path to the folder where you want to save the image
            folder_path = 'static/img/'

            # Full path to the image file to delete it
            db_image = get_table.image_name
            if db_image:
                file_path1 = os.path.join(folder_path, db_image)
                if os.path.exists(file_path1):
                    # If the file exists, delete it
                    os.remove(file_path1)

            db.session.delete(get_table)
            db.session.commit()
            flash('Recommendation data deleted successfully')

        else:
            flash('Please Check If You Have Selected Correct Row For Deleting Recommendation Data!!')

        #----------Default-----------------------#
        my_recommendations = all_recommendations.query.all()
        db.session.commit()
        r_count = len(my_recommendations)

        return render_template('admin/recommendation.html', params=params, active4=active4, my_recommendations=my_recommendations, districts=districts, r_count=r_count)







@app.route("/adminfeedback", methods=['GET', 'POST'])
def adminfeedback():
    active5 = "active"

    all_feedbacks = user_feedback.query.order_by(user_feedback.date.desc()).all()
    db.session.commit()

    if request.method == "POST":
        pass

    # user_feedback
    # return f"({self.feedback_id},{self.name},{self.email},{self.subject},{self.message},{self.status})"

    return render_template('admin/feedback.html', params=params, active5=active5, all_feedbacks=all_feedbacks)




@app.route("/feedbackdelete", methods=['GET', 'POST'])
def feedbackdelete():
    active5 = "active"

    all_feedbacks = user_feedback.query.order_by(user_feedback.date.desc()).all()
    db.session.commit()

    if request.method == "POST":
        f_id = request.form['feedback_id']
        if f_id:
            del_feedback = user_feedback.query.filter_by(feedback_id=f_id).first()
            db.session.delete(del_feedback)
            db.session.commit()
            flash('Feedback Deleted !')

            all_feedbacks = user_feedback.query.order_by(user_feedback.date.desc()).all()
            db.session.commit()

            return render_template('admin/feedback.html', params=params, active5=active5, all_feedbacks=all_feedbacks)

    # user_feedback
    # return f"({self.feedback_id},{self.name},{self.email},{self.subject},{self.message},{self.status})"

    return render_template('admin/feedback.html', params=params, active5=active5, all_feedbacks=all_feedbacks)






@app.route("/", methods=['GET', 'POST'])
def home():
    active1 = "active"
    display = "none"
    found = "none"


    if request.method == "POST":
        print(request.method)

        # Get user district name from the submited form
        user_district = request.form['user_district']
        print(user_district)

        # Get district_name from database
        fortsname = Forts.query.filter_by(fort_district=user_district).all()
        if fortsname:
            # declaring district name for later use
            global district_name
            district_name = user_district

            # variable for showing container or simple text
            found = "found"
            display = "block"

            # Rendering Template if district name is found
            return render_template("index.html", params=params, display=display, active1=active1, fortsname=fortsname,
                                   found=found, user_district=user_district)

        else:
            # if wrong district name is entered !!!
            print("District not found !!!")
            found = "nodata"
            return render_template("index.html", params=params, display=display, active1=active1, found=found)


    # This will load the index file at start , when no entry is entered
    return render_template("index.html", params=params, display=display, active1=active1, found=found)





@app.route("/send-coordinates", methods=["POST"])
def send_coordinates():

    usr_latitude = request.form.get("latitude")
    usr_longitude = request.form.get("longitude")
    print(usr_latitude)
    print(usr_longitude)

    # deleting database data if already existed
    db.session.query(latitude_longitude).delete()
    db.session.commit()
    print("deleted table vales ")

    # Inserting user location to database
    user_lat_long = latitude_longitude(origin_latitude=usr_latitude, origin_longitude=usr_longitude)
    db.session.add(user_lat_long)
    db.session.commit()

    # Deleting user locations table
    db.session.query(user_location).delete()
    db.session.commit()

    new_user_lat_long = user_location(user_latitude=usr_latitude, user_longitude=usr_longitude)
    db.session.add(new_user_lat_long)
    db.session.commit()

    # deleting route table data
    db.session.query(Route).delete()
    db.session.commit()
    print("deleted route table vales ")

    # deleting result table data
    db.session.query(Result).delete()
    db.session.commit()
    print("deleted result table vales ")


    return "Coordinates saved successfully!"



@app.route("/generateplan", methods=['GET', 'POST'])
def generateplan():

    triggerplan = "none"
    active1 = "active"
    found = "none"
    ltlg = "none"
    fort_sel = "none"

    if request.method == "POST":

        milage = request.form['milage']
        p_liter = request.form['p_liter']

        loading_animation = "ON"
        print(f"Method {request.method} of generate plan")
        print(f"Got user district {district_name}")            # Getting access of user district
        print(request.form.getlist('selected_checkbox'))

        selected_forts = request.form.getlist('selected_checkbox')
        print("This is selected forts", selected_forts)
        if not selected_forts:
            fort_sel = "none"
            print("fort none")

            abcd = user_location.query.first()
            print(abcd)
            db.session.commit()
            db.session.query(user_location).delete()
            db.session.commit()


            if not abcd:
                print("no lt-lg")
                ltlg = "nolocation"

            return render_template("index.html", params=params, active1=active1, ltlg=ltlg, fort_sel=fort_sel, loading_animation=loading_animation)


        else:
            fort_sel = "selected"

            # added another table containing user_location ()

            user_lat_long = user_location.query.first()
            db.session.commit()

            if user_lat_long is not None:
                user_lat = user_lat_long.user_latitude
                user_long = user_lat_long.user_longitude
                db.session.commit()

                # deleting user loaction table
                db.session.query(user_location).delete()
                db.session.commit()
                print("deleted  user location table vales in user location table ")
                print(f"User location : user_lt: {user_lat} user_lg: {user_long}")


                # -----------------------------------------------------------------------------------------------------------------------
                # Adding function for getting best path to visit various destinations
                path_id_name = []
                plan_sorted_locatons = []

                def optimal_path():
                    URL = "https://api.routific.com/v1/vrp"

                    visits = {}
                    fleet = {}

                    temp_fleet = {
                        "vehicle_1": {
                            "start_location": {
                                "id": "depot",
                                "name": "Your Location",
                                "lat": user_lat,
                                "lng": user_long
                            }
                        }
                    }

                    fleet.update(temp_fleet)

                    for i in selected_forts:
                        # print(i)
                        user_sel_fort = Forts.query.filter_by(fort_id=i).first()
                        db.session.commit()

                        user_sel_fort_lat = user_sel_fort.fort_latitude
                        user_sel_fort_long = user_sel_fort.fort_longitude
                        user_sel_fort_id = user_sel_fort.fort_id
                        user_sel_fort_name = user_sel_fort.fort_name
                        db.session.commit()

                        # converting key string
                        id = str(user_sel_fort_id)

                        temp_visits = {
                            id: {
                                "location": {
                                    "name": user_sel_fort_name,
                                    "lat": user_sel_fort_lat,
                                    "lng": user_sel_fort_long
                                }
                            }
                        }

                        visits.update(temp_visits)

                    # Prepare data payload
                    data = {
                        "visits": visits,
                        "fleet": fleet
                    }

                    # Put together request
                    # This is your demo token
                    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NjNiY2RmODQ3N2JmMTAwMWI2OTIyNGIiLCJpYXQiOjE3MTUxOTU0MTh9.S7HkQ8z3_jNAf8El2m1cwSLDNwbd2AGrzZ0IKV-dkZU'

                    http = urllib3.PoolManager()
                    req = http.request('POST', URL, body=json.dumps(data),
                                       headers={'Content-Type': 'application/json', 'Authorization': "bearer " + token})

                    # Get route
                    res = json.loads(req.data.decode('utf-8'))


                    # Extracting location_id and location_name pairs
                    locations = {}
                    for vehicle, visits in res['solution'].items():
                        for visit in visits:
                            locations[visit['location_id']] = visit['location_name']

                    # Printing location_id and location_name pairs
                    for location_id, location_name in locations.items():
                        path_id_name.append((location_id, location_name))
                        plan_sorted_locatons.append(location_name)
                        print(f"Location ID: {location_id}, Location Name: {location_name}")

                # calling Function for path finding
                optimal_path()

                # ---------------------------------------------------------------------------
                # adding values to database
                global count
                global old_value
                count = 0
                old_value = ""

                for new_id, name in path_id_name:
                    if new_id == "depot":
                        # print(new_id)
                        print("got user location ")
                    else:
                        # print(new_id)
                        print("got plan functionality")
                        user_sel_fort1 = Forts.query.filter_by(fort_id=new_id).first()
                        user_sel_fort_lat1 = user_sel_fort1.fort_latitude
                        user_sel_fort_long1 = user_sel_fort1.fort_longitude
                        db.session.commit()

                        # for updating lt/lg in database for planning tour

                        user_g_lat_long1 = latitude_longitude.query.first()
                        if user_g_lat_long1 is not None and count == 0:
                            user_g_lat_long1.destination_latitude = user_sel_fort_lat1
                            user_g_lat_long1.destination_longitude = user_sel_fort_long1
                            db.session.commit()

                            new_user_lat_long1 = latitude_longitude(origin_latitude=user_sel_fort_lat1,
                                                                    origin_longitude=user_sel_fort_long1)
                            db.session.add(new_user_lat_long1)
                            db.session.commit()

                            old_value = str(user_sel_fort_lat1)
                            count = count + 1
                            print(f"Plan {count} Uploaded to database")

                        else:
                            new_plan = latitude_longitude.query.filter_by(origin_latitude=old_value).first()
                            new_plan.destination_latitude = user_sel_fort_lat1
                            new_plan.destination_longitude = user_sel_fort_long1
                            db.session.commit()

                            new_plan_lat_long = latitude_longitude(origin_latitude=user_sel_fort_lat1,
                                                                   origin_longitude=user_sel_fort_long1)
                            db.session.add(new_plan_lat_long)
                            db.session.commit()

                            old_value = str(user_sel_fort_lat1)
                            count = count + 1
                            print(f"New plan {count} Uploaded to database")

                # -----------------------------------------------------------------------------------------------------------------------
                # Using distance matrix api

                # filling values in th table to be used in function
                # filling values in the table to be used in the function
                table_fill = latitude_longitude.query.all()
                print(table_fill)

                for row in table_fill:
                    o_lt, o_lg, d_lt, d_lg = row.origin_latitude, row.origin_longitude, row.destination_latitude, row.destination_longitude
                    if d_lt is not None and d_lg is not None:
                        o_lt_lg = f"{o_lt},{o_lg}"
                        d_lt_lg = f"{d_lt},{d_lg}"

                        fill_data = Route(origin=o_lt_lg, destination=d_lt_lg, mode="driving",
                                          traffic_model="best_guess",
                                          departure_time="now")
                        db.session.add(fill_data)

                # Commit once after all the additions
                db.session.commit()

                # ------------------------------------------------------#
                # main function to calculate distance
                BASE_URL = "https://api.distancematrix.ai"

                API_KEY = "Qch6PH8V1Na2mRn2zVQy5VPPpUNNnsZPQeZEXnOvvWtqUOLVy3Xc7NjS36IbimbY"
                #h7umDGRk3n0JI4RA1Zm1fkFRFnp1sFiEUYAysjrURSuPBZpZh2Db4gMPSHLTSUdc#
                # Loading data from database
                def load_data():
                    count_rows = 0
                    data = []

                    # Query data from the Route table
                    routes = Route.query.all()

                    for route in routes:
                        origin = route.origin
                        destination = route.destination
                        mode = route.mode
                        traffic_model = route.traffic_model
                        departure_time = route.departure_time

                        data.append({
                            "origin": "%s" % origin.replace('&', ' '),
                            "destination": "%s" % destination.replace('&', ' '),
                            "mode": "%s" % mode.replace('&', ' '),
                            "traffic_model": "%s" % traffic_model.replace('&', ' '),
                            "departure_time": "%s" % departure_time.replace('&', ' ')
                        })
                        count_rows += 1

                    print(" \nTotal rows in the database = %s \n" % (count_rows))
                    return data

                # craeting a request
                def make_request(base_url, api_key, origin, destination, mode, traffic_model, departure_time):
                    url = "{base_url}/maps/api/distancematrix/json" \
                          "?key={api_key}" \
                          "&origins={origin}" \
                          "&destinations={destination}" \
                          "&mode={mode}" \
                          "&traffic_model={traffic_model}" \
                          "&departure_time={departure_time}".format(base_url=base_url,
                                                                    api_key=api_key,
                                                                    origin=origin,
                                                                    destination=destination,
                                                                    mode=mode,
                                                                    traffic_model=traffic_model,
                                                                    departure_time=departure_time)
                    # logging.info("URL: %s" % url)
                    result = requests.get(url)
                    return result.json()

                def main():
                    data = load_data()
                    n = 0
                    for t in data:
                        time.sleep(0)
                        request_time = datetime.datetime.now()
                        dm_res = make_request(BASE_URL, API_KEY, t['origin'], t['destination'], t['mode'],
                                              t['traffic_model'],
                                              t['departure_time'])

                        if dm_res['status'] == 'REQUEST_DENIED':
                            if dm_res['error_message'] == 'The provided API key is invalid or token limit exceeded.':
                                print(dm_res['error_message'])
                                break
                        n += 1
                        try:
                            dm_distance = dm_res['rows'][0]['elements'][0]['distance']
                            dm_duration = dm_res['rows'][0]['elements'][0]['duration']
                            dm_duration_in_traffic = dm_res['rows'][0]['elements'][0]['duration_in_traffic']
                            origin_addresses = dm_res['origin_addresses']
                            destination_addresses = dm_res['destination_addresses']

                        except Exception as exc:
                            print("%s) Please check if the address or coordinates in this line are correct" % n)
                            continue

                        result = Result(
                            request_time=request_time,
                            origin=t['origin'],
                            destination=t['destination'],
                            origin_addresses=origin_addresses,
                            destination_addresses=destination_addresses,
                            mode=t['mode'],
                            traffic_model=t['traffic_model'],
                            departure_time=t['departure_time'],
                            distance_value=dm_distance['value'],
                            distance_text=dm_distance['text'],
                            duration_value=dm_duration['value'],
                            duration_text=dm_duration['text'],
                            duration_in_traffic_value=dm_duration_in_traffic['value'],
                            duration_in_traffic_text=dm_duration_in_traffic['text']
                        )
                        db.session.add(result)
                        db.session.commit()

                # calling function
                main()


                # ----------------------------------------------------------------------------------------------------------#
                # Adding values to box container
                global info_box
                global data
                info_box = []
                l_names = []
                d_t_val = []

                # list containing  sorted loc coordinates for direction
                data = []
                # for temp total time
                total = []

                # ---- used for getting distance value separated for using it in fuel cost function ----#
                d_val = []
                # - end -#

                # filling sorted location names and there values for loopng to work
                for name in range(len(plan_sorted_locatons) - 1):
                    l_names.append((plan_sorted_locatons[name], plan_sorted_locatons[name + 1]))

                plan_box = Result.query.all()
                for dt in plan_box:
                    org = dt.origin
                    dis = dt.destination
                    dist = dt.distance_text
                    t_time = dt.duration_in_traffic_text
                    d_t_val.append((dist, t_time))
                    data.append(dis)   # look here for go to map
                    total.append(t_time)
                    d_val.append(dist)
                db.session.commit()

                print("this is data in data :", data)
                # -------------------------------------------------------------#
                # For showing Fuel required and cost for trip

                fuel_n_cost = []
                total_f_c = []
                t_f = 0
                t_c = 0

                # Define average fuel efficiency for petrol cars in India
                # milage = request.form['milage']
                # p_liter = request.form['liter']

                if milage :
                    AVERAGE_MILEAGE = int(milage)
                else:
                    AVERAGE_MILEAGE = 20  # kilometers per liter

                if p_liter:
                    price_per_liter = int(p_liter)
                else:
                    price_per_liter = 104.89  # price per liter


                for d in d_val:
                    # d = "25.7 km"
                    # Split the string to isolate the numeric part
                    numerical_value = d.split()[0]
                    distance = float(numerical_value)

                    def calculate_petrol_cost(distance, price_per_liter):
                        # Calculate required petrol in liters
                        required_petrol = distance / AVERAGE_MILEAGE

                        # Calculate total cost
                        cost = required_petrol * price_per_liter

                        return required_petrol, cost

                    # Calculate and display results
                    required_petrol, total_cost = calculate_petrol_cost(distance, price_per_liter)

                    # for getting total
                    t_f = t_f + required_petrol
                    t_c = t_c + total_cost


                    fuel = f"Required Fuel: {required_petrol:.2f} liters"
                    cost = f"Travel cost: ₹{total_cost:.2f}"
                    fuel_n_cost.append((fuel, cost))

                print(fuel_n_cost)

                # for getting total values in list
                total_f_c.append(round(t_f, 2))
                total_f_c.append(round(t_c, 2))

                print(f"This is list for total f and c : {total_f_c}")

                # appending all in one list
                for i in range(len(l_names)):
                    location_info = l_names[i]
                    distance_info = d_t_val[i]
                    fuel_and_cost = fuel_n_cost[i]
                    info_box.append((*location_info, *distance_info, *fuel_and_cost))
                print(info_box)

                #-------------------------------------------------------------------------------------------------------#
                # for getting values in all_trips table
                raw_data = []
                if len(info_box) > 1:
                    for tuple_data in info_box[1:]:
                        first_string = tuple_data[0]
                        second_string = tuple_data[1]
                        last_string = tuple_data[-1]
                        raw_data.append((first_string, second_string, last_string))
                else:
                    raw_data.append((info_box[0][1], info_box[0][-1]))
                # print(raw_data)
                # print(len(raw_data))


                #---old code--#
                # for tuple_data in info_box[1:]:
                #     first_string = tuple_data[0]
                #     second_string = tuple_data[1]
                #     last_string = tuple_data[-1]
                #     raw_data.append((first_string, second_string, last_string))
                #end#
                # print(raw_data)
                # raw_data = [('Sankshi fort', 'Manikgad (Raigad)', 'Travel cost: ₹113.28'),
                #         ('Manikgad (Raigad)', 'Sudhagad', 'Travel cost: ₹373.93'),
                #         ('Sudhagad', 'Mrugagad', 'Travel cost: ₹194.05'),
                #         ('Mrugagad', 'Padargad', 'Travel cost: ₹413.79')]

                fort_names = []
                cost = []


                if len(raw_data) == 1:
                    if len(raw_data[0]) == 3:
                        # Get first and second string of the first tuple
                        fort_names.append(raw_data[0][0])
                        fort_names.append(raw_data[0][1])

                        # Extract travel cost values and calculate total cost
                        for _, _, travel_cost in raw_data:
                            cost.append(float(travel_cost.split('₹')[-1]))

                        total_cost = sum(cost)

                    else:
                        fort_names.append(raw_data[0][0])
                        # Extract travel cost values and calculate total cost
                        for _, travel_cost in raw_data:
                            cost.append(float(travel_cost.split('₹')[-1]))

                        total_cost = sum(cost)

                else:
                    # Get first and second string of the first tuple
                    fort_names.append(raw_data[0][0])
                    fort_names.append(raw_data[0][1])

                    # Get second string of each tuple from the second tuple onwards
                    for i in range(1, len(raw_data)):
                        fort_names.append(raw_data[i][1])

                    # Extract travel cost values and calculate total cost
                    for _, _, travel_cost in raw_data:
                        cost.append(float(travel_cost.split('₹')[-1]))

                    total_cost = sum(cost)

                    # print("Forts:", fort_names)
                    # print("Travel Costs:", cost)
                    # print("Total Travel Cost:", total_cost)



                # -----------------------------------------------------------------------------------------#
                # Getting total time for showing user
                # Aceesing total list which stores all times

                print(total)
                # total = ['50 mins', '2 hour 14 mins']

                # Initialize variables to store total hours and minutes
                total_hours = 0
                total_minutes = 0

                # Iterate through each travel time
                for time_str in total:
                    # Split the string to extract hours and minutes
                    time_parts = time_str.split()

                    # Convert hours and minutes to integers
                    hours = 0
                    minutes = 0
                    if 'hour' in time_parts:
                        hours = int(time_parts[0])
                    if 'mins' in time_parts:
                        minutes = int(time_parts[time_parts.index('mins') - 1])

                    # Update total hours and minutes
                    total_hours += hours
                    total_minutes += minutes

                # Adjust total hours and minutes
                total_hours += total_minutes // 60
                total_minutes = total_minutes % 60

                # Format the total travel time
                total_travel_time = f"{total_hours} hour {total_minutes} mins"
                print("Total Travel Time:", total_travel_time)

                def calculate_estimated_days(total_travel_time, overnight_break_duration_range=(8, 13)):

                    # Extract travel time in hours
                    hours = int(total_travel_time.split()[0])

                    # Check if trip can be completed in one day (considering lower bound of overnight break range)
                    if hours <= overnight_break_duration_range[0]:
                        return 1

                    # Calculate estimated days based on lower bound of overnight break range
                    estimated_days = math.ceil(hours / overnight_break_duration_range[0])

                    return estimated_days

                estimated_days = calculate_estimated_days(total_travel_time)
                print(f"Estimated days required for the trip: {estimated_days}")
                #----------------------End-----------------------------#


                # let see we can acces all fields required for all_trips

                if estimated_days < 2:
                    req_time = f"1 day"
                else:
                    req_time = f"{estimated_days} days"

                # Converting list to string for database
                forts_visited_string = ','.join(fort_names)
                #Getting current Date
                current_date = datetime.datetime.now().date()
                # print(current_date)

                trip_data = all_trips(trip_district=district_name, forts_visited=forts_visited_string, required_time=req_time, minimum_cost=total_cost, date=current_date)
                db.session.add(trip_data)
                db.session.commit()


                #----------------- code for adding fort and district names ------------------------------------ #
                # d_v_n = []
                # f_v_n = []
                # fil = Forts.query.all()
                # # db.session.commit()
                # for rec in fil:
                #     d_v_n.append(rec.fort_district)
                #     f_v_n.append(rec.fort_name)
                # db.session.commit()
                #
                # for dd, vv in zip(d_v_n, f_v_n):
                #     v_data = visit_count(district_name=dd, fort_name=vv)
                #     db.session.add(v_data)
                #     db.session.commit()
                #--------------------------- end --------------------------------------#



                triggerplan = "trigger"
                ltlg = "none"

                return render_template("index.html", params=params, triggerplan=triggerplan, active1=active1, ltlg=ltlg, fort_sel=fort_sel, loading_animation=loading_animation, info_box=info_box, items=data, total_travel_time=total_travel_time, estimated_days=estimated_days, fuel_n_cost=fuel_n_cost, total_f_c=total_f_c)




            else:
                print("no lt-lg")
                ltlg = "nolocation"

                return render_template("index.html", params=params, active1=active1, ltlg=ltlg, fort_sel=fort_sel, loading_animation=loading_animation)






#-----------------------------------------------------------------------------------------------------------#





@app.route("/ourplans", methods=['GET', 'POST'])
def ourplans():
    active2 = "active"
    tbl_data = all_recommendations.query.all()
    db.session.commit()
    # print(tbl_data)
    # return f"({self.recommendation_id},{self.trip_id},{self.trip_district},{self.forts_visited},{self.required_time},{self.minimum_cost},{self.trip_title},{self.trip_details})"

    planned_trips = all_trips.query.order_by(all_trips.date.desc()).all()
    db.session.commit()
    # print(planned_trips)

    return render_template("ourplans.html", params=params, active2=active2, tbl_data=tbl_data, planned_trips=planned_trips)



@app.route("/recommdirection", methods=['GET', 'POST'])
def recommdirection():
    active2 = "active"

    # To show all recommendations in slider
    tbl_data = all_recommendations.query.all()
    db.session.commit()

    # Code for after clicking get directions
    recom_id = request.form['rec_id']
    print(recom_id)

    direc_data = all_recommendations.query.filter_by(recommendation_id=recom_id).first()
    db.session.commit()
    print(direc_data)

    # for checking in html page
    found = "found"

    # getting district
    global district_name
    district_name = direc_data.trip_district


    # getting fort names and id
    fort_string = direc_data.forts_visited
    fortsinfo = fort_string.split(",")
    print(fortsinfo)

    fortsname =[]

    for i in fortsinfo:
        get_data = Forts.query.filter_by(fort_name=i).first()
        fortsname.append((get_data.fort_id, get_data.fort_name))
        db.session.commit()

    # return f"({self.recommendation_id},{self.trip_id},{self.trip_district},{self.forts_visited},{self.required_time},{self.minimum_cost},{self.trip_title},{self.trip_details})"
    # return render_template("index.html", params=params, active1=active1, fortsname=fortsname,
    #                        found=found, user_district=user_district)

    return render_template("ourplans.html", params=params, active2=active2, tbl_data=tbl_data, found=found, fortsname=fortsname, direc_data=direc_data)





@app.route("/recommgenerateplan", methods=['GET', 'POST'])
def recommgenerateplan():
    triggerplan = "none"
    active2 = "active"
    found = "none"
    ltlg = "none"
    fort_sel = "none"

    if request.method == "POST":
        milage = request.form['milage']
        p_liter = request.form['p_liter']

        loading_animation = "ON"
        print(f"Method {request.method} of  recommendation generate plan")
        print(f"Got user district {district_name}")            # Getting access of user district
        # print(request.form.getlist('selected_checkbox'))

        selected_forts = request.form.getlist('selected_checkbox')
        print("This is selected forts", selected_forts)
        if not selected_forts:
            fort_sel = "none"
            print("fort none")

            abcd = user_location.query.first()
            print(abcd)
            db.session.commit()
            db.session.query(user_location).delete()
            db.session.commit()

            # To show all recommendations in slider
            tbl_data = all_recommendations.query.all()
            db.session.commit()

            if not abcd:
                print("no lt-lg")
                ltlg = "nolocation"

            return render_template("ourplans.html", params=params, tbl_data=tbl_data, active2=active2, ltlg=ltlg, fort_sel=fort_sel, loading_animation=loading_animation)


        else:
            fort_sel = "selected"

            # added another table containing user_location ()

            user_lat_long = user_location.query.first()
            db.session.commit()

            if user_lat_long is not None:
                user_lat = user_lat_long.user_latitude
                user_long = user_lat_long.user_longitude
                db.session.commit()

                # deleting user loaction table
                db.session.query(user_location).delete()
                db.session.commit()
                print("deleted  user location table vales in user location table ")
                print(f"User location : user_lt: {user_lat} user_lg: {user_long}")


                # -----------------------------------------------------------------------------------------------------------------------
                # Adding function for getting best path to visit various destinations
                path_id_name = []
                plan_sorted_locatons = []

                def optimal_path():
                    URL = "https://api.routific.com/v1/vrp"

                    visits = {}
                    fleet = {}

                    temp_fleet = {
                        "vehicle_1": {
                            "start_location": {
                                "id": "depot",
                                "name": "Your Location",
                                "lat": user_lat,
                                "lng": user_long
                            }
                        }
                    }

                    fleet.update(temp_fleet)

                    for i in selected_forts:
                        # print(i)
                        user_sel_fort = Forts.query.filter_by(fort_id=i).first()
                        db.session.commit()

                        user_sel_fort_lat = user_sel_fort.fort_latitude
                        user_sel_fort_long = user_sel_fort.fort_longitude
                        user_sel_fort_id = user_sel_fort.fort_id
                        user_sel_fort_name = user_sel_fort.fort_name
                        db.session.commit()

                        # converting key string
                        id = str(user_sel_fort_id)

                        temp_visits = {
                            id: {
                                "location": {
                                    "name": user_sel_fort_name,
                                    "lat": user_sel_fort_lat,
                                    "lng": user_sel_fort_long
                                }
                            }
                        }

                        visits.update(temp_visits)

                    # Prepare data payload
                    data = {
                        "visits": visits,
                        "fleet": fleet
                    }

                    # Put together request
                    # This is your demo token
                    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2NjNiY2RmODQ3N2JmMTAwMWI2OTIyNGIiLCJpYXQiOjE3MTUxOTU0MTh9.S7HkQ8z3_jNAf8El2m1cwSLDNwbd2AGrzZ0IKV-dkZU'

                    http = urllib3.PoolManager()
                    req = http.request('POST', URL, body=json.dumps(data),
                                       headers={'Content-Type': 'application/json', 'Authorization': "bearer " + token})

                    # Get route
                    res = json.loads(req.data.decode('utf-8'))


                    # Extracting location_id and location_name pairs
                    locations = {}
                    for vehicle, visits in res['solution'].items():
                        for visit in visits:
                            locations[visit['location_id']] = visit['location_name']

                    # Printing location_id and location_name pairs
                    for location_id, location_name in locations.items():
                        path_id_name.append((location_id, location_name))
                        plan_sorted_locatons.append(location_name)
                        print(f"Location ID: {location_id}, Location Name: {location_name}")

                # calling Function for path finding
                optimal_path()

                # ---------------------------------------------------------------------------
                # adding values to database
                global count
                global old_value
                count = 0
                old_value = ""

                for new_id, name in path_id_name:
                    if new_id == "depot":
                        # print(new_id)
                        print("got user location ")
                    else:
                        # print(new_id)
                        print("got plan functionality")
                        user_sel_fort1 = Forts.query.filter_by(fort_id=new_id).first()
                        user_sel_fort_lat1 = user_sel_fort1.fort_latitude
                        user_sel_fort_long1 = user_sel_fort1.fort_longitude
                        db.session.commit()

                        # for updating lt/lg in database for planning tour

                        user_g_lat_long1 = latitude_longitude.query.first()
                        if user_g_lat_long1 is not None and count == 0:
                            user_g_lat_long1.destination_latitude = user_sel_fort_lat1
                            user_g_lat_long1.destination_longitude = user_sel_fort_long1
                            db.session.commit()

                            new_user_lat_long1 = latitude_longitude(origin_latitude=user_sel_fort_lat1,
                                                                    origin_longitude=user_sel_fort_long1)
                            db.session.add(new_user_lat_long1)
                            db.session.commit()

                            old_value = str(user_sel_fort_lat1)
                            count = count + 1
                            print(f"Plan {count} Uploaded to database")

                        else:
                            new_plan = latitude_longitude.query.filter_by(origin_latitude=old_value).first()
                            new_plan.destination_latitude = user_sel_fort_lat1
                            new_plan.destination_longitude = user_sel_fort_long1
                            db.session.commit()

                            new_plan_lat_long = latitude_longitude(origin_latitude=user_sel_fort_lat1,
                                                                   origin_longitude=user_sel_fort_long1)
                            db.session.add(new_plan_lat_long)
                            db.session.commit()

                            old_value = str(user_sel_fort_lat1)
                            count = count + 1
                            print(f"New plan {count} Uploaded to database")

                # -----------------------------------------------------------------------------------------------------------------------
                # Using distance matrix api

                # filling values in th table to be used in function
                # filling values in the table to be used in the function
                table_fill = latitude_longitude.query.all()
                print(table_fill)

                for row in table_fill:
                    o_lt, o_lg, d_lt, d_lg = row.origin_latitude, row.origin_longitude, row.destination_latitude, row.destination_longitude
                    if d_lt is not None and d_lg is not None:
                        o_lt_lg = f"{o_lt},{o_lg}"
                        d_lt_lg = f"{d_lt},{d_lg}"

                        fill_data = Route(origin=o_lt_lg, destination=d_lt_lg, mode="driving",
                                          traffic_model="best_guess",
                                          departure_time="now")
                        db.session.add(fill_data)

                # Commit once after all the additions
                db.session.commit()

                # ------------------------------------------------------#
                # main function to calculate distance
                BASE_URL = "https://api.distancematrix.ai"

                API_KEY = "h7umDGRk3n0JI4RA1Zm1fkFRFnp1sFiEUYAysjrURSuPBZpZh2Db4gMPSHLTSUdc"

                # Loading data from database
                def load_data():
                    count_rows = 0
                    data = []

                    # Query data from the Route table
                    routes = Route.query.all()

                    for route in routes:
                        origin = route.origin
                        destination = route.destination
                        mode = route.mode
                        traffic_model = route.traffic_model
                        departure_time = route.departure_time

                        data.append({
                            "origin": "%s" % origin.replace('&', ' '),
                            "destination": "%s" % destination.replace('&', ' '),
                            "mode": "%s" % mode.replace('&', ' '),
                            "traffic_model": "%s" % traffic_model.replace('&', ' '),
                            "departure_time": "%s" % departure_time.replace('&', ' ')
                        })
                        count_rows += 1

                    print(" \nTotal rows in the database = %s \n" % (count_rows))
                    return data

                # craeting a request
                def make_request(base_url, api_key, origin, destination, mode, traffic_model, departure_time):
                    url = "{base_url}/maps/api/distancematrix/json" \
                          "?key={api_key}" \
                          "&origins={origin}" \
                          "&destinations={destination}" \
                          "&mode={mode}" \
                          "&traffic_model={traffic_model}" \
                          "&departure_time={departure_time}".format(base_url=base_url,
                                                                    api_key=api_key,
                                                                    origin=origin,
                                                                    destination=destination,
                                                                    mode=mode,
                                                                    traffic_model=traffic_model,
                                                                    departure_time=departure_time)
                    # logging.info("URL: %s" % url)
                    result = requests.get(url)
                    return result.json()

                def main():
                    data = load_data()
                    n = 0
                    for t in data:
                        time.sleep(0)
                        request_time = datetime.datetime.now()
                        dm_res = make_request(BASE_URL, API_KEY, t['origin'], t['destination'], t['mode'],
                                              t['traffic_model'],
                                              t['departure_time'])

                        if dm_res['status'] == 'REQUEST_DENIED':
                            if dm_res['error_message'] == 'The provided API key is invalid or token limit exceeded.':
                                print(dm_res['error_message'])
                                break
                        n += 1
                        try:
                            dm_distance = dm_res['rows'][0]['elements'][0]['distance']
                            dm_duration = dm_res['rows'][0]['elements'][0]['duration']
                            dm_duration_in_traffic = dm_res['rows'][0]['elements'][0]['duration_in_traffic']
                            origin_addresses = dm_res['origin_addresses']
                            destination_addresses = dm_res['destination_addresses']

                        except Exception as exc:
                            print("%s) Please check if the address or coordinates in this line are correct" % n)
                            continue

                        result = Result(
                            request_time=request_time,
                            origin=t['origin'],
                            destination=t['destination'],
                            origin_addresses=origin_addresses,
                            destination_addresses=destination_addresses,
                            mode=t['mode'],
                            traffic_model=t['traffic_model'],
                            departure_time=t['departure_time'],
                            distance_value=dm_distance['value'],
                            distance_text=dm_distance['text'],
                            duration_value=dm_duration['value'],
                            duration_text=dm_duration['text'],
                            duration_in_traffic_value=dm_duration_in_traffic['value'],
                            duration_in_traffic_text=dm_duration_in_traffic['text']
                        )
                        db.session.add(result)
                        db.session.commit()

                # calling function
                main()


                # ----------------------------------------------------------------------------------------------------------#
                # Adding values to box container
                global info_box
                global data
                info_box = []
                l_names = []
                d_t_val = []

                # list containing  sorted loc coordinates for direction
                data = []
                # for temp total time
                total = []

                # ---- used for getting distance value separated for using it in fuel cost function ----#
                d_val = []
                # - end -#

                # filling sorted location names and there values for loopng to work
                for name in range(len(plan_sorted_locatons) - 1):
                    l_names.append((plan_sorted_locatons[name], plan_sorted_locatons[name + 1]))

                plan_box = Result.query.all()
                for dt in plan_box:
                    org = dt.origin
                    dis = dt.destination
                    dist = dt.distance_text
                    t_time = dt.duration_in_traffic_text
                    d_t_val.append((dist, t_time))
                    data.append(dis)   # look here for go to map
                    total.append(t_time)
                    d_val.append(dist)
                db.session.commit()

                print("this is data in data :", data)
                # -------------------------------------------------------------#
                # For showing Fuel required and cost for trip

                fuel_n_cost = []
                total_f_c = []
                t_f = 0
                t_c = 0

                # Define average fuel efficiency for petrol cars in India
                if milage:
                    AVERAGE_MILEAGE = int(milage)
                else:
                    AVERAGE_MILEAGE = 20  # kilometers per liter

                if p_liter:
                    price_per_liter = int(p_liter)
                else:
                    price_per_liter = 104.89  # price per liter

                for d in d_val:
                    # d = "25.7 km"
                    # Split the string to isolate the numeric part
                    numerical_value = d.split()[0]
                    distance = float(numerical_value)

                    def calculate_petrol_cost(distance, price_per_liter):
                        # Calculate required petrol in liters
                        required_petrol = distance / AVERAGE_MILEAGE

                        # Calculate total cost
                        cost = required_petrol * price_per_liter

                        return required_petrol, cost

                    # Calculate and display results
                    required_petrol, total_cost = calculate_petrol_cost(distance, price_per_liter)

                    # for getting total
                    t_f = t_f + required_petrol
                    t_c = t_c + total_cost


                    fuel = f"Required Fuel: {required_petrol:.2f} liters"
                    cost = f"Travel cost: ₹{total_cost:.2f}"
                    fuel_n_cost.append((fuel, cost))

                print(fuel_n_cost)

                # for getting total values in list
                total_f_c.append(round(t_f, 2))
                total_f_c.append(round(t_c, 2))

                print(f"This is list for total f and c : {total_f_c}")

                # appending all in one list
                for i in range(len(l_names)):
                    location_info = l_names[i]
                    distance_info = d_t_val[i]
                    fuel_and_cost = fuel_n_cost[i]
                    info_box.append((*location_info, *distance_info, *fuel_and_cost))
                print(info_box)

                #-------------------------------------------------------------------------------------------------------#
                # for getting values in all_trips table
                raw_data = []
                if len(info_box) > 1:
                    for tuple_data in info_box[1:]:
                        first_string = tuple_data[0]
                        second_string = tuple_data[1]
                        last_string = tuple_data[-1]
                        raw_data.append((first_string, second_string, last_string))
                else:
                    raw_data.append((info_box[0][1], info_box[0][-1]))
                # print(raw_data)
                # print(len(raw_data))


                fort_names = []
                cost = []

                if len(raw_data) == 1:
                    if len(raw_data[0]) == 3:
                        # Get first and second string of the first tuple
                        fort_names.append(raw_data[0][0])
                        fort_names.append(raw_data[0][1])

                        # Extract travel cost values and calculate total cost
                        for _, _, travel_cost in raw_data:
                            cost.append(float(travel_cost.split('₹')[-1]))

                        total_cost = sum(cost)

                    else:
                        fort_names.append(raw_data[0][0])
                        # Extract travel cost values and calculate total cost
                        for _, travel_cost in raw_data:
                            cost.append(float(travel_cost.split('₹')[-1]))

                        total_cost = sum(cost)

                else:
                    # Get first and second string of the first tuple
                    fort_names.append(raw_data[0][0])
                    fort_names.append(raw_data[0][1])

                    # Get second string of each tuple from the second tuple onwards
                    for i in range(1, len(raw_data)):
                        fort_names.append(raw_data[i][1])

                    # Extract travel cost values and calculate total cost
                    for _, _, travel_cost in raw_data:
                        cost.append(float(travel_cost.split('₹')[-1]))

                    total_cost = sum(cost)


                # -----------------------------------------------------------------------------------------#
                # Getting total time for showing user
                # Aceesing total list which stores all times

                print(total)
                # total = ['50 mins', '2 hour 14 mins']

                # Initialize variables to store total hours and minutes
                total_hours = 0
                total_minutes = 0

                # Iterate through each travel time
                for time_str in total:
                    # Split the string to extract hours and minutes
                    time_parts = time_str.split()

                    # Convert hours and minutes to integers
                    hours = 0
                    minutes = 0
                    if 'hour' in time_parts:
                        hours = int(time_parts[0])
                    if 'mins' in time_parts:
                        minutes = int(time_parts[time_parts.index('mins') - 1])

                    # Update total hours and minutes
                    total_hours += hours
                    total_minutes += minutes

                # Adjust total hours and minutes
                total_hours += total_minutes // 60
                total_minutes = total_minutes % 60

                # Format the total travel time
                total_travel_time = f"{total_hours} hour {total_minutes} mins"
                print("Total Travel Time:", total_travel_time)

                def calculate_estimated_days(total_travel_time, overnight_break_duration_range=(8, 13)):

                    # Extract travel time in hours
                    hours = int(total_travel_time.split()[0])

                    # Check if trip can be completed in one day (considering lower bound of overnight break range)
                    if hours <= overnight_break_duration_range[0]:
                        return 1

                    # Calculate estimated days based on lower bound of overnight break range
                    estimated_days = math.ceil(hours / overnight_break_duration_range[0])

                    return estimated_days

                estimated_days = calculate_estimated_days(total_travel_time)
                print(f"Estimated days required for the trip: {estimated_days}")
                #----------------------End-----------------------------#


                # let see we can acces all fields required for all_trips

                if estimated_days < 2:
                    req_time = f"1 day"
                else:
                    req_time = f"{estimated_days} days"

                # Converting list to string for database
                forts_visited_string = ','.join(fort_names)
                #Getting current Date
                current_date = datetime.datetime.now().date()
                # print(current_date)

                trip_data = all_trips(trip_district=district_name, forts_visited=forts_visited_string, required_time=req_time, minimum_cost=total_cost, date=current_date)
                db.session.add(trip_data)
                db.session.commit()



                triggerplan = "trigger"
                ltlg = "none"

                return render_template("ourplans.html", params=params, triggerplan=triggerplan, active2=active2, ltlg=ltlg, fort_sel=fort_sel, loading_animation=loading_animation, info_box=info_box, items=data, total_travel_time=total_travel_time, estimated_days=estimated_days, fuel_n_cost=fuel_n_cost, total_f_c=total_f_c)

            else:
                print("no lt-lg")
                ltlg = "nolocation"

                # To show all recommendations in slider
                tbl_data = all_recommendations.query.all()
                db.session.commit()

                return render_template("ourplans.html", params=params, tbl_data=tbl_data, active2=active2, ltlg=ltlg, fort_sel=fort_sel, loading_animation=loading_animation)







@app.route("/knowaboutforts", methods=['GET', 'POST'])
def knowaboutforts():
    active3 = "active"

    if request.method == "POST":
        print(request.method)

        knowforts = "selected"
        print("got know about forts")

        # logic for filtering fort name
        g_f_n = request.form.get("fort_name")
        # print("Searched for fort ", g_f_n)

        try:
            f_name = Forts.query.filter(Forts.fort_name.like(f'%{g_f_n}%')).first()
            d_info = f_name.detail
            db.session.commit()
            # print("this id d_info", d_info)
            if f_name:
                # ----code for getting content properly in list----#
                d_l = []
                # Provided paragraph
                paragraph = d_info
                # Regular expression pattern to extract strings between "." and "[edit]"
                pattern = r'(.*?)\[edit\]'
                # Extracted strings
                extracted_strings = re.findall(pattern, paragraph, re.DOTALL)
                print(extracted_strings)
                if not len(extracted_strings):
                    print("got empty")
                    return render_template("knowaboutforts.html", params=params, d_info=d_info, knowforts=knowforts, active3=active3)

                # Print extracted items
                for string in extracted_strings:
                    # print(string.strip()) # Remove leading/trailing whitespaces
                    d_l.append(string.strip())
                # ------------------end----------#

            return render_template("knowaboutforts.html", params=params, d_l=d_l, knowforts=knowforts, active3=active3)

        except Exception :
            print("data not found")
            f_data = "none"
            return render_template("knowaboutforts.html", params=params, f_data=f_data, active3=active3)

    return render_template("knowaboutforts.html", params=params, active3=active3)






@app.route("/feedback", methods=['GET', 'POST'])
def feedback():
    active4 = "active"

    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        print(name, email, subject, message)

        if message:
            # status = "unread"
            current_date = datetime.datetime.now().date()
            upload_msg = user_feedback(name=name, email=email, subject=subject, message=message, date=current_date)
            db.session.add(upload_msg)
            db.session.commit()

            return render_template("feedback.html", params=params, active4=active4)

        # user_feedback
        # return f"({self.feedback_id},{self.name},{self.email},{self.subject},{self.message},{self.status})"

    return render_template("feedback.html", params=params, active4=active4)





if __name__ == '__main__':
    app.run(debug=True)



