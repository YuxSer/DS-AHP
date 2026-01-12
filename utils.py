from typing import List, Set, Dict, Any, Union
from config import Config


class Utils:
    """Утилиты для работы с данными"""

    @staticmethod
    def parse_group_string(group_str: str, separators: List[str] = None) -> List[str]:
        """
        Парсинг строки группы альтернатив

        Args:
            group_str: строка с группой альтернатив
            separators: список разделителей

        Returns:
            Список альтернатив
        """
        if separators is None:
            separators = Config.GROUP_SEPARATORS

        group_str = str(group_str).strip()

        # Если строка пустая
        if not group_str:
            return []

        # Если это 'ALL' или 'Θ' (универсальное множество)
        if group_str.upper() in ['ALL', 'THETA', 'Θ', 'Ω']:
            return ['ALL']

        # Пробуем разные разделители
        for separator in separators:
            if separator in group_str:
                parts = [part.strip() for part in group_str.split(separator)]
                return [p for p in parts if p]

        # Если нет разделителей - возвращаем как есть
        return [group_str]

    @staticmethod
    def parse_gdm_group_string(group_str: str) -> List[str]:
        """Парсинг строки группы для GDM режима"""
        return Utils.parse_group_string(group_str, Config.GDM_GROUP_SEPARATORS)

    @staticmethod
    def format_group_string(alts: List[str], separator: str = ','):
        """Форматирование списка альтернатив в строку"""
        if not alts:
            return ""

        # Если это универсальное множество
        if alts == ['ALL'] or set(alts) == {'ALL'}:
            return 'ALL'

        return separator.join(sorted(alts))

    @staticmethod
    def validate_positive_float(prompt: str, min_val: float = 0.0,
                                max_val: float = None) -> float:
        """
        Валидация положительного числа с плавающей точкой

        Args:
            prompt: приглашение для ввода
            min_val: минимальное значение
            max_val: максимальное значение

        Returns:
            Валидное число
        """
        while True:
            try:
                value = float(input(prompt).strip())

                if value < min_val:
                    print(f"❌ Значение должно быть не меньше {min_val}!")
                    continue

                if max_val is not None and value > max_val:
                    print(f"❌ Значение должно быть не больше {max_val}!")
                    continue

                return value

            except ValueError:
                print("❌ Введите числовое значение!")

    @staticmethod
    def validate_positive_int(prompt: str, min_val: int = 1,
                              max_val: int = None) -> int:
        """
        Валидация положительного целого числа
        """
        while True:
            try:
                value = int(input(prompt).strip())

                if value < min_val:
                    print(f"❌ Значение должно быть не меньше {min_val}!")
                    continue

                if max_val is not None and value > max_val:
                    print(f"❌ Значение должно быть не больше {max_val}!")
                    continue

                return value

            except ValueError:
                print("❌ Введите целое число!")

    @staticmethod
    def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
        """
        Нормализация весов к сумме = 1

        Args:
            weights: словарь {имя: вес}

        Returns:
            Нормализованный словарь весов
        """
        if not weights:
            return {}

        total = sum(weights.values())

        if abs(total) < 1e-10:
            print("⚠️  Сумма весов равна 0!")
            return {k: 0.0 for k in weights.keys()}

        if abs(total - 1.0) > 0.001:
            print(f"⚠️  Сумма весов ({total:.4f}) не равна 1. Нормализую...")

        return {k: v / total for k, v in weights.items()}

    @staticmethod
    def round_value(value: float, precision: int = None) -> float:
        """Округление значения с заданной точностью"""
        if precision is None:
            precision = Config.PRECISION

        return round(value, precision)

    @staticmethod
    def format_value(value: float, precision: int = None) -> str:
        """Форматирование значения для вывода"""
        if precision is None:
            precision = Config.PRECISION

        if abs(value) < 10 ** (-precision):
            return f"0.{'0' * precision}"

        return f"{value:.{precision}f}"

    @staticmethod
    def calculate_geometric_mean(values: List[float]) -> float:
        """
        Вычисление среднего геометрического

        Args:
            values: список значений

        Returns:
            Среднее геометрическое
        """
        if not values:
            return 0.0

        # Фильтруем нулевые значения
        non_zero_values = [v for v in values if v > 1e-10]

        if not non_zero_values:
            return 0.0

        # Вычисляем произведение
        product = 1.0
        for v in non_zero_values:
            product *= v

        # Извлекаем корень n-ой степени
        n = len(values)  # Используем общее количество элементов
        return product ** (1.0 / n)

    @staticmethod
    def calculate_cpv_sum(cpvs: Dict[str, float]) -> float:
        """
        Проверка суммы CPV

        Args:
            cpvs: словарь {критерий: CPV}

        Returns:
            Сумма CPV
        """
        return sum(cpvs.values())

    @staticmethod
    def normalize_cpvs(cpvs: Dict[str, float]) -> Dict[str, float]:
        """
        Нормализация CPV к сумме = 1

        Args:
            cpvs: словарь {критерий: CPV}

        Returns:
            Нормализованные CPV
        """
        total = sum(cpvs.values())

        if abs(total) < 1e-10:
            print("⚠️  Сумма CPV равна 0!")
            return {k: 0.0 for k in cpvs.keys()}

        return {k: v / total for k, v in cpvs.items()}

    @staticmethod
    def print_matrix_info(matrix, name: str):
        """
        Вывод информации о матрице

        Args:
            matrix: матрица (DataFrame или list of lists)
            name: название матрицы
        """
        print(f"\n{name}:")

        try:
            # Если это pandas DataFrame
            import pandas as pd
            if isinstance(matrix, pd.DataFrame):
                print(f"Размер: {matrix.shape}")
                print("Матрица:")
                print(matrix.to_string())
                return
        except ImportError:
            pass

        # Если это список списков
        if isinstance(matrix, list):
            print(f"Размер: {len(matrix)}x{len(matrix[0]) if matrix else 0}")
            print("Матрица:")
            for row in matrix:
                print("  " + " ".join(f"{x:.4f}" for x in row))
            return

        # Общий случай
        print(matrix)

    @staticmethod
    def print_dict_table(data: Dict[str, Any], title: str = "",
                         sort_by_value: bool = False):
        """
        Вывод словаря в виде таблицы

        Args:
            data: словарь для вывода
            title: заголовок таблицы
            sort_by_value: сортировать по значению
        """
        if not data:
            print(f"{title}: пусто")
            return

        if title:
            print(f"\n{title}")
            print("-" * 40)

        items = data.items()
        if sort_by_value:
            items = sorted(items, key=lambda x: x[1], reverse=True)

        max_key_len = max(len(str(k)) for k in data.keys())

        for key, value in items:
            if isinstance(value, float):
                value_str = f"{value:.6f}"
            else:
                value_str = str(value)

            print(f"  {str(key):{max_key_len}} : {value_str}")

    @staticmethod
    def validate_cpvs(cpvs: Dict[str, float], criteria: List[str]) -> bool:
        """
        Проверка корректности CPV

        Args:
            cpvs: словарь CPV
            criteria: список критериев

        Returns:
            True если корректно
        """
        if not cpvs:
            print("❌ CPV не заданы")
            return False

        # Проверяем, что все критерии есть в CPV
        for criterion in criteria:
            if criterion not in cpvs:
                print(f"❌ Нет CPV для критерия '{criterion}'")
                return False

        # Проверяем значения
        for criterion, cpv in cpvs.items():
            if cpv < Config.MIN_CPV_VALUE or cpv > Config.MAX_CPV_VALUE:
                print(f"❌ CPV для '{criterion}' = {cpv} вне диапазона "
                      f"[{Config.MIN_CPV_VALUE}, {Config.MAX_CPV_VALUE}]")
                return False

        # Проверяем сумму (должна быть <= 1)
        total = sum(cpvs.values())
        if total > 1.0 + 1e-5:
            print(f"❌ Сумма CPV = {total:.3f} > 1.0")
            return False

        return True

    @staticmethod
    def validate_preferences(preferences: Dict[str, Dict[str, int]],
                             alternatives: List[str]) -> bool:
        """
        Проверка корректности предпочтений

        Args:
            preferences: словарь предпочтений
            alternatives: список альтернатив

        Returns:
            True если корректно
        """
        if not preferences:
            return True

        for criterion, groups in preferences.items():
            all_alts_in_criterion = []
            preference_values = []

            for group_str in groups.keys():
                group_alts = [alt.strip() for alt in group_str.split(',')]
                all_alts_in_criterion.extend(group_alts)

                pref_value = groups[group_str]
                preference_values.append(pref_value)

            # Проверяем количество альтернатив
            if len(all_alts_in_criterion) != len(alternatives):
                return False

            # Проверяем уникальность альтернатив
            if len(set(all_alts_in_criterion)) != len(alternatives):
                return False

            # Проверяем, что все альтернативы присутствуют
            missing = set(alternatives) - set(all_alts_in_criterion)
            if missing:
                return False

            # Проверяем значения предпочтений (должны быть положительными)
            if any(p <= 0 for p in preference_values):
                return False

            # Проверяем уникальность предпочтений
            if len(set(preference_values)) != len(preference_values):
                return False

        # Проверяем, что каждая альтернатива встречается не более одного раза в критерии
        for criterion, groups in preferences.items():
            alt_occurrences = {}
            for group_str in groups.keys():
                group_alts = Utils.parse_gdm_group_string(group_str)
                for alt in group_alts:
                    if alt in alt_occurrences:
                        print(f"❌ Альтернатива '{alt}' встречается более одного раза "
                              f"в критерии '{criterion}'")
                        return False
                    alt_occurrences[alt] = True

        return True