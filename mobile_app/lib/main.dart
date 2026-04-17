import 'package:flutter/material.dart'; // Базовый Flutter UI
import 'package:flutter_localizations/flutter_localizations.dart'; // Системная локализация Flutter

import 'core/app_colors.dart'; // Централизованная палитра приложения
import 'core/app_language_controller.dart'; // Управление текущим языком интерфейса
import 'generated/app_localizations.dart'; // Сгенерированные локализованные строки
import 'screens/upload_screen.dart'; // Главный экран приложения

void main() {
  // Точка входа Flutter-приложения.
  // Именно отсюда запускается весь клиентский интерфейс.
  runApp(const MyApp());
}

/// Корневой виджет приложения.
///
/// Здесь настраиваются:
/// - тема,
/// - локализация,
/// - список поддерживаемых языков,
/// - стартовый экран.
class MyApp extends StatefulWidget {
  const MyApp({super.key});

  /// Позволяет дочерним экранам получить доступ к состоянию MyApp.
  ///
  /// Это нужно, чтобы из любого экрана можно было переключить язык
  /// без отдельного глобального state management на текущем этапе.
  static _MyAppState of(BuildContext context) {
    final state = context.findAncestorStateOfType<_MyAppState>();

    assert(
      state != null,
      'MyApp.of() was called with a context that does not contain MyApp.',
    );

    return state!;
  }

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  /// Контроллер языка приложения.
  ///
  /// Он хранит текущую локаль и уведомляет интерфейс при изменении языка.
  final AppLanguageController languageController = AppLanguageController();

  @override
  void initState() {
    super.initState();

    // Подписываемся на изменения языка,
    // чтобы MaterialApp автоматически перестраивался
    // с новой локалью.
    languageController.addListener(_onLanguageChanged);
  }

  @override
  void dispose() {
    // Корректно снимаем подписку и освобождаем ресурсы контроллера.
    languageController.removeListener(_onLanguageChanged);
    languageController.dispose();
    super.dispose();
  }

  /// Вызывается, когда контроллер языка сообщает об изменении локали.
  ///
  /// setState здесь нужен, чтобы корневой MaterialApp
  /// пересобрался с новым языком.
  void _onLanguageChanged() {
    setState(() {});
  }

  /// Публичный метод для смены языка приложения.
  ///
  /// Например:
  /// - ru
  /// - en
  void changeLanguage(String code) {
    languageController.setLanguageCode(code);
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      // Убираем debug-баннер в правом верхнем углу.
      debugShowCheckedModeBanner: false,

      // Текущая активная локаль приложения.
      locale: languageController.locale,

      // Делегаты локализации:
      // - AppLocalizations.delegate — строки нашего приложения
      // - остальные delegate — встроенные переводы Flutter-компонентов
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],

      // Список языков интерфейса, которые поддерживает приложение.
      supportedLocales: const [
        Locale('ru'),
        Locale('en'),
      ],

      // Название приложения берётся из локализации,
      // чтобы title тоже менялся вместе с языком.
      onGenerateTitle: (context) => AppLocalizations.of(context)!.appTitle,

      // Базовая тема приложения.
      theme: ThemeData(
        scaffoldBackgroundColor: AppColors.background,
        colorScheme: ColorScheme.fromSeed(
          seedColor: AppColors.primary,
          primary: AppColors.primary,
        ),
        useMaterial3: true,
      ),

      // Стартовый экран приложения.
      home: const UploadScreen(),
    );
  }
}