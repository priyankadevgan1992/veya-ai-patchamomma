import 'dart:convert';
import 'package:http/http.dart' as http;

class VeyaApiService {
  static const String baseUrl = "http://localhost:8080/api";

  static Future<Map<String, dynamic>> fetchSession(String email) async {
    final response = await http.post(
      Uri.parse("$baseUrl/auth/session"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"email": email}),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception("Failed to load session");
  }

  static Future<Map<String, dynamic>> fetchHome(String uuid) async {
    final response = await http.get(Uri.parse("$baseUrl/home?uuid=$uuid"));
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception("Failed to load home");
  }

  static Future<Map<String, dynamic>> fetchInsights(String uuid) async {
    final response = await http.get(Uri.parse("$baseUrl/insights?uuid=$uuid"));
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception("Failed to load insights");
  }

  static Future<Map<String, dynamic>> deriveMetric(String uuid, String metricId) async {
    final response = await http.post(
      Uri.parse("$baseUrl/insights/derive"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"uuid": uuid, "metric_id": metricId}),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception("Failed to derive metric");
  }

  static Future<Map<String, dynamic>> fetchTomorrowPlan(String uuid) async {
    final response = await http.get(Uri.parse("$baseUrl/planning/tomorrow?uuid=$uuid"));
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception("Failed to load planning");
  }

  static Future<Map<String, dynamic>> submitFeasibility(String uuid, bool feasible, {String? comment, int? itemNum}) async {
    final response = await http.post(
      Uri.parse("$baseUrl/planning/feasibility"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "uuid": uuid,
        "feasible": feasible,
        "comment": comment,
        "item_num": itemNum
      }),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception("Failed to submit feasibility");
  }

  static Future<Map<String, dynamic>> sendChatMessage(String uuid, String message) async {
    final response = await http.post(
      Uri.parse("$baseUrl/chat"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"uuid": uuid, "message": message}),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception("Failed to send message");
  }
}
