// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Russian (`ru`).
class AppLocalizationsRu extends AppLocalizations {
  AppLocalizationsRu([String locale = 'ru']) : super(locale);

  @override
  String get appTitle => 'Smart Health';

  @override
  String get heroTitle => 'Smart Health AI';

  @override
  String get heroSubtitle =>
      'Загрузите медицинский анализ и получите предварительный структурированный разбор с выделением отклонений, рисков и следующих шагов.';

  @override
  String get safetyNote =>
      'Результат является предварительным и не заменяет очную консультацию врача.';

  @override
  String get fileSectionTitle => 'Файл анализа';

  @override
  String get chooseFile => 'Выбрать файл';

  @override
  String get noFileSelected => 'Файл пока не выбран';

  @override
  String get commentTitle => 'Комментарий к анализу';

  @override
  String get commentHint =>
      'Например: слабость, головокружение, посмотрите гемоглобин, анализ сдавался не натощак...';

  @override
  String get languageTitle => 'Язык';

  @override
  String get sendButton => 'Отправить на анализ';

  @override
  String get sendingButton => 'Анализируем...';

  @override
  String get resultTitle => 'Результат анализа';

  @override
  String get summaryTitle => 'Краткое резюме';

  @override
  String get abnormalitiesTitle => 'Отклонения';

  @override
  String get risksTitle => 'Риски и на что обратить внимание';

  @override
  String get doctorsTitle => 'Рекомендуемые врачи';

  @override
  String get supportOptionsTitle => 'Что можно обсудить с врачом';

  @override
  String get recommendationsTitle => 'Следующие шаги';

  @override
  String get disclaimerTitle => 'Важно';

  @override
  String get sourceTitle => 'Источник обработки';

  @override
  String get deepseekLabel => 'DeepSeek AI';

  @override
  String get fallbackLabel => 'Локальный анализ';

  @override
  String get fileTypeTitle => 'Тип файла';

  @override
  String get commentUsedTitle => 'Комментарий учтён';

  @override
  String get commentUsedYes => 'Да';

  @override
  String get commentUsedNo => 'Нет';

  @override
  String get pickFileFirst => 'Сначала выберите файл анализа';

  @override
  String get noData => 'Нет данных';

  @override
  String get statusLow => 'Понижен';

  @override
  String get statusHigh => 'Повышен';

  @override
  String get statusAttention => 'Внимание';

  @override
  String get outputInfo =>
      'Для корректной интерпретации результата необходимо учитывать симптомы, анамнез и рекомендации врача.';

  @override
  String get supportedFormats =>
      'Поддерживаются PDF, JPG, JPEG, PNG, DOC, DOCX, XLS, XLSX, CSV, TXT';

  @override
  String get possibleConditionsTitle => 'Возможные состояния';

  @override
  String get additionalTestsTitle => 'Дополнительные анализы';

  @override
  String get medicineOptionsTitle => 'Что можно обсудить по препаратам';

  @override
  String get medicineExamplesTitle => 'Примеры рыночных вариантов';

  @override
  String get cautionTitle => 'С осторожностью';

  @override
  String get urgencyTitle => 'Срочность';

  @override
  String get redFlagsTitle => 'Красные флаги';

  @override
  String get missingDataTitle => 'Чего не хватает';

  @override
  String get patternsTitle => 'Связи между показателями';

  @override
  String get urgencyRoutine => 'Планово';

  @override
  String get urgencySoon => 'В ближайшее время';

  @override
  String get urgencyUrgent => 'Срочно';
}
