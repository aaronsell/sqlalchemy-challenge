# Import the dependencies.
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func

import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# measurement = base.classes.measurement

# reflect the tables
Base = automap_base()
Base.prepare(autoload_with=engine)
#Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
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
        f"/api/v1.0/temp/"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the date and precipitation scores
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= query_date).all()
    
    # Save the query results as a Pandas DataFrame. Explicitly set the column names
    measurement_df = pd.DataFrame(prcp_data, columns = ['Date', 'Precipitation']) 
    
    session.close()

    # Create a dictionary from the row data and append to a list
    prcp_list = []
    for index, row in measurement_df.iterrows():
        prcp_dict = {}
        prcp_dict['date'] = row['Date']
        prcp_dict['prcp'] = row['Precipitation']
        prcp_list.append(prcp_dict)
  
    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    # Create a query for to find all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert tuple into a list
    all_stations = list(np.ravel(results))
    
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Using the most active station id
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram

    # Calculate the date one year from the last date in data set.
    yearBeforeEnd = dt.date(2017, 8, 18) - dt.timedelta(days=365)

    # Query to get the temperatures observed during the last year at station 'USC00519281'
    activeTOBS = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= yearBeforeEnd).\
        filter(Measurement.station == 'USC00519281').all()
    
    # Put the data into a dataframe
    activeDF = pd.DataFrame(activeTOBS, columns = ['Date', 'TOBS'])

    # Put the data into a list of dictionaries
    tobs_list = []
    for index, row in activeDF.iterrows():
        tobs_dict = {}
        tobs_dict['Date'] = row['Date']
        tobs_dict['Temperature'] = row['TOBS']
        tobs_list.append(tobs_dict)
  
    return jsonify(tobs_list)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):

    user_picks = [func.min(Measurement.tobs), func.max(Measurement.tobs), \
                 func.avg(Measurement.tobs)]
    
    if not end:

        startDate = dt.datetime.strptime(start, "%m%d%Y")

        # Query to get the temperature observed during the specied date
        results = session.query(*user_picks)\
            .filter(Measurement.date >= startDate).all()

        session.close()

        # Convert tuples into a list
        tobs_list1 = list(np.ravel(results))

        return jsonify(tobs_list1)

    startDate = dt.datetime.strptime(start, "%m%d%Y")
    endDate = dt.datetime.strptime(end, "%m%d%Y")

    # Query to get the temperatures observed during the specied start and end dates  
    results = session.query(*user_picks)\
            .filter(Measurement.date >= startDate)\
            .filter(Measurement.date <= endDate).all()

    session.close()

    # Convert tuples into a list
    tobs_list1 = list(np.ravel(results))

    return jsonify(tobs_list1)

if __name__ == '__main__':
    app.run(debug=True)