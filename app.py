# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"<br/>"
        f"For all dates, please use YYYY-MM-DD format."

    )

@app.route("/api/v1.0/precipitation")
def precipitation():    
    # Create session (link)
    session = Session(engine)

    """Return last 12 months of precipitation data"""
    # Use most recent date in Measurement data to retrieve results from past year
    most_recent_dt = dt.date(2017, 8, 23)
    year_ago_dt = most_recent_dt - dt.timedelta(days=365)
    sel = [Measurement.date, Measurement.prcp]
    year_data = session.query(*sel).filter(Measurement.date >= year_ago_dt).order_by(Measurement.date).all()
    session.close()
    
    # Create dictionary with 'date' as the key and 'prcp' as the value
    # Return json
    year_data_dict = {}
    for date, prcp in year_data:
        year_data_dict[date] = prcp
    return jsonify(year_data_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create session (link)
    session = Session(engine)

    """Return list of stations"""
    # Query station values from Station
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()

    # Create list of station data and return json
    station_list = []
    for row in results:
        station_dict = {}
        station_dict['station_id'] = row[0]
        station_dict['name'] = row[1]
        station_dict['lat'] = row[2]
        station_dict['long'] = row[3]
        station_dict['elevation'] = row[4]
        station_list.append(station_dict)
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session (link)
    session = Session(engine)

    """Return dates and temperatures for most active station in last year"""
    # Query the last year's dates and temperatures from the most active station
    most_recent_dt = dt.date(2017, 8, 23)
    year_ago_dt = most_recent_dt - dt.timedelta(days=365)
    most_active = 'USC00519281'
    year_tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago_dt).filter(Measurement.station == most_active)
    session.close()

    # Compile list of date and temperature data and return json
    tobs_data_list = []
    for row in year_tobs_data:
        tobs_dict = {}
        tobs_dict['date'] = row[0]
        tobs_dict['temperature'] = row[1]
        tobs_data_list.append(tobs_dict)
    return jsonify(tobs_data_list)

@app.route("/api/v1.0/<start>")
def start_tempdata(start):
    # Create session (link)
    session = Session(engine)

    """Return the minimum, average, and maximum temperatures from a given start date"""
    # Convert input start date to datetime object and retrieve temperature data
    start_date_str = start
    start_date_dt = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    range_data = session.query(*sel).filter(Measurement.date >= start_date_dt)
    session.close()

    # Create dictionary of values and return json
    for row in range_data:
        data_dict = {
        'min_temp': row[0],
        'max_temp': row[1],
        'avg_temp': round(row[2], 2)
        }
    return jsonify(data_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end_tempdata(start, end):
    # Create session (link)
    session = Session(engine)
  
    """Return the minimum, average, and maximum temperatures from given start and end dates"""
    # Convert input start/end dates to datetime object
    start_date_str = start
    start_date_dt = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date_str = end
    end_date_dt = datetime.strptime(end_date_str, "%Y-%m-%d").date()

    # Check that start date occurs before end date
    if (start > end):
        return jsonify({"Error": "start date must occur before end date"})
    
    # Retrieve temperature data from time-range
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    range_data = session.query(*sel).filter(Measurement.date >= start_date_dt).filter(Measurement.date <= end_date_dt)
    session.close()

    # Create dictionary of values and return json
    for row in range_data:
        data_dict = {
        'min_temp': row[0],
        'max_temp': row[1],
        'avg_temp': round(row[2], 2)
        }
    return jsonify(data_dict)

if __name__ == "__main__":
    app.run(debug=True)