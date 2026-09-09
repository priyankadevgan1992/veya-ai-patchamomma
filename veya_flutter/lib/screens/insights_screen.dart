import 'package:flutter/material.dart';
import '../services/api_service.dart';

class InsightsScreen extends StatefulWidget {
  final String uuid;
  const InsightsScreen({super.key, required this.uuid});

  @override
  State<InsightsScreen> createState() => _InsightsScreenState();
}

class _InsightsScreenState extends State<InsightsScreen> {
  Map<String, dynamic>? insightsData;
  Map<String, dynamic>? derivationData;
  bool isDrawerOpen = false;

  @override
  void initState() {
    super.initState();
    _loadInsights();
  }

  Future<void> _loadInsights() async {
    final data = await VeyaApiService.fetchInsights(widget.uuid);
    setState(() {
      insightsData = data;
    });
  }

  Future<void> _openDerivation(String metricId) async {
    final data = await VeyaApiService.deriveMetric(widget.uuid, metricId);
    setState(() {
      derivationData = data;
      isDrawerOpen = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (insightsData == null) {
      return const Center(child: CircularProgressIndicator());
    }

    final metrics = insightsData!["metrics"] as List;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text("Living Twin Insights", style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          const Text("Tap any metric to view its 5–10 line derivation explanation.", style: TextStyle(fontSize: 12, color: Colors.grey)),
          const SizedBox(height: 16),

          ...metrics.map((m) {
            return GestureDetector(
              onTap: () => _openDerivation(m["id"]),
              child: Card(
                color: const Color(0xFFFBFBFD),
                elevation: 0,
                margin: const EdgeInsets.only(bottom: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(18),
                  side: const BorderSide(color: Color(0xFFE5E5EA)),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(m["title"], style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.grey)),
                          Text(m["score"], style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text("Status: ${m['status']}", style: const TextStyle(fontSize: 12, color: Colors.grey)),
                          Text(m["trend"], style: const TextStyle(fontSize: 12, color: Colors.grey)),
                        ],
                      )
                    ],
                  ),
                ),
              ),
            );
          }),

          // DERIVATION CHAT DRAWER (5-10 Line Explanation)
          if (isDrawerOpen && derivationData != null)
            Card(
              color: const Color(0xFFFBFBFD),
              elevation: 0,
              margin: const EdgeInsets.only(top: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
                side: const BorderSide(color: Color(0xFFE5E5EA), width: 1.5),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(derivationData!["metric_title"], style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                        IconButton(
                          icon: const Icon(Icons.close, size: 18),
                          onPressed: () => setState(() => isDrawerOpen = false),
                        )
                      ],
                    ),
                    const SizedBox(height: 12),
                    ...(derivationData!["explanation_lines"] as List).map(
                      (line) => Padding(
                        padding: const EdgeInsets.only(bottom: 6.0),
                        child: Text(line, style: const TextStyle(fontSize: 13, height: 1.5, color: Color(0xFF3A3A3C))),
                      ),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      derivationData!["follow_up_prompt"],
                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
                    )
                  ],
                ),
              ),
            )
        ],
      ),
    );
  }
}
