# config.py
"""
Конфигурационные параметры для DS/AHP-GDM системы
"""


class Config:
    # Режимы работы системы
    MODE_SINGLE = "single"  # Классический DS/AHP (один ЛПР)
    MODE_GROUP = "group"  # Групповой DS/AHP-GDM (несколько экспертов)

    MODE_NAMES = {
        MODE_SINGLE: "Одиночный режим (классический DS/AHP)",
        MODE_GROUP: "Групповой режим (DS/AHP-GDM)"
    }

    # Методы расчета весов критериев (для одиночного режима)
    WEIGHT_METHOD_MANUAL = "manual"
    WEIGHT_METHOD_AUTO = "auto"

    WEIGHT_METHOD_NAMES = {
        WEIGHT_METHOD_MANUAL: "Ручной ввод",
        WEIGHT_METHOD_AUTO: "Автоматический расчет"
    }

    # Правила комбинирования
    COMBINATION_RULE_DEMPSTER = "dempster"
    COMBINATION_RULE_YAGER = "yager"
    COMBINATION_RULE_ADAPTIVE = "adaptive"  # НОВОЕ ПРАВИЛО

    COMBINATION_RULE_NAMES = {
        COMBINATION_RULE_DEMPSTER: "Правило Демпстера",
        COMBINATION_RULE_YAGER: "Правило Ягера",
        COMBINATION_RULE_ADAPTIVE: "Адаптивное правило"  # НОВОЕ ПРАВИЛО
    }

    COMBINATION_RULE_DESCRIPTIONS = {
        COMBINATION_RULE_DEMPSTER: "Нормализует конфликт, перераспределяет среди непротиворечивых свидетельств",
        COMBINATION_RULE_YAGER: "Переносит конфликт в универсальное множество Θ, не нормализует",
        COMBINATION_RULE_ADAPTIVE: "Автоматически выбирает между Демпстером и Ягером на основе уровня конфликта"
    }

    # Параметры адаптивного правила
    DEFAULT_CONFLICT_THRESHOLD = 0.4  # Порог по умолчанию
    MIN_CONFLICT_THRESHOLD = 0.0
    MAX_CONFLICT_THRESHOLD = 1.0

    # Значения по умолчанию
    DEFAULT_COMBINATION_RULE = COMBINATION_RULE_DEMPSTER
    DEFAULT_WEIGHT_METHOD = WEIGHT_METHOD_MANUAL
    DEFAULT_PESSIMISM_COEFFICIENT = 0.5
    DEFAULT_CONFIDENCE_THRESHOLD = 0.001

    # Диапазоны значений
    MIN_PESSIMISM_COEFFICIENT = 0.0
    MAX_PESSIMISM_COEFFICIENT = 1.0
    MIN_CPV_VALUE = 0.0
    MAX_CPV_VALUE = 1.0

    # Точность вычислений
    PRECISION = 6
    GDM_PRECISION = 8

    # Шкала предпочтений для GDM
    PREFERENCE_SCALE = {
        1: "Умеренное предпочтение",
        2: "Между умеренным и сильным",
        3: "Сильное предпочтение",
        4: "Между сильным и очень сильным",
        5: "Очень сильное предпочтение",
        6: "Между очень сильным и крайне сильным",
        7: "Крайне сильное предпочтение"
    }

    # Разделители для групп альтернатив
    GROUP_SEPARATORS = [',', ';', ' ', '&']
    GDM_GROUP_SEPARATORS = [',', ';', '&']

    # Экспорт
    EXPORT_DIR = "results"
    EXPORT_FORMATS = ['xml', 'json', 'csv', 'txt']


