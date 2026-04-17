import 'package:flutter/material.dart'; // Базовый класс ChangeNotifier и Locale

/// Контроллер текущего языка приложения.
///
/// Нужен для того, чтобы:
/// - централизованно хранить выбранную локаль,
/// - переключать язык интерфейса,
/// - использовать тот же код языка в backend-запросах.
class AppLanguageController extends ChangeNotifier {
  /// Текущая локаль приложения.
  ///
  /// По умолчанию используется русский язык.
  Locale _locale = const Locale('ru');

  /// Публичный доступ к текущей локали.
  Locale get locale => _locale;

  /// Удобный getter для короткого кода языка.
  ///
  /// Например:
  /// - ru
  /// - en
  String get languageCode => _locale.languageCode;

  /// Устанавливает новую локаль.
  ///
  /// Если локаль не изменилась, уведомление не отправляется.
  void setLocale(Locale locale) {
    if (_locale == locale) return;
    _locale = locale;
    notifyListeners();
  }

  /// Упрощённое переключение языка по строковому коду.
  void setLanguageCode(String code) {
    setLocale(Locale(code));
  }
}