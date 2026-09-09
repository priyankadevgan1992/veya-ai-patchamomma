import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'insights_screen.dart';
import 'planning_screen.dart';

class MainLayoutScreen extends StatefulWidget {
  const MainLayoutScreen({super.key});

  @override
  State<MainLayoutScreen> createState() => _MainLayoutScreenState();
}

class _MainLayoutScreenState extends State<MainLayoutScreen> {
  int _selectedIndex = 1; // Default to Home
  String currentEmail = "meera@gmail.com";
  String currentUUID = "v_e95c19cdd20c";
  Map<String, dynamic>? homeData;

  @override
  void initState() {
    super.initState();
    _loadHomeData();
  }

  Future<void> _loadHomeData() async {
    try {
      final session = await VeyaApiService.fetchSession(currentEmail);
      currentUUID = session["internal_uuid"];
      final data = await VeyaApiService.fetchHome(currentUUID);
      setState(() {
        homeData = data;
      });
    } catch (e) {
      debugPrint("Error loading home: $e");
    }
  }

  void _openVoiceModal() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        TextEditingController controller = TextEditingController();
        return Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(context).viewInsets.bottom + 20,
            left: 20,
            right: 20,
            top: 20,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                "Talk to Veya",
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.graphic_eq, color: Color(0xFF34C759), size: 30),
                  SizedBox(width: 8),
                  Text("Listening...", style: TextStyle(color: Colors.grey)),
                ],
              ),
              const SizedBox(height: 16),
              TextField(
                controller: controller,
                decoration: const InputDecoration(
                  hintText: "Or type your message here...",
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.all(Radius.circular(16)),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF1D1D1F),
                  foregroundColor: Colors.white,
                  minimumSize: const Size.fromHeight(48),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
                onPressed: () async {
                  if (controller.text.isNotEmpty) {
                    final res = await VeyaApiService.sendChatMessage(
                      currentUUID,
                      controller.text,
                    );
                    if (context.mounted) {
                      Navigator.pop(context);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text("Veya: ${res['reply']}")),
                      );
                    }
                  }
                },
                child: const Text("Send Message"),
              )
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    List<Widget> screens = [
      InsightsScreen(uuid: currentUUID),
      _buildHomeScreen(),
      PlanningScreen(uuid: currentUUID),
    ];

    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFFFAF7F2),
        elevation: 0,
        title: const Text(
          "VeyaAI",
          style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF1D1D1F)),
        ),
        actions: [
          // Persistent Top-Right Voice Button
          Padding(
            padding: const EdgeInsets.only(right: 16.0),
            child: ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFF0EAE1),
                foregroundColor: const Color(0xFF1D1D1F),
                elevation: 0,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(18),
                ),
              ),
              onPressed: _openVoiceModal,
              icon: const Icon(Icons.mic, color: Color(0xFF34C759), size: 18),
              label: const Text("Voice"),
            ),
          )
        ],
      ),
      body: screens[_selectedIndex],

      // EXACT MATCH BOTTOM NAVIGATION BAR
      bottomNavigationBar: Container(
        height: 76,
        decoration: const BoxDecoration(
          color: Colors.white,
          border: Border(top: BorderSide(color: Color(0xFFE5E5EA))),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            // LEFT TAB: INSIGHTS
            IconButton(
              icon: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.bar_chart,
                    color: _selectedIndex == 0 ? const Color(0xFF1D1D1F) : Colors.grey,
                  ),
                  Text(
                    "Insights",
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: _selectedIndex == 0 ? const Color(0xFF1D1D1F) : Colors.grey,
                    ),
                  )
                ],
              ),
              onPressed: () => setState(() => _selectedIndex = 0),
            ),

            // CENTER ELEVATED DARK CIRCLE: TALK TO VEYA
            GestureDetector(
              onTap: _openVoiceModal,
              child: Container(
                width: 52,
                height: 52,
                decoration: const BoxDecoration(
                  color: Color(0xFF1C1C1E),
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(color: Colors.black12, blurRadius: 8, offset: Offset(0, 4))
                  ],
                ),
                child: const Icon(Icons.chat_bubble_outline, color: Color(0xFFE8DDF2), size: 22),
              ),
            ),

            // RIGHT TAB: PLANNING
            IconButton(
              icon: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.calendar_today_outlined,
                    color: _selectedIndex == 2 ? const Color(0xFF1D1D1F) : Colors.grey,
                  ),
                  Text(
                    "Planning",
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: _selectedIndex == 2 ? const Color(0xFF1D1D1F) : Colors.grey,
                    ),
                  )
                ],
              ),
              onPressed: () => setState(() => _selectedIndex = 2),
            ),
          ],
        ),
      ),
    );
  }

  // ULTRA-LIGHT HOME PAGE (Zero planning widgets)
  Widget _buildHomeScreen() {
    if (homeData == null) {
      return const Center(child: CircularProgressIndicator());
    }

    return Padding(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            homeData!["greeting_title"],
            style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          Card(
            color: const Color(0xFFFBFBFD),
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20),
              side: const BorderSide(color: Color(0xFFE5E5EA)),
            ),
            child: Padding(
              padding: const EdgeInsets.all(18.0),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const CircleAvatar(
                    backgroundColor: Color(0xFFE8DDF2),
                    child: Text("v", style: TextStyle(fontWeight: FontWeight.bold)),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text("Veya", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                        const SizedBox(height: 6),
                        Text(
                          homeData!["greeting_bubble"],
                          style: const TextStyle(fontSize: 14, color: Color(0xFF3A3A3C), height: 1.4),
                        ),
                        const SizedBox(height: 14),
                        ...List.generate(
                          (homeData!["quick_chips"] as List).length,
                          (index) {
                            final chip = homeData!["quick_chips"][index];
                            return Padding(
                              padding: const EdgeInsets.only(bottom: 8.0),
                              child: OutlinedButton(
                                style: OutlinedButton.styleFrom(
                                  side: BorderSide(
                                    color: chip["type"] == "success"
                                        ? const Color(0xFF34C759)
                                        : const Color(0xFFD97706),
                                  ),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(16),
                                  ),
                                ),
                                onPressed: () {
                                  _openVoiceModal();
                                },
                                child: Text(
                                  chip["text"],
                                  style: TextStyle(
                                    color: chip["type"] == "success"
                                        ? const Color(0xFF34C759)
                                        : const Color(0xFFD97706),
                                  ),
                                ),
                              ),
                            );
                          },
                        )
                      ],
                    ),
                  )
                ],
              ),
            ),
          ),
          const SizedBox(height: 30),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFFFAF7F2),
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("Ultra-Light Companion Stream", style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: Colors.grey)),
                SizedBox(height: 4),
                Text(
                  "Zero clutter on home. Planning lives on the right tab, Insights on the left.",
                  style: TextStyle(fontSize: 12, color: Colors.grey),
                )
              ],
            ),
          )
        ],
      ),
    );
  }
}
