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
// - удобную работу с данными в UI,
// - более безопасный парсинг ответа.
//
// ВАЖНО:
// AI-ответы могут быть не всегда идеально одинаковыми.
// Поэтому ниже добавлены безопасные helper-функции,
// которые защищают приложение от падений,
// если backend или AI вернул неожиданную структуру.
// ------------------------------------------------------------

/// ------------------------------------------------------------
/// ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
/// ------------------------------------------------------------

/// Безопасно превращает любое значение в строку.
///
/// Если значение null — вернётся пустая строка.
/// Если пришло число, bool и т.д. — оно будет превращено в строку.
String _asString(dynamic value) {
  if (value == null) return "";
  return value.toString();
}

/// Безопасно превращает любое значение в int.
///
/// AI иногда может вернуть:
/// - int
/// - double
/// - строку вроде "70"
/// - null
///
/// Эта функция старается аккуратно привести значение к целому числу.
int _asInt(dynamic value) {
  if (value == null) return 0;

  if (value is int) return value;

  if (value is double) return value.toInt();

  if (value is String) {
    return int.tryParse(value) ?? 0;
  }

  return 0;
}

/// Безопасно превращает любое значение в bool.
///
/// Если значение не bool, вернётся false.
bool _asBool(dynamic value) {
  if (value is bool) return value;
  return false;
}

/// Безопасно превращает значение в Map<String, dynamic>.
///
/// Это особенно важно, когда backend прислал:
/// - корректный Map
/// - null
/// - список или строку по ошибке
///
/// Если значение не является Map — возвращается пустой объект.
Map<String, dynamic> _asMap(dynamic value) {
  if (value is Map) {
    return Map<String, dynamic>.from(value);
  }
  return {};
}

/// Безопасно превращает значение в список строк.
///
/// Если пришёл не список — вернётся пустой список.
/// Если внутри списка есть не-строки, они будут приведены к строке.
List<String> _asStringList(dynamic value) {
  if (value is! List) return [];
  return value.map((e) => e.toString()).toList();
}

/// Безопасно превращает значение в список моделей.
///
/// Используется для случаев, когда ожидается List<Map>,
/// но AI может вернуть:
/// - пустой список
/// - null
/// - список строк
/// - смешанные значения
///
/// Мы берём только те элементы, которые действительно являются Map,
/// и пропускаем всё остальное.
List<T> _asModelList<T>(
  dynamic value,
  T Function(Map<String, dynamic>) fromJson,
) {
  if (value is! List) return [];

  return value
      .where((e) => e is Map)
      .map((e) => fromJson(Map<String, dynamic>.from(e as Map)))
      .toList();
}

/// ------------------------------------------------------------
/// МОДЕЛИ ОТВЕТА
/// ------------------------------------------------------------

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
      name: _asString(json["name"]),
      value: _asString(json["value"]),
      status: _asString(json["status"]),
      comment: _asString(json["comment"]),
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
      name: _asString(json["name"]),
      value: _asString(json["value"]),
      comment: _asString(json["comment"]),
    );
  }
}

/// Нормальный, но клинически значимый показатель.
///
/// Иногда показатель формально в норме,
/// но всё равно полезен для общей интерпретации.
class NormalRelevantValue {
  final String name;
  final String value;
  final String comment;

  NormalRelevantValue({
    required this.name,
    required this.value,
    required this.comment,
  });

  factory NormalRelevantValue.fromJson(Map<String, dynamic> json) {
    return NormalRelevantValue(
      name: _asString(json["name"]),
      value: _asString(json["value"]),
      comment: _asString(json["comment"]),
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
      name: _asString(json["name"]),
      probabilityPercent: _asInt(json["probability_percent"]),
      confidence: _asString(json["confidence"]),
      comment: _asString(json["comment"]),
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
      specialist: _asString(json["specialist"]),
      reason: _asString(json["reason"]),
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
      name: _asString(json["name"]),
      reason: _asString(json["reason"]),
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
      category: _asString(json["category"]),
      examples: _asStringList(json["examples"]),
      comment: _asString(json["comment"]),
      limitations: _asString(json["limitations"]),
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
      category: _asString(json["category"]),
      activeIngredients: _asStringList(json["active_ingredients"]),
      exampleBrands: _asStringList(json["example_brands"]),
      note: _asString(json["note"]),
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
      context: _asString(json["context"]),
      avoid: _asStringList(json["avoid"]),
      reason: _asString(json["reason"]),
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
      isTextComplete: _asBool(json["is_text_complete"]),
      possibleOcrIssues: _asStringList(json["possible_ocr_issues"]),
      comment: _asString(json["comment"]),
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
      overallImpression: _asString(json["overall_impression"]),
      mainConcerns: _asStringList(json["main_concerns"]),
      dataQuality: DataQuality.fromJson(_asMap(json["data_quality"])),
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
      level: _asString(json["level"]),
      comment: _asString(json["comment"]),
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
  final List<NormalRelevantValue> normalButRelevantValues;
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
  ///
  /// ВАЖНО:
  /// Все поля ниже парсятся через безопасные helper-функции.
  /// Это защищает приложение от падений,
  /// если AI где-то вернул немного не ту структуру.
  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    return AnalysisResult(
      summary: _asString(json["summary"]),

      analysisOverview: AnalysisOverview.fromJson(
        _asMap(json["analysis_overview"]),
      ),

      abnormalValues: _asModelList(
        json["abnormal_values"],
        AbnormalValue.fromJson,
      ),

      borderlineValues: _asModelList(
        json["borderline_values"],
        BorderlineValue.fromJson,
      ),

      normalButRelevantValues: _asModelList(
        json["normal_but_relevant_values"],
        NormalRelevantValue.fromJson,
      ),

      possibleConditions: _asModelList(
        json["possible_conditions"],
        PossibleCondition.fromJson,
      ),

      patternsAndConnections: _asStringList(
        json["patterns_and_connections"],
      ),

      risks: _asStringList(
        json["risks"],
      ),

      recommendedDoctors: _asModelList(
        json["recommended_doctors"],
        RecommendedDoctor.fromJson,
      ),

      additionalTests: _asModelList(
        json["additional_tests"],
        AdditionalTest.fromJson,
      ),

      medicationDiscussionOptions: _asModelList(
        json["medication_discussion_options"],
        MedicationDiscussionOption.fromJson,
      ),

      medicationExamplesInfo: _asModelList(
        json["medication_examples_info"],
        MedicationExampleInfo.fromJson,
      ),

      cautionNotes: _asModelList(
        json["caution_notes"],
        CautionNote.fromJson,
      ),

      possibleSupportOptions: _asStringList(
        json["possible_support_options"],
      ),

      recommendations: _asStringList(
        json["recommendations"],
      ),

      redFlags: _asStringList(
        json["red_flags"],
      ),

      urgencyAssessment: UrgencyAssessment.fromJson(
        _asMap(json["urgency_assessment"]),
      ),

      missingImportantData: _asStringList(
        json["missing_important_data"],
      ),

      disclaimer: _asString(json["disclaimer"]),
    );
  }
}