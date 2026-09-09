import 'package:flutter/material.dart';
import '../services/api_service.dart';

class PlanningScreen extends StatefulWidget {
  final String uuid;
  const PlanningScreen({super.key, required this.uuid});

  @override
  State<PlanningScreen> createState() => _PlanningScreenState();
}

class _PlanningScreenState extends State<PlanningScreen> {
  Map<String, dynamic>? planningData;

  @override
  void initState() {
    super.initState();
    _loadPlanning();
  }

  Future<void> _loadPlanning() async {
    final data = await VeyaApiService.fetchTomorrowPlan(widget.uuid);
    setState(() {
      planningData = data;
    });
  }

  Future<void> _submitFeasibility(bool isFeasible) async {
    final res = await VeyaApiService.submitFeasibility(widget.uuid, isFeasible);
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(res["reply"])),
      );
      _loadPlanning();
    }
  }

  @override
  Widget build(BuildContext context) {
    if (planningData == null) {
      return const Center(child: CircularProgressIndicator());
    }

    final items = planningData!["action_items"] as List;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text("Tomorrow's Plan", style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text(planningData!["intro"], style: const TextStyle(fontSize: 12, color: Colors.grey)),
          const SizedBox(height: 16),

          // CONVERSATIONAL 1, 2, 3... ACTION LIST WITH REASONS
          Card(
            color: const Color(0xFFFBFBFD),
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20),
              side: const BorderSide(color: Color(0xFFE5E5EA)),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: items.map((item) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          "${item['num']}. ${item['action']}",
                          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 4),
                        Padding(
                          padding: const EdgeInsets.only(left: 12.0),
                          child: Text(
                            "👉 Reason: ${item['reason']}",
                            style: const TextStyle(fontSize: 12, color: Color(0xFFD97706), height: 1.4),
                          ),
                        )
                      ],
                    ),
                  );
                }).toList(),
              ),
            ),
          ),
          const SizedBox(height: 20),

          // FEASIBILITY CARD
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFFFAF7F2),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Column(
              children: [
                const Text("Is this plan Feasible for you?", style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    OutlinedButton(
                      style: OutlinedButton.styleFrom(
                        side: const BorderSide(color: Color(0xFF34C759), width: 2),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                      ),
                      onPressed: () => _submitFeasibility(true),
                      child: const Text("🟢 Feasible", style: TextStyle(color: Color(0xFF34C759), fontWeight: FontWeight.bold)),
                    ),
                    const SizedBox(width: 10),
                    OutlinedButton(
                      style: OutlinedButton.styleFrom(
                        side: const BorderSide(color: Color(0xFFD97706), width: 2),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                      ),
                      onPressed: () => _submitFeasibility(false),
                      child: const Text("🟠 Not Feasible", style: TextStyle(color: Color(0xFFD97706), fontWeight: FontWeight.bold)),
                    )
                  ],
                )
              ],
            ),
          )
        ],
      ),
    );
  }
}
