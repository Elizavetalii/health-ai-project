import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_ru.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'generated/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('ru'),
  ];

  /// No description provided for @appTitle.
  ///
  /// In en, this message translates to:
  /// **'Smart Health'**
  String get appTitle;

  /// No description provided for @heroTitle.
  ///
  /// In en, this message translates to:
  /// **'Smart Health AI'**
  String get heroTitle;

  /// No description provided for @heroSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Upload a medical test result and receive a structured preliminary interpretation with abnormalities, risks and next steps.'**
  String get heroSubtitle;

  /// No description provided for @safetyNote.
  ///
  /// In en, this message translates to:
  /// **'This result is preliminary and does not replace an in-person doctor consultation.'**
  String get safetyNote;

  /// No description provided for @fileSectionTitle.
  ///
  /// In en, this message translates to:
  /// **'Analysis file'**
  String get fileSectionTitle;

  /// No description provided for @chooseFile.
  ///
  /// In en, this message translates to:
  /// **'Choose file'**
  String get chooseFile;

  /// No description provided for @noFileSelected.
  ///
  /// In en, this message translates to:
  /// **'No file selected yet'**
  String get noFileSelected;

  /// No description provided for @commentTitle.
  ///
  /// In en, this message translates to:
  /// **'Comment about the analysis'**
  String get commentTitle;

  /// No description provided for @commentHint.
  ///
  /// In en, this message translates to:
  /// **'For example: weakness, dizziness, please check hemoglobin, the test was not fasting...'**
  String get commentHint;

  /// No description provided for @languageTitle.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get languageTitle;

  /// No description provided for @sendButton.
  ///
  /// In en, this message translates to:
  /// **'Send for analysis'**
  String get sendButton;

  /// No description provided for @sendingButton.
  ///
  /// In en, this message translates to:
  /// **'Analyzing...'**
  String get sendingButton;

  /// No description provided for @resultTitle.
  ///
  /// In en, this message translates to:
  /// **'Analysis result'**
  String get resultTitle;

  /// No description provided for @summaryTitle.
  ///
  /// In en, this message translates to:
  /// **'Summary'**
  String get summaryTitle;

  /// No description provided for @abnormalitiesTitle.
  ///
  /// In en, this message translates to:
  /// **'Abnormalities'**
  String get abnormalitiesTitle;

  /// No description provided for @risksTitle.
  ///
  /// In en, this message translates to:
  /// **'Risks and attention points'**
  String get risksTitle;

  /// No description provided for @doctorsTitle.
  ///
  /// In en, this message translates to:
  /// **'Recommended doctors'**
  String get doctorsTitle;

  /// No description provided for @supportOptionsTitle.
  ///
  /// In en, this message translates to:
  /// **'What can be discussed with a doctor'**
  String get supportOptionsTitle;

  /// No description provided for @recommendationsTitle.
  ///
  /// In en, this message translates to:
  /// **'Next steps'**
  String get recommendationsTitle;

  /// No description provided for @disclaimerTitle.
  ///
  /// In en, this message translates to:
  /// **'Important'**
  String get disclaimerTitle;

  /// No description provided for @sourceTitle.
  ///
  /// In en, this message translates to:
  /// **'Processing source'**
  String get sourceTitle;

  /// No description provided for @deepseekLabel.
  ///
  /// In en, this message translates to:
  /// **'DeepSeek AI'**
  String get deepseekLabel;

  /// No description provided for @fallbackLabel.
  ///
  /// In en, this message translates to:
  /// **'Local analysis'**
  String get fallbackLabel;

  /// No description provided for @fileTypeTitle.
  ///
  /// In en, this message translates to:
  /// **'File type'**
  String get fileTypeTitle;

  /// No description provided for @commentUsedTitle.
  ///
  /// In en, this message translates to:
  /// **'Comment used'**
  String get commentUsedTitle;

  /// No description provided for @commentUsedYes.
  ///
  /// In en, this message translates to:
  /// **'Yes'**
  String get commentUsedYes;

  /// No description provided for @commentUsedNo.
  ///
  /// In en, this message translates to:
  /// **'No'**
  String get commentUsedNo;

  /// No description provided for @pickFileFirst.
  ///
  /// In en, this message translates to:
  /// **'Please select an analysis file first'**
  String get pickFileFirst;

  /// No description provided for @noData.
  ///
  /// In en, this message translates to:
  /// **'No data'**
  String get noData;

  /// No description provided for @statusLow.
  ///
  /// In en, this message translates to:
  /// **'Low'**
  String get statusLow;

  /// No description provided for @statusHigh.
  ///
  /// In en, this message translates to:
  /// **'High'**
  String get statusHigh;

  /// No description provided for @statusAttention.
  ///
  /// In en, this message translates to:
  /// **'Attention'**
  String get statusAttention;

  /// No description provided for @outputInfo.
  ///
  /// In en, this message translates to:
  /// **'For better interpretation, compare the result with symptoms, medical history and a doctor\'s recommendations.'**
  String get outputInfo;

  /// No description provided for @supportedFormats.
  ///
  /// In en, this message translates to:
  /// **'Supported: PDF, JPG, JPEG, PNG, DOC, DOCX, XLS, XLSX, CSV, TXT'**
  String get supportedFormats;

  /// No description provided for @possibleConditionsTitle.
  ///
  /// In en, this message translates to:
  /// **'Possible conditions'**
  String get possibleConditionsTitle;

  /// No description provided for @additionalTestsTitle.
  ///
  /// In en, this message translates to:
  /// **'Additional tests'**
  String get additionalTestsTitle;

  /// No description provided for @medicineOptionsTitle.
  ///
  /// In en, this message translates to:
  /// **'Medication discussion options'**
  String get medicineOptionsTitle;

  /// No description provided for @medicineExamplesTitle.
  ///
  /// In en, this message translates to:
  /// **'Example market products'**
  String get medicineExamplesTitle;

  /// No description provided for @cautionTitle.
  ///
  /// In en, this message translates to:
  /// **'Caution notes'**
  String get cautionTitle;

  /// No description provided for @urgencyTitle.
  ///
  /// In en, this message translates to:
  /// **'Urgency'**
  String get urgencyTitle;

  /// No description provided for @redFlagsTitle.
  ///
  /// In en, this message translates to:
  /// **'Red flags'**
  String get redFlagsTitle;

  /// No description provided for @missingDataTitle.
  ///
  /// In en, this message translates to:
  /// **'Missing important data'**
  String get missingDataTitle;

  /// No description provided for @patternsTitle.
  ///
  /// In en, this message translates to:
  /// **'Connections between findings'**
  String get patternsTitle;

  /// No description provided for @urgencyRoutine.
  ///
  /// In en, this message translates to:
  /// **'Routine'**
  String get urgencyRoutine;

  /// No description provided for @urgencySoon.
  ///
  /// In en, this message translates to:
  /// **'Soon'**
  String get urgencySoon;

  /// No description provided for @urgencyUrgent.
  ///
  /// In en, this message translates to:
  /// **'Urgent'**
  String get urgencyUrgent;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['en', 'ru'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppLocalizationsEn();
    case 'ru':
      return AppLocalizationsRu();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
