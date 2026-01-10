from typing import Dict, List, Tuple
from itertools import combinations
from config import Config

class BeliefPlausibilityCalculator:
    """
    Калькулятор функций доверия и правдоподобия
    """

    def __init__(self):
        self.belief_functions = {}
        self.plausibility_functions = {}
        self.intervals = {}
        self.scores = {}
        self.optimal_alternative = None
        self.ranking = []
        self.all_alternatives = set()

    def calculate_belief_plausibility(self, combined_beliefs: Dict[frozenset, float],
                                      all_alternatives: List[str]) -> Tuple[Dict, Dict]:
        """
        Вычисление функций доверия и правдоподобия для всех подмножеств
        """
        print("\n" + "=" * 60)
        print("ВЫЧИСЛЕНИЕ ФУНКЦИЙ ДОВЕРИЯ И ПРАВДОПОДОБИЯ")
        print("=" * 60)

        self.belief_functions = {}
        self.plausibility_functions = {}
        self.intervals = {}
        self.all_alternatives = set(all_alternatives)

        print("Комбинированные вероятности для вычислений:")
        for group, prob in combined_beliefs.items():
            if prob > Config.DEFAULT_CONFIDENCE_THRESHOLD:
                group_str = "Θ" if group == frozenset(all_alternatives) else set(group)
                print(f"  m({group_str}) = {prob:.6f}")

        print(f"\nАльтернативы: {sorted(self.all_alternatives)}")

        # Генерируем все возможные подмножества
        all_subsets = self.generate_all_subsets(all_alternatives)

        # Вычисляем для каждого подмножества
        for subset in all_subsets:
            belief = self.calculate_belief_for_subset(subset, combined_beliefs)
            plausibility = self.calculate_plausibility_for_subset(subset, combined_beliefs)

            subset_key = frozenset(subset)
            self.belief_functions[subset_key] = belief
            self.plausibility_functions[subset_key] = plausibility
            self.intervals[subset_key] = (belief, plausibility)

        # Выводим интервалы для одиночных альтернатив
        self.print_single_alternative_intervals()

        return self.belief_functions.copy(), self.plausibility_functions.copy()

    def generate_all_subsets(self, alternatives: List[str]) -> List[List[str]]:
        """Генерация всех возможных подмножеств альтернатив"""
        all_subsets = []
        n = len(alternatives)

        # Генерируем подмножества всех размеров
        for size in range(1, n + 1):
            for combo in combinations(alternatives, size):
                all_subsets.append(list(combo))

        return all_subsets

    def calculate_belief_for_subset(self, subset: List[str],
                                     combined_beliefs: Dict[frozenset, float]) -> float:
        """
        Вычисление Belief для подмножества
        """
        belief = 0.0
        subset_set = set(subset)

        for focal, mass in combined_beliefs.items():
            focal_set = set(focal)

            # Если фокальный элемент полностью содержится в подмножестве
            if focal_set.issubset(subset_set):
                belief += mass

        return belief

    def calculate_plausibility_for_subset(self, subset: List[str],
                                           combined_beliefs: Dict[frozenset, float]) -> float:
        """
        Вычисление Plausibility для подмножества
        """
        plausibility = 0.0
        subset_set = set(subset)

        for focal, mass in combined_beliefs.items():
            focal_set = set(focal)

            # Если фокальный элемент пересекается с подмножеством
            if focal_set.intersection(subset_set):
                plausibility += mass

        return plausibility

    def print_single_alternative_intervals(self):
        """Вывод интервалов для одиночных альтернатив"""
        print(f"\n📊 ИНТЕРВАЛЫ ДОВЕРИЯ ДЛЯ АЛЬТЕРНАТИВ:")
        print("-" * 60)
        print(f"{'Альтернатива':15} {'Belief':12} {'Plausibility':12} {'Интервал':20} {'Ширина':10}")
        print("-" * 60)

        for alt in sorted(self.all_alternatives):
            alt_set = frozenset([alt])
            if alt_set in self.intervals:
                belief, plausibility = self.intervals[alt_set]
                interval = f"[{belief:.4f}, {plausibility:.4f}]"
                width = plausibility - belief

                print(f"{alt:15} {belief:12.6f} {plausibility:12.6f} {interval:20} {width:10.6f}")

    def find_optimal_alternative(self, pessimism_coef: float = None) -> str:
        """
        Поиск оптимальной альтернативы и ранжирование

        Args:
            pessimism_coef: коэффициент пессимизма γ (0-1)
                          None = использовать коэффициент из конфига

        Returns:
            Оптимальная альтернатива
        """
        if pessimism_coef is None:
            pessimism_coef = Config.DEFAULT_PESSIMISM_COEFFICIENT

        print("\n" + "=" * 60)
        print("ПОИСК ОПТИМАЛЬНОЙ АЛЬТЕРНАТИВЫ И РАНЖИРОВАНИЕ")
        print("=" * 60)
        print(f"Коэффициент пессимизма: γ = {pessimism_coef}")

        if not self.intervals:
            print("❌ Нет данных для сравнения!")
            return None

        # Ранжируем все альтернативы с коэффициентом пессимизма
        self.rank_alternatives(pessimism_coef)

        # Финальный вывод
        self.print_final_results(pessimism_coef)

        return self.optimal_alternative

    def rank_alternatives(self, pessimism_coef: float):
        """
        Ранжирование всех альтернатив с коэффициентом пессимизма

        Формула: Score = γ·Bel + (1-γ)·Pl
        """
        print(f"\nФормула ранжирования: {pessimism_coef}·Bel + (1-{pessimism_coef})·Pl")
        print("-" * 50)

        self.scores = {}
        for alt in sorted(self.all_alternatives):
            alt_set = frozenset([alt])
            if alt_set in self.intervals:
                bel = self.belief_functions[alt_set]
                pl = self.plausibility_functions[alt_set]
                score = pessimism_coef * bel + (1 - pessimism_coef) * pl
                self.scores[alt] = score

                print(f"  {alt}: {pessimism_coef}×{bel:.4f} + {1 - pessimism_coef}×{pl:.4f} = {score:.4f}")

        # Сортируем альтернативы по убыванию оценки
        self.ranking = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)

        # Определяем оптимальную альтернативу
        if self.ranking:
            self.optimal_alternative = self.ranking[0][0]

        print(f"\n🏆 РАНЖИРОВАНИЕ АЛЬТЕРНАТИВ:")
        for i, (alt, score) in enumerate(self.ranking, 1):
            alt_set = frozenset([alt])
            if alt_set in self.intervals:
                bel, pl = self.intervals[alt_set]
                optimal_mark = " 🏆" if i == 1 else ""
                print(f"  {i:2d}. {alt:10} {score:8.4f}  ([{bel:.4f}, {pl:.4f}]){optimal_mark}")

    def print_final_results(self, pessimism_coef: float):
        """Вывод финальных результатов"""
        print("\n" + "=" * 60)
        print("ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ")
        print("=" * 60)

        print(f"\nОПТИМАЛЬНАЯ АЛЬТЕРНАТИВА: {self.optimal_alternative}")

        if self.optimal_alternative:
            alt_set = frozenset([self.optimal_alternative])
            if alt_set in self.intervals:
                bel, pl = self.intervals[alt_set]
                score = self.scores.get(self.optimal_alternative, 0.0)

                print(f"\n📈 Характеристики оптимальной альтернативы:")
                print(f"  • Belief:       {bel:.6f}")
                print(f"  • Plausibility: {pl:.6f}")
                print(f"  • Интервал:     [{bel:.4f}, {pl:.4f}]")
                print(f"  • Ширина:       {pl - bel:.6f}")
                print(f"  • Финальная оценка: {score:.6f}")


    def get_belief_functions(self) -> Dict[frozenset, float]:
        """Получить функции доверия"""
        return self.belief_functions.copy()

    def get_plausibility_functions(self) -> Dict[frozenset, float]:
        """Получить функции правдоподобия"""
        return self.plausibility_functions.copy()

    def get_intervals(self) -> Dict[frozenset, Tuple[float, float]]:
        """Получить интервалы доверия"""
        return self.intervals.copy()

    def get_scores(self) -> Dict[str, float]:
        """Получить оценки альтернатив"""
        return self.scores.copy()

    def get_ranking(self) -> List[Tuple[str, float]]:
        """Получить ранжирование альтернатив"""
        return self.ranking.copy()

