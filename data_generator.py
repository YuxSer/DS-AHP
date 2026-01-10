import random
from datetime import datetime
from typing import List, Dict, Tuple, Set


class DataGenerator:
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)

    def generate_alternatives(self, n: int) -> List[str]:
        """Генерация n альтернатив с именами A001, A002, ..."""
        return [f"A{i:03d}" for i in range(1, n + 1)]

    def generate_criteria(self, m: int) -> List[str]:
        """Генерация m критериев"""
        base_names = ["Качество", "Стоимость", "Надёжность", "Удобство", "Производительность"]
        if m <= len(base_names):
            return base_names[:m]
        return [f"Критерий_{i + 1}" for i in range(m)]

    def generate_expert_weights(self, k: int,
                                distribution: str = "uniform") -> Dict[str, float]:
        """Генерация весов экспертов"""
        experts = {f"E{i + 1}": 1.0 for i in range(k)}

        if distribution == "uniform":
            for name in experts:
                experts[name] = round(random.uniform(0.3, 1.0), 2)
        elif distribution == "decreasing":
            base_weights = [1.0 - i * 0.7 / (k - 1) for i in range(k)]
            for i, name in enumerate(experts.keys()):
                experts[name] = round(base_weights[i], 2)

        return experts

    def generate_cpvs(self, criteria: List[str]) -> Dict[str, float]:
        """Генерация случайных CPV с нормализацией суммы=1"""
        cpvs = {c: random.random() for c in criteria}
        total = sum(cpvs.values())
        return {c: round(v / total, 3) for c, v in cpvs.items()}

    def generate_sparse_groups(self, alternatives: List[str],
                               max_groups: int = 30,
                               max_group_size: int = 2) -> List[str]:
        """
        Генерация разреженных групп (только для 100+ альтернатив)
        Каждая группа - это 1-2 случайные альтернативы
        """
        groups = []
        n = len(alternatives)

        # Выбираем случайные альтернативы для упоминания (10-20% от общего числа)
        mention_count = random.randint(n // 10, n // 5)
        mentioned_alts = random.sample(alternatives, mention_count)

        for _ in range(max_groups):
            # 80% одиночных, 20% пар
            if random.random() < 0.8 or max_group_size < 2:
                # Одиночная альтернатива
                group = [random.choice(mentioned_alts)]
            else:
                # Пара альтернатив
                pair = random.sample(mentioned_alts, 2)
                group = sorted(pair)

            # Форматируем группу
            group_str = ",".join(group)
            if group_str not in groups:
                groups.append(group_str)

        return groups

    def generate_preferences(self, groups: List[str]) -> Dict[str, int]:
        """Назначение предпочтений группам (шкала 1-7)"""
        preferences = {}
        # Сортируем группы по алфавиту для детерминированности
        sorted_groups = sorted(groups)

        # Назначаем предпочтения от высоких к низким
        max_pref = 7
        for i, group in enumerate(sorted_groups):
            # Предпочтения постепенно снижаются
            pref = max(1, max_pref - (i % 3))
            preferences[group] = pref

        return preferences

    def generate_dataset(self,
                         n_alternatives: int = 100,
                         m_criteria: int = 3,
                         k_experts: int = 4,
                         max_groups_per_expert: int = 25,
                         max_group_size: int = 2) -> Dict:
        """
        Основная функция генерации данных

        Args:
            n_alternatives: количество альтернатив (100)
            m_criteria: количество критериев
            k_experts: количество экспертов
            max_groups_per_expert: максимально групп на эксперта
            max_group_size: максимальный размер группы (1 или 2)
        """
        print(f"\n⚡ ГЕНЕРАЦИЯ ДАННЫХ: {n_alternatives} альтернатив")
        print("=" * 60)

        # Генерация базовых структур
        alternatives = self.generate_alternatives(n_alternatives)
        criteria = self.generate_criteria(m_criteria)
        expert_weights = self.generate_expert_weights(k_experts)

        # Генерация данных экспертов
        experts_data = {}
        for expert_name, weight in expert_weights.items():
            cpvs = self.generate_cpvs(criteria)
            preferences = {}

            # Для каждого критерия генерируем группы
            for criterion in criteria:
                groups = self.generate_sparse_groups(
                    alternatives,
                    max_groups=random.randint(5, max_groups_per_expert // m_criteria),
                    max_group_size=max_group_size
                )

                if groups:
                    preferences[criterion] = self.generate_preferences(groups)

            experts_data[expert_name] = {
                'weight': weight,
                'cpvs': cpvs,
                'preferences': preferences
            }

        # Формируем итоговый набор
        dataset = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'parameters': {
                    'n_alternatives': n_alternatives,
                    'm_criteria': m_criteria,
                    'k_experts': k_experts,
                    'max_group_size': max_group_size
                }
            },
            'alternatives': alternatives,
            'criteria': criteria,
            'experts': experts_data
        }

        self.print_summary(dataset)
        return dataset

    def print_summary(self, dataset: Dict):
        print("\n СВОДКА:")
        print(f"  Альтернатив: {len(dataset['alternatives'])}")
        print(f"  Критериев: {len(dataset['criteria'])}")
        print(f"  Экспертов: {len(dataset['experts'])}")

        # Подсчет групп
        total_groups = 0
        mentioned_alts = set()

        for expert_data in dataset['experts'].values():
            for criterion, groups in expert_data['preferences'].items():
                total_groups += len(groups)
                for group_str in groups:
                    for alt in group_str.split(','):
                        mentioned_alts.add(alt.strip())

        print(f"  Всего групп: {total_groups}")
        print(f"  Упомянуто альтернатив: {len(mentioned_alts)}/{len(dataset['alternatives'])}")
        print(f"  Покрытие: {len(mentioned_alts) / len(dataset['alternatives']):.1%}")

