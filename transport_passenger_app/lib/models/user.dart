class User {
  final int id;
  final String email;
  final String role;
  final String? firstName;
  final String? lastName;

  User({
    required this.id,
    required this.email,
    required this.role,
    this.firstName,
    this.lastName,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'],
      role: json['role'],
      firstName: json['first_name'],
      lastName: json['last_name'],
    );
  }

  String get displayName {
    if (firstName != null && lastName != null) {
      return '$firstName $lastName';
    }
    return email;
  }
}
