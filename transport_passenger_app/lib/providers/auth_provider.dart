import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
import '../models/user.dart';

class AuthProvider extends ChangeNotifier {
  User? _user;
  bool _isLoading = false;

  User? get user => _user;
  bool get isAuthenticated => _user != null;
  bool get isLoading => _isLoading;

  Future<void> checkAuthStatus() async {
    final prefs = await SharedPreferences.getInstance();
    final email = prefs.getString('user_email');
    final role = prefs.getString('user_role');
    final firstName = prefs.getString('user_first_name');
    final lastName = prefs.getString('user_last_name');
    
    if (email != null && role != null) {
      _user = User(
        id: 1, 
        email: email, 
        role: role,
        firstName: firstName,
        lastName: lastName,
      );
      notifyListeners();
    }
  }

  Future<String?> login(String email, String password) async {
    _isLoading = true;
    notifyListeners();

    try {
      final result = await ApiService.login(email, password);
      
      if (result['success'] == true) {
        final userData = result['user'];
        _user = User(
          id: userData['id'] ?? 1,
          email: userData['email'],
          role: userData['role'],
          firstName: userData['first_name'],
          lastName: userData['last_name'],
        );

        // Save to preferences
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('user_email', _user!.email);
        await prefs.setString('user_role', _user!.role);
        if (_user!.firstName != null) {
          await prefs.setString('user_first_name', _user!.firstName!);
        }
        if (_user!.lastName != null) {
          await prefs.setString('user_last_name', _user!.lastName!);
        }

        _isLoading = false;
        notifyListeners();
        return null; // Success
      } else {
        _isLoading = false;
        notifyListeners();
        return result['error'] ?? 'Login failed';
      }
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      return 'Network error: $e';
    }
  }

  // NEW SIGNUP METHOD
  Future<String?> signup({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
  }) async {
    _isLoading = true;
    notifyListeners();

    try {
      final result = await ApiService.signup(
        email: email,
        password: password,
        firstName: firstName,
        lastName: lastName,
      );
      
      if (result['success'] == true) {
        // Auto-login after successful signup
        final loginError = await login(email, password);
        _isLoading = false;
        notifyListeners();
        return loginError;
      } else {
        _isLoading = false;
        notifyListeners();
        return result['error'] ?? 'Signup failed';
      }
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      return 'Network error: $e';
    }
  }

  Future<void> logout() async {
  _user = null;
  ApiService.clearSession(); // Add this line
  final prefs = await SharedPreferences.getInstance();
  await prefs.clear();
  notifyListeners();
}

  void debugAuthStatus() {
  print('DEBUG AUTH: User authenticated: $isAuthenticated');
  print('DEBUG AUTH: User: ${_user?.email}');
  print('DEBUG AUTH: User role: ${_user?.role}');
}
}


