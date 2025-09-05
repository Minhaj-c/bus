import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/bus.dart';

class PreInformScreen extends StatefulWidget {
  const PreInformScreen({Key? key}) : super(key: key);

  @override
  State<PreInformScreen> createState() => _PreInformScreenState();
}

class _PreInformScreenState extends State<PreInformScreen> {
  final _formKey = GlobalKey<FormState>();
  final _passengerCountController = TextEditingController(text: '1');
  
  List<BusRoute> _routes = [];
  List<BusStop> _stops = [];
  BusRoute? _selectedRoute;
  BusStop? _selectedStop;
  DateTime? _selectedDate;
  TimeOfDay? _selectedTime;
  bool _isLoading = false;
  bool _isLoadingRoutes = true;

  @override
  void initState() {
    super.initState();
    _loadRoutes();
    _selectedDate = DateTime.now();
    _selectedTime = TimeOfDay.now();
  }

  @override
  void dispose() {
    _passengerCountController.dispose();
    super.dispose();
  }

  Future<void> _loadRoutes() async {
    setState(() => _isLoadingRoutes = true);
    
    try {
      final routes = await ApiService.getRoutes();
      setState(() {
        _routes = routes;
        _isLoadingRoutes = false;
      });
    } catch (e) {
      setState(() => _isLoadingRoutes = false);
      _showSnackBar('Failed to load routes: $e', Colors.red);
    }
  }

  void _onRouteChanged(BusRoute? route) {
    setState(() {
      _selectedRoute = route;
      _stops = route?.stops ?? [];
      _selectedStop = null;
    });
  }

  Future<void> _selectDate() async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate ?? DateTime.now(),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 30)),
    );
    if (picked != null) {
      setState(() => _selectedDate = picked);
    }
  }

  Future<void> _selectTime() async {
    final TimeOfDay? picked = await showTimePicker(
      context: context,
      initialTime: _selectedTime ?? TimeOfDay.now(),
    );
    if (picked != null) {
      setState(() => _selectedTime = picked);
    }
  }

  Future<void> _submitPreInform() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    final data = {
      'route': _selectedRoute?.id,
      'date_of_travel': '${_selectedDate!.year}-${_selectedDate!.month.toString().padLeft(2, '0')}-${_selectedDate!.day.toString().padLeft(2, '0')}',
      'desired_time': '${_selectedTime!.hour.toString().padLeft(2, '0')}:${_selectedTime!.minute.toString().padLeft(2, '0')}:00',
      'boarding_stop': _selectedStop?.id,
      'passenger_count': int.parse(_passengerCountController.text),
    };

    try {
      final success = await ApiService.submitPreInform(data);
      
      if (success) {
        _showSnackBar('Pre-inform submitted successfully!', Colors.green);
        _formKey.currentState!.reset();
        setState(() {
          _selectedRoute = null;
          _selectedStop = null;
          _stops = [];
        });
        _passengerCountController.text = '1';
      } else {
        _showSnackBar('Failed to submit pre-inform', Colors.red);
      }
    } catch (e) {
      _showSnackBar('Network error: $e', Colors.red);
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _showSnackBar(String message, Color color) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message), backgroundColor: color),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Pre-Inform Journey'),
        backgroundColor: Colors.orange,
        foregroundColor: Colors.white,
      ),
      body: _isLoadingRoutes
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Row(
                              children: [
                                Icon(Icons.schedule, color: Colors.orange),
                                SizedBox(width: 8),
                                Text(
                                  'Pre-Inform Your Journey',
                                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            const Text(
                              'Let us know about your travel plans in advance to help improve service planning.',
                              style: TextStyle(color: Colors.grey),
                            ),
                          ],
                        ),
                      ),
                    ),

                    const SizedBox(height: 20),

                    const Text('Select Route', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    DropdownButtonFormField<BusRoute>(
                      value: _selectedRoute,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        hintText: 'Choose a route',
                        prefixIcon: Icon(Icons.route),
                      ),
                      items: _routes.map((route) {
                        return DropdownMenuItem<BusRoute>(
                          value: route,
                          child: Text('${route.number}: ${route.name}'),
                        );
                      }).toList(),
                      onChanged: _onRouteChanged,
                      validator: (value) => value == null ? 'Please select a route' : null,
                    ),

                    const SizedBox(height: 20),

                    if (_stops.isNotEmpty) ...[
                      const Text('Boarding Stop', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 8),
                      DropdownButtonFormField<BusStop>(
                        value: _selectedStop,
                        decoration: const InputDecoration(
                          border: OutlineInputBorder(),
                          hintText: 'Choose boarding stop',
                          prefixIcon: Icon(Icons.location_on),
                        ),
                        items: _stops.map((stop) {
                          return DropdownMenuItem<BusStop>(
                            value: stop,
                            child: Text('${stop.sequence}. ${stop.name}'),
                          );
                        }).toList(),
                        onChanged: (stop) => setState(() => _selectedStop = stop),
                        validator: (value) => value == null ? 'Please select a stop' : null,
                      ),
                      const SizedBox(height: 20),
                    ],

                    Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('Travel Date', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                              const SizedBox(height: 8),
                              InkWell(
                                onTap: _selectDate,
                                child: Container(
                                  padding: const EdgeInsets.all(16),
                                  decoration: BoxDecoration(
                                    border: Border.all(color: Colors.grey),
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Row(
                                    children: [
                                      const Icon(Icons.calendar_today),
                                      const SizedBox(width: 8),
                                      Text(_selectedDate != null 
                                          ? '${_selectedDate!.day}/${_selectedDate!.month}/${_selectedDate!.year}'
                                          : 'Select Date'),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('Preferred Time', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                              const SizedBox(height: 8),
                              InkWell(
                                onTap: _selectTime,
                                child: Container(
                                  padding: const EdgeInsets.all(16),
                                  decoration: BoxDecoration(
                                    border: Border.all(color: Colors.grey),
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Row(
                                    children: [
                                      const Icon(Icons.access_time),
                                      const SizedBox(width: 8),
                                      Text(_selectedTime != null 
                                          ? '${_selectedTime!.hour}:${_selectedTime!.minute.toString().padLeft(2, '0')}'
                                          : 'Select Time'),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 20),

                    const Text('Number of Passengers', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _passengerCountController,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        hintText: 'Number of passengers',
                        prefixIcon: Icon(Icons.people),
                      ),
                      keyboardType: TextInputType.number,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter number of passengers';
                        }
                        final number = int.tryParse(value);
                        if (number == null || number < 1) {
                          return 'Please enter a valid number (minimum 1)';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 30),

                    SizedBox(
                      width: double.infinity,
                      height: 50,
                      child: ElevatedButton.icon(
                        onPressed: _isLoading ? null : _submitPreInform,
                        icon: _isLoading 
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                              )
                            : const Icon(Icons.send),
                        label: Text(_isLoading ? 'Submitting...' : 'Submit Pre-Inform'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.orange,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
    );
  }
}