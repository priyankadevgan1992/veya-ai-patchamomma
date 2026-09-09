import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:dynamic_color/dynamic_color.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const VeyaApp());
}

class VeyaApp extends StatelessWidget {
  const VeyaApp({super.key});

  @override
  Widget build(BuildContext context) {
    // Dynamic System Theme matching (Material You / iOS system color tint)
    return DynamicColorBuilder(
      builder: (ColorScheme? lightDynamic, ColorScheme? darkDynamic) {
        ColorScheme lightScheme = lightDynamic ??
            ColorScheme.fromSeed(
              seedColor: const Color(0xFF34C759),
              brightness: Brightness.light,
              surface: const Color(0xFFFAF7F2),
              onSurface: const Color(0xFF1D1D1F),
            );

        return MaterialApp(
          title: 'VeyaAI',
          debugShowCheckedModeBanner: false,
          theme: ThemeData(
            useMaterial3: true,
            colorScheme: lightScheme,
            scaffoldBackgroundColor: const Color(0xFFFAF7F2),
            textTheme: GoogleFonts.plusJakartaSansTextTheme(
              Theme.of(context).textTheme,
            ),
          ),
          home: const MainLayoutScreen(),
        );
      },
    );
  }
}
