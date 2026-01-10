import math
from typing import Dict, List, Any
from config import Config
from utils import Utils


class ExpertManager:
    """
    Менеджер экспертов для группового режима DS/AHP-GDM

    Реализует:
    1. Хранение данных экспертов
    2. Вычисление BOE
    3. Дисконтирование по важности экспертов
    4. Комбинирование свидетельств экспертов
    """

    def __init__(self, alternatives: List[str], criteria: List[str]):
        """
        Инициализация менеджера экспертов

        Args:
            alternatives: список всех альтернатив
            criteria: список критериев
        """
        self.alternatives = alternatives
        self.criteria = criteria

        # Универсальное множество (Θ)
        self.universal_set = frozenset(alternatives)

        # Данные экспертов
        self.experts = {}  # {имя: данные}
        self.expert_weights = {}  # {имя: вес}
        self.discount_rates = {}  # {имя: коэффициент дисконтирования}

        # BOE экспертов
        self.criterion_boes = {}  # {эксперт: {критерий: BOE}}
        self.individual_boes = {}  # {эксперт: индивидуальный BOE}
        self.adjusted_boes = {}  # {эксперт: скорректированный BOE}

        # Результаты
        self.group_boe = None
        self.conflict_history = []

        print(f"✅ Инициализирован ExpertManager")
        print(f"   Альтернативы: {len(alternatives)}")
        print(f"   Критерии: {len(criteria)}")

    def add_expert(self, name: str, weight: float,
                   cpvs: Dict[str, float],
                   preferences: Dict[str, Dict[str, int]]) -> bool:
        """
        Добавление эксперта в систему

        Args:
            name: имя эксперта
            weight: вес важности эксперта (0-1)
            cpvs: словарь CPV по критериям
            preferences: предпочтения по критериям

        Returns:
            True если успешно
        """
        # Проверка данных
        if not self.validate_expert_data(name, weight, cpvs, preferences):
            return False

        # Сохраняем данные эксперта
        self.experts[name] = {
            'weight': weight,
            'cpvs': cpvs,
            'preferences': preferences
        }

        self.expert_weights[name] = weight

        print(f"✅ Добавлен эксперт: {name}")
        print(f"   Вес: {weight}")
        print(f"   CPV: {cpvs}")

        return True

    def validate_expert_data(self, name: str, weight: float,
                              cpvs: Dict[str, float],
                              preferences: Dict[str, Dict[str, int]]) -> bool:
        """Проверка корректности данных эксперта"""

        # Проверка имени
        if not name or name.strip() == "":
            print(f"❌ Пустое имя эксперта")
            return False

        # Проверка веса
        if weight < 0 or weight > 1:
            print(f"❌ Вес эксперта {name} = {weight} вне диапазона [0, 1]")
            return False

        # Проверка CPV
        if not Utils.validate_cpvs(cpvs, self.criteria):
            print(f"❌ Некорректные CPV для эксперта {name}")
            return False

        # Проверка предпочтений
        if not Utils.validate_preferences(preferences, self.alternatives):
            print(f"❌ Некорректные предпочтения для эксперта {name}")
            return False

        return True

    def calculate_discount_rates(self) -> Dict[str, float]:
        """
        Расчет коэффициентов дисконтирования

        Формула (1.6): ω_k* = ω_k / max(ω_1, ..., ω_n)
        """
        if not self.expert_weights:
            print("⚠️  Нет данных об экспертах")
            return {}

        max_weight = max(self.expert_weights.values())

        if max_weight == 0:
            print("❌ Максимальный вес равен 0")
            return {}

        self.discount_rates = {}
        for expert, weight in self.expert_weights.items():
            self.discount_rates[expert] = weight / max_weight

        print("\n" + "=" * 50)
        print("КОЭФФИЦИЕНТЫ ДИСКОНТИРОВАНИЯ ЭКСПЕРТОВ")
        print("=" * 50)

        for expert, rate in self.discount_rates.items():
            weight = self.expert_weights[expert]
            print(f"  {expert}: ω = {weight:.3f} → ω* = {rate:.3f}")

        return self.discount_rates.copy()

    def compute_criterion_boe(self, expert_name: str, criterion: str) -> Dict[frozenset, float]:
        """
        Вычисление BOE для одного критерия эксперта

        Формулы (1.1)-(1.2):
        m(s_i) = (a_i * p) / (∑ a_j * p + √d)
        m(Θ) = √d / (∑ a_j * p + √d)
        """
        if expert_name not in self.experts:
            print(f"❌ Эксперт {expert_name} не найден")
            return {}

        expert = self.experts[expert_name]

        # Получаем данные для критерия
        if criterion not in expert['preferences']:
            print(f"⚠️  Нет предпочтений для эксперта {expert_name} по критерию {criterion}")
            return {self.universal_set: 1.0}

        preferences = expert['preferences'][criterion]
        cpv = expert['cpvs'].get(criterion, 0.0)

        # Если CPV = 0 или нет предпочтений - полное незнание
        if cpv == 0 or not preferences:
            return {self.universal_set: 1.0}

        # Количество фокальных элементов (групп)
        d = len(preferences)

        # Вычисляем сумму a_j * p
        sum_aj_p = sum(pref * cpv for pref in preferences.values())

        # Знаменатель: sum_aj_p + √d
        denominator = sum_aj_p + math.sqrt(d)

        if denominator == 0:
            print(f"⚠️  Нулевой знаменатель для {expert_name}/{criterion}")
            return {self.universal_set: 1.0}

        # Вычисляем BOE
        boe = {}

        for group_str, preference in preferences.items():
            # Парсим группу альтернатив
            group_alts = Utils.parse_gdm_group_string(group_str)
            if not group_alts:
                continue

            group_set = frozenset(group_alts)

            # Формула (1.1)
            m_value = (preference * cpv) / denominator
            boe[group_set] = m_value

        # Формула (1.2) для неопределенности (Θ)
        boe[self.universal_set] = math.sqrt(d) / denominator

        # Нормализация (сумма должна быть 1)
        total = sum(boe.values())
        if abs(total - 1.0) > 0.0001:
            # Нормализуем
            boe = {k: v / total for k, v in boe.items()}

        # Инициализируем словарь для эксперта, если нужно
        if expert_name not in self.criterion_boes:
            self.criterion_boes[expert_name] = {}

        # Сохраняем BOE критерия
        self.criterion_boes[expert_name][criterion] = boe

        return boe

    def compute_all_criterion_boes(self):
        """Вычисление BOE для всех критериев всех экспертов"""
        print("\n" + "=" * 60)
        print("ВЫЧИСЛЕНИЕ BOE ДЛЯ ВСЕХ КРИТЕРИЕВ")
        print("=" * 60)

        for expert_name in self.experts.keys():
            print(f"\n📊 Эксперт: {expert_name}")

            for criterion in self.criteria:
                boe = self.compute_criterion_boe(expert_name, criterion)

                if boe:
                    print(f"  Критерий {criterion}: {len(boe)} фокальных элементов")

                    # Выводим топ-3 значения
                    sorted_boe = sorted(boe.items(), key=lambda x: x[1], reverse=True)
                    for i, (focal, mass) in enumerate(sorted_boe[:3]):
                        if mass > Config.DEFAULT_CONFIDENCE_THRESHOLD:
                            focal_str = "Θ" if focal == self.universal_set else set(focal)
                            print(f"    m({focal_str}) = {mass:.4f}")

    def compute_individual_boe(self, expert_name: str,
                               combination_rule: str = "dempster",
                               conflict_threshold: float = None) -> Dict[frozenset, float]:
        """
        Вычисление общего BOE эксперта путем комбинирования BOE по всем критериям

        Args:
            expert_name: имя эксперта
            combination_rule: правило комбинирования

        Returns:
            Индивидуальный BOE эксперта
        """
        if expert_name not in self.experts:
            print(f"❌ Эксперт {expert_name} не найден")
            return {}

        print(f"\n{'=' * 50}")
        print(f"ВЫЧИСЛЕНИЕ ИНДИВИДУАЛЬНОГО BOE: {expert_name}")
        print(f"Правило комбинирования: {combination_rule}")
        print(f"{'=' * 50}")

        # Получаем BOE всех критериев для эксперта
        if expert_name not in self.criterion_boes:
            self.compute_all_criterion_boes()

        if expert_name not in self.criterion_boes:
            print(f"⚠️  Нет BOE для эксперта {expert_name}")
            return {self.universal_set: 1.0}

        criterion_boes = self.criterion_boes[expert_name]

        if not criterion_boes:
            print(f"⚠️  Пустые BOE для эксперта {expert_name}")
            return {self.universal_set: 1.0}

        from combination_rules import CombinationRules
        # Создаем комбайнер с учетом порога конфликта
        if combination_rule == "adaptive" and conflict_threshold is not None:
            combiner = CombinationRules(self.alternatives, conflict_threshold)
        else:
            combiner = CombinationRules(self.alternatives)

        # Преобразуем в список BOE
        boe_list = list(criterion_boes.values())

        # Комбинируем
        if combination_rule == "yager":
            individual_boe = combiner.yager_combine_multiple(*boe_list)
        elif combination_rule == "adaptive":
            individual_boe = combiner.adaptive_combine_multiple(*boe_list)
        else:  # Демпстер по умолчанию
            individual_boe = combiner.dempster_combine_multiple(*boe_list)

        # Сохраняем результат
        self.individual_boes[expert_name] = individual_boe

        # Выводим результат
        print(f"\n📈 Итоговый BOE эксперта {expert_name}:")
        total = 0.0
        for focal, mass in sorted(individual_boe.items(),
                                  key=lambda x: x[1], reverse=True):
            if mass > Config.DEFAULT_CONFIDENCE_THRESHOLD:
                focal_str = "Θ" if focal == self.universal_set else set(focal)
                print(f"  m({focal_str}) = {mass:.4f}")
                total += mass

        print(f"  Сумма: {total:.6f}")

        return individual_boe

    def adjust_boe_with_importance(self, expert_name: str) -> Dict[frozenset, float]:
        """
        Корректировка BOE с учетом важности эксперта

        Формулы (1.7)-(1.10):
        1. m_k*(s_i) = ω_k* · m_k(s_i) для s_i ≠ Θ
        2. m_k*(Θ) = m_k(Θ)
        3. Нормализация
        """
        if expert_name not in self.individual_boes:
            print(f"❌ Нет индивидуального BOE для эксперта {expert_name}")
            return {}

        if expert_name not in self.discount_rates:
            print(f"❌ Нет коэффициента дисконтирования для эксперта {expert_name}")
            return self.individual_boes[expert_name]

        discount_rate = self.discount_rates[expert_name]

        # Если самый важный эксперт (ω* = 1), возвращаем без изменений
        if abs(discount_rate - 1.0) < 1e-10:
            self.adjusted_boes[expert_name] = self.individual_boes[expert_name]
            return self.individual_boes[expert_name]

        print(f"\n--- Дисконтирование BOE эксперта {expert_name} ---")
        print(f"Коэффициент дисконтирования: ω* = {discount_rate:.3f}")

        individual_boe = self.individual_boes[expert_name]

        # Шаг 1: Применение дисконтирования
        adjusted_boe = {}
        sum_adjusted = 0.0
        ignorance_mass = 0.0

        for focal, mass in individual_boe.items():
            if focal == self.universal_set:
                # Θ не дисконтируется
                ignorance_mass = mass
                adjusted_boe[self.universal_set] = mass
            else:
                # Явные предпочтения дисконтируются
                adjusted_mass = mass * discount_rate
                adjusted_boe[focal] = adjusted_mass
                sum_adjusted += adjusted_mass

        # Шаг 2: Нормализация
        total = sum_adjusted + ignorance_mass

        if total == 0:
            print(f"⚠️  Общая масса после дисконтирования равна 0")
            adjusted_boe = {self.universal_set: 1.0}
        else:
            normalized_boe = {}
            for focal, mass in adjusted_boe.items():
                normalized_boe[focal] = mass / total
            adjusted_boe = normalized_boe

        # Сохраняем результат
        self.adjusted_boes[expert_name] = adjusted_boe

        # Выводим результат
        print(f"\n📊 BOE после дисконтирования:")
        total_mass = 0.0
        for focal, mass in sorted(adjusted_boe.items(),
                                  key=lambda x: x[1], reverse=True):
            if mass > Config.DEFAULT_CONFIDENCE_THRESHOLD:
                focal_str = "Θ" if focal == self.universal_set else set(focal)
                print(f"  m^N({focal_str}) = {mass:.4f}")
                total_mass += mass

        print(f"  Сумма: {total_mass:.6f}")

        return adjusted_boe

    def compute_group_boe(self, combination_rule: str = "dempster",
                          use_adjusted: bool = True,
                          conflict_threshold: float = None) -> Dict[frozenset, float]:

        print("\n" + "=" * 60)
        print("ВЫЧИСЛЕНИЕ ГРУППОВОГО BOE")
        print(f"Правило: {combination_rule}")

        if combination_rule == "adaptive" and conflict_threshold is not None:
            print(f"Порог конфликта: X = {conflict_threshold}")

        print(f"Использовать скорректированные BOE: {use_adjusted}")
        print("=" * 60)

        # Получаем BOE для комбинирования
        if use_adjusted:
            boes_to_combine = self.adjusted_boes
        else:
            boes_to_combine = self.individual_boes

        if not boes_to_combine:
            print("❌ Нет BOE для комбинирования")
            return {}

        print(f"\nБудет объединено {len(boes_to_combine)} экспертов:")
        for expert_name in boes_to_combine.keys():
            print(f"  • {expert_name}")

        # Комбинируем BOE экспертов
        from combination_rules import CombinationRules

        # Создаем комбайнер с учетом порога конфликта
        if combination_rule == "adaptive" and conflict_threshold is not None:
            combiner = CombinationRules(self.alternatives, conflict_threshold)
        else:
            combiner = CombinationRules(self.alternatives)

        # Преобразуем в список BOE
        boe_list = list(boes_to_combine.values())

        # Комбинируем
        if combination_rule == "yager":
            group_boe = combiner.yager_combine_multiple(*boe_list)
        elif combination_rule == "adaptive":
            group_boe = combiner.adaptive_combine_multiple(*boe_list)
        else:  # Демпстер по умолчанию
            group_boe = combiner.dempster_combine_multiple(*boe_list)

        # Сохраняем результат
        self.group_boe = group_boe

        # Выводим результат
        print(f"\n🎯 Групповой BOE ({combination_rule}):")
        total = 0.0
        for focal, mass in sorted(group_boe.items(),
                                  key=lambda x: x[1], reverse=True):
            if mass > Config.DEFAULT_CONFIDENCE_THRESHOLD:
                focal_str = "Θ" if focal == self.universal_set else set(focal)
                print(f"  m_group({focal_str}) = {mass:.4f}")
                total += mass

        print(f"  Сумма: {total:.6f}")

        return group_boe

    def get_expert_summary(self) -> Dict[str, Any]:
        """Получить сводку по всем экспертам"""
        summary = {
            'alternatives': self.alternatives,
            'criteria': self.criteria,
            'experts_count': len(self.experts),
            'experts': {}
        }

        for expert_name, expert_data in self.experts.items():
            summary['experts'][expert_name] = {
                'weight': expert_data['weight'],
                'cpvs': expert_data['cpvs'],
                'preferences': expert_data['preferences'],
                'discount_rate': self.discount_rates.get(expert_name, 0.0)
            }

        return summary

    def print_detailed_report(self):
        """Вывод подробного отчета"""
        print("\n" + "=" * 70)
        print("ДЕТАЛЬНЫЙ ОТЧЕТ ПО ЭКСПЕРТАМ")
        print("=" * 70)

        print(f"\n📊 Общая информация:")
        print(f"  Альтернативы: {', '.join(self.alternatives)}")
        print(f"  Критерии: {', '.join(self.criteria)}")
        print(f"  Количество экспертов: {len(self.experts)}")

        print(f"\n👥 Данные экспертов:")
        for expert_name, expert_data in self.experts.items():
            print(f"\n  Эксперт: {expert_name}")
            print(f"    Вес: {expert_data['weight']}")

            discount_rate = self.discount_rates.get(expert_name, 0.0)
            print(f"    Коэффициент дисконтирования: {discount_rate:.3f}")

            print(f"    CPV:")
            for criterion, cpv in expert_data['cpvs'].items():
                print(f"      {criterion}: {cpv:.3f}")