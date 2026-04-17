# app/models/schemas.py

# Импортируем BaseModel для создания Pydantic-схем.
# Эти схемы помогают:
# - описывать структуру данных,
# - валидировать ответ,
# - красиво показывать Swagger/OpenAPI.
from pydantic import BaseModel
from typing import List


class AbnormalValue(BaseModel):
    """
    Один отклонённый показатель анализа.
    """
    name: str
    value: str
    status: str
    comment: str


class BorderlineValue(BaseModel):
    """
    Один пограничный показатель.
    """
    name: str
    value: str
    comment: str


class PossibleCondition(BaseModel):
    """
    Возможное состояние / направление / заболевание,
    которое модель считает вероятным.
    """
    name: str
    probability_percent: int
    confidence: str
    comment: str


class DoctorRecommendation(BaseModel):
    """
    Рекомендация по врачу:
    к кому идти и почему.
    """
    specialist: str
    reason: str


class AdditionalTest(BaseModel):
    """
    Дополнительный анализ или обследование.
    """
    name: str
    reason: str


class MedicationDiscussionOption(BaseModel):
    """
    Варианты веществ / направлений / классов средств,
    которые можно обсуждать по логике анализа.
    """
    category: str
    examples: List[str]
    comment: str
    limitations: str


class MedicationExampleInfo(BaseModel):
    """
    Блок с примерами рыночных вариантов:
    действующие вещества + примеры препаратов/брендов.

    Важно:
    это не назначение, а информационная справка.
    """
    category: str
    active_ingredients: List[str]
    example_brands: List[str]
    note: str


class CautionNote(BaseModel):
    """
    Блок с предупреждением:
    где нужна осторожность, что нежелательно и почему.
    """
    context: str
    avoid: List[str]
    reason: str


class DataQuality(BaseModel):
    """
    Оценка качества данных:
    насколько текст полный,
    были ли проблемы OCR,
    насколько это влияет на вывод.
    """
    is_text_complete: bool
    possible_ocr_issues: List[str]
    comment: str


class AnalysisOverview(BaseModel):
    """
    Общий обзор результата анализа.
    """
    overall_impression: str
    main_concerns: List[str]
    data_quality: DataQuality


class UrgencyAssessment(BaseModel):
    """
    Оценка срочности:
    routine / soon / urgent
    """
    level: str
    comment: str


class AnalysisResult(BaseModel):
    """
    Главная схема результата анализа.
    Именно такой объект backend будет отдавать наружу.
    """
    summary: str
    analysis_overview: AnalysisOverview
    abnormal_values: List[AbnormalValue]
    borderline_values: List[BorderlineValue]
    normal_but_relevant_values: List[BorderlineValue]
    possible_conditions: List[PossibleCondition]
    patterns_and_connections: List[str]
    risks: List[str]
    recommended_doctors: List[DoctorRecommendation]
    additional_tests: List[AdditionalTest]
    medication_discussion_options: List[MedicationDiscussionOption]
    medication_examples_info: List[MedicationExampleInfo]
    caution_notes: List[CautionNote]
    possible_support_options: List[str]
    recommendations: List[str]
    red_flags: List[str]
    urgency_assessment: UrgencyAssessment
    missing_important_data: List[str]
    disclaimer: str