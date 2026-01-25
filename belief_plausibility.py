from typing import Dict, List, Tuple
from config import Config

class BeliefPlausibilityCalculator:
    def __init__(self):
        """Инициализация калькулятора"""
        self.belief_functions = {}
        self.plausibility_functions = {}
        self.intervals = {}
        self.scores = {}
        self.ranking = []
        self.optimal_alternative = None
        self.all_alternatives = []

    def calculate_belief_plausibility(self, combined_beliefs: Dict[frozenset, float],
                                      all_alternatives: List[str]) -> Tuple[Dict, Dict]:
        print("\n" + "=" * 60)
        print("ВЫЧИСЛЕНИЕ BELIEF И PLAUSIBILITY ДЛЯ РАНЖИРОВАНИЯ")
        print("=" * 60)

        self.belief_functions = {}
        self.plausibility_functions = {}
        self.intervals = {}
        self.all_alternatives = all_alternatives

        n = len(all_alternatives)

        # 1. Сначала предварительно вычисляем Plausibility для всех альтернатив
        plausibility_cache = {alt: 0.0 for alt in all_alternatives}
        for focal, mass in combined_beliefs.items():
            # Для каждой альтернативы во фокальном элементе добавляем массу
            for alt in focal:
                if alt in plausibility_cache:
                    plausibility_cache[alt] += mass

        # 2. Вычисляем Belief и Plausibility для каждой одиночной альтернативы
        print(f"\n2️⃣  Вычисление для {n} одиночных альтернатив...")

        for alt in all_alternatives:
            alt_set = frozenset([alt])

            # Belief для одиночной альтернативы = масса фокального элемента {alt}
            belief = combined_beliefs.get(alt_set, 0.0)

            # Plausibility берем из кэша
            plausibility = plausibility_cache.get(alt, 0.0)

            # Сохраняем результаты
            self.belief_functions[alt_set] = belief
            self.plausibility_functions[alt_set] = plausibility
            self.intervals[alt_set] = (belief, plausibility)

        # 3. Выводим интервалы для одиночных альтернатив
        self.print_single_alternative_intervals()

        return self.belief_functions.copy(), self.plausibility_functions.copy()

    def print_single_alternative_intervals(self):
        """Вывод интервалов для одиночных альтернатив"""
        print(f"\n📊 ИНТЕРВАЛЫ ДОВЕРИЯ ДЛЯ АЛЬТЕРНАТИВ:")
        print("-" * 70)
        print(f"{'Альтернатива':15} {'Belief':12} {'Plausibility':12} {'Интервал':25} {'Ширина':10}")
        print("-" * 70)

        for alt in sorted(self.all_alternatives):
            alt_set = frozenset([alt])
            if alt_set in self.intervals:
                belief, plausibility = self.intervals[alt_set]
                interval = f"[{belief:.4f}, {plausibility:.4f}]"
                width = plausibility - belief

                print(f"{alt:15} {belief:12.6f} {plausibility:12.6f} {interval:25} {width:10.6f}")

    def find_optimal_alternative(self, pessimism_coef: float = None) -> str:
        if pessimism_coef is None:
            pessimism_coef = Config.DEFAULT_PESSIMISM_COEFFICIENT

        print("\n" + "=" * 60)
        print("РАНЖИРОВАНИЕ АЛЬТЕРНАТИВ")
        print("=" * 60)
        print(f"Коэффициент пессимизма: γ = {pessimism_coef}")

        if not self.intervals:
            print("❌ Нет данных для сравнения!")
            return None

        # Вычисляем оценки для каждой альтернативы
        self.calculate_scores(pessimism_coef)

        # Ранжируем альтернативы
        self.rank_alternatives()

        # Выводим результаты
        self.print_ranking_results(pessimism_coef)

        return self.optimal_alternative

    def calculate_scores(self, pessimism_coef: float):
        """Вычисление оценок для всех альтернатив"""
        print(f"\n📈 ВЫЧИСЛЕНИЕ ОЦЕНОК:")
        print(f"Формула: оценка = {pessimism_coef}·Bel + (1-{pessimism_coef})·Pl")
        print("-" * 50)

        self.scores = {}

        for alt in self.all_alternatives:
            alt_set = frozenset([alt])
            if alt_set in self.intervals:
                bel, pl = self.intervals[alt_set]
                score = pessimism_coef * bel + (1 - pessimism_coef) * pl
                self.scores[alt] = score

                print(f"  {alt}: {pessimism_coef:.3f}×{bel:.4f} + {1 - pessimism_coef:.3f}×{pl:.4f} = {score:.4f}")

    def rank_alternatives(self):
        """Ранжирование альтернатив по убыванию оценки"""
        self.ranking = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)

        if self.ranking:
            self.optimal_alternative = self.ranking[0][0]

    def print_ranking_results(self, pessimism_coef: float):
        """Вывод результатов ранжирования"""
        print(f"\n🏆 РАНЖИРОВАНИЕ АЛЬТЕРНАТИВ:")
        print("-" * 70)
        print(f"{'Ранг':5} {'Альтернатива':15} {'Оценка':10} {'Belief':10} {'Plausibility':12} {'Интервал':25}")
        print("-" * 70)

        for i, (alt, score) in enumerate(self.ranking, 1):
            alt_set = frozenset([alt])
            if alt_set in self.intervals:
                bel, pl = self.intervals[alt_set]
                interval = f"[{bel:.4f}, {pl:.4f}]"
                optimal_mark = "" if i == 1 else ""

                print(f"{i:3d}{optimal_mark:2} {alt:15} {score:10.6f} {bel:10.6f} {pl:12.6f} {interval:25}")

        # Вывод информации об оптимальной альтернативе
        if self.optimal_alternative:
            self.print_optimal_alternative_info()

    def print_optimal_alternative_info(self):
        """Вывод информации об оптимальной альтернативе"""
        print(f"\n🎯 ОПТИМАЛЬНАЯ АЛЬТЕРНАТИВА: {self.optimal_alternative}")

        alt_set = frozenset([self.optimal_alternative])
        if alt_set in self.intervals:
            bel, pl = self.intervals[alt_set]
            score = self.scores.get(self.optimal_alternative, 0.0)

            print(f"\n📈 Характеристики:")
            print(f"  • Оценка: {score:.6f}")
            print(f"  • Belief: {bel:.6f}")
            print(f"  • Plausibility: {pl:.6f}")
            print(f"  • Интервал: [{bel:.4f}, {pl:.4f}]")
            print(f"  • Ширина интервала: {pl - bel:.6f}")


    def get_belief_functions(self) -> Dict[frozenset, float]:
        """Получить функции доверия (только для одиночных альтернатив)"""
        return self.belief_functions.copy()

    def get_plausibility_functions(self) -> Dict[frozenset, float]:
        """Получить функции правдоподобия (только для одиночных альтернатив)"""
        return self.plausibility_functions.copy()

    def get_intervals(self) -> Dict[frozenset, Tuple[float, float]]:
        """Получить интервалы доверия (только для одиночных альтернатив)"""
        return self.intervals.copy()

    def get_scores(self) -> Dict[str, float]:
        """Получить оценки альтернатив"""
        return self.scores.copy()

    def get_ranking(self) -> List[Tuple[str, float]]:
        """Получить ранжирование альтернатив"""
        return self.ranking.copy()
