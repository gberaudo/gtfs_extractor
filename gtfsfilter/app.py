import csv
import re

keep_agencies = [
  '000151'  # TL
]

path_in = 'extract'
path_out = 'filtered'

# ==> extract/agency.txt <==
# agency_id,agency_name,agency_url,agency_timezone,agency_lang,agency_phone
#
# ==> extract/calendar_dates.txt <==
# service_id,date,exception_type
#
# ==> extract/calendar.txt <==
# service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date
#
# ==> extract/feed_info.txt <==
# feed_publisher_name,feed_publisher_url,feed_lang,feed_start_date,feed_end_date,feed_version
#
# ==> extract/frequencies.txt <==
# trip_id,start_time,end_time,headway_secs
#
# ==> extract/routes.txt <==
# route_id,agency_id,route_short_name,route_long_name,route_desc,route_type,route_url,route_color,route_text_color
#
# ==> extract/stops.txt <==
# stop_id,stop_code,stop_name,stop_desc,stop_lat,stop_lon,stop_elevation,zone_id,stop_url,location_type,parent_station,platform_code,ch_station_long_name,ch_station_synonym1,ch_station_synonym2,ch_station_synonym3,ch_station_synonym4
#
# ==> extract/stop_times.txt <==
# trip_id,arrival_time,departure_time,stop_id,stop_sequence,stop_headsign,pickup_type,drop_off_type,shape_dist_traveled,attributes_ch
#
# ==> extract/transfers.txt <==
# from_stop_id,to_stop_id,transfer_type,min_transfer_time
#
# ==> extract/trips.txt <==
# route_id,service_id,trip_id,trip_headsign,trip_short_name,direction_id,block_id,shape_id,bikes_allowed,attributes_ch


# Keep only some agencies
with open(path_in + '/agency.txt', 'r') as agency_file:
  with open(path_out + '/agency.txt', 'w') as agency_file_out:
    first = True
    for line in agency_file:
      keep = first
      first = False
      for agency_id in keep_agencies:
        if line.startswith('{},'.format(agency_id)):
          keep = True
          break
      if keep:
        agency_file_out.write(line)

print(len(keep_agencies), ' agencies to keep')

# Keep the routes used by the agencies
route_ids_to_keep = []
with open(path_in + '/routes.txt', 'r') as routes_file:
  with open(path_out + '/routes.txt', 'w') as routes_file_out:
    # route_id,agency_id,...
    matchers = [re.compile('([^,])+,{},'.format(agency_id)) for agency_id in keep_agencies]
    first = True
    for line in routes_file:
      keep = first
      first = False
      for matcher in matchers:
        match = matcher.match(line)
        if match:
          route_ids_to_keep.append(match.group(0))
          keep = True
          break
      if keep:
        routes_file_out.write(line)

print(len(route_ids_to_keep), ' routes to keep')

# Keep the trips used by the routes
trip_ids_to_keep = []
service_ids_to_keep = []
with open(path_in + '/trips.txt', 'r') as trips_file:
  with open(path_out + '/trips.txt', 'w') as trips_file_out:
    # route_id,service_id,trip_id,...
    matchers = [re.compile('{},([^,])+,([^,])+,'.format(route_id)) for route_id in route_ids_to_keep]
    first = True
    for line in trips_file:
      keep = first
      first = False
      for matcher in matchers:
        match = matcher.match(line)
        if match:
          service_ids_to_keep.append(match.group(0))
          trip_ids_to_keep.append(match.group(1))
          keep = True
          break
      if keep:
        trips_file_out.write(line)

print(len(trip_ids_to_keep), ' trips to keep')
print(len(service_ids_to_keep), ' services to keep')
