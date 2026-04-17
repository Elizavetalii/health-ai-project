import 'package:flutter/material.dart';

/// Централизованная палитра приложения.
///
/// Такой подход нужен, чтобы:
/// - поддерживать единый стиль,
/// - быстро менять цвета продукта,
/// - не дублировать константы по разным экранам.
class AppColors {
  static const Color primary = Color(0xFF157BC5);
  static const Color secondary = Color(0xFF58C4D6);
  static const Color accent = Color(0xFF0F5DA0);

  static const Color background = Color(0xFFF3F8FC);
  static const Color card = Colors.white;

  static const Color textMain = Color(0xFF1B2A38);
  static const Color textSecondary = Color(0xFF6E7E8E);

  static const Color border = Color(0xFFE2EDF4);

  static const Color success = Color(0xFF2E9E5B);
  static const Color warning = Color(0xFFF0A63A);
  static const Color danger = Color(0xFFD9534F);

  static const Color softBlue = Color(0xFFEAF5FD);
  static const Color softGreen = Color(0xFFEAF8EF);
  static const Color softOrange = Color(0xFFFFF5E8);
  static const Color softRed = Color(0xFFFFEFEF);
}