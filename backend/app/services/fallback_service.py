# app/services/fallback_service.py

# Импортируем вспомогательные функции для локального резервного анализа.
# - parse_number_from_text: пытается найти число по шаблону в тексте анализа
# - build_abnormal_item: создаёт объект для списка abnormal_values
from app.utils.parsing_utils import parse_number_from_text, build_abnormal_item


def _ensure_list(value):
    """
    Гарантирует, что значение является списком.

    Если AI или другая логика вернула не список,
    вместо ошибки мы просто возвращаем пустой список.
    """
    return value if isinstance(value, list) else []


def _ensure_dict(value):
    """
    Гарантирует, что значение является словарём.

    Если пришёл не dict, возвращаем пустой словарь.
    """
    return value if isinstance(value, dict) else {}


def fallback_empty_result(summary: str) -> dict:
    """
    Возвращает "пустой", но полностью корректный результат.

    Это нужно, чтобы frontend всегда получал стабильную структуру,
    даже если AI недоступен или данных недостаточно.
    """
    return {
        "summary": summary,
        "analysis_overview": {
            "overall_impression": summary,
            "main_concerns": [],
            "data_quality": {
                "is_text_complete": False,
                "possible_ocr_issues": [],
                "comment": "Недостаточно данных для полной интерпретации.",
            },
        },
        "abnormal_values": [],
        "borderline_values": [],
        "normal_but_relevant_values": [],
        "possible_conditions": [],
        "patterns_and_connections": [],
        "risks": [],
        "recommended_doctors": [],
        "additional_tests": [],
        "medication_discussion_options": [],
        "medication_examples_info": [],
        "caution_notes": [],
        "possible_support_options": [],
        "recommendations": [],
        "red_flags": [],
        "urgency_assessment": {
            "level": "routine",
            "comment": "Недостаточно данных для точной оценки срочности.",
        },
        "missing_important_data": [],
        "disclaimer": "Это не диагноз. Для точной интерпретации нужна консультация врача.",
    }


def normalize_ai_result(result: dict) -> dict:
    """
    Приводит ответ AI к стабильной структуре.

    Это нужно, потому что модель может:
    - пропустить часть полей;
    - вернуть не тот тип данных;
    - частично нарушить JSON-контракт.

    Эта функция делает ответ безопаснее для frontend.
    """
    if not isinstance(result, dict):
        return fallback_empty_result("Не удалось корректно получить ответ модели")

    analysis_overview = _ensure_dict(result.get("analysis_overview"))
    data_quality = _ensure_dict(analysis_overview.get("data_quality"))
    urgency_assessment = _ensure_dict(result.get("urgency_assessment"))

    return {
        "summary": str(result.get("summary", "Нет данных")),
        "analysis_overview": {
            "overall_impression": str(
                analysis_overview.get(
                    "overall_impression",
                    result.get("summary", "Нет данных"),
                )
            ),
            "main_concerns": _ensure_list(analysis_overview.get("main_concerns")),
            "data_quality": {
                "is_text_complete": bool(data_quality.get("is_text_complete", True)),
                "possible_ocr_issues": _ensure_list(
                    data_quality.get("possible_ocr_issues")
                ),
                "comment": str(
                    data_quality.get(
                        "comment",
                        "Оценка качества данных не была подробно указана.",
                    )
                ),
            },
        },
        "abnormal_values": _ensure_list(result.get("abnormal_values")),
        "borderline_values": _ensure_list(result.get("borderline_values")),
        "normal_but_relevant_values": _ensure_list(
            result.get("normal_but_relevant_values")
        ),
        "possible_conditions": _ensure_list(result.get("possible_conditions")),
        "patterns_and_connections": _ensure_list(
            result.get("patterns_and_connections")
        ),
        "risks": _ensure_list(result.get("risks")),
        "recommended_doctors": _ensure_list(result.get("recommended_doctors")),
        "additional_tests": _ensure_list(result.get("additional_tests")),
        "medication_discussion_options": _ensure_list(
            result.get("medication_discussion_options")
        ),
        "medication_examples_info": _ensure_list(
            result.get("medication_examples_info")
        ),
        "caution_notes": _ensure_list(result.get("caution_notes")),
        "possible_support_options": _ensure_list(
            result.get("possible_support_options")
        ),
        "recommendations": _ensure_list(result.get("recommendations")),
        "red_flags": _ensure_list(result.get("red_flags")),
        "urgency_assessment": {
            "level": str(urgency_assessment.get("level", "routine")),
            "comment": str(
                urgency_assessment.get(
                    "comment",
                    "Недостаточно данных для оценки срочности.",
                )
            ),
        },
        "missing_important_data": _ensure_list(
            result.get("missing_important_data")
        ),
        "disclaimer": str(
            result.get(
                "disclaimer",
                "Это не диагноз. Для точной интерпретации нужна консультация врача.",
            )
        ),
    }


def local_medical_analysis(
    extracted_text: str,
    user_comment: str = "",
    language: str = "ru",
) -> dict:
    """
    Локальный резервный анализ.

    Используется, если:
    - AI недоступен;
    - ответ модели не удалось распарсить;
    - произошла ошибка сети.

    Это упрощённая логика, которая не заменяет AI-разбор,
    но позволяет вернуть пользователю корректную структуру данных.
    """
    abnormal_values = []
    borderline_values = []
    normal_but_relevant_values = []
    possible_conditions = []
    patterns_and_connections = []
    risks = []
    recommended_doctors = []
    additional_tests = []
    medication_discussion_options = []
    medication_examples_info = []
    caution_notes = []
    possible_support_options = []
    recommendations = []
    red_flags = []
    missing_important_data = []

    hemoglobin = parse_number_from_text(
        r"(?:гемоглобин|hemoglobin|hgb)[^\d]{0,20}(\d+[.,]?\d*)",
        extracted_text,
    )

    glucose = parse_number_from_text(
        r"(?:глюкоза|glucose)[^\d]{0,20}(\d+[.,]?\d*)",
        extracted_text,
    )

    cholesterol = parse_number_from_text(
        r"(?:холестерин|cholesterol)[^\d]{0,20}(\d+[.,]?\d*)",
        extracted_text,
    )

    leukocytes = parse_number_from_text(
        r"(?:лейкоциты|leukocytes|wbc)[^\d]{0,20}(\d+[.,]?\d*)",
        extracted_text,
    )

    platelets = parse_number_from_text(
        r"(?:тромбоциты|platelets|plt)[^\d]{0,20}(\d+[.,]?\d*)",
        extracted_text,
    )

    if hemoglobin is not None and hemoglobin < 120:
        abnormal_values.append(
            build_abnormal_item(
                "Гемоглобин",
                hemoglobin,
                "low",
                "Показатель может быть снижен. Это может соответствовать анемическому или дефицитному направлению и требует уточнения причин.",
            )
        )
        risks.append("Стоит исключить анемию или дефицитные состояния.")
        recommended_doctors.extend([
            {
                "specialist": "Терапевт",
                "reason": "Для первичной оценки общего состояния и направления на дообследование.",
            },
            {
                "specialist": "Гематолог",
                "reason": "Если снижение гемоглобина подтверждается или выражено клинически.",
            },
        ])
        additional_tests.extend([
            {"name": "Ферритин", "reason": "Для оценки запасов железа."},
            {"name": "Железо сыворотки", "reason": "Для уточнения железодефицитного направления."},
            {"name": "Витамин B12", "reason": "Для исключения дефицитных причин анемии."},
            {"name": "Фолиевая кислота", "reason": "Может быть значима при анемическом синдроме."},
        ])
        possible_support_options.append(
            "С врачом можно обсудить обследование на дефицит железа, ферритина, витамина B12 и фолатов."
        )
        recommendations.extend([
            "Обсудить с врачом необходимость повторного общего анализа крови.",
            "Проверить дефицитные показатели по рекомендации врача.",
        ])
        possible_conditions.append(
            {
                "name": "Анемическое или дефицитное состояние",
                "probability_percent": 70,
                "confidence": "moderate",
                "comment": "Снижение гемоглобина поддерживает это направление, но без остальных показателей крови и клиники уверенность ограничена.",
            }
        )
    elif hemoglobin is None:
        missing_important_data.append("Не удалось уверенно извлечь показатель гемоглобина.")

    if glucose is not None and glucose > 6.1:
        abnormal_values.append(
            build_abnormal_item(
                "Глюкоза",
                glucose,
                "high",
                "Показатель может быть выше желаемых значений. Это требует уточнения условий сдачи анализа и дополнительной оценки углеводного обмена.",
            )
        )
        risks.append("Стоит исключить нарушение углеводного обмена.")
        recommended_doctors.extend([
            {
                "specialist": "Терапевт",
                "reason": "Для первичной оценки результата и маршрутизации.",
            },
            {
                "specialist": "Эндокринолог",
                "reason": "Если повышение подтверждается или есть факторы риска нарушений углеводного обмена.",
            },
        ])
        additional_tests.extend([
            {"name": "HbA1c", "reason": "Для оценки среднего уровня глюкозы за последние месяцы."},
            {"name": "Повторная глюкоза натощак", "reason": "Для подтверждения отклонения."},
        ])
        recommendations.extend([
            "Уточнить, сдавался ли анализ натощак.",
            "Обсудить с врачом необходимость дополнительного обследования.",
        ])
    elif glucose is None:
        missing_important_data.append("Не удалось уверенно извлечь показатель глюкозы.")

    if cholesterol is not None and cholesterol > 5.2:
        abnormal_values.append(
            build_abnormal_item(
                "Холестерин",
                cholesterol,
                "high",
                "Показатель может быть повышен и может иметь значение для сердечно-сосудистого риска.",
            )
        )
        risks.append("Повышенный холестерин может быть фактором сердечно-сосудистого риска.")
        recommended_doctors.extend([
            {
                "specialist": "Терапевт",
                "reason": "Для первичной интерпретации и оценки факторов риска.",
            },
            {
                "specialist": "Кардиолог",
                "reason": "Если есть сопутствующие факторы риска, жалобы или выраженные липидные нарушения.",
            },
        ])
        additional_tests.append(
            {"name": "Расширенный липидный профиль", "reason": "Для уточнения характера липидных нарушений."}
        )
    elif cholesterol is None:
        missing_important_data.append("Не удалось уверенно извлечь показатель холестерина.")

    if leukocytes is not None:
        if leukocytes > 9.0:
            abnormal_values.append(
                build_abnormal_item(
                    "Лейкоциты",
                    leukocytes,
                    "high",
                    "Показатель может быть повышен. Это может соответствовать воспалительной или инфекционной реакции, но требует сопоставления с клиникой.",
                )
            )
            risks.append("Повышение лейкоцитов может встречаться при воспалении или инфекции.")
        elif leukocytes < 4.0:
            abnormal_values.append(
                build_abnormal_item(
                    "Лейкоциты",
                    leukocytes,
                    "low",
                    "Показатель может быть снижен и требует врачебной оценки в зависимости от выраженности, жалоб и других данных.",
                )
            )
            risks.append("Снижение лейкоцитов требует оценки врачом.")
    else:
        missing_important_data.append("Не удалось уверенно извлечь показатель лейкоцитов.")

    if platelets is not None:
        if platelets < 150:
            abnormal_values.append(
                build_abnormal_item(
                    "Тромбоциты",
                    platelets,
                    "low",
                    "Показатель может быть снижен и требует дополнительной оценки с учётом клинической картины.",
                )
            )
            risks.append("Снижение тромбоцитов требует дополнительной оценки.")
        elif platelets > 400:
            abnormal_values.append(
                build_abnormal_item(
                    "Тромбоциты",
                    platelets,
                    "high",
                    "Показатель может быть повышен и требует интерпретации с учётом общей картины крови, воспаления и других причин.",
                )
            )
            risks.append("Повышение тромбоцитов требует интерпретации с учётом клинической картины.")
    else:
        missing_important_data.append("Не удалось уверенно извлечь показатель тромбоцитов.")

    if user_comment.strip():
        lowered_comment = user_comment.lower()
        if any(word in lowered_comment for word in ["слабость", "усталость", "головокруж", "weakness", "fatigue"]):
            risks.append("Жалобы пользователя стоит учитывать при интерпретации результатов.")
            recommendations.append("Сообщить врачу о симптомах, их длительности и выраженности.")

    if hemoglobin is not None and hemoglobin < 90:
        red_flags.append(
            "Значительно сниженный гемоглобин может требовать более быстрой очной оценки, особенно при слабости, одышке, сердцебиении или головокружении."
        )

    if glucose is not None and glucose > 10:
        red_flags.append(
            "Выраженно повышенная глюкоза требует более быстрого очного обсуждения, особенно при жажде, учащённом мочеиспускании, слабости или ухудшении самочувствия."
        )

    if not abnormal_values and not borderline_values:
        summary = (
            "Явных отклонений по автоматически распознанным показателям не найдено, "
            "однако автоматический анализ ограничен и результат всё равно стоит показать врачу."
        )
        risks.append("Локальный автоматический анализ ограничен и не заменяет медицинскую интерпретацию.")
        recommended_doctors.append(
            {
                "specialist": "Терапевт",
                "reason": "Для сопоставления результатов анализа с жалобами и анамнезом.",
            }
        )
        recommendations.extend([
            "Показать результат врачу.",
            "Сопоставить показатели с жалобами и анамнезом.",
        ])
    else:
        summary = (
            "Обнаружены показатели, которые могут требовать дополнительного внимания, "
            "дообследования или очной оценки врачом."
        )

    if not possible_support_options:
        possible_support_options.append(
            "Все дальнейшие шаги, дополнительные обследования и варианты поддержки следует обсуждать с врачом."
        )

    urgency_level = "routine"
    urgency_comment = "Ситуация по доступным данным не выглядит как явно срочная, но требует плановой медицинской интерпретации."

    if red_flags:
        urgency_level = "soon"
        urgency_comment = "Есть признаки, которые желательно обсудить очно без излишнего откладывания, особенно если есть симптомы."

    return {
        "summary": summary,
        "analysis_overview": {
            "overall_impression": summary,
            "main_concerns": risks[:5],
            "data_quality": {
                "is_text_complete": False,
                "possible_ocr_issues": [],
                "comment": "Локальный fallback-анализ ограничен и опирается только на автоматически извлечённые фрагменты текста.",
            },
        },
        "abnormal_values": abnormal_values,
        "borderline_values": borderline_values,
        "normal_but_relevant_values": normal_but_relevant_values,
        "possible_conditions": possible_conditions,
        "patterns_and_connections": patterns_and_connections,
        "risks": list(dict.fromkeys(risks)),
        "recommended_doctors": recommended_doctors,
        "additional_tests": additional_tests,
        "medication_discussion_options": medication_discussion_options,
        "medication_examples_info": medication_examples_info,
        "caution_notes": caution_notes,
        "possible_support_options": list(dict.fromkeys(possible_support_options)),
        "recommendations": list(dict.fromkeys(recommendations)),
        "red_flags": list(dict.fromkeys(red_flags)),
        "urgency_assessment": {
            "level": urgency_level,
            "comment": urgency_comment,
        },
        "missing_important_data": list(dict.fromkeys(missing_important_data)),
        "disclaimer": "Это не диагноз и не назначение лечения. Для точной интерпретации анализа нужна очная консультация врача.",
    }