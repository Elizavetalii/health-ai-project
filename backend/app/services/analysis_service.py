# app/services/analysis_service.py

# Импортируем функцию, которая отправляет запрос в AI-модель.
# Она возвращает либо словарь с ответом модели, либо None,
# если AI недоступен или ответ не удалось корректно получить.
from app.services.ai_service import analyze_with_deepseek

# Импортируем вспомогательные функции:
# - parse_number_from_text: ищет числовой показатель в тексте анализа
# - build_abnormal_item: создаёт удобный словарь для abnormal_values
from app.utils.parsing_utils import parse_number_from_text, build_abnormal_item


def fallback_empty_result(summary: str) -> dict:
    """
    Возвращает "пустой", но полностью корректный результат.

    Зачем нужен этот fallback:
    - если AI не ответил;
    - если AI вернул сломанный JSON;
    - если данных слишком мало;
    - если backend должен всё равно отдать понятную структуру.

    Почему это важно:
    frontend (например, Flutter) обычно ожидает фиксированный набор полей.
    Если какие-то поля отсутствуют, интерфейс может сломаться
    или просто не показать часть информации.
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
    Нормализует ответ AI-модели.

    Почему это нужно:
    модель может:
    - пропустить часть полей;
    - вернуть данные не того типа;
    - вернуть неполный JSON;
    - где-то вернуть строку вместо списка.

    Эта функция приводит результат к стабильной форме,
    чтобы дальше backend и frontend работали предсказуемо.
    """
    if not isinstance(result, dict):
        return fallback_empty_result("Не удалось корректно получить ответ модели")

    # Достаём вложенный блок analysis_overview.
    # Если модель не вернула словарь, заменяем пустым.
    analysis_overview = result.get("analysis_overview", {})
    if not isinstance(analysis_overview, dict):
        analysis_overview = {}

    # Достаём вложенный блок data_quality.
    data_quality = analysis_overview.get("data_quality", {})
    if not isinstance(data_quality, dict):
        data_quality = {}

    # Достаём блок срочности.
    urgency_assessment = result.get("urgency_assessment", {})
    if not isinstance(urgency_assessment, dict):
        urgency_assessment = {}

    # Возвращаем единый и стабильный формат результата.
    return {
        "summary": str(result.get("summary", "Нет данных")),
        "analysis_overview": {
            "overall_impression": str(
                analysis_overview.get(
                    "overall_impression",
                    result.get("summary", "Нет данных"),
                )
            ),
            "main_concerns": analysis_overview.get("main_concerns", []),
            "data_quality": {
                "is_text_complete": bool(data_quality.get("is_text_complete", True)),
                "possible_ocr_issues": data_quality.get("possible_ocr_issues", []),
                "comment": str(
                    data_quality.get(
                        "comment",
                        "Оценка качества данных не была подробно указана.",
                    )
                ),
            },
        },
        "abnormal_values": result.get("abnormal_values", []),
        "borderline_values": result.get("borderline_values", []),
        "normal_but_relevant_values": result.get("normal_but_relevant_values", []),
        "possible_conditions": result.get("possible_conditions", []),
        "patterns_and_connections": result.get("patterns_and_connections", []),
        "risks": result.get("risks", []),
        "recommended_doctors": result.get("recommended_doctors", []),
        "additional_tests": result.get("additional_tests", []),
        "medication_discussion_options": result.get("medication_discussion_options", []),
        "medication_examples_info": result.get("medication_examples_info", []),
        "caution_notes": result.get("caution_notes", []),
        "possible_support_options": result.get("possible_support_options", []),
        "recommendations": result.get("recommendations", []),
        "red_flags": result.get("red_flags", []),
        "urgency_assessment": {
            "level": str(urgency_assessment.get("level", "routine")),
            "comment": str(
                urgency_assessment.get(
                    "comment",
                    "Недостаточно данных для оценки срочности.",
                )
            ),
        },
        "missing_important_data": result.get("missing_important_data", []),
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
    Это локальный fallback-анализ.

    Он используется, если:
    - нет API-ключа,
    - AI не ответил,
    - ответ модели не удалось распарсить,
    - произошла ошибка сети.

    Важно:
    это не полноценная медицинская интерпретация,
    а упрощённая резервная логика.
    """
    # Основные списки, которые мы будем заполнять.
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

    # ------------------------------------------------------
    # Ниже извлекаем некоторые базовые показатели из текста.
    # Это простая резервная логика.
    # При желании её можно расширить дальше.
    # ------------------------------------------------------
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

    # ======================================================
    # Гемоглобин
    # ======================================================
    if hemoglobin is not None:
        if hemoglobin < 120:
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

            medication_discussion_options.append(
                {
                    "category": "Коррекция возможного дефицитного состояния",
                    "examples": [
                        "железо",
                        "двухвалентное железо",
                        "железо (III) гидроксид полимальтозат",
                        "витамин B12",
                        "фолаты",
                    ],
                    "comment": "Такие варианты могут рассматриваться при подтверждении соответствующего дефицита.",
                    "limitations": "Без подтверждения дефицита и оценки причины анемии выбор может быть неуместен.",
                }
            )

            medication_examples_info.append(
                {
                    "category": "Возможные варианты препаратов железа",
                    "active_ingredients": [
                        "железо",
                        "железо (III) гидроксид полимальтозат",
                        "сульфат железа",
                    ],
                    "example_brands": [
                        "Мальтофер",
                        "Сорбифер",
                        "Феррум Лек",
                    ],
                    "note": "Это не назначение, а примеры препаратов, которые могут встречаться на рынке.",
                }
            )

            caution_notes.append(
                {
                    "context": "подозрение на дефицит железа или анемическое направление",
                    "avoid": [
                        "самостоятельный выбор препарата без подтверждения причины снижения гемоглобина",
                        "приём без оценки ферритина и сопутствующих показателей",
                    ],
                    "reason": "Снижение гемоглобина не всегда связано именно с дефицитом железа.",
                }
            )

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

        elif 120 <= hemoglobin <= 125:
            borderline_values.append(
                {
                    "name": "Гемоглобин",
                    "value": str(hemoglobin),
                    "comment": "Пограничное значение, которое может быть клинически важным в зависимости от пола, жалоб и других показателей.",
                }
            )

        elif hemoglobin > 160:
            abnormal_values.append(
                build_abnormal_item(
                    "Гемоглобин",
                    hemoglobin,
                    "high",
                    "Показатель может быть повышен и требует очной оценки с учётом симптомов, гидратации и общего контекста.",
                )
            )

            risks.append("Повышение гемоглобина требует оценки с учётом симптомов, анамнеза и возможного обезвоживания.")

            recommended_doctors.append(
                {
                    "specialist": "Терапевт",
                    "reason": "Для первичной оценки причины повышения гемоглобина.",
                }
            )

            recommendations.append("Обсудить результат с врачом и при необходимости пересдать анализ.")

            possible_conditions.append(
                {
                    "name": "Гемоконцентрация или иное состояние с повышением гемоглобина",
                    "probability_percent": 45,
                    "confidence": "low",
                    "comment": "Нужно учитывать гидратацию, курение, высоту проживания, хронические состояния и другие показатели крови.",
                }
            )
    else:
        missing_important_data.append("Не удалось уверенно извлечь показатель гемоглобина.")

    # ======================================================
    # Глюкоза
    # ======================================================
    if glucose is not None:
        if glucose > 6.1:
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

            medication_discussion_options.append(
                {
                    "category": "Поддержка углеводного обмена",
                    "examples": [
                        "подходы к коррекции питания",
                        "средства, применяемые при нарушениях углеводного обмена по решению врача",
                    ],
                    "comment": "Конкретный выбор зависит от подтверждения отклонения и клинического контекста.",
                    "limitations": "Без уточнения условий сдачи анализа и подтверждения нарушений делать конкретный выбор преждевременно.",
                }
            )

            caution_notes.append(
                {
                    "context": "повышенная глюкоза",
                    "avoid": [
                        "самостоятельная интерпретация как окончательного диагноза",
                        "самостоятельный подбор средств без подтверждающих анализов",
                    ],
                    "reason": "Нужно уточнить, сдавался ли анализ натощак, и подтвердить отклонение.",
                }
            )

            recommendations.extend([
                "Уточнить, сдавался ли анализ натощак.",
                "Обсудить с врачом необходимость дополнительного обследования.",
            ])

            possible_conditions.append(
                {
                    "name": "Нарушение углеводного обмена",
                    "probability_percent": 65,
                    "confidence": "moderate",
                    "comment": "Повышенная глюкоза поддерживает это направление, но для большей уверенности нужны условия сдачи, повторный анализ и/или HbA1c.",
                }
            )

        elif 5.6 <= glucose <= 6.1:
            borderline_values.append(
                {
                    "name": "Глюкоза",
                    "value": str(glucose),
                    "comment": "Пограничное значение, которое может требовать внимания в зависимости от условий сдачи и факторов риска.",
                }
            )
    else:
        missing_important_data.append("Не удалось уверенно извлечь показатель глюкозы.")

    # ======================================================
    # Холестерин
    # ======================================================
    if cholesterol is not None:
        if cholesterol > 5.2:
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

            medication_discussion_options.append(
                {
                    "category": "Поддержка липидного обмена",
                    "examples": [
                        "изменение питания",
                        "физическая активность",
                        "липидснижающие подходы по решению врача",
                    ],
                    "comment": "Выбор зависит от общего сердечно-сосудистого риска и структуры липидограммы.",
                    "limitations": "Без полного липидного профиля и оценки общего риска конкретика ограничена.",
                }
            )

            recommendations.extend([
                "Обсудить питание, физическую активность и семейный анамнез.",
                "При необходимости сдать расширенный липидный профиль.",
            ])

            possible_conditions.append(
                {
                    "name": "Липидное нарушение",
                    "probability_percent": 60,
                    "confidence": "moderate",
                    "comment": "Повышенный общий холестерин поддерживает это направление, но желательно видеть полный липидный профиль.",
                }
            )

        elif 5.0 <= cholesterol <= 5.2:
            borderline_values.append(
                {
                    "name": "Холестерин",
                    "value": str(cholesterol),
                    "comment": "Пограничное значение, которое желательно оценивать вместе с другими факторами риска и липидным профилем.",
                }
            )
    else:
        missing_important_data.append("Не удалось уверенно извлечь показатель холестерина.")

    # ======================================================
    # Лейкоциты
    # ======================================================
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

            recommended_doctors.append(
                {
                    "specialist": "Терапевт",
                    "reason": "Для оценки клинического значения повышения лейкоцитов.",
                }
            )

            recommendations.append("Сопоставить результат с жалобами, температурой и другими показателями крови.")

            possible_conditions.append(
                {
                    "name": "Воспалительный или инфекционный процесс",
                    "probability_percent": 55,
                    "confidence": "low",
                    "comment": "Повышенные лейкоциты поддерживают это направление, но важны симптомы, формула крови и другие маркеры.",
                }
            )

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

            recommended_doctors.extend([
                {
                    "specialist": "Терапевт",
                    "reason": "Для первичной оценки снижения лейкоцитов.",
                },
                {
                    "specialist": "Гематолог",
                    "reason": "Если снижение подтверждается или сочетается с другими отклонениями крови.",
                },
            ])

            recommendations.append("При необходимости повторить общий анализ крови.")
    else:
        missing_important_data.append("Не удалось уверенно извлечь показатель лейкоцитов.")

    # ======================================================
    # Тромбоциты
    # ======================================================
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

            recommended_doctors.extend([
                {
                    "specialist": "Терапевт",
                    "reason": "Для первичной оценки результата.",
                },
                {
                    "specialist": "Гематолог",
                    "reason": "Если снижение подтверждается или выражено.",
                },
            ])

            recommendations.append("Обсудить результат с врачом и необходимость повторного анализа.")

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

            recommended_doctors.append(
                {
                    "specialist": "Терапевт",
                    "reason": "Для первичной оценки причины повышения тромбоцитов.",
                }
            )

            recommendations.append("Повторить анализ по рекомендации врача.")
    else:
        missing_important_data.append("Не удалось уверенно извлечь показатель тромбоцитов.")

    # ======================================================
    # Связи между показателями
    # ======================================================
    if hemoglobin is not None and hemoglobin < 120:
        if platelets is not None and platelets > 400:
            patterns_and_connections.append(
                "Сочетание сниженного гемоглобина и повышенных тромбоцитов иногда может встречаться при дефицитных состояниях, но требует уточнения."
            )

        if leukocytes is not None and leukocytes > 9.0:
            patterns_and_connections.append(
                "Сочетание сниженного гемоглобина и повышенных лейкоцитов требует оценки на предмет одновременного воспалительного и дефицитного направления."
            )

    if glucose is not None and glucose > 6.1 and cholesterol is not None and cholesterol > 5.2:
        patterns_and_connections.append(
            "Сочетание повышенной глюкозы и повышенного холестерина может указывать на метаболическое направление риска и требует более широкой оценки факторов обмена."
        )

    # ======================================================
    # Учёт комментария пользователя
    # ======================================================
    if user_comment.strip():
        lowered_comment = user_comment.lower()

        if any(word in lowered_comment for word in ["слабость", "усталость", "головокруж", "weakness", "fatigue"]):
            risks.append("Жалобы пользователя стоит учитывать при интерпретации результатов.")
            recommendations.append("Сообщить врачу о симптомах, их длительности и выраженности.")

            if hemoglobin is not None and hemoglobin < 120:
                patterns_and_connections.append(
                    "Симптомы слабости или утомляемости могут быть связаны со снижением гемоглобина, если это подтверждается клинически."
                )

    # ======================================================
    # Red flags
    # ======================================================
    if hemoglobin is not None and hemoglobin < 90:
        red_flags.append(
            "Значительно сниженный гемоглобин может требовать более быстрой очной оценки, особенно при слабости, одышке, сердцебиении или головокружении."
        )

    if glucose is not None and glucose > 10:
        red_flags.append(
            "Выраженно повышенная глюкоза требует более быстрого очного обсуждения, особенно при жажде, учащённом мочеиспускании, слабости или ухудшении самочувствия."
        )

    # ======================================================
    # Общий summary
    # ======================================================
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

    # ======================================================
    # Удаление дублей
    # ======================================================
    def unique_list_of_dicts(items: list[dict]) -> list[dict]:
        seen = set()
        result = []

        for item in items:
            key = str(sorted(item.items()))
            if key not in seen:
                seen.add(key)
                result.append(item)

        return result

    abnormal_values = unique_list_of_dicts(abnormal_values)
    borderline_values = unique_list_of_dicts(borderline_values)
    normal_but_relevant_values = unique_list_of_dicts(normal_but_relevant_values)
    possible_conditions = unique_list_of_dicts(possible_conditions)
    recommended_doctors = unique_list_of_dicts(recommended_doctors)
    additional_tests = unique_list_of_dicts(additional_tests)
    medication_discussion_options = unique_list_of_dicts(medication_discussion_options)
    medication_examples_info = unique_list_of_dicts(medication_examples_info)
    caution_notes = unique_list_of_dicts(caution_notes)

    risks = list(dict.fromkeys(risks))
    possible_support_options = list(dict.fromkeys(possible_support_options))
    recommendations = list(dict.fromkeys(recommendations))
    red_flags = list(dict.fromkeys(red_flags))
    missing_important_data = list(dict.fromkeys(missing_important_data))
    patterns_and_connections = list(dict.fromkeys(patterns_and_connections))

    # ======================================================
    # Оценка срочности
    # ======================================================
    urgency_level = "routine"
    urgency_comment = "Ситуация по доступным данным не выглядит как явно срочная, но требует плановой медицинской интерпретации."

    if red_flags:
        urgency_level = "soon"
        urgency_comment = "Есть признаки, которые желательно обсудить очно без излишнего откладывания, особенно если есть симптомы."

    # ======================================================
    # Финальный результат
    # ======================================================
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
        "risks": risks,
        "recommended_doctors": recommended_doctors,
        "additional_tests": additional_tests,
        "medication_discussion_options": medication_discussion_options,
        "medication_examples_info": medication_examples_info,
        "caution_notes": caution_notes,
        "possible_support_options": possible_support_options,
        "recommendations": recommendations,
        "red_flags": red_flags,
        "urgency_assessment": {
            "level": urgency_level,
            "comment": urgency_comment,
        },
        "missing_important_data": missing_important_data,
        "disclaimer": "Это не диагноз и не назначение лечения. Для точной интерпретации анализа нужна очная консультация врача.",
    }


def analyze_text(extracted_text: str, user_comment: str = "", language: str = "ru") -> dict:
    """
    Главная функция анализа текста.

    Логика:
    1. Сначала пробуем получить результат от AI.
    2. Если получилось — нормализуем.
    3. Если не получилось — используем локальный fallback.
    """
    ai_result = analyze_with_deepseek(extracted_text, user_comment, language)

    if ai_result is not None:
        return normalize_ai_result(ai_result)

    return local_medical_analysis(extracted_text, user_comment, language)