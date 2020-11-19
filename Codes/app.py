import numpy as np
import datetime as dt
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table 
ME = Base.classes.measurement
ST = Base.classes.station

#create session from python to the DB
session = Session(engine)


#################################################
# Flask Setup
app = Flask(__name__)

#################################################
# Flask Routes

@app.route("/")
def welcome():
    return (
        f"Welcome to Hawaii Climate Analysis <br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
        
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipiation data for the last year"""
    # Calculate the date 1 year ago from the last data point in the database
    latest = session.query(ME.date).order_by(ME.date.desc()).first()[0]
    query_date = dt.datetime.strptime(latest, '%Y-%m-%d') - dt.timedelta(days=366)
 
    # Perform a query to retrieve the data and precipitation scores
    prcp = session.query(ME.date, ME.prcp).filter(ME.date>=query_date).order_by(ME.date.desc()).all()

    # Dictionary with data and precipitation data
    pre = {date: p for date, p in prcp}

    return jsonify(pre)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    station = session.query(ME.station).all()
    stations = list(np.ravel(station))
    return jsonify(stations=stations)



@app.route("/api/v1.0/tobs")
def temps():
    """Return the temperature data for the last year"""
     # Calculate the date 1 year ago from the last data point in the database
    latest = session.query(ME.date).order_by(ME.date.desc()).first()[0]
    query_date = dt.datetime.strptime(latest, '%Y-%m-%d') - dt.timedelta(days=366)
    
    # Query the last 12 months of temperature observation data for the busiest station
    data = session.query(ME.tobs).filter(ME.station =='USC00519281').\
    filter(ME.date>=query_date).all()

    temps = list(np.ravel(data))

    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stat(start=None, end=None):
    sel=[func.max(ME.tobs), func.min(ME.tobs), func.avg(ME.tobs)]

    if not end:
        temp = session.query(*sel).filter(ME.date>=start).all()
        temps = list(np.ravel(temp))
        return jsonify (temps)
    
    temp = session.query(*sel).filter(ME.date>=start).filter(ME.date<=end).all()
    temps = list(np.ravel(temp))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run(debug=True)
