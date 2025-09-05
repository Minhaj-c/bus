class Bus {
  final int id;
  final String numberPlate;
  final int capacity;
  final double? latitude;
  final double? longitude;
  final DateTime? lastLocationUpdate;
  final bool isRunning;
  final BusRoute? route;
  final BusSchedule? schedule;
  final double? distanceKm;

  Bus({
    required this.id,
    required this.numberPlate,
    required this.capacity,
    this.latitude,
    this.longitude,
    this.lastLocationUpdate,
    required this.isRunning,
    this.route,
    this.schedule,
    this.distanceKm,
  });

  factory Bus.fromJson(Map<String, dynamic> json) {
    return Bus(
      id: json['id'],
      numberPlate: json['number_plate'],
      capacity: json['capacity'],
      latitude: json['current_latitude'] != null 
          ? double.parse(json['current_latitude'].toString()) 
          : null,
      longitude: json['current_longitude'] != null 
          ? double.parse(json['current_longitude'].toString()) 
          : null,
      lastLocationUpdate: json['last_location_update'] != null
          ? DateTime.parse(json['last_location_update'])
          : null,
      isRunning: json['is_running'] ?? false,
      route: json['route'] != null ? BusRoute.fromJson(json['route']) : null,
      schedule: json['schedule'] != null 
          ? BusSchedule.fromJson(json['schedule']) 
          : null,
      distanceKm: json['distance_km']?.toDouble(),
    );
  }
}

class BusRoute {
  final int id;
  final String number;
  final String name;
  final String origin;
  final String destination;
  final double totalDistance;
  final List<BusStop> stops;

  BusRoute({
    required this.id,
    required this.number,
    required this.name,
    required this.origin,
    required this.destination,
    required this.totalDistance,
    this.stops = const [],
  });

  factory BusRoute.fromJson(Map<String, dynamic> json) {
    return BusRoute(
      id: json['id'],
      number: json['number'],
      name: json['name'],
      origin: json['origin'],
      destination: json['destination'],
      totalDistance: double.parse(json['total_distance'].toString()),
      stops: (json['stops'] as List?)
          ?.map((stop) => BusStop.fromJson(stop))
          .toList() ?? [],
    );
  }
}

class BusStop {
  final int id;
  final String name;
  final int sequence;
  final double distanceFromOrigin;

  BusStop({
    required this.id,
    required this.name,
    required this.sequence,
    required this.distanceFromOrigin,
  });

  factory BusStop.fromJson(Map<String, dynamic> json) {
    return BusStop(
      id: json['id'],
      name: json['name'],
      sequence: json['sequence'],
      distanceFromOrigin: double.parse(json['distance_from_origin'].toString()),
    );
  }
}

class BusSchedule {
  final int id;
  final int availableSeats;
  final int totalSeats;
  final String departureTime;
  final String arrivalTime;
  final String date;

  BusSchedule({
    required this.id,
    required this.availableSeats,
    required this.totalSeats,
    required this.departureTime,
    required this.arrivalTime,
    required this.date,
  });

  factory BusSchedule.fromJson(Map<String, dynamic> json) {
    return BusSchedule(
      id: json['id'],
      availableSeats: json['available_seats'],
      totalSeats: json['total_seats'],
      departureTime: json['departure_time'],
      arrivalTime: json['arrival_time'],
      date: json['date'],
    );
  }
}
