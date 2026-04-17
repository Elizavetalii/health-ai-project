import 'dart:io'; // Работа с локальным файлом, выбранным пользователем

import 'package:file_picker/file_picker.dart'; // Выбор файлов через системный диалог
import 'package:flutter/material.dart'; // Базовые UI-компоненты Flutter
import 'package:image_picker/image_picker.dart'; // Выбор фото из галереи и камеры

import '../core/app_colors.dart'; // Единая цветовая палитра приложения
import '../generated/app_localizations.dart'; // Локализованные строки интерфейса
import '../main.dart'; // Доступ к смене языка через корневой виджет приложения
import '../models/analysis_result.dart'; // Типизированная модель результата анализа
import '../services/analysis_api_service.dart'; // Сервис отправки файла на backend
import '../l10n/app_en.arb'; // Сервис 
import '../l10n/app_ru.arb'; // Сервис 

/// Главный экран приложения.
///
/// Экран объединяет основной пользовательский сценарий:
/// - выбор файла анализа;
/// - выбор изображения из галереи или камеры;
/// - добавление комментария;
/// - отправку данных на backend;
/// - отображение структурированного результата анализа.
class UploadScreen extends StatefulWidget {
  const UploadScreen({super.key});

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  /// Контроллер текстового поля для пользовательского комментария.
  ///
  /// Через него приложение получает текст,
  /// который пользователь хочет добавить к анализу.
  final TextEditingController commentController = TextEditingController();

  /// Компонент для выбора изображения из галереи или камеры.
  final ImagePicker imagePicker = ImagePicker();

  /// Сервис сетевого взаимодействия с backend.
  ///
  /// Экран не работает напрямую с HTTP, а делегирует это отдельному слою.
  final AnalysisApiService apiService = AnalysisApiService();

  /// Выбранный пользователем файл анализа.
  File? selectedFile;

  /// Имя выбранного файла для отображения в интерфейсе.
  String selectedFileName = 'Файл пока не выбран';

  /// Флаг состояния загрузки.
  ///
  /// Используется для:
  /// - блокировки повторной отправки,
  /// - отключения некоторых действий,
  /// - показа индикатора обработки.
  bool isLoading = false;

  /// Типизированный результат анализа, полученный с backend.
  AnalysisResult? analysisResult;

  /// Служебная meta-информация от backend.
  ///
  /// Например:
  /// - источник обработки;
  /// - тип файла;
  /// - использовался ли комментарий пользователя.
  Map<String, dynamic>? meta;

  /// Текст ошибки, который показывается пользователю.
  String? errorText;



  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    // Если файл ещё не выбран, обновляем подпись
    // в соответствии с текущим языком интерфейса.
    if (selectedFile == null) {
      final strings = AppLocalizations.of(context)!;
      selectedFileName = strings.noFileSelected;
    }
  }

  @override
  void dispose() {
    // Освобождаем контроллер при уничтожении экрана.
    commentController.dispose();
    super.dispose();
  }

  /// Текущий код языка интерфейса.
  ///
  /// Этот же код передаётся на backend,
  /// чтобы результат анализа приходил на нужном языке.
  String get currentLanguageCode => Localizations.localeOf(context).languageCode;

  /// Открывает системный диалог выбора файла.
  ///
  /// Используется для документов:
  /// - PDF
  /// - DOC / DOCX
  /// - XLS / XLSX
  /// - CSV / TXT
  ///
  /// А также может использоваться для изображений,
  /// если пользователь хочет выбрать их именно как файл.
  Future<void> pickFile() async {
    final result = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: [
        'pdf',
        'jpg',
        'jpeg',
        'png',
        'doc',
        'docx',
        'xls',
        'xlsx',
        'csv',
        'txt',
      ],
    );

    if (result != null && result.files.single.path != null) {
      setState(() {
        selectedFile = File(result.files.single.path!);
        selectedFileName = result.files.single.name;
        errorText = null;
      });
    }
  }

  /// Выбирает изображение из заданного источника:
  /// - галерея
  /// - камера
  ///
  /// После выбора изображение приводится к локальному File,
  /// чтобы его можно было отправить на backend так же, как обычный файл.
  Future<void> pickImageFromSource(ImageSource source) async {
    try {
      final XFile? image = await imagePicker.pickImage(
        source: source,

        // Снижаем качество изображения умеренно,
        // чтобы не отправлять слишком тяжёлые файлы без необходимости.
        imageQuality: 85,
      );

      if (image != null) {
        setState(() {
          selectedFile = File(image.path);
          selectedFileName = image.name;
          errorText = null;
        });
      }
    } catch (e) {
      setState(() {
        errorText = currentLanguageCode == 'ru'
            ? 'Ошибка выбора изображения: $e'
            : 'Image picking error: $e';
      });
    }
  }

  /// Показывает пользователю варианты выбора источника.
  ///
  /// Это более удобный UX, чем один-единственный выбор файла,
  /// потому что пользователь может:
  /// - открыть галерею;
  /// - сделать фото с камеры;
  /// - выбрать документ как файл.
  void showPickOptions() {
    final strings = AppLocalizations.of(context)!;

    showModalBottomSheet(
      context: context,
      builder: (bottomSheetContext) {
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.photo),
                title: Text(
                  currentLanguageCode == 'ru'
                      ? 'Выбрать из галереи'
                      : 'Choose from gallery',
                ),
                onTap: () {
                  Navigator.pop(bottomSheetContext);
                  pickImageFromSource(ImageSource.gallery);
                },
              ),
              ListTile(
                leading: const Icon(Icons.camera_alt),
                title: Text(
                  currentLanguageCode == 'ru'
                      ? 'Сделать фото'
                      : 'Take a photo',
                ),
                onTap: () {
                  Navigator.pop(bottomSheetContext);
                  pickImageFromSource(ImageSource.camera);
                },
              ),
              ListTile(
                leading: const Icon(Icons.insert_drive_file),
                title: Text(
                  currentLanguageCode == 'ru'
                      ? 'Выбрать файл'
                      : 'Choose file',
                ),
                subtitle: Text(strings.supportedFormats),
                onTap: () {
                  Navigator.pop(bottomSheetContext);
                  pickFile();
                },
              ),
            ],
          ),
        );
      },
    );
  }

  /// Отправляет выбранный файл на backend.
  ///
  /// Логика:
  /// - проверяем, что файл выбран;
  /// - переводим экран в состояние загрузки;
  /// - вызываем API;
  /// - сохраняем результат или ошибку.
  Future<void> sendFile() async {
    final strings = AppLocalizations.of(context)!;

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
      final response = await apiService.analyzeFile(
        file: selectedFile!,
        fileName: selectedFileName,
        language: currentLanguageCode,
        userComment: commentController.text.trim(),
      );

      if (response.success) {
        setState(() {
          analysisResult = response.analysisResult;
          meta = response.meta;
        });
      } else {
        setState(() {
          errorText = response.message ?? 'Unknown error';
        });
      }
    } catch (e) {
      setState(() {
        errorText = currentLanguageCode == 'ru'
            ? 'Ошибка при отправке: $e'
            : 'Send error: $e';
      });
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

/// Возвращает локализованную подпись уровня срочности.
///
/// Backend хранит короткие технические коды:
/// - routine
/// - soon
/// - urgent
///
/// В интерфейсе пользователю нужно показывать
/// уже понятный переведённый текст.
String getUrgencyLabel(String level, AppLocalizations strings) {
  switch (level) {
    case 'routine':
      return strings.urgencyRoutine;
    case 'soon':
      return strings.urgencySoon;
    case 'urgent':
      return strings.urgencyUrgent;
    default:
      return level;
  }
}
  /// Возвращает читаемую подпись источника обработки результата.
  String getMetaSourceLabel(AppLocalizations strings) {
    final source = meta?['source_type']?.toString() ?? '';
    if (source == 'deepseek') {
      return strings.deepseekLabel;
    }
    return strings.fallbackLabel;
  }

  /// Возвращает читаемый тип файла из meta-данных.
  String getMetaFileType() {
    return (meta?['file_type']?.toString() ?? '-').toUpperCase();
  }

  /// Возвращает признак, был ли учтён комментарий пользователя.
  String getMetaCommentUsed(AppLocalizations strings) {
    final used = meta?['user_comment_used'] == true;
    return used ? strings.commentUsedYes : strings.commentUsedNo;
  }

  /// Цвет статуса показателя.
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

  /// Цвет подложки карточки показателя.
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

  /// Локализованная подпись статуса показателя.
  String getStatusLabel(String status, AppLocalizations strings) {
    switch (status) {
      case 'low':
        return strings.statusLow;
      case 'high':
        return strings.statusHigh;
      default:
        return strings.statusAttention;
    }
  }

  /// Верхняя hero-карточка с позиционированием продукта.
  Widget buildHeroCard(AppLocalizations strings) {
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

  /// Информационная плашка о предварительном характере результата.
  Widget buildInfoStrip(AppLocalizations strings) {
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

  /// Переключатель языка интерфейса.
  ///
  /// Язык интерфейса и язык backend-запроса синхронизированы.
  Widget buildLanguageSelector(AppLocalizations strings) {
    final currentCode = Localizations.localeOf(context).languageCode;

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
                  selected: currentCode == 'ru',
                  onSelected: (_) {
                    MyApp.of(context).changeLanguage('ru');
                  },
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: ChoiceChip(
                  label: const Text('English'),
                  selected: currentCode == 'en',
                  onSelected: (_) {
                    MyApp.of(context).changeLanguage('en');
                  },
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// Карточка выбора файла, ввода комментария и запуска анализа.
  Widget buildUploadCard(AppLocalizations strings) {
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
            onTap: isLoading ? null : showPickOptions,
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

  /// Карточка meta-информации о результате.
  Widget buildMetaCard(AppLocalizations strings) {
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
                label: getMetaSourceLabel(strings),
                isPrimary: true,
              ),
              buildInfoChip(
                icon: Icons.insert_drive_file_outlined,
                label: '${strings.fileTypeTitle}: ${getMetaFileType()}',
              ),
              buildInfoChip(
                icon: Icons.comment_outlined,
                label: '${strings.commentUsedTitle}: ${getMetaCommentUsed(strings)}',
              ),
            ],
          ),
        ],
      ),
    );
  }

  /// Компактный элемент для отображения служебной информации.
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

  /// Универсальная карточка секции результата.
  Widget buildSectionCard({
    required String title,
    required IconData icon,
    required Widget child,
  }) {
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
          child,
        ],
      ),
    );
  }

  /// Базовый рендер списка строк.
  Widget buildStringList(AppLocalizations strings, List<String> items) {
    if (items.isEmpty) {
      return Text(
        strings.noData,
        style: const TextStyle(
          fontSize: 15,
          height: 1.5,
          color: AppColors.textSecondary,
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: items
          .map(
            (e) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Text(
                '• $e',
                style: const TextStyle(
                  fontSize: 15,
                  height: 1.5,
                  color: AppColors.textSecondary,
                ),
              ),
            ),
          )
          .toList(),
    );
  }

  /// Специальная карточка отклонённых показателей с цветовой акцентуацией.
  Widget buildAbnormalValuesCard(AppLocalizations strings) {
    final values = analysisResult?.abnormalValues ?? [];

    if (values.isEmpty) {
      return buildSectionCard(
        title: strings.abnormalitiesTitle,
        icon: Icons.analytics_outlined,
        child: Text(
          strings.noData,
          style: const TextStyle(
            fontSize: 15,
            height: 1.5,
            color: AppColors.textSecondary,
          ),
        ),
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
            return Container(
              width: double.infinity,
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: getStatusBackground(item.status),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: getStatusColor(item.status).withOpacity(0.18),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          item.name,
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
                          color: getStatusColor(item.status),
                          borderRadius: BorderRadius.circular(30),
                        ),
                        child: Text(
                          getStatusLabel(item.status, strings),
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
                    item.value,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w800,
                      color: getStatusColor(item.status),
                    ),
                  ),
                  if (item.comment.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Text(
                      item.comment,
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
          }),
        ],
      ),
    );
  }

  /// Нижняя информационная плашка с пояснением по интерпретации.
  Widget buildBottomInfoCard(AppLocalizations strings) {
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
    final strings = AppLocalizations.of(context)!;
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
              buildHeroCard(strings),
              const SizedBox(height: 16),
              buildInfoStrip(strings),
              const SizedBox(height: 16),
              buildLanguageSelector(strings),
              const SizedBox(height: 16),
              buildUploadCard(strings),
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

                buildMetaCard(strings),

                buildSectionCard(
                  title: strings.summaryTitle,
                  icon: Icons.summarize_outlined,
                  child: Text(
                    analysis.summary,
                    style: const TextStyle(
                      fontSize: 15,
                      height: 1.55,
                      color: AppColors.textSecondary,
                    ),
                  ),
                ),

                buildAbnormalValuesCard(strings),

                buildSectionCard(
                  title: strings.possibleConditionsTitle,
                  icon: Icons.psychology_alt_outlined,
                  child: buildStringList(
                    strings,
                    analysis.possibleConditions
                        .map(
                          (e) =>
                              '${e.name} — ${e.probabilityPercent}% (${e.confidence}). ${e.comment}',
                        )
                        .toList(),
                  ),
                ),

                buildSectionCard(
                  title: strings.patternsTitle,
                  icon: Icons.hub_outlined,
                  child: buildStringList(strings, analysis.patternsAndConnections),
                ),

                buildSectionCard(
                  title: strings.risksTitle,
                  icon: Icons.warning_amber_rounded,
                  child: buildStringList(strings, analysis.risks),
                ),

                buildSectionCard(
                  title: strings.doctorsTitle,
                  icon: Icons.local_hospital_outlined,
                  child: buildStringList(
                    strings,
                    analysis.recommendedDoctors
                        .map((e) => '${e.specialist} — ${e.reason}')
                        .toList(),
                  ),
                ),

                buildSectionCard(
                  title: strings.additionalTestsTitle,
                  icon: Icons.science_outlined,
                  child: buildStringList(
                    strings,
                    analysis.additionalTests
                        .map((e) => '${e.name} — ${e.reason}')
                        .toList(),
                  ),
                ),

                buildSectionCard(
                  title: strings.medicineOptionsTitle,
                  icon: Icons.medication_liquid_outlined,
                  child: buildStringList(
                    strings,
                    analysis.medicationDiscussionOptions
                        .map(
                          (e) =>
                              '${e.category}: ${e.examples.join(", ")}. ${e.comment}. Ограничения: ${e.limitations}',
                        )
                        .toList(),
                  ),
                ),

                buildSectionCard(
                  title: strings.medicineExamplesTitle,
                  icon: Icons.local_pharmacy_outlined,
                  child: buildStringList(
                    strings,
                    analysis.medicationExamplesInfo
                        .map(
                          (e) =>
                              '${e.category}: ${e.activeIngredients.join(", ")}. Примеры: ${e.exampleBrands.join(", ")}. ${e.note}',
                        )
                        .toList(),
                  ),
                ),

                buildSectionCard(
                  title: strings.cautionTitle,
                  icon: Icons.error_outline_rounded,
                  child: buildStringList(
                    strings,
                    analysis.cautionNotes
                        .map(
                          (e) =>
                              '${e.context}: избегать — ${e.avoid.join(", ")}. Причина: ${e.reason}',
                        )
                        .toList(),
                  ),
                ),

                buildSectionCard(
                  title: strings.supportOptionsTitle,
                  icon: Icons.favorite_border_outlined,
                  child: buildStringList(strings, analysis.possibleSupportOptions),
                ),

                buildSectionCard(
                  title: strings.recommendationsTitle,
                  icon: Icons.fact_check_outlined,
                  child: buildStringList(strings, analysis.recommendations),
                ),

                buildSectionCard(
                  title: strings.urgencyTitle,
                  icon: Icons.schedule_outlined,
                  child: Text(
                    '${getUrgencyLabel(analysis.urgencyAssessment.level, strings)}: ${analysis.urgencyAssessment.comment}',
                    style: const TextStyle(
                      fontSize: 15,
                      height: 1.55,
                      color: AppColors.textSecondary,
                    ),
                  ),
                ),

                buildSectionCard(
                  title: strings.redFlagsTitle,
                  icon: Icons.report_gmailerrorred_outlined,
                  child: buildStringList(strings, analysis.redFlags),
                ),

                buildSectionCard(
                  title: strings.missingDataTitle,
                  icon: Icons.help_outline_rounded,
                  child: buildStringList(strings, analysis.missingImportantData),
                ),

                buildSectionCard(
                  title: strings.disclaimerTitle,
                  icon: Icons.info_outline_rounded,
                  child: Text(
                    analysis.disclaimer,
                    style: const TextStyle(
                      fontSize: 15,
                      height: 1.55,
                      color: AppColors.textSecondary,
                    ),
                  ),
                ),

                buildBottomInfoCard(strings),
              ],
            ],
          ),
        ),
      ),
    );
  }
}