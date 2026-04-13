import 'dart:io';

import 'package:dio/dio.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

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

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Health AI',
      theme: ThemeData(
        scaffoldBackgroundColor: AppColors.background,
        colorScheme: ColorScheme.fromSeed(
          seedColor: AppColors.primary,
          primary: AppColors.primary,
        ),
        useMaterial3: true,
      ),
      home: const UploadScreen(),
    );
  }
}

class AppStrings {
  final String appTitle;
  final String heroTitle;
  final String heroSubtitle;
  final String safetyNote;
  final String fileSectionTitle;
  final String chooseFile;
  final String noFileSelected;
  final String commentTitle;
  final String commentHint;
  final String languageTitle;
  final String sendButton;
  final String sendingButton;
  final String resultTitle;
  final String summaryTitle;
  final String abnormalitiesTitle;
  final String risksTitle;
  final String doctorsTitle;
  final String supportOptionsTitle;
  final String recommendationsTitle;
  final String disclaimerTitle;
  final String sourceTitle;
  final String deepseekLabel;
  final String fallbackLabel;
  final String fileTypeTitle;
  final String commentUsedTitle;
  final String commentUsedYes;
  final String commentUsedNo;
  final String pickFileFirst;
  final String unsupportedEmpty;
  final String noData;
  final String statusLow;
  final String statusHigh;
  final String statusAttention;
  final String outputInfo;
  final String supportedFormats;

  const AppStrings({
    required this.appTitle,
    required this.heroTitle,
    required this.heroSubtitle,
    required this.safetyNote,
    required this.fileSectionTitle,
    required this.chooseFile,
    required this.noFileSelected,
    required this.commentTitle,
    required this.commentHint,
    required this.languageTitle,
    required this.sendButton,
    required this.sendingButton,
    required this.resultTitle,
    required this.summaryTitle,
    required this.abnormalitiesTitle,
    required this.risksTitle,
    required this.doctorsTitle,
    required this.supportOptionsTitle,
    required this.recommendationsTitle,
    required this.disclaimerTitle,
    required this.sourceTitle,
    required this.deepseekLabel,
    required this.fallbackLabel,
    required this.fileTypeTitle,
    required this.commentUsedTitle,
    required this.commentUsedYes,
    required this.commentUsedNo,
    required this.pickFileFirst,
    required this.unsupportedEmpty,
    required this.noData,
    required this.statusLow,
    required this.statusHigh,
    required this.statusAttention,
    required this.outputInfo,
    required this.supportedFormats,
  });

  static const ru = AppStrings(
    appTitle: 'Smart Health',
    heroTitle: 'Smart Health AI',
    heroSubtitle:
        'Загрузите анализ крови или мочи в формате PDF или фото. Система выполнит предварительный разбор, выделит возможные отклонения, риски и подскажет, к каким врачам можно обратиться.',
    safetyNote:
        'Результат является предварительным и не заменяет очную консультацию врача.',
    fileSectionTitle: 'Файл анализа',
    chooseFile: 'Выбрать файл',
    noFileSelected: 'Файл пока не выбран',
    commentTitle: 'Комментарий к анализу',
    commentHint:
        'Например: слабость, головокружение, посмотрите гемоглобин, анализ сдавался не натощак...',
    languageTitle: 'Язык',
    sendButton: 'Отправить на анализ',
    sendingButton: 'Анализируем...',
    resultTitle: 'Результат анализа',
    summaryTitle: 'Краткое резюме',
    abnormalitiesTitle: 'Отклонения',
    risksTitle: 'Риски и на что обратить внимание',
    doctorsTitle: 'Рекомендуемые врачи',
    supportOptionsTitle: 'Что можно обсудить с врачом',
    recommendationsTitle: 'Следующие шаги',
    disclaimerTitle: 'Важно',
    sourceTitle: 'Источник обработки',
    deepseekLabel: 'DeepSeek AI',
    fallbackLabel: 'Локальный анализ',
    fileTypeTitle: 'Тип файла',
    commentUsedTitle: 'Комментарий учтён',
    commentUsedYes: 'Да',
    commentUsedNo: 'Нет',
    pickFileFirst: 'Сначала выберите файл анализа',
    unsupportedEmpty: 'Нет данных',
    noData: 'Нет данных',
    statusLow: 'Понижен',
    statusHigh: 'Повышен',
    statusAttention: 'Внимание',
    outputInfo:
        'Для повышения точности сопоставляйте результат с жалобами, симптомами и рекомендациями врача.',
    supportedFormats: 'Поддерживаются PDF, JPG, JPEG, PNG',
  );

  static const en = AppStrings(
    appTitle: 'Smart Health',
    heroTitle: 'Smart Health AI',
    heroSubtitle:
        'Upload a blood or urine test result as a PDF or photo. The system will perform a preliminary review, highlight possible abnormalities, risks, and suggest which doctors may be relevant.',
    safetyNote:
        'This result is preliminary and does not replace an in-person doctor consultation.',
    fileSectionTitle: 'Analysis file',
    chooseFile: 'Choose file',
    noFileSelected: 'No file selected yet',
    commentTitle: 'Comment about the analysis',
    commentHint:
        'For example: weakness, dizziness, please check hemoglobin, the test was not fasting...',
    languageTitle: 'Language',
    sendButton: 'Send for analysis',
    sendingButton: 'Analyzing...',
    resultTitle: 'Analysis result',
    summaryTitle: 'Summary',
    abnormalitiesTitle: 'Abnormalities',
    risksTitle: 'Risks and attention points',
    doctorsTitle: 'Recommended doctors',
    supportOptionsTitle: 'What can be discussed with a doctor',
    recommendationsTitle: 'Next steps',
    disclaimerTitle: 'Important',
    sourceTitle: 'Processing source',
    deepseekLabel: 'DeepSeek AI',
    fallbackLabel: 'Local analysis',
    fileTypeTitle: 'File type',
    commentUsedTitle: 'Comment used',
    commentUsedYes: 'Yes',
    commentUsedNo: 'No',
    pickFileFirst: 'Please select an analysis file first',
    unsupportedEmpty: 'No data',
    noData: 'No data',
    statusLow: 'Low',
    statusHigh: 'High',
    statusAttention: 'Attention',
    outputInfo:
        'For better accuracy, compare the result with symptoms, complaints, and a doctor’s recommendations.',
    supportedFormats: 'Supported: PDF, JPG, JPEG, PNG',
  );
}

class UploadScreen extends StatefulWidget {
  const UploadScreen({super.key});

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  static const String apiUrl = 'http://127.0.0.1:8000/analyze';


  // static const String apiUrl = 'http://10.0.2.2:8000/analyze';
  final TextEditingController commentController = TextEditingController();

  File? selectedFile;
  String selectedFileName = AppStrings.ru.noFileSelected;
  bool isLoading = false;
  String selectedLanguage = 'ru';

  Map<String, dynamic>? analysisResult;
  Map<String, dynamic>? meta;
  String? errorText;

  AppStrings get strings => selectedLanguage == 'en' ? AppStrings.en : AppStrings.ru;

  @override
  void dispose() {
    commentController.dispose();
    super.dispose();
  }

  Future<void> pickFile() async {
    final result = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'jpg', 'jpeg', 'png'],
    );

    if (result != null && result.files.single.path != null) {
      setState(() {
        selectedFile = File(result.files.single.path!);
        selectedFileName = result.files.single.name;
        errorText = null;
      });
    }
  }

  Future<void> sendFile() async {
    if (selectedFile == null) {
      setState(() {
        errorText = strings.pickFileFirst;
      });
      return;
    }

    setState(() {
      isLoading = true;
      errorText = null;
      analysisResult = null;
      meta = null;
    });

    try {
      final dio = Dio();

      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          selectedFile!.path,
          filename: selectedFileName,
        ),
        'language': selectedLanguage,
        'user_comment': commentController.text.trim(),
      });

      final response = await dio.post(
        apiUrl,
        data: formData,
      );

      if (response.data['success'] == true) {
        setState(() {
          analysisResult = Map<String, dynamic>.from(
            response.data['analysis_result'],
          );
          final rawMeta = response.data['meta'];
          if (rawMeta is Map) {
            meta = Map<String, dynamic>.from(rawMeta);
          }
        });
      } else {
        setState(() {
          errorText = response.data['message']?.toString() ?? 'Unknown error';
        });
      }
    } catch (e) {
      setState(() {
        errorText = 'Ошибка при отправке: $e';
      });
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  String getMetaSourceLabel() {
    final source = meta?['source_type']?.toString() ?? '';
    if (source == 'deepseek') {
      return strings.deepseekLabel;
    }
    return strings.fallbackLabel;
  }

  String getMetaFileType() {
    return (meta?['file_type']?.toString() ?? '-').toUpperCase();
  }

  String getMetaCommentUsed() {
    final used = meta?['user_comment_used'] == true;
    return used ? strings.commentUsedYes : strings.commentUsedNo;
  }

  Color getStatusColor(String status) {
    switch (status) {
      case 'low':
        return AppColors.warning;
      case 'high':
        return AppColors.danger;
      default:
        return AppColors.primary;
    }
  }

  Color getStatusBackground(String status) {
    switch (status) {
      case 'low':
        return AppColors.softOrange;
      case 'high':
        return AppColors.softRed;
      default:
        return AppColors.softBlue;
    }
  }

  String getStatusLabel(String status) {
    switch (status) {
      case 'low':
        return strings.statusLow;
      case 'high':
        return strings.statusHigh;
      default:
        return strings.statusAttention;
    }
  }

  Widget buildHeroCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [AppColors.primary, AppColors.secondary],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(28),
        boxShadow: const [
          BoxShadow(
            color: Color(0x1A157BC5),
            blurRadius: 18,
            offset: Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              CircleAvatar(
                radius: 24,
                backgroundColor: Colors.white24,
                child: Icon(
                  Icons.health_and_safety_rounded,
                  color: Colors.white,
                  size: 26,
                ),
              ),
              SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Smart Health AI',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),
          Text(
            strings.heroTitle,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            strings.heroSubtitle,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 14.5,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }

  Widget buildInfoStrip() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        children: [
          const Icon(Icons.verified_user_outlined, color: AppColors.success),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              strings.safetyNote,
              style: const TextStyle(
                color: AppColors.textSecondary,
                fontSize: 14,
                height: 1.45,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget buildLanguageSelector() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppColors.card,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            strings.languageTitle,
            style: const TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.w800,
              color: AppColors.textMain,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: ChoiceChip(
                  label: const Text('Русский'),
                  selected: selectedLanguage == 'ru',
                  onSelected: (_) {
                    setState(() {
                      selectedLanguage = 'ru';
                      if (selectedFile == null) {
                        selectedFileName = AppStrings.ru.noFileSelected;
                      }
                    });
                  },
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: ChoiceChip(
                  label: const Text('English'),
                  selected: selectedLanguage == 'en',
                  onSelected: (_) {
                    setState(() {
                      selectedLanguage = 'en';
                      if (selectedFile == null) {
                        selectedFileName = AppStrings.en.noFileSelected;
                      }
                    });
                  },
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget buildUploadCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppColors.card,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppColors.border),
        boxShadow: const [
          BoxShadow(
            color: Color(0x12000000),
            blurRadius: 16,
            offset: Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.description_outlined, color: AppColors.primary),
              const SizedBox(width: 8),
              Text(
                strings.fileSectionTitle,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w800,
                  color: AppColors.textMain,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            strings.supportedFormats,
            style: const TextStyle(
              color: AppColors.textSecondary,
              fontSize: 13.5,
            ),
          ),
          const SizedBox(height: 16),
          InkWell(
            onTap: isLoading ? null : pickFile,
            borderRadius: BorderRadius.circular(20),
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 16),
              decoration: BoxDecoration(
                color: AppColors.softBlue,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppColors.primary.withOpacity(0.22)),
              ),
              child: Column(
                children: [
                  const Icon(
                    Icons.upload_file_rounded,
                    size: 34,
                    color: AppColors.primary,
                  ),
                  const SizedBox(height: 10),
                  Text(
                    strings.chooseFile,
                    style: const TextStyle(
                      color: AppColors.primary,
                      fontSize: 17,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    selectedFileName,
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      color: AppColors.textSecondary,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            strings.commentTitle,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w700,
              color: AppColors.textMain,
            ),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: commentController,
            minLines: 3,
            maxLines: 5,
            decoration: InputDecoration(
              hintText: strings.commentHint,
              filled: true,
              fillColor: const Color(0xFFF9FCFE),
              contentPadding: const EdgeInsets.all(16),
              enabledBorder: OutlineInputBorder(
                borderSide: const BorderSide(color: AppColors.border),
                borderRadius: BorderRadius.circular(18),
              ),
              focusedBorder: OutlineInputBorder(
                borderSide: const BorderSide(color: AppColors.primary),
                borderRadius: BorderRadius.circular(18),
              ),
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: isLoading ? null : sendFile,
              icon: isLoading
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                        strokeWidth: 2.2,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.auto_awesome_rounded),
              label: Text(isLoading ? strings.sendingButton : strings.sendButton),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                foregroundColor: Colors.white,
                minimumSize: const Size(double.infinity, 56),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(18),
                ),
                elevation: 0,
              ),
            ),
          ),
          if (errorText != null) ...[
            const SizedBox(height: 14),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFFFF1F0),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFFFD7D2)),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.error_outline_rounded, color: AppColors.danger),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      errorText!,
                      style: const TextStyle(
                        color: AppColors.danger,
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        height: 1.4,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget buildMetaCard() {
    if (meta == null) return const SizedBox.shrink();

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppColors.card,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            strings.sourceTitle,
            style: const TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.w800,
              color: AppColors.textMain,
            ),
          ),
          const SizedBox(height: 14),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              buildInfoChip(
                icon: Icons.memory_rounded,
                label: getMetaSourceLabel(),
                isPrimary: true,
              ),
              buildInfoChip(
                icon: Icons.insert_drive_file_outlined,
                label: '${strings.fileTypeTitle}: ${getMetaFileType()}',
              ),
              buildInfoChip(
                icon: Icons.comment_outlined,
                label: '${strings.commentUsedTitle}: ${getMetaCommentUsed()}',
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget buildInfoChip({
    required IconData icon,
    required String label,
    bool isPrimary = false,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: isPrimary ? AppColors.softBlue : const Color(0xFFF8FBFD),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isPrimary ? AppColors.primary.withOpacity(0.22) : AppColors.border,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 18,
            color: isPrimary ? AppColors.primary : AppColors.textSecondary,
          ),
          const SizedBox(width: 8),
          Text(
            label,
            style: TextStyle(
              color: isPrimary ? AppColors.primary : AppColors.textMain,
              fontSize: 13.5,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget buildSectionCard({
    required String title,
    required IconData icon,
    required dynamic content,
  }) {
    String text = '';

    if (content is List) {
      text = content.isEmpty
          ? strings.noData
          : content.map((e) => '• $e').join('\n');
    } else {
      text = (content ?? '').toString().trim().isEmpty
          ? strings.noData
          : content.toString();
    }

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppColors.card,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: AppColors.border),
        boxShadow: const [
          BoxShadow(
            color: Color(0x10000000),
            blurRadius: 14,
            offset: Offset(0, 7),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  color: AppColors.softBlue,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: AppColors.primary),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.w800,
                    color: AppColors.textMain,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Text(
            text,
            style: const TextStyle(
              fontSize: 15,
              height: 1.55,
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget buildAbnormalValuesCard() {
    final values = analysisResult?['abnormal_values'];

    if (values is! List || values.isEmpty) {
      return buildSectionCard(
        title: strings.abnormalitiesTitle,
        icon: Icons.analytics_outlined,
        content: strings.noData,
      );
    }

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppColors.card,
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: AppColors.border),
        boxShadow: const [
          BoxShadow(
            color: Color(0x10000000),
            blurRadius: 14,
            offset: Offset(0, 7),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 38,
                height: 38,
                decoration: BoxDecoration(
                  color: AppColors.softBlue,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.analytics_outlined, color: AppColors.primary),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  strings.abnormalitiesTitle,
                  style: const TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.w800,
                    color: AppColors.textMain,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          ...values.map((item) {
            if (item is! Map) return const SizedBox.shrink();

            final map = Map<String, dynamic>.from(item);
            final name = map['name']?.toString() ?? '-';
            final value = map['value']?.toString() ?? '-';
            final status = map['status']?.toString() ?? 'attention';
            final comment = map['comment']?.toString() ?? '';

            return Container(
              width: double.infinity,
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: getStatusBackground(status),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: getStatusColor(status).withOpacity(0.18)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          name,
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w800,
                            color: AppColors.textMain,
                          ),
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: getStatusColor(status),
                          borderRadius: BorderRadius.circular(30),
                        ),
                        child: Text(
                          getStatusLabel(status),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 12.5,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    value,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w800,
                      color: getStatusColor(status),
                    ),
                  ),
                  if (comment.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Text(
                      comment,
                      style: const TextStyle(
                        fontSize: 14.5,
                        height: 1.45,
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ],
              ),
            );
          }).toList(),
        ],
      ),
    );
  }

  Widget buildBottomInfoCard() {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(top: 4),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.info_outline_rounded, color: AppColors.primary),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              strings.outputInfo,
              style: const TextStyle(
                color: AppColors.textSecondary,
                fontSize: 14,
                height: 1.45,
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final analysis = analysisResult;

    return Scaffold(
      appBar: AppBar(
        elevation: 0,
        backgroundColor: AppColors.background,
        centerTitle: true,
        title: Text(
          strings.appTitle,
          style: const TextStyle(
            color: AppColors.textMain,
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(16, 10, 16, 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              buildHeroCard(),
              const SizedBox(height: 16),
              buildInfoStrip(),
              const SizedBox(height: 16),
              buildLanguageSelector(),
              const SizedBox(height: 16),
              buildUploadCard(),
              const SizedBox(height: 20),
              if (analysis != null) ...[
                Text(
                  strings.resultTitle,
                  style: const TextStyle(
                    fontSize: 23,
                    fontWeight: FontWeight.w800,
                    color: AppColors.textMain,
                  ),
                ),
                const SizedBox(height: 14),
                buildMetaCard(),
                buildSectionCard(
                  title: strings.summaryTitle,
                  icon: Icons.summarize_outlined,
                  content: analysis['summary'],
                ),
                buildAbnormalValuesCard(),
                buildSectionCard(
                  title: strings.risksTitle,
                  icon: Icons.warning_amber_rounded,
                  content: analysis['risks'],
                ),
                buildSectionCard(
                  title: strings.doctorsTitle,
                  icon: Icons.local_hospital_outlined,
                  content: analysis['recommended_doctors'],
                ),
                buildSectionCard(
                  title: strings.supportOptionsTitle,
                  icon: Icons.medication_liquid_outlined,
                  content: analysis['possible_support_options'],
                ),
                buildSectionCard(
                  title: strings.recommendationsTitle,
                  icon: Icons.fact_check_outlined,
                  content: analysis['recommendations'],
                ),
                buildSectionCard(
                  title: strings.disclaimerTitle,
                  icon: Icons.info_outline_rounded,
                  content: analysis['disclaimer'],
                ),
                buildBottomInfoCard(),
              ],
            ],
          ),
        ),
      ),
    );
  }
}