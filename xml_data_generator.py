import random
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
from datetime import datetime
from typing import List, Dict, Tuple, Set
import itertools


class XMLDataGenerator:
    """Генератор XML файлов для DS/AHP-GDM"""

    def __init__(self, seed: int = None):

        if seed is not None:
            random.seed(seed)
        self.generated_files = []

    def generate_alternatives(self, n: int) -> List[str]:
        if n < 1:
            n = 1
        elif n > 100:
            n = 100

        return [f"A{i:03d}" for i in range(1, n + 1)]

    def generate_criteria(self, m: int) -> List[str]:
        """
        Генерация m критериев

        Args:
            m: количество критериев (1-10)

        Returns:
            Список критериев
        """
        base_criteria = [
            "Качество", "Стоимость", "Надежность", "Удобство", "Производительность",
            "Безопасность", "Экологичность", "Срок службы", "Гарантия", "Поддержка"
        ]

        if m <= len(base_criteria):
            return base_criteria[:m]
        else:
            return [f"Критерий_{i + 1}" for i in range(m)]

    def generate_expert_names(self, k: int) -> List[str]:
        """
        Генерация имен экспертов

        Args:
            k: количество экспертов (1-10)

        Returns:
            Список имен экспертов
        """
        base_names = ["Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнов",
                      "Попов", "Лебедев", "Козлов", "Новиков", "Морозов"]

        if k <= len(base_names):
            return base_names[:k]
        else:
            return [f"Эксперт_{i + 1}" for i in range(k)]

    def generate_expert_weights(self, k: int,
                                distribution: str = "uniform") -> List[float]:
        """
        Генерация весов экспертов

        Args:
            k: количество экспертов
            distribution: тип распределения ('uniform', 'decreasing', 'equal')

        Returns:
            Список весов экспертов
        """
        if distribution == "equal":
            return [1.0] * k
        elif distribution == "decreasing":
            # Веса уменьшаются от 1.0
            weights = [1.0 - i * 0.8 / (k - 1) for i in range(k)]
            return [max(w, 0.1) for w in weights]  # Минимум 0.1
        else:  # uniform
            return [round(random.uniform(0.3, 1.0), 2) for _ in range(k)]

    def generate_cpvs(self, criteria: List[str]) -> Dict[str, float]:
        """
        Абсолютно надежный метод генерации CPV

        Генерирует целые числа, затем нормализует
        """
        n = len(criteria)

        if n == 1:
            return {criteria[0]: 1.0}

        # Генерируем целые числа от 1 до 10
        int_values = [random.randint(1, 10) for _ in range(n)]

        # Нормализуем к сумме 1.0
        total = sum(int_values)
        cpvs = {}

        for i, criterion in enumerate(criteria):
            cpv = int_values[i] / total

            # Округляем до 3 знаков
            cpvs[criterion] = round(cpv, 3)

        # Корректируем последнее значение для точной суммы
        current_sum = sum(cpvs.values())
        if abs(current_sum - 1.0) > 0.0001:
            last_criterion = criteria[-1]
            cpvs[last_criterion] = round(cpvs[last_criterion] + (1.0 - current_sum), 3)

        # Финальная проверка
        final_sum = sum(cpvs.values())
        if abs(final_sum - 1.0) > 0.001:
            # Экстренная корректировка
            equal_value = round(1.0 / n, 3)
            cpvs = {c: equal_value for c in criteria}

            # Подгоняем сумму
            adjusted_sum = sum(cpvs.values())
            if adjusted_sum != 1.0:
                cpvs[criteria[0]] = round(cpvs[criteria[0]] + (1.0 - adjusted_sum), 3)

        return cpvs

    def generate_preferences_for_expert(self, alternatives: List[str],
                                        criteria: List[str],
                                        min_groups_per_criterion: int = 2,
                                        max_groups_per_criterion: int = 5) -> Dict[str, Dict[str, int]]:
        """
        Генерация предпочтений для одного эксперта

        Важно: Каждая альтернатива должна встречаться ровно 1 раз в каждом критерии
        """
        preferences = {}
        n = len(alternatives)

        for criterion in criteria:
            # Создаем копию альтернатив для перемешивания
            shuffled_alts = alternatives.copy()
            random.shuffle(shuffled_alts)

            # Определяем количество групп для этого критерия
            num_groups = random.randint(min_groups_per_criterion,
                                        min(max_groups_per_criterion, n // 2))

            # Распределяем альтернативы по группам
            groups = []
            remaining_alts = shuffled_alts.copy()

            # Создаем группы
            for i in range(num_groups - 1):
                # Определяем размер группы (минимум 1, максимум оставшиеся/2)
                max_size = max(1, len(remaining_alts) - (num_groups - i - 1))
                group_size = random.randint(1, min(3, max_size))

                # Берем альтернативы для группы
                group = remaining_alts[:group_size]
                groups.append(group)
                remaining_alts = remaining_alts[group_size:]

            # Последняя группа получает все оставшиеся альтернативы
            if remaining_alts:
                groups.append(remaining_alts)
            else:
                # Если альтернатив не осталось, добавляем одну из существующих групп
                if groups:
                    group_to_split = random.choice(groups)
                    if len(group_to_split) > 1:
                        split_point = random.randint(1, len(group_to_split) - 1)
                        new_group = group_to_split[split_point:]
                        group_to_split = group_to_split[:split_point]
                        groups.append(new_group)

            # Назначаем предпочтения группам (шкала 1-7)
            # Сортируем группы по количеству альтернатив (большие группы получают более высокие предпочтения)
            groups_sorted = sorted(groups, key=len, reverse=True)

            criterion_preferences = {}
            used_preferences = set()

            for i, group in enumerate(groups_sorted):
                # Вычисляем базовое предпочтение (от 7 до 1)
                base_pref = 7 - i
                if base_pref < 1:
                    base_pref = 1

                # Добавляем небольшую случайную вариацию
                pref = base_pref + random.randint(-1, 1)
                pref = max(1, min(7, pref))

                # Убеждаемся, что предпочтения уникальны
                while pref in used_preferences:
                    pref += random.choice([-1, 1])
                    pref = max(1, min(7, pref))

                used_preferences.add(pref)

                # Форматируем группу как строку
                group_str = ",".join(sorted(group))
                criterion_preferences[group_str] = pref

            preferences[criterion] = criterion_preferences

            # ПРОВЕРКА: каждая альтернатива должна встречаться ровно 1 раз
            all_alts_in_groups = []
            for group in groups:
                all_alts_in_groups.extend(group)

            if sorted(all_alts_in_groups) != sorted(alternatives):
                print(f"⚠️  Ошибка: не все альтернативы учтены в критерии {criterion}")
                print(f"  Учтено: {len(all_alts_in_groups)} из {len(alternatives)}")
                # Исправляем: находим пропущенные альтернативы
                missing = set(alternatives) - set(all_alts_in_groups)
                duplicates = set([x for x in all_alts_in_groups if all_alts_in_groups.count(x) > 1])

                if missing:
                    print(f"  Пропущены: {missing}")
                    # Добавляем пропущенные в случайную группу
                    for alt in missing:
                        random.choice(groups).append(alt)

                if duplicates:
                    print(f"  Дубликаты: {duplicates}")

        return preferences

    def validate_preferences(self, preferences: Dict[str, Dict[str, int]],
                             alternatives: List[str]) -> bool:
        """
        Валидация предпочтений

        Проверяет, что каждая альтернатива встречается ровно 1 раз в каждом критерии
        """
        for criterion, groups in preferences.items():
            all_alts_in_criterion = []

            for group_str in groups.keys():
                group_alts = [alt.strip() for alt in group_str.split(',')]
                all_alts_in_criterion.extend(group_alts)

            # Проверяем количество
            if len(all_alts_in_criterion) != len(alternatives):
                print(f"❌ Критерий {criterion}: {len(all_alts_in_criterion)} альтернатив вместо {len(alternatives)}")
                return False

            # Проверяем уникальность
            if len(set(all_alts_in_criterion)) != len(alternatives):
                duplicates = [x for x in all_alts_in_criterion if all_alts_in_criterion.count(x) > 1]
                print(f"❌ Критерий {criterion}: дубликаты {duplicates}")
                return False

            # Проверяем, что все альтернативы присутствуют
            missing = set(alternatives) - set(all_alts_in_criterion)
            if missing:
                print(f"❌ Критерий {criterion}: пропущены {missing}")
                return False

        return True

    def generate_dataset(self,
                         n_alternatives: int = 10,
                         m_criteria: int = 3,
                         k_experts: int = 4,
                         weight_distribution: str = "uniform",
                         output_dir: str = "generated_xml") -> Dict:
        print("\n" + "=" * 70)
        print("ГЕНЕРАЦИЯ ДАННЫХ ДЛЯ DS/AHP-GDM")
        print("=" * 70)

        # Ограничиваем значения
        n_alternatives = max(1, min(100, n_alternatives))
        m_criteria = max(1, min(10, m_criteria))
        k_experts = max(1, min(10, k_experts))

        print(f"\n Параметры генерации:")
        print(f"  • Альтернатив: {n_alternatives}")
        print(f"  • Критериев: {m_criteria}")
        print(f"  • Экспертов: {k_experts}")
        print(f"  • Распределение весов: {weight_distribution}")

        # Генерируем базовые структуры
        alternatives = self.generate_alternatives(n_alternatives)
        criteria = self.generate_criteria(m_criteria)
        expert_names = self.generate_expert_names(k_experts)
        expert_weights = self.generate_expert_weights(k_experts, weight_distribution)

        print(f"\n✅ Сгенерированы базовые структуры:")
        print(f"  Альтернативы: {alternatives[:5]}{'...' if len(alternatives) > 5 else ''}")
        print(f"  Критерии: {criteria}")
        print(f"  Эксперты: {expert_names}")
        print(f"  Веса экспертов: {expert_weights}")

        # Генерируем данные для каждого эксперта
        experts_data = {}

        print(f"\n🔧 Генерация данных экспертов...")

        for i, expert_name in enumerate(expert_names):
            print(f"  Эксперт {i + 1}: {expert_name} (вес: {expert_weights[i]})")

            # Генерируем CPV
            cpvs = self.generate_cpvs(criteria)

            # Генерируем предпочтения
            preferences = self.generate_preferences_for_expert(
                alternatives, criteria,
                min_groups_per_criterion=2,
                max_groups_per_criterion=min(5, n_alternatives // 2)
            )

            # Валидируем предпочтения
            if not self.validate_preferences(preferences, alternatives):
                print(f"  ⚠️  Проблемы с валидацией предпочтений для эксперта {expert_name}")
                print(f"   Исправление...")
                # Исправляем предпочтения
                preferences = self.fix_preferences(preferences, alternatives, criteria)

            experts_data[expert_name] = {
                'weight': expert_weights[i],
                'cpvs': cpvs,
                'preferences': preferences
            }

            # Выводим краткую информацию
            total_groups = sum(len(groups) for groups in preferences.values())
            print(f"    • CPV: {cpvs}")
            print(f"    • Групп предпочтений: {total_groups}")

        # Формируем итоговый набор
        dataset = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'parameters': {
                    'n_alternatives': n_alternatives,
                    'm_criteria': m_criteria,
                    'k_experts': k_experts,
                    'weight_distribution': weight_distribution
                }
            },
            'alternatives': alternatives,
            'criteria': criteria,
            'experts': experts_data
        }

        # Выводим сводку
        self.print_summary(dataset)

        # Сохраняем в XML
        xml_file = self.save_to_xml(dataset, output_dir)

        return dataset, xml_file

    def fix_preferences(self, preferences: Dict[str, Dict[str, int]],
                         alternatives: List[str],
                         criteria: List[str]) -> Dict[str, Dict[str, int]]:
        """
        Исправление предпочтений, чтобы каждая альтернатива встречалась ровно 1 раз
        """
        fixed_preferences = {}

        for criterion in criteria:
            if criterion not in preferences:
                # Создаем новые предпочтения для этого критерия
                groups = []
                shuffled_alts = alternatives.copy()
                random.shuffle(shuffled_alts)

                # Разбиваем на 2-5 групп
                num_groups = random.randint(2, min(5, len(alternatives) // 2))

                for i in range(num_groups - 1):
                    group_size = random.randint(1, len(shuffled_alts) - (num_groups - i - 1))
                    group = shuffled_alts[:group_size]
                    groups.append(group)
                    shuffled_alts = shuffled_alts[group_size:]

                if shuffled_alts:
                    groups.append(shuffled_alts)

                # Назначаем предпочтения
                criterion_prefs = {}
                groups_sorted = sorted(groups, key=len, reverse=True)
                used_prefs = set()

                for i, group in enumerate(groups_sorted):
                    base_pref = 7 - i
                    if base_pref < 1:
                        base_pref = 1

                    pref = base_pref + random.randint(-1, 1)
                    pref = max(1, min(7, pref))

                    while pref in used_prefs:
                        pref += random.choice([-1, 1])
                        pref = max(1, min(7, pref))

                    used_prefs.add(pref)
                    group_str = ",".join(sorted(group))
                    criterion_prefs[group_str] = pref

                fixed_preferences[criterion] = criterion_prefs
            else:
                # Исправляем существующие предпочтения
                original_groups = list(preferences[criterion].keys())
                original_prefs = list(preferences[criterion].values())

                # Собираем все альтернативы из групп
                all_alts = []
                for group_str in original_groups:
                    group_alts = [alt.strip() for alt in group_str.split(',')]
                    all_alts.extend(group_alts)

                # Находим проблемы
                alt_counts = {}
                for alt in all_alts:
                    alt_counts[alt] = alt_counts.get(alt, 0) + 1

                missing_alts = set(alternatives) - set(all_alts)
                duplicate_alts = {alt for alt, count in alt_counts.items() if count > 1}

                if not missing_alts and not duplicate_alts:
                    # Все в порядке
                    fixed_preferences[criterion] = preferences[criterion]
                    continue

                # Исправляем: сначала удаляем дубликаты
                fixed_groups = []
                used_alts = set()

                for group_str in original_groups:
                    group_alts = [alt.strip() for alt in group_str.split(',')]
                    # Убираем дубликаты
                    unique_alts = []
                    for alt in group_alts:
                        if alt not in used_alts:
                            unique_alts.append(alt)
                            used_alts.add(alt)

                    if unique_alts:
                        fixed_groups.append(unique_alts)

                # Добавляем пропущенные альтернативы
                for alt in missing_alts:
                    if alt not in used_alts:
                        # Добавляем в случайную группу
                        if fixed_groups:
                            random.choice(fixed_groups).append(alt)
                            used_alts.add(alt)
                        else:
                            fixed_groups.append([alt])
                            used_alts.add(alt)

                # Создаем фиксированные предпочтения
                fixed_prefs = {}
                groups_sorted = sorted(fixed_groups, key=len, reverse=True)

                # Используем оригинальные предпочтения, если возможно
                for i, group in enumerate(groups_sorted):
                    group_str = ",".join(sorted(group))

                    if i < len(original_prefs):
                        pref = original_prefs[i]
                    else:
                        base_pref = 7 - i
                        if base_pref < 1:
                            base_pref = 1
                        pref = base_pref

                    fixed_prefs[group_str] = pref

                fixed_preferences[criterion] = fixed_prefs

        return fixed_preferences

    def print_summary(self, dataset: Dict):
        """Вывод сводки по сгенерированным данным"""
        print("\n" + "=" * 70)
        print("СВОДКА ПО СГЕНЕРИРОВАННЫМ ДАННЫМ")
        print("=" * 70)

        alternatives = dataset['alternatives']
        criteria = dataset['criteria']
        experts = dataset['experts']

        print(f"\n Общая информация:")
        print(f"  • Альтернатив: {len(alternatives)}")
        print(f"  • Критериев: {len(criteria)}")
        print(f"  • Экспертов: {len(experts)}")

        print(f"\n Проверка корректности:")

        # Проверяем каждого эксперта
        all_valid = True

        for expert_name, expert_data in experts.items():
            print(f"\n Эксперт: {expert_name}")
            print(f"    • Вес: {expert_data['weight']}")
            print(f"    • Сумма CPV: {sum(expert_data['cpvs'].values()):.3f}")

            # Проверяем предпочтения
            preferences = expert_data['preferences']
            is_valid = self.validate_preferences(preferences, alternatives)

            if is_valid:
                print(f"    • ✅ Предпочтения корректны")

                # Считаем статистику по группам
                total_groups = sum(len(groups) for groups in preferences.values())
                avg_group_size = sum(len(group_str.split(',')) for criterion_groups in preferences.values()
                                     for group_str in criterion_groups.keys()) / total_groups if total_groups > 0 else 0

                print(f"    • Групп: {total_groups}")
                print(f"    • Средний размер группы: {avg_group_size:.1f}")
            else:
                print(f"    • ❌ Предпочтения содержат ошибки")
                all_valid = False

        if all_valid:
            print(f"\n ВСЕ ДАННЫЕ КОРРЕКТНЫ!")
        else:
            print(f"\n⚠️  Обнаружены проблемы в данных")

    def save_to_xml(self, dataset: Dict, output_dir: str = "generated_xml") -> str:
        # Создаем директорию если нужно
        os.makedirs(output_dir, exist_ok=True)

        # Генерируем имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        n_alts = len(dataset['alternatives'])
        n_experts = len(dataset['experts'])
        filename = f"gdm_data_{n_alts}alt_{n_experts}exp_{timestamp}.xml"
        filepath = os.path.join(output_dir, filename)

        print(f"\n💾 Сохранение в XML файл: {filename}")

        # Создаем корневой элемент
        root = ET.Element('ds_ahp_gdm_analysis')

        # Добавляем комментарий
        comment = ET.Comment(' Сгенерировано XMLDataGenerator для DS/AHP-GDM ')
        root.append(comment)

        # Метаданные
        metadata = ET.SubElement(root, 'metadata')

        # Альтернативы
        alts_elem = ET.SubElement(metadata, 'alternatives')
        alts_elem.text = ','.join(dataset['alternatives'])

        # Критерии
        criteria_elem = ET.SubElement(metadata, 'criteria')
        criteria_elem.text = ','.join(dataset['criteria'])

        # Эксперты
        experts_elem = ET.SubElement(metadata, 'experts')
        experts_elem.text = ','.join(dataset['experts'].keys())

        # Информация о генерации
        gen_info = ET.SubElement(metadata, 'generation_info')
        gen_info.set('timestamp', dataset['metadata']['generated_at'])
        gen_info.set('n_alternatives', str(dataset['metadata']['parameters']['n_alternatives']))
        gen_info.set('n_criteria', str(dataset['metadata']['parameters']['m_criteria']))
        gen_info.set('n_experts', str(dataset['metadata']['parameters']['k_experts']))

        # Эксперты
        experts_root = ET.SubElement(root, 'experts')

        for expert_name, expert_data in dataset['experts'].items():
            expert_elem = ET.SubElement(experts_root, 'expert')
            expert_elem.set('name', expert_name)
            expert_elem.set('weight', f"{expert_data['weight']:.2f}")

            # CPV
            cpvs_elem = ET.SubElement(expert_elem, 'cpvs')
            for criterion, cpv in expert_data['cpvs'].items():
                criterion_elem = ET.SubElement(cpvs_elem, 'criterion')
                criterion_elem.set('name', criterion)
                criterion_elem.text = f"{cpv:.3f}"

            # Предпочтения
            prefs_elem = ET.SubElement(expert_elem, 'preferences')
            for criterion, groups in expert_data['preferences'].items():
                criterion_elem = ET.SubElement(prefs_elem, 'criterion')
                criterion_elem.set('name', criterion)

                for group_str, preference in groups.items():
                    group_elem = ET.SubElement(criterion_elem, 'group')
                    group_elem.set('preference', str(preference))
                    group_elem.text = group_str

        # Форматируем XML
        xml_string = ET.tostring(root, encoding='unicode', method='xml')

        # Добавляем XML декларацию
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        full_xml = xml_declaration + xml_string

        # Делаем красивое форматирование
        dom = minidom.parseString(full_xml)
        pretty_xml = dom.toprettyxml(indent="  ")

        # Убираем лишние пустые строки
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        formatted_xml = '\n'.join(lines)

        # Сохраняем файл
        with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
            f.write(formatted_xml)

        print(f"✅ Файл успешно сохранен: {filepath}")

        # Добавляем в список сгенерированных файлов
        self.generated_files.append(filepath)

        return filepath
