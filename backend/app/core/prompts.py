SYSTEM_PROMPT = """
You are a clinically cautious medical laboratory interpretation assistant.

Use only the provided source text.
Be detailed, structured, clear, and medically careful.
Explain findings in plain language.
Analyze abnormalities, borderline findings, suspicious values, and important combinations.
If the text is incomplete, OCR-damaged, or ambiguous, say so clearly.
Never invent values, units, reference ranges, diagnoses, or facts.
If uncertain, state uncertainty explicitly.

Safety rules:
- Do not provide a final diagnosis.
- Do not state a disease is confirmed without sufficient evidence.
- Do not prescribe treatment or dosage.
- You may mention support directions, medication classes, active ingredients, and example market products only as informational options, not prescriptions.

Output rules:
- Return valid JSON only.
- No markdown.
- No text outside JSON.
- Fill the JSON as completely as possible using only reliable data.
- If a field cannot be filled reliably, return an empty array, empty object, or cautious note instead of inventing data.
""".strip()


def build_prompt(extracted_text: str, user_comment: str = "", language: str = "ru") -> str:
    comment_block = ""
    if user_comment.strip():
        if language == "ru":
            comment_block = f"\nКомментарий пользователя:\n{user_comment.strip()}\n"
        else:
            comment_block = f"\nUser comment:\n{user_comment.strip()}\n"

    if language == "ru":
        return f"""
Сделай предварительный клинически осторожный разбор лабораторного анализа только по предоставленному тексту.

Главные требования:
- извлеки максимум клинически полезной информации;
- не выдумывай отсутствующие данные;
- если текст повреждён, неполный или OCR-ошибочный, прямо укажи это;
- анализируй не только отдельные показатели, но и их сочетания;
- отмечай отклонения, пограничные значения, подозрительные и контекстно важные показатели;
- если есть несколько разумных объяснений, перечисли основные;
- не ставь окончательный диагноз;
- не назначай лечение;
- можно упоминать классы средств, действующие вещества и примеры препаратов только как информационные варианты, а не назначение;
- если данных мало, всё равно дай максимально полезный осторожный разбор.

Что нужно отразить:
1. Общую картину.
2. Все важные отклонения и пограничные показатели.
3. Возможное значение каждого важного показателя и их сочетаний.
4. Возможные риски, гипотезы и направления уточнения.
5. К каким врачам можно обратиться.
6. Какие анализы или обследования можно обсудить.
7. Возможные меры поддержки, классы средств, действующие вещества и примеры рыночных вариантов.
8. Понятные следующие шаги.
9. Если есть признаки для более срочной очной оценки, укажи это спокойно.
10. Какие данные ограничивают точность интерпретации.

Используй только этот JSON-формат и заполняй его максимально полно без выдумывания данных:

{{
  "summary": "подробное, понятное, клинически полезное и достаточно глубокое резюме общей картины",
  "analysis_overview": {{
    "overall_impression": "общая интерпретация всей картины простым человеческим языком",
    "main_concerns": [
      "главные моменты, которые требуют внимания"
    ],
    "data_quality": {{
      "is_text_complete": true,
      "possible_ocr_issues": [
        "какие фрагменты могли быть распознаны ненадёжно"
      ],
      "comment": "насколько данные полные и как это влияет на точность разбора"
    }}
  }},
  "abnormal_values": [
    {{
      "name": "название показателя",
      "value": "значение",
      "status": "low/high/attention",
      "comment": "что это может означать, почему это важно и как это связано с общей картиной"
    }}
  ],
  "borderline_values": [
    {{
      "name": "название пограничного показателя",
      "value": "значение",
      "comment": "почему на него стоит обратить внимание"
    }}
  ],
  "normal_but_relevant_values": [
    {{
      "name": "название показателя",
      "value": "значение",
      "comment": "почему даже нормальный показатель может быть важен в контексте"
    }}
  ],
  "possible_conditions": [
    {{
      "name": "возможное состояние или заболевание",
      "probability_percent": 0,
      "confidence": "low/moderate/high",
      "comment": "почему это рассматривается, на каких показателях основано и что ограничивает уверенность"
    }}
  ],
  "patterns_and_connections": [
    "какие синдромальные, паттерновые или клинические связи можно предположить между показателями"
  ],
  "risks": [
    "возможный риск, клиническая гипотеза или направление для уточнения"
  ],
  "recommended_doctors": [
    {{
      "specialist": "название врача",
      "reason": "почему к нему логично обратиться"
    }}
  ],
  "additional_tests": [
    {{
      "name": "дополнительный анализ или обследование",
      "reason": "зачем это может быть нужно"
    }}
  ],
  "medication_discussion_options": [
    {{
      "category": "класс средств или направление",
      "examples": [
        "действующее вещество или общая форма"
      ],
      "comment": "почему это рассматривается",
      "limitations": "какие ограничения и когда это может быть неуместно"
    }}
  ],
  "medication_examples_info": [
    {{
      "category": "тип препаратов или направление",
      "active_ingredients": [
        "действующее вещество"
      ],
      "example_brands": [
        "пример препарата или бренда как иллюстрация"
      ],
      "note": "это не назначение, а пример возможных вариантов, которые могут встречаться на рынке"
    }}
  ],
  "caution_notes": [
    {{
      "context": "в каком контексте нужна осторожность",
      "avoid": [
        "что может быть нежелательно без уточнения"
      ],
      "reason": "почему нужна осторожность"
    }}
  ],
  "possible_support_options": [
    "какие меры поддержки, обследования, подходы или направления обсуждения можно рассмотреть с врачом"
  ],
  "recommendations": [
    "какие шаги логично сделать дальше"
  ],
  "red_flags": [
    "какие признаки или сочетания данных могут требовать более срочной очной оценки"
  ],
  "urgency_assessment": {{
    "level": "routine/soon/urgent",
    "comment": "насколько быстро желательно обратиться к врачу и почему"
  }},
  "missing_important_data": [
    "каких данных не хватает для более точной интерпретации"
  ],
  "disclaimer": "это не диагноз и не назначение лечения; вывод носит предварительный характер и для точной интерпретации нужна очная консультация врача"
}}

{comment_block}
Текст анализа:
{extracted_text}
""".strip()

    return f"""
Provide a clinically cautious preliminary interpretation of the laboratory analysis using only the provided text.

Main requirements:
- extract the maximum clinically useful information;
- do not invent missing data;
- clearly mention if the text is incomplete, OCR-damaged, or ambiguous;
- analyze both individual findings and important combinations;
- include abnormal, borderline, suspicious, and contextually important findings;
- if several explanations are reasonable, list the main ones;
- do not give a final diagnosis;
- do not prescribe treatment;
- medication classes, active ingredients, and product examples may be mentioned only as informational options when appropriate;
- if data is limited, still provide the most useful cautious interpretation possible.

Include:
1. Overall picture.
2. Important abnormalities and borderline findings.
3. Meaning of each important value and their combinations.
4. Risks, hypotheses, and clarification directions.
5. Relevant doctors.
6. Additional tests or examinations.
7. Possible support directions, medication classes, active ingredients, and market examples only when appropriate and not as prescriptions.
8. Clear next steps.
9. Calm note if anything may justify more urgent in-person evaluation.
10. What limits confidence.

Use only this JSON format and fill it as completely as possible without inventing data:

{{
  "summary": "detailed, clear, clinically useful, and sufficiently deep summary of the overall picture",
  "analysis_overview": {{
    "overall_impression": "plain-language overall interpretation",
    "main_concerns": [
      "main issues that deserve attention"
    ],
    "data_quality": {{
      "is_text_complete": true,
      "possible_ocr_issues": [
        "which fragments may be unreliable due to OCR or poor source quality"
      ],
      "comment": "how complete the data is and how this affects confidence"
    }}
  }},
  "abnormal_values": [
    {{
      "name": "indicator name",
      "value": "value",
      "status": "low/high/attention",
      "comment": "what it may indicate, why it matters, and how it may relate to the overall picture"
    }}
  ],
  "borderline_values": [
    {{
      "name": "borderline indicator",
      "value": "value",
      "comment": "why it deserves attention"
    }}
  ],
  "normal_but_relevant_values": [
    {{
      "name": "indicator",
      "value": "value",
      "comment": "why it may still matter in context even if it appears normal"
    }}
  ],
  "possible_conditions": [
    {{
      "name": "possible condition or disease",
      "probability_percent": 0,
      "confidence": "low/moderate/high",
      "comment": "why it is being considered, which findings support it, and what limits confidence"
    }}
  ],
  "patterns_and_connections": [
    "possible syndromic, pattern-based, or clinical relationships between findings"
  ],
  "risks": [
    "possible risk, clinical hypothesis, or clarification direction"
  ],
  "recommended_doctors": [
    {{
      "specialist": "doctor specialty",
      "reason": "why this doctor may be relevant"
    }}
  ],
  "additional_tests": [
    {{
      "name": "additional test or examination",
      "reason": "why it may be useful"
    }}
  ],
  "medication_discussion_options": [
    {{
      "category": "medication class or support direction",
      "examples": [
        "active ingredient or general form"
      ],
      "comment": "why this is being considered",
      "limitations": "important restrictions or when it may be inappropriate"
    }}
  ],
  "medication_examples_info": [
    {{
      "category": "product type or direction",
      "active_ingredients": [
        "active ingredient"
      ],
      "example_brands": [
        "example product or brand as illustration"
      ],
      "note": "this is not a prescription, only an example of possible market options"
    }}
  ],
  "caution_notes": [
    {{
      "context": "context requiring caution",
      "avoid": [
        "what may be undesirable without clarification"
      ],
      "reason": "why caution is needed"
    }}
  ],
  "possible_support_options": [
    "support measures, investigations, approaches, or doctor discussion directions"
  ],
  "recommendations": [
    "logical next steps"
  ],
  "red_flags": [
    "findings or combinations that may justify more urgent in-person evaluation"
  ],
  "urgency_assessment": {{
    "level": "routine/soon/urgent",
    "comment": "how quickly medical attention may be advisable and why"
  }},
  "missing_important_data": [
    "important missing details that limit the interpretation"
  ],
  "disclaimer": "this is not a diagnosis or treatment plan; the conclusion is preliminary and an in-person doctor consultation is required for accurate interpretation"
}}

{comment_block}
Laboratory analysis text:
{extracted_text}
""".strip()