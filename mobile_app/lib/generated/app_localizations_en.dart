// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'Smart Health';

  @override
  String get heroTitle => 'Smart Health AI';

  @override
  String get heroSubtitle =>
      'Upload a medical test result and receive a structured preliminary interpretation with abnormalities, risks and next steps.';

  @override
  String get safetyNote =>
      'This result is preliminary and does not replace an in-person doctor consultation.';

  @override
  String get fileSectionTitle => 'Analysis file';

  @override
  String get chooseFile => 'Choose file';

  @override
  String get noFileSelected => 'No file selected yet';

  @override
  String get commentTitle => 'Comment about the analysis';

  @override
  String get commentHint =>
      'For example: weakness, dizziness, please check hemoglobin, the test was not fasting...';

  @override
  String get languageTitle => 'Language';

  @override
  String get sendButton => 'Send for analysis';

  @override
  String get sendingButton => 'Analyzing...';

  @override
  String get resultTitle => 'Analysis result';

  @override
  String get summaryTitle => 'Summary';

  @override
  String get abnormalitiesTitle => 'Abnormalities';

  @override
  String get risksTitle => 'Risks and attention points';

  @override
  String get doctorsTitle => 'Recommended doctors';

  @override
  String get supportOptionsTitle => 'What can be discussed with a doctor';

  @override
  String get recommendationsTitle => 'Next steps';

  @override
  String get disclaimerTitle => 'Important';

  @override
  String get sourceTitle => 'Processing source';

  @override
  String get deepseekLabel => 'DeepSeek AI';

  @override
  String get fallbackLabel => 'Local analysis';

  @override
  String get fileTypeTitle => 'File type';

  @override
  String get commentUsedTitle => 'Comment used';

  @override
  String get commentUsedYes => 'Yes';

  @override
  String get commentUsedNo => 'No';

  @override
  String get pickFileFirst => 'Please select an analysis file first';

  @override
  String get noData => 'No data';

  @override
  String get statusLow => 'Low';

  @override
  String get statusHigh => 'High';

  @override
  String get statusAttention => 'Attention';

  @override
  String get outputInfo =>
      'For better interpretation, compare the result with symptoms, medical history and a doctor\'s recommendations.';

  @override
  String get supportedFormats =>
      'Supported: PDF, JPG, JPEG, PNG, DOC, DOCX, XLS, XLSX, CSV, TXT';

  @override
  String get possibleConditionsTitle => 'Possible conditions';

  @override
  String get additionalTestsTitle => 'Additional tests';

  @override
  String get medicineOptionsTitle => 'Medication discussion options';

  @override
  String get medicineExamplesTitle => 'Example market products';

  @override
  String get cautionTitle => 'Caution notes';

  @override
  String get urgencyTitle => 'Urgency';

  @override
  String get redFlagsTitle => 'Red flags';

  @override
  String get missingDataTitle => 'Missing important data';

  @override
  String get patternsTitle => 'Connections between findings';

  @override
  String get urgencyRoutine => 'Routine';

  @override
  String get urgencySoon => 'Soon';

  @override
  String get urgencyUrgent => 'Urgent';
}
