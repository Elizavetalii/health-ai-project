import 'dart:io';

import 'package:dio/dio.dart';

import '../models/analysis_result.dart';


class AnalysisApiService {
  static const String apiUrl = 'http://77.222.35.62/analyze';

  final Dio _dio = Dio(
    BaseOptions(
      connectTimeout: const Duration(seconds: 30),
      sendTimeout: const Duration(seconds: 120),
      receiveTimeout: const Duration(minutes: 3),
    ),
  );

  Future<AnalysisApiResponse> analyzeFile({
    required File file,
    required String fileName,
    required String language,
    required String userComment,
  }) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          file.path,
          filename: fileName,
        ),
        'language': language,
        'user_comment': userComment,
      });

      final response = await _dio.post(
        apiUrl,
        data: formData,
      );

      final rawData = response.data;
      final data = rawData is Map
          ? Map<String, dynamic>.from(rawData)
          : <String, dynamic>{};

      if (data['success'] == true) {
        final rawAnalysis = data['analysis_result'];
        final analysisMap = rawAnalysis is Map
            ? Map<String, dynamic>.from(rawAnalysis)
            : <String, dynamic>{};

        final rawMeta = data['meta'];
        final metaMap = rawMeta is Map
            ? Map<String, dynamic>.from(rawMeta)
            : <String, dynamic>{};

        return AnalysisApiResponse(
          success: true,
          analysisResult: AnalysisResult.fromJson(analysisMap),
          meta: metaMap,
          message: data['message']?.toString(),
        );
      }

      return AnalysisApiResponse(
        success: false,
        analysisResult: null,
        meta: const {},
        message: data['message']?.toString() ?? 'Unknown error',
      );
    } on DioException catch (e) {
      return AnalysisApiResponse(
        success: false,
        analysisResult: null,
        meta: const {},
        message: _mapDioError(e),
      );
    } catch (e) {
      return AnalysisApiResponse(
        success: false,
        analysisResult: null,
        meta: const {},
        message: 'Unexpected error: $e',
      );
    }
  }

  String _mapDioError(DioException e) {
    if (e.type == DioExceptionType.connectionTimeout) {
      return 'Connection timeout';
    }
    if (e.type == DioExceptionType.sendTimeout) {
      return 'Send timeout';
    }
    if (e.type == DioExceptionType.receiveTimeout) {
      return 'Receive timeout';
    }
    if (e.type == DioExceptionType.badResponse) {
      return 'Server error: ${e.response?.statusCode}';
    }
    if (e.type == DioExceptionType.connectionError) {
      return 'Connection error';
    }
    return e.message ?? 'Network error';
  }
}

class AnalysisApiResponse {
  final bool success;
  final AnalysisResult? analysisResult;
  final Map<String, dynamic> meta;
  final String? message;

  AnalysisApiResponse({
    required this.success,
    required this.analysisResult,
    required this.meta,
    required this.message,
  });
}