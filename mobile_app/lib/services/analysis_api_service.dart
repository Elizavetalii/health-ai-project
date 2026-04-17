import 'dart:io'; // Работа с локальным файлом анализа

import 'package:dio/dio.dart'; // HTTP-клиент для запросов к backend

import '../models/analysis_result.dart'; // Типизированная модель результата анализа

/// Сервис для взаимодействия с backend.
///
/// Этот слой отвечает только за сетевую логику:
/// - принимает файл и параметры,
/// - отправляет запрос,
/// - получает JSON,
/// - преобразует его в удобную модель.
///
/// Экран не должен напрямую работать с низкоуровневым HTTP.
class AnalysisApiService {
  /// Endpoint backend для анализа файла.
  ///
  /// Для desktop/iOS simulator обычно подходит 127.0.0.1.
  /// Для Android emulator обычно используется 10.0.2.2.
  static const String apiUrl = 'http://127.0.0.1:8000/analyze';

  // Для Android-эмулятора:
  // static const String apiUrl = 'http://10.0.2.2:8000/analyze';

  /// HTTP-клиент.
  final Dio _dio = Dio();

  /// Отправляет файл анализа на backend.
  ///
  /// На вход:
  /// - [file] — локальный файл;
  /// - [fileName] — имя файла для backend;
  /// - [language] — код языка (ru, en);
  /// - [userComment] — дополнительный комментарий пользователя.
  ///
  /// На выход:
  /// типизированный объект [AnalysisApiResponse].
  Future<AnalysisApiResponse> analyzeFile({
    required File file,
    required String fileName,
    required String language,
    required String userComment,
  }) async {
    // Формируем multipart/form-data:
    // файл + параметры формы.
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(
        file.path,
        filename: fileName,
      ),
      'language': language,
      'user_comment': userComment,
    });

    // Отправляем POST-запрос на backend.
    final response = await _dio.post(
      apiUrl,
      data: formData,
    );

    // Упрощаем доступ к данным ответа.
    final data = response.data;

    // Если backend сообщил об успешной обработке.
    if (data['success'] == true) {
      return AnalysisApiResponse(
        success: true,

        // Преобразуем JSON в типизированную модель результата.
        analysisResult: AnalysisResult.fromJson(
          Map<String, dynamic>.from(data['analysis_result']),
        ),

        // Meta-данные могут отсутствовать, поэтому проверяем тип.
        meta: data['meta'] is Map
            ? Map<String, dynamic>.from(data['meta'])
            : {},

        message: data['message']?.toString(),
      );
    }

    // Если backend вернул ошибку, всё равно отдаём
    // единый нормализованный объект ответа.
    return AnalysisApiResponse(
      success: false,
      analysisResult: null,
      meta: const {},
      message: data['message']?.toString() ?? 'Unknown error',
    );
  }
}

/// Нормализованная модель ответа API.
///
/// Нужна, чтобы UI не работал напрямую с сырым response.data.
class AnalysisApiResponse {
  /// Признак успешности запроса.
  final bool success;

  /// Типизированный результат анализа.
  ///
  /// Будет null, если запрос завершился неуспешно.
  final AnalysisResult? analysisResult;

  /// Дополнительные служебные данные.
  ///
  /// Например:
  /// - источник обработки,
  /// - тип файла,
  /// - был ли учтён комментарий пользователя.
  final Map<String, dynamic> meta;

  /// Сообщение backend.
  ///
  /// Может использоваться для ошибок или статуса.
  final String? message;

  AnalysisApiResponse({
    required this.success,
    required this.analysisResult,
    required this.meta,
    required this.message,
  });
}