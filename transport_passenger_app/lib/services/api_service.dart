import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/bus.dart';

class ApiService {
  static const String baseUrl = 'http://192.168.163.81:3000';
  static String? _cookies;

  static Map<String, String> get headers {
    Map<String, String> headers = {
      'Content-Type': 'application/json',
    };
    
    if (_cookies != null) {
      headers['Cookie'] = _cookies!;
      print('DEBUG: Using cookies: $_cookies');
    }
    
    return headers;
  }

  static void _updateCookies(http.Response response) {
    String? rawCookies = response.headers['set-cookie'];
    if (rawCookies != null) {
      print('DEBUG: Raw cookies received: $rawCookies');
      
      // Parse multiple cookies from set-cookie header
      List<String> cookies = [];
      
      // Extract sessionid
      RegExp sessionRegex = RegExp(r'sessionid=([^;]+)');
      Match? sessionMatch = sessionRegex.firstMatch(rawCookies);
      if (sessionMatch != null) {
        cookies.add('sessionid=${sessionMatch.group(1)}');
      }
      
      // Extract csrftoken
      RegExp csrfRegex = RegExp(r'csrftoken=([^;]+)');
      Match? csrfMatch = csrfRegex.firstMatch(rawCookies);
      if (csrfMatch != null) {
        cookies.add('csrftoken=${csrfMatch.group(1)}');
      }
      
      if (cookies.isNotEmpty) {
        _cookies = cookies.join('; ');
        print('DEBUG: Parsed cookies: $_cookies');
      }
    }
  }

  static Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      print('DEBUG: Login attempt for: $email');
      
      final response = await http.post(
        Uri.parse('$baseUrl/api/login/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );

      print('DEBUG: Login response status: ${response.statusCode}');
      print('DEBUG: Login response headers: ${response.headers}');
      print('DEBUG: Login response body: ${response.body}');

      if (response.body.startsWith('<!DOCTYPE html>')) {
        return {
          'success': false,
          'error': 'Server returned HTML. Check if login endpoint exists.',
        };
      }

      // Update cookies from login response
      _updateCookies(response);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {'success': true, 'user': data['user']};
      } else {
        final data = json.decode(response.body);
        return {'success': false, 'error': data['error'] ?? 'Login failed'};
      }
    } catch (e) {
      print('DEBUG: Login error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> signup({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
  }) async {
    try {
      print('DEBUG: Signup attempt for: $email');
      
      final response = await http.post(
        Uri.parse('$baseUrl/api/signup/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
          'first_name': firstName,
          'last_name': lastName,
          'role': 'passenger',
        }),
      );

      print('DEBUG: Signup response status: ${response.statusCode}');
      print('DEBUG: Signup response body: ${response.body}');

      if (response.body.startsWith('<!DOCTYPE html>')) {
        return {
          'success': false,
          'error': 'Server returned HTML. Check signup endpoint.',
        };
      }

      if (response.statusCode == 201) {
        final data = json.decode(response.body);
        return {'success': true, 'user': data['user']};
      } else {
        final data = json.decode(response.body);
        return {'success': false, 'error': data['error'] ?? 'Signup failed'};
      }
    } catch (e) {
      print('DEBUG: Signup error: $e');
      return {'success': false, 'error': 'Network error: $e'};
    }
  }

  static Future<bool> submitPreInform(Map<String, dynamic> data) async {
    try {
      print('DEBUG: Pre-inform submission');
      print('DEBUG: URL: $baseUrl/api/preinforms/');
      print('DEBUG: Data: $data');
      print('DEBUG: Headers: $headers');
      
      final response = await http.post(
        Uri.parse('$baseUrl/api/preinforms/'),
        headers: headers,
        body: json.encode(data),
      );

      print('DEBUG: Pre-inform response status: ${response.statusCode}');
      print('DEBUG: Pre-inform response body: ${response.body}');
      
      if (response.statusCode == 403) {
        print('DEBUG: Authentication required for pre-inform');
        return false;
      }

      return response.statusCode == 201;
    } catch (e) {
      print('DEBUG: Pre-inform error: $e');
      return false;
    }
  }

  static Future<bool> submitDemandAlert(Map<String, dynamic> data) async {
    try {
      print('DEBUG: Demand alert submission');
      print('DEBUG: URL: $baseUrl/api/demand-alerts/');
      print('DEBUG: Data: $data');
      print('DEBUG: Headers: $headers');
      
      final response = await http.post(
        Uri.parse('$baseUrl/api/demand-alerts/'),
        headers: headers,
        body: json.encode(data),
      );

      print('DEBUG: Demand alert response status: ${response.statusCode}');
      print('DEBUG: Demand alert response body: ${response.body}');
      
      if (response.statusCode == 403) {
        print('DEBUG: Authentication required for demand alert');
        return false;
      }

      return response.statusCode == 201;
    } catch (e) {
      print('DEBUG: Demand alert error: $e');
      return false;
    }
  }

  static Future<Map<String, dynamic>> getNearbyBuses(
    double latitude,
    double longitude, {
    double radius = 5.0,
  }) async {
    try {
      print('DEBUG: Fetching nearby buses');
      print('DEBUG: Location: $latitude, $longitude');
      
      final response = await http.get(
        Uri.parse(
          '$baseUrl/api/buses/nearby/?latitude=$latitude&longitude=$longitude&radius=$radius',
        ),
        headers: headers,
      );

      print('DEBUG: Nearby buses response status: ${response.statusCode}');
      print('DEBUG: Nearby buses response: ${response.body}');

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      return {'buses': [], 'error': 'Failed to fetch buses'};
    } catch (e) {
      print('DEBUG: Nearby buses error: $e');
      return {'buses': [], 'error': 'Network error: $e'};
    }
  }

  static Future<Map<String, dynamic>> getBusDetails(int busId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/buses/$busId/'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
      return {'error': 'Bus not found'};
    } catch (e) {
      return {'error': 'Network error: $e'};
    }
  }

  static Future<List<BusRoute>> getRoutes() async {
    try {
      print('DEBUG: Fetching routes');
      
      final response = await http.get(
        Uri.parse('$baseUrl/api/routes/'),
        headers: headers,
      );

      print('DEBUG: Routes response status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((route) => BusRoute.fromJson(route)).toList();
      }
      return [];
    } catch (e) {
      print('DEBUG: Routes error: $e');
      return [];
    }
  }

  static void clearSession() {
    _cookies = null;
    print('DEBUG: Session cleared');
  }
}