import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:geolocator/geolocator.dart';
import '../providers/bus_provider.dart';
import '../models/bus.dart';
import 'bus_details_screen.dart';

class LiveBusMapScreen extends StatefulWidget {
  const LiveBusMapScreen({Key? key}) : super(key: key);

  @override
  State<LiveBusMapScreen> createState() => _LiveBusMapScreenState();
}

class _LiveBusMapScreenState extends State<LiveBusMapScreen> {
  Position? _currentPosition;
  bool _isLoadingLocation = false;

  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
  }

  Future<void> _getCurrentLocation() async {
    setState(() => _isLoadingLocation = true);

    try {
      // Check if location services are enabled
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        if (mounted) {
          setState(() => _isLoadingLocation = false);
          _showError('Location services are disabled. Please enable GPS in your device settings.');
        }
        return;
      }

      // Check permissions
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          if (mounted) {
            setState(() => _isLoadingLocation = false);
            _showError('Location permission denied. Please enable location permission in app settings.');
          }
          return;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        if (mounted) {
          setState(() => _isLoadingLocation = false);
          _showError('Location permission permanently denied. Please enable in Settings > Apps > Transport App > Permissions');
        }
        return;
      }

      print('DEBUG: Attempting to get location...');

      // Try last known position first
      Position? position = await Geolocator.getLastKnownPosition();
      
      if (position == null) {
        print('DEBUG: No last known position, getting current...');
        // Get current position with timeout
        position = await Geolocator.getCurrentPosition(
          desiredAccuracy: LocationAccuracy.medium,
          timeLimit: const Duration(seconds: 20),
        );
      }

      print('DEBUG: Got position: ${position.latitude}, ${position.longitude}');

      if (mounted) {
        setState(() {
          _currentPosition = position;
          _isLoadingLocation = false;
        });
        await _fetchNearbyBuses();
      }
    } catch (e) {
      print('DEBUG: Location error: $e');
      if (mounted) {
        setState(() => _isLoadingLocation = false);
        
        String errorMessage = 'Failed to get location';
        if (e.toString().contains('TimeoutException')) {
          errorMessage = 'GPS timeout. Try going outside for better signal, or use manual location.';
        } else if (e.toString().contains('permission')) {
          errorMessage = 'Location permission required. Enable in device settings.';
        } else {
          errorMessage = 'Location error: ${e.toString()}';
        }
        
        _showError(errorMessage);
      }
    }
  }

  Future<void> _fetchNearbyBuses() async {
    if (_currentPosition == null || !mounted) return;

    print('DEBUG: Fetching nearby buses for location: ${_currentPosition!.latitude}, ${_currentPosition!.longitude}');
    
    final busProvider = Provider.of<BusProvider>(context, listen: false);
    await busProvider.fetchNearbyBuses(
      _currentPosition!.latitude,
      _currentPosition!.longitude,
    );
  }

  void _showError(String message) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message), backgroundColor: Colors.red),
      );
    }
  }

  void _showManualLocationDialog() {
    final latController = TextEditingController();
    final lngController = TextEditingController();
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Enter Location Manually'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Enter your coordinates for testing:'),
            const SizedBox(height: 16),
            TextField(
              controller: latController,
              decoration: const InputDecoration(
                labelText: 'Latitude',
                hintText: '11.2588',
              ),
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: lngController,
              decoration: const InputDecoration(
                labelText: 'Longitude',
                hintText: '75.7804',
              ),
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              final lat = double.tryParse(latController.text);
              final lng = double.tryParse(lngController.text);
              
              if (lat != null && lng != null) {
                setState(() {
                  _currentPosition = Position(
                    latitude: lat,
                    longitude: lng,
                    timestamp: DateTime.now(),
                    accuracy: 10.0,
                    altitude: 0.0,
                    heading: 0.0,
                    speed: 0.0,
                    speedAccuracy: 0.0,
                    altitudeAccuracy: 0.0,
                    headingAccuracy: 0.0,
                  );
                });
                Navigator.pop(context);
                _fetchNearbyBuses();
              } else {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Please enter valid coordinates')),
                );
              }
            },
            child: const Text('Use Location'),
          ),
        ],
      ),
    );
  }

  void _showBusDetails(Bus bus) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => BusDetailsScreen(bus: bus),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Live Bus Tracking'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _fetchNearbyBuses,
          ),
        ],
      ),
      body: _isLoadingLocation
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Getting your location...'),
                  SizedBox(height: 8),
                  Text('This may take a moment outdoors', 
                       style: TextStyle(fontSize: 12, color: Colors.grey)),
                ],
              ),
            )
          : _currentPosition == null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.location_off, size: 64, color: Colors.grey),
                      const SizedBox(height: 16),
                      const Text('Location not available', 
                                 style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 8),
                      const Padding(
                        padding: EdgeInsets.symmetric(horizontal: 32),
                        child: Text('GPS works best outdoors. Try going near a window or outside.',
                                   textAlign: TextAlign.center,
                                   style: TextStyle(color: Colors.grey)),
                      ),
                      const SizedBox(height: 20),
                      ElevatedButton.icon(
                        onPressed: _getCurrentLocation,
                        icon: const Icon(Icons.gps_fixed),
                        label: const Text('Try GPS Again'),
                      ),
                      const SizedBox(height: 10),
                      TextButton.icon(
                        onPressed: _showManualLocationDialog,
                        icon: const Icon(Icons.edit_location),
                        label: const Text('Enter Location Manually'),
                      ),
                    ],
                  ),
                )
              : Column(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(16),
                      color: Colors.blue[50],
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Your Location:', 
                                     style: TextStyle(fontWeight: FontWeight.bold)),
                          Text('Lat: ${_currentPosition!.latitude.toStringAsFixed(6)}'),
                          Text('Lng: ${_currentPosition!.longitude.toStringAsFixed(6)}'),
                          const SizedBox(height: 8),
                          Row(
                            children: [
                              ElevatedButton.icon(
                                onPressed: _getCurrentLocation,
                                icon: const Icon(Icons.refresh, size: 16),
                                label: const Text('Update Location'),
                                style: ElevatedButton.styleFrom(
                                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    Expanded(
                      child: Consumer<BusProvider>(
                        builder: (context, busProvider, _) {
                          if (busProvider.isLoading) {
                            return const Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  CircularProgressIndicator(),
                                  SizedBox(height: 16),
                                  Text('Searching for buses...'),
                                ],
                              ),
                            );
                          }

                          if (busProvider.error != null) {
                            return Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  const Icon(Icons.error, size: 64, color: Colors.red),
                                  const SizedBox(height: 16),
                                  Text('Error: ${busProvider.error}'),
                                  const SizedBox(height: 16),
                                  ElevatedButton(
                                    onPressed: _fetchNearbyBuses,
                                    child: const Text('Retry'),
                                  ),
                                ],
                              ),
                            );
                          }

                          if (busProvider.nearbyBuses.isEmpty) {
                            return const Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(Icons.directions_bus_filled, size: 64, color: Colors.grey),
                                  SizedBox(height: 16),
                                  Text('No buses found nearby'),
                                  SizedBox(height: 8),
                                  Text('Make sure buses are running with GPS enabled',
                                       style: TextStyle(color: Colors.grey)),
                                ],
                              ),
                            );
                          }

                          return ListView.builder(
                            padding: const EdgeInsets.all(16),
                            itemCount: busProvider.nearbyBuses.length,
                            itemBuilder: (context, index) {
                              final bus = busProvider.nearbyBuses[index];
                              return Card(
                                margin: const EdgeInsets.only(bottom: 12),
                                elevation: 4,
                                child: ListTile(
                                  leading: const Icon(Icons.directions_bus, 
                                                    color: Colors.green, size: 32),
                                  title: Text('Bus ${bus.numberPlate}',
                                             style: const TextStyle(fontWeight: FontWeight.bold)),
                                  subtitle: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      const SizedBox(height: 4),
                                      Text('Route: ${bus.route?.name ?? 'Unknown Route'}'),
                                      Text('Distance: ${bus.distanceKm?.toStringAsFixed(1) ?? '?'} km away'),
                                      if (bus.schedule != null)
                                        Text('Seats: ${bus.schedule!.availableSeats}/${bus.schedule!.totalSeats} available'),
                                    ],
                                  ),
                                  trailing: const Icon(Icons.arrow_forward_ios),
                                  onTap: () => _showBusDetails(bus),
                                ),
                              );
                            },
                          );
                        },
                      ),
                    ),
                  ],
                ),
    );
  }
}