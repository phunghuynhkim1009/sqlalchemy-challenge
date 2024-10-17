# activate environment
#. .venv/bin/activate

# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime
import os
import numpy as np
import pandas as pd
import datetime as dt

#################################################
# Database Setup
#################################################
base_dir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(base_dir, "Resources", "hawaii.sqlite")
engine = create_engine(f"sqlite:///{database_path}")
#engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)


# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route('/')
def home():
    return '''
    Available Routes:<br>
    /api/v1.0/precipitation<br>
    /api/v1.0/stations<br>
    /api/v1.0/tobs<br>
    /api/v1.0/<start><br>
    /api/v1.0/<start>/<end><br>
    '''

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    # Find the most recent date in the data set.
    recent_date = session.query(func.max(measurement.date)).scalar()
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    # Calculate the date one year from the last date in data set.
    one_year_ago = recent_date - dt.timedelta(days=365)

# Perform a query to retrieve the data and precipitation scores
# Query to retrieve the last 12 months of precipitation data
    results = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= one_year_ago).\
    order_by(measurement.date).all()
    session.close()

    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    results = session.query(station.station).all()
    session.close()

    stations_list = [station[0] for station in results]
    return jsonify(stations_list)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    # Find the most recent date in the data set.
    recent_date = session.query(func.max(measurement.date)).scalar()
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    # Calculate the date one year from the last date in data set.
    one_year_ago = recent_date - dt.timedelta(days=365)
    active_stations = session.query(
    measurement.station,
    func.count(measurement.id).label('count')
    ).group_by(measurement.station).order_by(func.count(measurement.id).desc()).all()
    most_active_station = active_stations[0][0]

    results = session.query(measurement.tobs).\
    filter(measurement.station == most_active_station).\
    filter(measurement.date >= one_year_ago).\
    order_by(measurement.date).all()

    temperature_observations = [result[0] for result in results]
    session.close()

    return jsonify({
        "most_active_station": most_active_station,
        "tobs": temperature_observations})

@app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).all()
    session.close()

    return jsonify({"TMIN": results[0][0], "TAVG": results[0][1], "TMAX": results[0][2]})

@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()

    return jsonify({"TMIN": results[0][0], "TAVG": results[0][1], "TMAX": results[0][2]})

if __name__ == '__main__':
    app.run(debug=True)