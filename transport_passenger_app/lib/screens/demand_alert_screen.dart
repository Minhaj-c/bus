import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/bus.dart';

class DemandAlertScreen extends StatefulWidget {
  const DemandAlertScreen({super.key});

  @override
  State<DemandAlertScreen> createState() => _DemandAlertScreenState();
}

class _DemandAlertScreenState extends State<DemandAlertScreen> {
  final _formKey = GlobalKey<FormState>();
  final _peopleController = TextEditingController(text: '1');
  int? _selectedStopId;
  List<BusStop> _stops = [];
  bool _isLoading = false;
  bool _isLoadingStops = true;

  @override
  void initState() {
    super.initState();
    _loadStops();
  }

  @override
  void dispose() {
    _peopleController.dispose();
    super.dispose();
  }

  Future<void> _loadStops() async {
    setState(() => _isLoadingStops = true);
    
    try {
      final routes = await ApiService.getRoutes();
      final allStops = <BusStop>[];
      
      for (final route in routes) {
        allStops.addAll(route.stops);
      }
      
      setState(() {
        _stops = allStops;
        _isLoadingStops = false;
      });
    } catch (e) {
      setState(() => _isLoadingStops = false);
      _showSnackBar('Failed to load stops: $e', Colors.red);
    }
  }

  Future<void> _submitDemandAlert() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    final data = {
      'stop': _selectedStopId,
      'number_of_people': int.parse(_peopleController.text),
    };

    try {
      final success = await ApiService.submitDemandAlert(data);
      
      if (success) {
        _showSnackBar('Demand alert submitted successfully!', Colors.green);
        _formKey.currentState!.reset();
        setState(() => _selectedStopId = null);
        _peopleController.text = '1';
      } else {
        _showSnackBar('Failed to submit demand alert', Colors.red);
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
        title: const Text('Report Passenger Demand'),
        backgroundColor: Colors.red,
        foregroundColor: Colors.white,
      ),
      body: _isLoadingStops
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
                                Icon(Icons.report_problem, color: Colors.orange),
                                SizedBox(width: 8),
                                Text(
                                  'Report High Demand',
                                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            const Text(
                              'Help improve bus services by reporting when there are many '
                              'passengers waiting at a stop. Include yourself in the count.',
                              style: TextStyle(color: Colors.grey),
                            ),
                          ],
                        ),
                      ),
                    ),

                    const SizedBox(height: 20),

                    const Text(
                      'Select Bus Stop',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    DropdownButtonFormField<int>(
                      value: _selectedStopId,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        hintText: 'Choose a bus stop',
                        prefixIcon: Icon(Icons.location_on),
                      ),
                      items: _stops.map((stop) {
                        return DropdownMenuItem<int>(
                          value: stop.id,
                          child: Text('${stop.name} (Stop ${stop.sequence})'),
                        );
                      }).toList(),
                      onChanged: (value) => setState(() => _selectedStopId = value),
                      validator: (value) => value == null ? 'Please select a stop' : null,
                    ),

                    const SizedBox(height: 20),

                    const Text(
                      'Number of People Waiting',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _peopleController,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        hintText: 'Include yourself in the count',
                        prefixIcon: Icon(Icons.people),
                        suffixText: 'people',
                      ),
                      keyboardType: TextInputType.number,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter number of people';
                        }
                        final number = int.tryParse(value);
                        if (number == null || number < 1) {
                          return 'Please enter a valid number (minimum 1)';
                        }
                        if (number > 100) {
                          return 'Number seems too high (maximum 100)';
                        }
                        return null;
                      },
                    ),

                    const SizedBox(height: 30),

                    SizedBox(
                      width: double.infinity,
                      height: 50,
                      child: ElevatedButton.icon(
                        onPressed: _isLoading ? null : _submitDemandAlert,
                        icon: _isLoading 
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                              )
                            : const Icon(Icons.send),
                        label: Text(_isLoading ? 'Submitting...' : 'Submit Demand Alert'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.red,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ),

                    const SizedBox(height: 20),

                    Card(
                      color: Colors.blue[50],
                      child: const Padding(
                        padding: EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(Icons.info, color: Colors.blue),
                                SizedBox(width: 8),
                                Text(
                                  'How it helps',
                                  style: TextStyle(fontWeight: FontWeight.bold),
                                ),
                              ],
                            ),
                            SizedBox(height: 8),
                            Text(
                              '• Transport controllers get notified immediately\n'
                              '• Additional buses may be dispatched to high-demand stops\n'
                              '• Your report expires after 1 hour automatically\n'
                              '• Helps improve overall service planning',
                              style: TextStyle(fontSize: 14),
                            ),
                          ],
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
