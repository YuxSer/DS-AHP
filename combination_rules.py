from typing import Dict, List, Tuple
from collections import defaultdict
from config import Config


class CombinationRules:
    """Класс для работы с правилами комбинирования"""

    def __init__(self, all_alternatives: List[str], conflict_threshold: float = None):
        """
        Инициализация правил комбинирования

        Args:
            all_alternatives: список всех альтернатив
            conflict_threshold: порог для адаптивного правила
        """
        self.all_alternatives = all_alternatives
        self.universal_set = frozenset(all_alternatives)  # Θ
        self.conflict_history = []

        # Порог для адаптивного правила
        if conflict_threshold is None:
            self.conflict_threshold = Config.DEFAULT_CONFLICT_THRESHOLD
        else:
            self.conflict_threshold = conflict_threshold

        # Для отладки
        self.step_decisions = []  # Решения на каждом шаге

    def calculate_conflict(self, bpa1: Dict[frozenset, float],
                            bpa2: Dict[frozenset, float]) -> float:
        """
        Вычисление коэффициента конфликта K между двумя BPA

        Формула: K = Σ_{B∩C=∅} m1(B)m2(C)
        """
        conflict = 0.0

        for s1, m1 in bpa1.items():
            for s2, m2 in bpa2.items():
                if len(s1.intersection(s2)) == 0:
                    conflict += m1 * m2

        return conflict

    # ==================== ПРАВИЛО ДЕМПСТЕРА ====================

    def dempster_combine(self, bpa1: Dict[frozenset, float],
                         bpa2: Dict[frozenset, float]) -> Dict[frozenset, float]:
        """
        Правило комбинирования Демпстера для двух источников
        """
        print("\n" + "-" * 50)
        print("ПРАВИЛО ДЕМПСТЕРА")
        print("-" * 50)

        intersections = defaultdict(float)
        conflict = 0.0

        # Вычисляем все пересечения
        for s1, m1 in bpa1.items():
            for s2, m2 in bpa2.items():
                intersection = s1.intersection(s2)
                product = m1 * m2

                if len(intersection) == 0:
                    conflict += product
                else:
                    intersections[intersection] += product

        K = conflict

        print(f"Коэффициент конфликтности K = {K:.6f}")

        if K >= 1.0 - 1e-10:
            print("⚠️  Полный конфликт между свидетельствами!")
            print("   Возвращаем универсальное множество Θ")
            return {self.universal_set: 1.0}

        # Нормализация (деление на 1-K)
        normalization_factor = 1.0 - K

        combined_bpa = {}
        for focal, mass in intersections.items():
            combined_bpa[focal] = mass / normalization_factor

        # Сохраняем историю конфликтов
        self.conflict_history.append(K)

        # Выводим результат
        self.print_combination_result(combined_bpa, K, "Демпстер")

        return combined_bpa

    def dempster_combine_multiple(self, *bpas: Dict[frozenset, float]) -> Dict[frozenset, float]:
        """
        Правило комбинирования Демпстера для произвольного числа источников
        """
        print("\n" + "=" * 60)
        print(f"КОМБИНИРОВАНИЕ {len(bpas)} ИСТОЧНИКОВ ПО ПРАВИЛУ ДЕМПСТЕРА")
        print("=" * 60)

        if len(bpas) == 0:
            print("❌ Нет данных для комбинирования")
            return {}
        elif len(bpas) == 1:
            print("⚠️  Только один источник, возвращаем как есть")
            return bpas[0]

        print(f"Будет последовательно объединено {len(bpas)} BPA")

        # Начинаем с первого источника
        result = bpas[0]

        # Последовательно комбинируем с остальными источниками
        for i, bpa in enumerate(bpas[1:], 1):
            print(f"\n--- Шаг {i}: Комбинирование с источником {i + 1} ---")
            result = self.dempster_combine(result, bpa)

        return result

    def yager_combine(self, bpa1: Dict[frozenset, float],
                      bpa2: Dict[frozenset, float]) -> Dict[frozenset, float]:
        """
        Правило комбинирования Ягера для двух источников
        """
        print("\n" + "-" * 50)
        print("ПРАВИЛО ЯГЕРА")
        print("-" * 50)

        combined = defaultdict(float)
        conflict = 0.0

        # Вычисляем все пересечения
        for s1, m1 in bpa1.items():
            for s2, m2 in bpa2.items():
                intersection = s1.intersection(s2)
                product = m1 * m2

                if len(intersection) == 0:
                    conflict += product
                else:
                    combined[intersection] += product

        print(f"Коэффициент конфликтности K = {conflict:.6f}")
        print(f"Конфликт переносится в универсальное множество Θ")

        # Переносим конфликт в универсальное множество Θ
        combined[self.universal_set] = combined.get(self.universal_set, 0.0) + conflict
        combined[frozenset()] = 0.0  # Пустое множество = 0

        result = dict(combined)

        # Удаляем пустые множества с нулевой массой
        result = {k: v for k, v in result.items()
                  if v > 1e-10 or k == self.universal_set}

        # Сохраняем историю конфликтов
        self.conflict_history.append(conflict)

        # Выводим результат
        self.print_combination_result(result, conflict, "Ягер")

        return result

    def yager_combine_multiple(self, *bpas: Dict[frozenset, float]) -> Dict[frozenset, float]:
        """
        Правило комбинирования Ягера для произвольного числа источников
        """
        print("\n" + "=" * 60)
        print(f"КОМБИНИРОВАНИЕ {len(bpas)} ИСТОЧНИКОВ ПО ПРАВИЛОМ ЯГЕРА")
        print("=" * 60)

        if len(bpas) == 0:
            print("❌ Нет данных для комбинирования")
            return {}
        elif len(bpas) == 1:
            print("⚠️  Только один источник, возвращаем как есть")
            return bpas[0]

        print(f"Будет последовательно объединено {len(bpas)} BPA")

        result = bpas[0]

        for i, bpa in enumerate(bpas[1:], 1):
            print(f"\n--- Шаг {i}: Комбинирование с источником {i + 1} ---")
            result = self.yager_combine(result, bpa)

        return result

    # ==================== АДАПТИВНОЕ ПРАВИЛО ====================

    def adaptive_combine(self, bpa1: Dict[frozenset, float],
                         bpa2: Dict[frozenset, float]) -> Dict[frozenset, float]:
        """
        Адаптивное правило комбинирования для ДВУХ источников

        Принцип:
        - Если конфликт K < threshold: используем правило Демпстера
        - Если конфликт K >= threshold: используем правило Ягера
        """
        print("\n" + "-" * 50)
        print("АДАПТИВНОЕ ПРАВИЛО")
        print("-" * 50)

        print(f"Порог конфликта: X = {self.conflict_threshold}")

        # Вычисляем уровень конфликта
        conflict = self.calculate_conflict(bpa1, bpa2)

        print(f"Коэффициент конфликта между источниками: K = {conflict:.6f}")
        print(f"Сравнение: K ({conflict:.6f}) ? X ({self.conflict_threshold})")

        # Выбираем правило на основе конфликта
        if conflict < self.conflict_threshold:
            print(f"→ K < X → используем правило Демпстера")
            result = self.dempster_combine(bpa1, bpa2)
            used_rule = "Демпстер"
        else:
            print(f"→ K >= X → используем правило Ягера")
            result = self.yager_combine(bpa1, bpa2)
            used_rule = "Ягер"

        # Сохраняем информацию о решении
        self.step_decisions.append({
            'step': len(self.step_decisions) + 1,
            'conflict': conflict,
            'threshold': self.conflict_threshold,
            'used_rule': used_rule,
            'decision_logic': f"K ({conflict:.6f}) {'<' if conflict < self.conflict_threshold else '>='} X ({self.conflict_threshold})"
        })

        self.conflict_history.append(conflict)

        return result

    def adaptive_combine_multiple(self, *bpas: Dict[frozenset, float]) -> Dict[frozenset, float]:
        """
        Адаптивное правило комбинирования для ПРОИЗВОЛЬНОГО числа источников

        Принцип:
        - Последовательно комбинируем источники
        - На КАЖДОМ шаге проверяем конфликт и выбираем правило
        """
        print("\n" + "=" * 70)
        print(f"АДАПТИВНОЕ КОМБИНИРОВАНИЕ {len(bpas)} ИСТОЧНИКОВ")
        print("=" * 70)
        print(f"Порог конфликта: X = {self.conflict_threshold}")

        if len(bpas) == 0:
            print("❌ Нет данных для комбинирования")
            return {}
        elif len(bpas) == 1:
            print("⚠️  Только один источник, возвращаем как есть")
            return bpas[0]

        print(f"\n Будет последовательно объединено {len(bpas)} источников")
        print(f"На каждом шаге будет проверяться:")
        print(f"  • Если конфликт K < {self.conflict_threshold} → Демпстер")
        print(f"  • Если конфликт K >= {self.conflict_threshold} → Ягер")

        # Сбрасываем историю решений
        self.step_decisions = []

        # Начинаем с первого источника
        result = bpas[0]
        print(f"\n Начальный BPA (источник 1): {len(result)} фокальных элементов")

        # Последовательно комбинируем с остальными источниками
        for i, bpa in enumerate(bpas[1:], 1):
            print(f"\n" + "=" * 50)
            print(f"ШАГ {i}: КОМБИНИРОВАНИЕ С ИСТОЧНИКОМ {i + 1}")
            print("=" * 50)

            print(f"Текущий промежуточный результат: {len(result)} фокальных элементов")
            print(f"Новый источник {i + 1}: {len(bpa)} фокальных элементов")

            # Комбинируем с адаптивным правилом
            result = self.adaptive_combine(result, bpa)

        # Выводим итоговый отчет о решениях
        self.print_adaptive_decisions_report()

        return result

    def print_combination_result(self, combined_bpa: Dict[frozenset, float],
                                  conflict: float, rule_name: str):
        """Вывод результатов комбинирования"""
        print(f"\n Результат комбинирования ({rule_name}):")
        print(f"Конфликт K = {conflict:.6f}")

        total = 0.0
        significant_focals = []

        for focal, mass in sorted(combined_bpa.items(),
                                  key=lambda x: (-len(x[0]), -x[1])):
            if mass > 1e-6:
                focal_str = "Θ" if focal == self.universal_set else set(focal)
                significant_focals.append((focal_str, mass))
                total += mass

        # Показываем только значимые значения (или топ-5)
        for focal_str, mass in significant_focals[:5]:
            print(f"  m({focal_str}) = {mass:.6f}")

        if len(significant_focals) > 5:
            print(f"  ... и ещё {len(significant_focals) - 5} элементов")

        print(f"Сумма масс: {total:.6f}")

        if abs(total - 1.0) > 0.0001:
            print(f"⚠️  Внимание: сумма масс = {total:.6f} (должна быть 1.0)")

    def print_adaptive_decisions_report(self):
        """Вывод отчета о решениях адаптивного правила"""
        if not self.step_decisions:
            return

        print("\n" + "=" * 70)
        print("ОТЧЕТ О РЕШЕНИЯХ АДАПТИВНОГО ПРАВИЛА")
        print("=" * 70)

        print(f"\n Всего шагов комбинирования: {len(self.step_decisions)}")

        dempster_count = sum(1 for d in self.step_decisions if d['used_rule'] == 'Демпстер')
        yager_count = sum(1 for d in self.step_decisions if d['used_rule'] == 'Ягер')

        print(f" Статистика использования правил:")
        print(f"  • Правило Демпстера: {dempster_count} раз ({dempster_count / len(self.step_decisions) * 100:.1f}%)")
        print(f"  • Правило Ягера: {yager_count} раз ({yager_count / len(self.step_decisions) * 100:.1f}%)")

        print(f"\n Детали по шагам:")
        print("-" * 70)
        print(f"{'Шаг':5} {'Конфликт K':15} {'Порог X':10} {'Правило':12} {'Решение'}")
        print("-" * 70)

        for decision in self.step_decisions:
            k = decision['conflict']
            x = decision['threshold']
            rule = decision['used_rule']
            logic = decision['decision_logic']

            print(f"{decision['step']:5} {k:15.6f} {x:10.3f} {rule:12} {logic}")


    def set_conflict_threshold(self, threshold: float) -> bool:
        """Установка порога для адаптивного правила"""
        if Config.MIN_CONFLICT_THRESHOLD <= threshold <= Config.MAX_CONFLICT_THRESHOLD:
            self.conflict_threshold = threshold
            print(f"✅ Установлен порог конфликта: X = {threshold}")
            return True
        else:
            print(f"❌ Порог должен быть в диапазоне "
                  f"[{Config.MIN_CONFLICT_THRESHOLD}, {Config.MAX_CONFLICT_THRESHOLD}]")
            return False
