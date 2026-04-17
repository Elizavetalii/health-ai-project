// lib/models/analysis_result.dart

// ------------------------------------------------------------
// Этот файл описывает структуру данных, которую frontend получает
// от backend после анализа медицинского файла.
//
// Зачем это нужно:
// backend возвращает большой JSON-ответ,
// а приложению удобнее работать не с "сырыми Map",
// а с типизированными объектами Dart.
//
// Это даёт:
// - более понятный код,
// - меньше ошибок в ключах JSON,
// - удобную работу с данными в UI.
// ------------------------------------------------------------

/// Один показатель, который система сочла отклонённым.
///
/// Примеры:
/// - гемоглобин понижен
/// - глюкоза повышена
/// - лейкоциты требуют внимания
class AbnormalValue {
  final String name;
  final String value;
  final String status;
  final String comment;

  AbnormalValue({
    required this.name,
    required this.value,
    required this.status,
    required this.comment,
  });

  /// Создание объекта из JSON-словаря backend.
  factory AbnormalValue.fromJson(Map<String, dynamic> json) {
    return AbnormalValue(
      name: json["name"] ?? "",
      value: json["value"] ?? "",
      status: json["status"] ?? "",
      comment: json["comment"] ?? "",
    );
  }
}

/// Пограничный показатель.
///
/// Это не всегда явное отклонение, но значение уже близко к границе
/// и может быть клинически значимым в контексте других данных.
class BorderlineValue {
  final String name;
  final String value;
  final String comment;

  BorderlineValue({
    required this.name,
    required this.value,
    required this.comment,
  });

  factory BorderlineValue.fromJson(Map<String, dynamic> json) {
    return BorderlineValue(
      name: json["name"] ?? "",
      value: json["value"] ?? "",
      comment: json["comment"] ?? "",
    );
  }
}

/// Возможное состояние или направление интерпретации.
///
/// Важно:
/// это не диагноз, а вероятная гипотеза,
/// которую AI выделил на основе анализа.
class PossibleCondition {
  final String name;
  final int probabilityPercent;
  final String confidence;
  final String comment;

  PossibleCondition({
    required this.name,
    required this.probabilityPercent,
    required this.confidence,
    required this.comment,
  });

  factory PossibleCondition.fromJson(Map<String, dynamic> json) {
    return PossibleCondition(
      name: json["name"] ?? "",
      probabilityPercent: json["probability_percent"] ?? 0,
      confidence: json["confidence"] ?? "",
      comment: json["comment"] ?? "",
    );
  }
}

/// Рекомендованный специалист.
///
/// Здесь хранится:
/// - к какому врачу стоит обратиться
/// - почему это имеет смысл в текущем контексте
class RecommendedDoctor {
  final String specialist;
  final String reason;

  RecommendedDoctor({
    required this.specialist,
    required this.reason,
  });

  factory RecommendedDoctor.fromJson(Map<String, dynamic> json) {
    return RecommendedDoctor(
      specialist: json["specialist"] ?? "",
      reason: json["reason"] ?? "",
    );
  }
}

/// Дополнительный анализ или обследование.
///
/// Этот блок помогает показать пользователю,
/// какие данные полезно уточнить дальше.
class AdditionalTest {
  final String name;
  final String reason;

  AdditionalTest({
    required this.name,
    required this.reason,
  });

  factory AdditionalTest.fromJson(Map<String, dynamic> json) {
    return AdditionalTest(
      name: json["name"] ?? "",
      reason: json["reason"] ?? "",
    );
  }
}

/// Возможные варианты для обсуждения по препаратам / веществам.
///
/// Это не назначение, а информационный блок:
/// - какие вещества или формы могут рассматриваться
/// - почему они вообще упоминаются
/// - какие есть ограничения
class MedicationDiscussionOption {
  final String category;
  final List<String> examples;
  final String comment;
  final String limitations;

  MedicationDiscussionOption({
    required this.category,
    required this.examples,
    required this.comment,
    required this.limitations,
  });

  factory MedicationDiscussionOption.fromJson(Map<String, dynamic> json) {
    return MedicationDiscussionOption(
      category: json["category"] ?? "",
      examples: List<String>.from(json["examples"] ?? const []),
      comment: json["comment"] ?? "",
      limitations: json["limitations"] ?? "",
    );
  }
}

/// Примеры рыночных вариантов.
///
/// Этот блок используется, если backend прислал:
/// - действующие вещества
/// - примеры препаратов / брендов
/// - пояснение, что это только информационный пример
///
/// Важно:
/// это не означает, что приложение "назначает" конкретный препарат.
class MedicationExampleInfo {
  final String category;
  final List<String> activeIngredients;
  final List<String> exampleBrands;
  final String note;

  MedicationExampleInfo({
    required this.category,
    required this.activeIngredients,
    required this.exampleBrands,
    required this.note,
  });

  factory MedicationExampleInfo.fromJson(Map<String, dynamic> json) {
    return MedicationExampleInfo(
      category: json["category"] ?? "",
      activeIngredients:
          List<String>.from(json["active_ingredients"] ?? const []),
      exampleBrands: List<String>.from(json["example_brands"] ?? const []),
      note: json["note"] ?? "",
    );
  }
}

/// Предупреждение или зона осторожности.
///
/// Например:
/// - чего лучше избегать без уточняющих анализов
/// - в каком контексте самостоятельные действия нежелательны
class CautionNote {
  final String context;
  final List<String> avoid;
  final String reason;

  CautionNote({
    required this.context,
    required this.avoid,
    required this.reason,
  });

  factory CautionNote.fromJson(Map<String, dynamic> json) {
    return CautionNote(
      context: json["context"] ?? "",
      avoid: List<String>.from(json["avoid"] ?? const []),
      reason: json["reason"] ?? "",
    );
  }
}

/// Оценка качества входных данных.
///
/// Этот блок показывает:
/// - полный ли текст анализа удалось получить
/// - были ли возможные OCR-проблемы
/// - насколько качество данных влияет на уверенность результата
class DataQuality {
  final bool isTextComplete;
  final List<String> possibleOcrIssues;
  final String comment;

  DataQuality({
    required this.isTextComplete,
    required this.possibleOcrIssues,
    required this.comment,
  });

  factory DataQuality.fromJson(Map<String, dynamic> json) {
    return DataQuality(
      isTextComplete: json["is_text_complete"] ?? false,
      possibleOcrIssues:
          List<String>.from(json["possible_ocr_issues"] ?? const []),
      comment: json["comment"] ?? "",
    );
  }
}

/// Общий обзор результата анализа.
///
/// Это "верхнеуровневая" часть результата:
/// - общий вывод
/// - главные моменты
/// - качество входных данных
class AnalysisOverview {
  final String overallImpression;
  final List<String> mainConcerns;
  final DataQuality dataQuality;

  AnalysisOverview({
    required this.overallImpression,
    required this.mainConcerns,
    required this.dataQuality,
  });

  factory AnalysisOverview.fromJson(Map<String, dynamic> json) {
    return AnalysisOverview(
      overallImpression: json["overall_impression"] ?? "",
      mainConcerns: List<String>.from(json["main_concerns"] ?? const []),
      dataQuality: DataQuality.fromJson(json["data_quality"] ?? const {}),
    );
  }
}

/// Оценка срочности.
///
/// backend может вернуть:
/// - routine
/// - soon
/// - urgent
///
/// Вместе с коротким пояснением.
class UrgencyAssessment {
  final String level;
  final String comment;

  UrgencyAssessment({
    required this.level,
    required this.comment,
  });

  factory UrgencyAssessment.fromJson(Map<String, dynamic> json) {
    return UrgencyAssessment(
      level: json["level"] ?? "",
      comment: json["comment"] ?? "",
    );
  }
}

/// Главная модель результата анализа.
///
/// Это центральный объект, который собирает все части ответа backend.
/// После преобразования JSON в этот класс UI может удобно отрисовывать:
/// - резюме
/// - отклонения
/// - риски
/// - врачей
/// - вещества и варианты
/// - срочность
/// - предупреждения
class AnalysisResult {
  final String summary;
  final AnalysisOverview analysisOverview;
  final List<AbnormalValue> abnormalValues;
  final List<BorderlineValue> borderlineValues;
  final List<BorderlineValue> normalButRelevantValues;
  final List<PossibleCondition> possibleConditions;
  final List<String> patternsAndConnections;
  final List<String> risks;
  final List<RecommendedDoctor> recommendedDoctors;
  final List<AdditionalTest> additionalTests;
  final List<MedicationDiscussionOption> medicationDiscussionOptions;
  final List<MedicationExampleInfo> medicationExamplesInfo;
  final List<CautionNote> cautionNotes;
  final List<String> possibleSupportOptions;
  final List<String> recommendations;
  final List<String> redFlags;
  final UrgencyAssessment urgencyAssessment;
  final List<String> missingImportantData;
  final String disclaimer;

  AnalysisResult({
    required this.summary,
    required this.analysisOverview,
    required this.abnormalValues,
    required this.borderlineValues,
    required this.normalButRelevantValues,
    required this.possibleConditions,
    required this.patternsAndConnections,
    required this.risks,
    required this.recommendedDoctors,
    required this.additionalTests,
    required this.medicationDiscussionOptions,
    required this.medicationExamplesInfo,
    required this.cautionNotes,
    required this.possibleSupportOptions,
    required this.recommendations,
    required this.redFlags,
    required this.urgencyAssessment,
    required this.missingImportantData,
    required this.disclaimer,
  });

  /// Главный конструктор из JSON.
  ///
  /// Здесь мы преобразуем ответ backend в типизированную модель.
  /// Это даёт более устойчивый код, чем прямой доступ к Map по строковым ключам.
  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    return AnalysisResult(
      summary: json["summary"] ?? "",
      analysisOverview: AnalysisOverview.fromJson(
        json["analysis_overview"] ?? const {},
      ),
      abnormalValues: (json["abnormal_values"] as List? ?? const [])
          .map((e) => AbnormalValue.fromJson(Map<String, dynamic>.from(e)))
          .toList(),
      borderlineValues: (json["borderline_values"] as List? ?? const [])
          .map((e) => BorderlineValue.fromJson(Map<String, dynamic>.from(e)))
          .toList(),
      normalButRelevantValues:
          (json["normal_but_relevant_values"] as List? ?? const [])
              .map((e) => BorderlineValue.fromJson(Map<String, dynamic>.from(e)))
              .toList(),
      possibleConditions: (json["possible_conditions"] as List? ?? const [])
          .map((e) => PossibleCondition.fromJson(Map<String, dynamic>.from(e)))
          .toList(),
      patternsAndConnections:
          List<String>.from(json["patterns_and_connections"] ?? const []),
      risks: List<String>.from(json["risks"] ?? const []),
      recommendedDoctors:
          (json["recommended_doctors"] as List? ?? const [])
              .map((e) => RecommendedDoctor.fromJson(Map<String, dynamic>.from(e)))
              .toList(),
      additionalTests: (json["additional_tests"] as List? ?? const [])
          .map((e) => AdditionalTest.fromJson(Map<String, dynamic>.from(e)))
          .toList(),
      medicationDiscussionOptions:
          (json["medication_discussion_options"] as List? ?? const [])
              .map(
                (e) => MedicationDiscussionOption.fromJson(
                  Map<String, dynamic>.from(e),
                ),
              )
              .toList(),
      medicationExamplesInfo:
          (json["medication_examples_info"] as List? ?? const [])
              .map(
                (e) => MedicationExampleInfo.fromJson(
                  Map<String, dynamic>.from(e),
                ),
              )
              .toList(),
      cautionNotes: (json["caution_notes"] as List? ?? const [])
          .map((e) => CautionNote.fromJson(Map<String, dynamic>.from(e)))
          .toList(),
      possibleSupportOptions:
          List<String>.from(json["possible_support_options"] ?? const []),
      recommendations:
          List<String>.from(json["recommendations"] ?? const []),
      redFlags: List<String>.from(json["red_flags"] ?? const []),
      urgencyAssessment: UrgencyAssessment.fromJson(
        json["urgency_assessment"] ?? const {},
      ),
      missingImportantData:
          List<String>.from(json["missing_important_data"] ?? const []),
      disclaimer: json["disclaimer"] ?? "",
    );
  }
}