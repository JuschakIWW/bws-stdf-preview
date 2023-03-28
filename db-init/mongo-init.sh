#!/bin/bash
# Note: If this script is not automatically executed, make sure that the line endings are linux style
echo "Populating MongoDB with data..."

# Load OOWV meta data
mongoimport --username $MONGO_INITDB_ROOT_USERNAME --password $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin \
--db $MONGO_INITDB_DATABASE --collection devices --file /docker-entrypoint-initdb.d/data/pm_meta.json --jsonArray

# Laod OOWV measurements
mongoimport --username $MONGO_INITDB_ROOT_USERNAME --password $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin \
--db $MONGO_INITDB_DATABASE --collection deviceMeasurements --file /docker-entrypoint-initdb.d/data/pm_measurements.json --jsonArray

#### Old script for H2O dataset ####
# Import Meta data
#mongoimport --username $MONGO_INITDB_ROOT_USERNAME --password $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin \
#--db $MONGO_INITDB_DATABASE --collection virtualMeterMeta --file /docker-entrypoint-initdb.d/data/virtualMeterMeta.json --jsonArray

# Import readings
#mongoimport --username $MONGO_INITDB_ROOT_USERNAME --password $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin \
#            --db $MONGO_INITDB_DATABASE --collection measurements --file /docker-entrypoint-initdb.d/data/measurements.json --jsonArray

echo "Populating MongoDB done."
