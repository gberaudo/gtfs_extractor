import shutil
from contextlib import contextmanager

keep_agencies = {
  #'000151'  # TL
  '000029',  # MBC
}

path_in = 'extract'
path_out = 'filtered'


@contextmanager
def in_out_files(filename):
  with open('{}/{}'.format(path_in, filename), 'r') as in_file:
    with open('{}/{}'.format(path_out, filename), 'w') as out_file:
      out_file.write(in_file.readline())
      yield in_file, out_file


# Keep only some agencies
with in_out_files('agency.txt') as (in_file, out_file):
  for line in in_file:
    agency_id, _ = line.split(',', 1)
    if agency_id in keep_agencies:
      out_file.write(line)

print(len(keep_agencies), ' agencies to keep')

# Keep the routes used by the agencies
route_ids_to_keep = set()
with in_out_files('routes.txt') as (in_file, out_file):
  for line in in_file:
    route_id, agency_id, _ = line.split(',', 2)
    if agency_id in keep_agencies:
      route_ids_to_keep.add(route_id)
      out_file.write(line)

print(len(route_ids_to_keep), ' routes kept')

# Keep the trips used by the routes
trip_ids_to_keep = set()
service_ids_to_keep = set()
with in_out_files('trips.txt') as (in_file, out_file):
  for line in in_file:
    route_id, service_id, trip_id, _ = line.split(',', 3)
    if route_id in route_ids_to_keep:
      service_ids_to_keep.add(service_id)
      trip_ids_to_keep.add(trip_id)
      out_file.write(line)

print(len(trip_ids_to_keep), ' trips kept')
print(len(service_ids_to_keep), ' services to keep')


with in_out_files('calendar_dates.txt') as (in_file, out_file):
  for line in in_file:
    service_id, _ = line.split(',', 1)
    if service_id in service_ids_to_keep:
      out_file.write(line)


with in_out_files('calendar.txt') as (in_file, out_file):
  for line in in_file:
    service_id, _ = line.split(',', 1)
    if service_id in service_ids_to_keep:
      out_file.write(line)


with in_out_files('frequencies.txt') as (in_file, out_file):
  for line in in_file:
    trip_id, _ = line.split(',', 1)
    if trip_id in trip_ids_to_keep:
      out_file.write(line)


# Keep the stop_times used by the trips
stop_ids_to_keep = set()
with in_out_files('stop_times.txt') as (in_file, out_file):
  for line in in_file:
    trip_id, arrival_time, departure_time, stop_id, _ = line.split(',', 4)
    if trip_id in trip_ids_to_keep:
      stop_ids_to_keep.add(stop_id)
      out_file.write(line)

print(len(stop_ids_to_keep), ' stops to keep')


# Keep the transfers
with in_out_files('transfers.txt') as (in_file, out_file):
  for line in in_file:
    from_stop_id, to_stop_id, _ = line.split(',', 2)
    if from_stop_id in stop_ids_to_keep and to_stop_id in stop_ids_to_keep:
      out_file.write(line)


# Keep the stops
with in_out_files('stops.txt') as (in_file, out_file):
  for line in in_file:
    stop_id, _ = line.split(',', 1)
    if stop_id in stop_ids_to_keep:
      out_file.write(line)


# Copy the feed info
shutil.copyfile('{}/{}'.format(path_in, 'feed_info.txt'), '{}/{}'.format(path_out, 'feed_info.txt'))
