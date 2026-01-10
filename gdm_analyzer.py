from typing import Dict, List, Any, Optional, Tuple
from config import Config
from expert_manager import ExpertManager
from belief_plausibility import BeliefPlausibilityCalculator
from export_formats import ExportFormats
from gdm_xml_parser import GDMXMLParser


class GDMAnalyzer:
    """
    Главный анализатор для группового режима DS/AHP-GDM

    Координирует:
    1. Загрузку данных экспертов
    2. Вычисление BOE
    3. Комбинирование свидетельств
    4. Расчет функций доверия/правдоподобия
    5. Экспорт результатов
    """

    def __init__(self, combination_rule: str = None,
                 conflict_threshold: float = None):
        """
        Инициализация анализатора GDM
        """
        if combination_rule is None:
            combination_rule = Config.DEFAULT_COMBINATION_RULE

        self.combination_rule = combination_rule
        self.pessimism_coefficient = Config.DEFAULT_PESSIMISM_COEFFICIENT

        # Устанавливаем порог конфликта
        if conflict_threshold is None:
            self.conflict_threshold = Config.DEFAULT_CONFLICT_THRESHOLD
        else:
            self.conflict_threshold = conflict_threshold

        # Компоненты системы
        self.expert_manager = None
        self.belief_calculator = None
        self.exporter = ExportFormats()

        # Данные
        self.alternatives = []
        self.criteria = []
        self.experts_data = {}

        # Результаты
        self.results = {}
        self.group_boe = None

        print(f"✅ Инициализирован GDMAnalyzer")
        print(f"   Правило комбинирования: {Config.COMBINATION_RULE_NAMES[combination_rule]}")

        if combination_rule == Config.COMBINATION_RULE_ADAPTIVE:
            print(f"   Порог конфликта: X = {self.conflict_threshold}")

    def load_data_from_xml(self, xml_file_path: str) -> bool:
        print("\n" + "=" * 60)
        print("ЗАГРУЗКА ДАННЫХ ИЗ XML ФАЙЛА")
        print("=" * 60)

        # Парсим XML файл
        data = GDMXMLParser.parse_gdm_xml(xml_file_path)

        if not data:
            print("❌ Не удалось загрузить данные из XML")
            return False

        # Сохраняем данные
        self.alternatives = data['alternatives']
        self.criteria = data['criteria']
        self.experts_data = data['experts']

        # Выводим сводку
        GDMXMLParser.print_data_summary(data)

        # Создаем менеджер экспертов
        self.expert_manager = ExpertManager(self.alternatives, self.criteria)

        # Добавляем экспертов
        print(f"\n📥 Добавление экспертов в систему...")
        experts_added = 0

        for expert_name, expert_info in self.experts_data.items():
            success = self.expert_manager.add_expert(
                name=expert_name,
                weight=expert_info['weight'],
                cpvs=expert_info['cpvs'],
                preferences=expert_info['preferences']
            )

            if success:
                experts_added += 1

        if experts_added == 0:
            print("❌ Не удалось добавить ни одного эксперта")
            return False

        print(f"✅ Добавлено {experts_added} экспертов")
        return True

    def load_data_manually(self, alternatives: List[str], criteria: List[str],
                           experts_data: Dict[str, Dict]) -> bool:
        print("\n" + "=" * 60)
        print("РУЧНАЯ ЗАГРУЗКА ДАННЫХ")
        print("=" * 60)

        self.alternatives = alternatives
        self.criteria = criteria
        self.experts_data = experts_data

        # Создаем менеджер экспертов
        self.expert_manager = ExpertManager(self.alternatives, self.criteria)

        # Добавляем экспертов
        print(f"\n📥 Добавление экспертов в систему...")
        experts_added = 0

        for expert_name, expert_info in self.experts_data.items():
            success = self.expert_manager.add_expert(
                name=expert_name,
                weight=expert_info['weight'],
                cpvs=expert_info['cpvs'],
                preferences=expert_info['preferences']
            )

            if success:
                experts_added += 1

        if experts_added == 0:
            print("❌ Не удалось добавить ни одного эксперта")
            return False

        print(f"✅ Добавлено {experts_added} экспертов")
        return True

    def set_combination_rule(self, rule: str) -> bool:
        """
        Установка правила комбинирования
        """
        if rule in [Config.COMBINATION_RULE_DEMPSTER,
                    Config.COMBINATION_RULE_YAGER,
                    Config.COMBINATION_RULE_ADAPTIVE]:
            self.combination_rule = rule
            print(f"✅ Установлено правило: {Config.COMBINATION_RULE_NAMES[rule]}")
            return True
        else:
            print(f"❌ Неизвестное правило: {rule}")
            return False

    def set_pessimism_coefficient(self, coefficient: float) -> bool:
        """
        Установка коэффициента пессимизма
        """
        if Config.MIN_PESSIMISM_COEFFICIENT <= coefficient <= Config.MAX_PESSIMISM_COEFFICIENT:
            self.pessimism_coefficient = coefficient
            print(f"✅ Установлен коэффициент пессимизма: {coefficient}")
            return True
        else:
            print(f"❌ Коэффициент должен быть в диапазоне "
                  f"[{Config.MIN_PESSIMISM_COEFFICIENT}, {Config.MAX_PESSIMISM_COEFFICIENT}]")
            return False

    def set_conflict_threshold(self, threshold: float) -> bool:
        """
        Установка порога для адаптивного правила
        """
        if Config.MIN_CONFLICT_THRESHOLD <= threshold <= Config.MAX_CONFLICT_THRESHOLD:
            self.conflict_threshold = threshold
            print(f"✅ Установлен порог конфликта для адаптивного правила: {threshold}")
            return True
        else:
            print(f"❌ Порог должен быть в диапазоне "
                  f"[{Config.MIN_CONFLICT_THRESHOLD}, {Config.MAX_CONFLICT_THRESHOLD}]")
            return False

    def run_analysis(self, use_adjusted_boe: bool = True) -> Optional[str]:
        """
        Запуск полного анализа GDM
        """
        print("\n" + "=" * 70)
        print("ЗАПУСК ПОЛНОГО АНАЛИЗА DS/AHP-GDM")
        print("=" * 70)

        print(f"\n📊 ПАРАМЕТРЫ АНАЛИЗА:")
        print(
            f"  • Правило комбинирования: {Config.COMBINATION_RULE_NAMES.get(self.combination_rule, self.combination_rule)}")

        if self.combination_rule == Config.COMBINATION_RULE_ADAPTIVE:
            print(f"  • Порог конфликта: X = {self.conflict_threshold}")

        print(f"  • Коэффициент пессимизма: {self.pessimism_coefficient}")
        print(f"  • Использовать скорректированные BOE: {use_adjusted_boe}")
        print(f"  • Альтернатив: {len(self.alternatives)}")
        print(f"  • Критериев: {len(self.criteria)}")
        print(f"  • Экспертов: {len(self.experts_data)}")

        try:
            # ШАГ 1: Расчет коэффициентов дисконтирования
            print(f"\n" + "-" * 50)
            print("ШАГ 1: РАСЧЕТ КОЭФФИЦИЕНТОВ ДИСКОНТИРОВАНИЯ")
            self.expert_manager.calculate_discount_rates()

            # ШАГ 2: Вычисление индивидуальных BOE с передачей порога
            print(f"\n" + "-" * 50)
            print("ШАГ 2: ВЫЧИСЛЕНИЕ ИНДИВИДУАЛЬНЫХ BOE")

            for expert_name in self.experts_data.keys():
                # Передаем порог конфликта для адаптивного правила
                if self.combination_rule == Config.COMBINATION_RULE_ADAPTIVE:
                    self.expert_manager.compute_individual_boe(
                        expert_name,
                        self.combination_rule,
                        conflict_threshold=self.conflict_threshold  # ПЕРЕДАЕМ ПОРОГ
                    )
                else:
                    self.expert_manager.compute_individual_boe(expert_name, self.combination_rule)

            # ШАГ 3: Корректировка BOE с учетом важности
            print(f"\n" + "-" * 50)
            print("ШАГ 3: КОРРЕКТИРОВКА BOE С УЧЕТОМ ВАЖНОСТИ")

            for expert_name in self.experts_data.keys():
                self.expert_manager.adjust_boe_with_importance(expert_name)

            # ШАГ 4: Вычисление группового BOE с передачей порога
            print(f"\n" + "-" * 50)
            print("ШАГ 4: ВЫЧИСЛЕНИЕ ГРУППОВОГО BOE")

            self.group_boe = self.expert_manager.compute_group_boe(
                combination_rule=self.combination_rule,
                use_adjusted=use_adjusted_boe,
                conflict_threshold=self.conflict_threshold  # ПЕРЕДАЕМ ПОРОГ
            )

            if not self.group_boe:
                print("❌ Ошибка при вычислении группового BOE")
                return None

            # ШАГ 5: Вычисление функций доверия и правдоподобия
            print(f"\n" + "-" * 50)
            print("ШАГ 5: ВЫЧИСЛЕНИЕ BELIEF И PLAUSIBILITY")

            self.belief_calculator = BeliefPlausibilityCalculator()
            belief, plausibility = self.belief_calculator.calculate_belief_plausibility(
                self.group_boe, self.alternatives
            )

            # ШАГ 6: Поиск оптимальной альтернативы
            print(f"\n" + "-" * 50)
            print("ШАГ 6: ПОИСК ОПТИМАЛЬНОЙ АЛЬТЕРНАТИВЫ")

            optimal = self.belief_calculator.find_optimal_alternative(self.pessimism_coefficient)

            # ШАГ 7: Сохранение результатов
            print(f"\n" + "-" * 50)
            print("ШАГ 7: СОХРАНЕНИЕ РЕЗУЛЬТАТОВ")

            self.save_results(optimal, use_adjusted_boe)

            # ШАГ 8: Экспорт результатов
            print(f"\n" + "-" * 50)
            print("ШАГ 8: ЭКСПОРТ РЕЗУЛЬТАТОВ")

            self.export_results()

            print("\n" + "=" * 70)
            print("🎉 АНАЛИЗ УСПЕШНО ЗАВЕРШЕН!")
            print("=" * 70)

            return optimal

        except Exception as e:
            print(f"\n❌ Ошибка при выполнении анализа: {e}")
            import traceback
            traceback.print_exc()
            return None

    def save_results(self, optimal_alternative: str, use_adjusted_boe: bool):
        """Сохранение результатов анализа"""
        if not self.belief_calculator:
            return

        self.results = {
            'optimal_alternative': optimal_alternative,
            'ranking': self.belief_calculator.get_ranking(),
            'scores': self.belief_calculator.get_scores(),
            'intervals': self.belief_calculator.get_intervals(),
            'belief_functions': self.belief_calculator.get_belief_functions(),
            'plausibility_functions': self.belief_calculator.get_plausibility_functions(),
            'analysis_params': {
                'combination_rule': self.combination_rule,
                'pessimism_coefficient': self.pessimism_coefficient,
                'use_adjusted_boe': use_adjusted_boe,
                'alternatives_count': len(self.alternatives),
                'criteria_count': len(self.criteria),
                'experts_count': len(self.experts_data)
            }
        }

    def export_results(self):
        """Экспорт результатов во все форматы"""
        if not self.results or not self.expert_manager:
            print("❌ Нет результатов для экспорта")
            return

        # Получаем данные экспертов для экспорта
        expert_summary = self.expert_manager.get_expert_summary()

        # Добавляем параметры анализа
        expert_summary['analysis_params'] = self.results['analysis_params']

        # Экспортируем
        self.exporter.export_to_all_formats(self.results, expert_summary)

