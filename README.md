# GTFS extractor

## Goal

GTFS files can be huge and may contain irrelevent data for one's usage.
This tool allows to extract a subset of the data, according the folowing riteria:
- the agencies the data is linked to;
- the bounding box of the stops the data is linked to.

As a consequence, less resources are necessary (CPU, memory, time, storage).


## Getting GTFS feeds for the whole Switzerland

```bash
wget http://gtfs.geops.ch/dl/gtfs_complete.zip -O feeds/gtfs_geops.zip
rm -rf feeds/geops
unzip feeds/gtfs_geops.zip -d feeds/geops

# See https://opentransportdata.swiss/en/dataset/timetable-2018-gtfs for updates
wget https://opentransportdata.swiss/dataset/b408f747-9838-4c05-bb98-10dac3996f17/resource/ceecb459-7c6f-40e3-92bf-d4612df7a54c/download/gtfsfp20182017-12-05.zip -O feeds/gtfs_otd.zip
rm -rf feeds/otd
unzip feeds/gtfs_otd.zip -d feeds/otd
./remove_bom.sh feeds/otd
```

## Extract data of interest

Extract by agencies:
```bash
export DATASET=otd
export AGENCIES="151,764"
rm -rf filtered/*
python3 gtfs_extractor/filters.py --from feeds/$DATASET --agencies $AGENCIES

```

Or extract by bounding box:
```bash
export DATASET=otd
export BBOX="46.44652,46.57948,6.40353,6.87899"
rm -rf filtered/*
python3 gtfs_extractor/filters.py --from feeds/$DATASET --bbox $BBOX
```

## Generate Trip Planner graph
```bash
mkdir -p otp/graphs
cd otp/
wget https://repo1.maven.org/maven2/org/opentripplanner/otp/1.2.0/otp-1.2.0-shaded.jar
wget https://planet.osm.ch/switzerland-padded.osm.pbf

export DATASET=otd
rm -rf graphs/$DATASET; mkdir graphs/$DATASET
ln -s ../../switzerland-padded.osm.pbf graphs/$DATASET/switzerland-padded.osm.pbf
(cd ../filtered; zip gtfs_extracted.zip *.txt)
mv ../filtered/gtfs_extracted.zip graphs/$DATASET/
java -Xmx8G -jar otp-1.2.0-shaded.jar --build graphs/$DATASET
java -Xmx8G -jar otp-1.2.0-shaded.jar --graphs graphs/ --router $DATASET --verbose --server
```
