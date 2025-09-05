import 'package:flutter/material.dart';
import '../models/bus.dart';
import '../services/api_service.dart';

class BusProvider extends ChangeNotifier {
  List<Bus> _nearbyBuses = [];
  bool _isLoading = false;
  String? _error;

  List<Bus> get nearbyBuses => _nearbyBuses;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> fetchNearbyBuses(double latitude, double longitude) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final result = await ApiService.getNearbyBuses(latitude, longitude);
      
      if (result['buses'] != null) {
        _nearbyBuses = (result['buses'] as List)
            .map((bus) => Bus.fromJson(bus))
            .toList();
      } else {
        _error = result['error'] ?? 'Failed to fetch buses';
      }
    } catch (e) {
      _error = 'Network error: $e';
    }

    _isLoading = false;
    notifyListeners();
  }

  void clearBuses() {
    _nearbyBuses.clear();
    _error = null;
    notifyListeners();
  }
}