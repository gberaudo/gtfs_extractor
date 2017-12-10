import codecs
import csv
import os.path


path_in = 'from'
path_out = 'filtered'

class Bbox:
  min_lat = None
  max_lat = None
  min_lon = None
  max_lon = None

  def contains(self, lat: float, lon: float):
    return lat <= self.max_lat and lat >= self.min_lat and lon <= self.max_lon and lon >= self.min_lon

  @staticmethod
  def create_from_coordinates(min_lat, max_lat, min_lon, max_lon):
    bbox = Bbox()
    bbox.min_lat = min_lat
    bbox.max_lat = max_lat
    bbox.min_lon = min_lon
    bbox.max_lon = max_lon
    return bbox


class InOutLine:
  keep = False
  line = None
  split = None


def remove_bom_crap(stuff):
  # See https://stackoverflow.com/questions/20899939/removing-bom-from-gziped-csv-in-python
  bommy = stuff[0]
  if bommy.encode('utf-8').startswith(codecs.BOM_UTF8):
    stuff[0] = bommy[1:]
  return stuff


def get_in_file(filename):
  return '{}/{}'.format(path_in, filename)


def get_out_file(filename):
  return '{}/{}'.format(path_out, filename)


def csv_line_reader(filename, fields):
  with open(get_in_file(filename), 'r', newline='') as in_file:
    reader = csv.reader(in_file)
    fieldnames = remove_bom_crap(next(reader))
    field_indices = [fieldnames.index(field) for field in fields]
    for row in reader:
      yield (row[idx] for idx in field_indices)


def line_filter(filename, maxsplit):
  io_line = InOutLine()
  with open(get_in_file(filename), 'r') as in_file:
    with open(get_out_file(filename), 'w') as out_file:
      out_file.write(in_file.readline())
      for line in in_file:
        io_line.keep = False
        io_line.line = line
        io_line.split = (item.strip('"') for item in line.split(',', maxsplit))
        yield io_line
        if io_line.keep:
          out_file.write(line)


def line_reader(filename, maxsplit):
  with open(get_in_file(filename), 'r') as in_file:
    for line in in_file:
      yield (item.strip('"') for item in line.split(',', maxsplit))


def split_writer(filename):
  with open(get_in_file(filename), 'r') as in_file:
    with open(get_out_file(filename), 'w') as out_file:
      out_file.write(in_file.readline())
      for line in in_file:
        keep = yield line
        if keep:
          out_file.write(line)


def filter_using_first_column(filename, ids):
  for line in line_filter(filename, 1):
    id, _ = line.split
    line.keep = id in ids


def filter_agencies(keep_agencies):
  filter_using_first_column('agency.txt', keep_agencies)


def filter_calendar_using_services(services):
  filter_using_first_column('calendar.txt', services)


def filter_calendar_dates_using_services(services):
  filter_using_first_column('calendar_dates.txt', services)


def filter_frequencies_using_trips(trips):
  if os.path.isfile(get_in_file('frequencies.txt')):
    filter_using_first_column('frequencies.txt', trips)


def filter_stops(stops):
  filter_using_first_column('stops.txt', stops)


def get_stops_in_bbox(bbox: Bbox):
  stops = set()
  reader = csv_line_reader('stops.txt', ['stop_id', 'stop_lat', 'stop_lon'])
  for line in reader:
    # stop_id,stop_code,stop_name,stop_desc,stop_lat,stop_lon
    stop_id, stop_lat, stop_lon = line
    if bbox.contains(float(stop_lat), float(stop_lon)):
      stops.add(stop_id)
  return stops


def get_trips_of_stops(stops):
  trips = set()
  for line in line_reader('stop_times.txt', 4):
    trip_id, arrival_time, departure_time, stop_id, _ = line
    if stop_id in stops:
      trips.add(trip_id)
  return trips


def filter_trips(trips, associated_routes, associated_services):
  for line in line_filter('trips.txt', 3):
    route_id, service_id, trip_id, _ = line.split
    if trip_id in trips:
      associated_routes.add(route_id)
      associated_services.add(service_id)
      line.keep = True


def filter_routes(routes, associated_agencies):
  for line in line_filter('routes.txt', 2):
    route_id, agency_id, _ = line.split
    if route_id in routes:
      associated_agencies.add(agency_id)
      line.keep = True


# Keep the routes used by the agencies
def filter_routes_of_agencies(keep_agencies, matching_routes):
  for line in line_filter('routes.txt', 2):
    route_id, agency_id, _ = line.split
    if agency_id in keep_agencies:
      matching_routes.add(route_id)
      line.keep = True


def filter_trips_of_routes(route_ids, matching_services, matching_trips):
  for line in line_filter('trips.txt', 3):
    route_id, service_id, trip_id, _ = line.split
    if route_id in route_ids:
      matching_services.add(service_id)
      matching_trips.add(trip_id)
      line.keep = True


def filter_stop_times_using_trips(trips, matching_stop_ids):
  for line in line_filter('stop_times.txt', 4):
    trip_id, arrival_time, departure_time, stop_id, _ = line.split
    if trip_id in trips:
      matching_stop_ids.add(stop_id)
      line.keep = True


# Keep the transfers
def filter_transfers_using_stops(stops):
  for line in line_filter('transfers.txt', 2):
    from_stop_id, to_stop_id, _ = line.split
    if from_stop_id in stops and to_stop_id in stops:
      line.keep = True


def simple_app_common(service_ids_to_keep, trip_ids_to_keep):
  import shutil
  filter_calendar_dates_using_services(service_ids_to_keep)
  filter_calendar_using_services(service_ids_to_keep)
  filter_frequencies_using_trips(trip_ids_to_keep)

  # Keep the stop_times used by the trips
  stop_ids_to_keep = set()
  filter_stop_times_using_trips(trip_ids_to_keep, stop_ids_to_keep)
  filter_stops(stop_ids_to_keep)
  filter_transfers_using_stops(stop_ids_to_keep)

  print(len(stop_ids_to_keep), ' stops to keep')

  # Copy the feed info
  shutil.copyfile(get_in_file('feed_info.txt'), get_out_file('feed_info.txt'))


def simple_app_by_agencies(keep_agencies):
  filter_agencies(keep_agencies)
  print('Kept {} agencies'.format(len(keep_agencies)))

  route_ids_to_keep = set()
  filter_routes_of_agencies(keep_agencies, route_ids_to_keep)
  print(len(route_ids_to_keep), ' routes kept')

  # Keep the trips used by the routes
  trip_ids_to_keep = set()
  service_ids_to_keep = set()
  filter_trips_of_routes(route_ids_to_keep, service_ids_to_keep, trip_ids_to_keep)
  print(len(trip_ids_to_keep), ' trips kept')
  print(len(service_ids_to_keep), ' services to keep')

  simple_app_common(service_ids_to_keep, trip_ids_to_keep)


def simple_app_by_bbox(bbox: Bbox):
  stop_ids_in_bbox = get_stops_in_bbox(bbox)
  print('Found {} stops in bbox'.format(len(stop_ids_in_bbox)))
  trip_ids = get_trips_of_stops(stop_ids_in_bbox)
  print('Found {} trips in bbox'.format(len(trip_ids)))

  print('Keeping {} trips'.format(len(trip_ids)))
  route_ids_to_keep = set()
  service_ids_to_keep = set()
  filter_trips(trip_ids, route_ids_to_keep, service_ids_to_keep)

  print('Keeping {} routes'.format(len(route_ids_to_keep)))
  agency_ids_to_keep = set()
  filter_routes(route_ids_to_keep, agency_ids_to_keep)

  print('Keeping {} agencies'.format(len(agency_ids_to_keep)))
  filter_agencies(agency_ids_to_keep)

  simple_app_common(service_ids_to_keep, trip_ids)


if __name__ == '__main__':
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option("-f", "--from", dest="path_in", help="directory from which the GFTS files are read", default='from')
  parser.add_option("-t", "--to", dest="path_out", help="directory to which the GFTS files are written", default='filtered')
  parser.add_option("--agencies", dest="agencies", help="the agency ids to keep")
  parser.add_option("--bbox", dest="bbox", help="the stop bbox for selecting the trips to keep")

  (options, args) = parser.parse_args()

  path_in = options.path_in
  path_out = options.path_out
  if options.agencies:
    # { '000151',  # TL,  '000764',  # MBC }
    keep_agencies = [x.strip() for x in options.agencies.split(',')]
    simple_app_by_agencies(keep_agencies)
  elif options.bbox:
    # top=46.57948 left=6.40353 bottom=46.44652 right=6.87899
    # [46.44652, 46.57948, 6.40353, 6.87899]
    coordinates = [float(x.strip()) for x in options.bbox.split(',')]
    keep_bbox = Bbox.create_from_coordinates(*coordinates)
    simple_app_by_bbox(keep_bbox)
