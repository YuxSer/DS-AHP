import random
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
from datetime import datetime
from typing import List, Dict, Tuple, Set

class XMLDataGenerator:
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
        self.generated_files = []

    def generate_alternatives(self, n: int) -> List[str]:
        """Генерация n альтернатив"""
        if n <= 0:
            return []

        # Для больших наборов используем компактный формат
        if n <= 1000:
            return [f"A{i:04d}" for i in range(1, n + 1)]
        else:
            return [f"A{i}" for i in range(1, n + 1)]

    def generate_criteria(self, m: int) -> List[str]:
        """
        Генерация m критериев
        """
        if m <= 0:
            return []

        base_criteria = [
            "Качество", "Стоимость", "Надежность", "Удобство", "Производительность",
            "Безопасность", "Экологичность", "Срок_службы", "Гарантия", "Поддержка",
            "Гибкость", "Совместимость", "Масштабируемость", "Простота_использования",
            "Техподдержка", "Документация", "Сообщество", "Обновления", "Интеграция",
            "Кастомизация", "Рентабельность", "Доступность", "Инновационность",
            "Стабильность", "Сервис", "Репутация", "Опыт", "Квалификация", "Ресурсы"
        ]

        if m <= len(base_criteria):
            return base_criteria[:m]
        else:
            # Генерируем дополнительные критерии
            additional = m - len(base_criteria)
            return base_criteria + [f"Критерий_{i + 30}" for i in range(additional)]

    def generate_expert_names(self, k: int) -> List[str]:
        """
        Генерация имен экспертов
        """
        if k <= 0:
            return []

        base_names = ["Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнов",
                      "Попов", "Лебедев", "Козлов", "Новиков", "Морозов",
                      "Волков", "Соловьев", "Васильев", "Зайцев", "Павлов",
                      "Семенов", "Голубев", "Виноградов", "Богданов", "Воробьев",
                      "Федоров", "Михайлов", "Беляев", "Тарасов", "Белов",
                      "Комаров", "Орлов", "Киселев", "Макаров", "Андреев",
                      "Николаев", "Максимов", "Осипов", "Марков", "Гусев",
                      "Титов", "Кузьмин", "Кудрявцев", "Баранов", "Куликов"]

        if k <= len(base_names):
            return base_names[:k]
        else:
            # Генерируем дополнительные имена
            additional = k - len(base_names)
            result = base_names.copy()

            for i in range(additional):
                if i < 100:
                    result.append(f"Эксперт_{i + 41}")
                else:
                    result.append(f"Expert_{i + 1}")

            return result

    def generate_expert_weights(self, k: int,
                                distribution: str = "random") -> List[float]:
        """
        Генерация весов экспертов (оптимизированная для больших наборов)
        """
        if k <= 0:
            return []

        if distribution == "equal":
            return [1.0] * k
        elif distribution == "decreasing":
            if k == 1:
                return [1.0]
            weights = [1.0 - i * 0.8 / (k - 1) for i in range(k)]
            return [max(w, 0.1) for w in weights]
        else:  # random (оптимизированный)
            if k == 1:
                return [1.0]

            # Генерируем случайные веса с разными распределениями
            weights = []
            for i in range(k):
                if i < k // 3:
                    # Первая треть - более высокие веса
                    weight = random.uniform(0.7, 1.0)
                elif i < 2 * k // 3:
                    # Вторая треть - средние веса
                    weight = random.uniform(0.4, 0.8)
                else:
                    # Последняя треть - более низкие веса
                    weight = random.uniform(0.2, 0.6)

                weights.append(round(weight, 3))

            # Нормализуем чтобы максимальный был 1.0
            max_weight = max(weights)
            if max_weight > 0:
                weights = [round(w / max_weight, 3) for w in weights]

            return weights

    def generate_cpvs(self, criteria: List[str]) -> Dict[str, float]:

        n = len(criteria)

        if n == 0:
            return {}
        if n == 1:
            return {criteria[0]: 1.0}

        # Генерируем случайные значения
        values = []
        for i in range(n):
            # Используем разные распределения для разнообразия
            if i < n // 3:
                # Первая треть - более высокие значения
                value = random.uniform(5, 10)
            elif i < 2 * n // 3:
                # Вторая треть - средние значения
                value = random.uniform(2, 6)
            else:
                # Последняя треть - более низкие значения
                value = random.uniform(1, 3)
            values.append(value)

        # Нормализуем
        total = sum(values)
        cpvs = {}

        for i, criterion in enumerate(criteria):
            cpv = values[i] / total
            # Округляем до 5 знаков для большей точности
            cpvs[criterion] = round(cpv, 5)

        return cpvs

    def generate_preferences_for_expert(self, alternatives: List[str],
                                        criteria: List[str]) -> Dict[str, Dict[str, int]]:
        """
        Оптимизированная генерация предпочтений для больших наборов
        """
        preferences = {}
        n = len(alternatives)

        if n == 0:
            return {}

        for criterion in criteria:
            # Создаем копию альтернатив для перемешивания
            shuffled_alts = alternatives.copy()
            random.shuffle(shuffled_alts)

            # Определяем количество групп (от 2 до min(20, n/3))
            max_groups = min(20, max(2, n // 3))
            min_groups = min(5, max_groups)

            num_groups = random.randint(min_groups, max_groups)

            # Распределяем альтернативы по группам
            groups = []
            remaining_alts = shuffled_alts.copy()

            # Создаем группы с оптимальным размером
            avg_group_size = max(1, n // num_groups)

            for i in range(num_groups - 1):
                # Размер группы варьируется вокруг среднего
                min_size = max(1, avg_group_size - 2)
                max_size = min(len(remaining_alts) - (num_groups - i - 1),
                               avg_group_size + 2)

                if max_size < min_size:
                    group_size = min_size
                else:
                    group_size = random.randint(min_size, max_size)

                group = remaining_alts[:group_size]
                groups.append(group)
                remaining_alts = remaining_alts[group_size:]

            # Последняя группа получает все оставшиеся альтернативы
            if remaining_alts:
                groups.append(remaining_alts)

            # Назначаем предпочтения группам
            groups_sorted = sorted(groups, key=len, reverse=True)

            # Определяем максимальное предпочтение
            max_pref = min(15, len(groups_sorted))
            if len(groups_sorted) > 15:
                max_pref = len(groups_sorted)

            criterion_preferences = {}
            used_preferences = set()

            for i, group in enumerate(groups_sorted):
                # Вычисляем базовое предпочтение
                base_pref = max_pref - i
                if base_pref < 1:
                    base_pref = 1

                # Добавляем небольшую вариацию
                if len(groups_sorted) <= 10:
                    pref = base_pref + random.randint(-1, 1)
                else:
                    pref = base_pref

                pref = max(1, pref)

                # Убеждаемся, что предпочтения уникальны
                attempts = 0
                while pref in used_preferences and attempts < 5:
                    pref = (pref % max_pref) + 1
                    attempts += 1

                used_preferences.add(pref)

                # Форматируем группу
                group_str = ",".join(sorted(group))
                criterion_preferences[group_str] = pref

            preferences[criterion] = criterion_preferences

        return preferences

    def generate_dataset(self,
                         n_alternatives: int = 50,
                         m_criteria: int = 8,
                         k_experts: int = 12,
                         weight_distribution: str = "random",
                         output_dir: str = "generated_xml") -> Dict:
        print("\n" + "=" * 70)
        print("ГЕНЕРАЦИЯ ОПТИМИЗИРОВАННЫХ ДАННЫХ ДЛЯ DS/AHP-GDM")
        print("=" * 70)

        # Проверяем и корректируем значения
        n_alternatives = max(1, min(1000, n_alternatives))
        m_criteria = max(1, min(100, m_criteria))
        k_experts = max(1, min(200, k_experts))

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
        print(f"  Альтернативы: первые 5 - {alternatives[:5]}")
        print(f"  Критерии: первые 5 - {criteria[:5]}")
        print(f"  Эксперты: первые 5 - {expert_names[:5]}")

        # Генерируем данные для каждого эксперта
        experts_data = {}

        print(f"\n🔧 Генерация данных экспертов...")

        # Прогресс-бар
        progress_step = max(1, k_experts // 10)

        for i, expert_name in enumerate(expert_names):
            if i % progress_step == 0:
                progress = (i + 1) / k_experts * 100
                print(f"  Прогресс: {progress:.0f}% ({i + 1}/{k_experts})")

            # Генерируем CPV
            cpvs = self.generate_cpvs(criteria)

            # Генерируем предпочтения
            preferences = self.generate_preferences_for_expert(alternatives, criteria)

            experts_data[expert_name] = {
                'weight': expert_weights[i],
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
                    'weight_distribution': weight_distribution,
                    'generator': 'XMLDataGenerator_optimized'
                }
            },
            'alternatives': alternatives,
            'criteria': criteria,
            'experts': experts_data
        }

        # Сохраняем в XML
        xml_file = self.save_to_xml(dataset, output_dir)

        return dataset, xml_file

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
        comment = ET.Comment(' Сгенерировано оптимизированным XMLDataGenerator для DS/AHP-GDM ')
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
        gen_info.set('weight_distribution', dataset['metadata']['parameters']['weight_distribution'])
        gen_info.set('generator', dataset['metadata']['parameters']['generator'])

        # Эксперты
        experts_root = ET.SubElement(root, 'experts')

        for expert_name, expert_data in dataset['experts'].items():
            expert_elem = ET.SubElement(experts_root, 'expert')
            expert_elem.set('name', expert_name)
            expert_elem.set('weight', f"{expert_data['weight']:.3f}")

            # CPV
            cpvs_elem = ET.SubElement(expert_elem, 'cpvs')
            for criterion, cpv in expert_data['cpvs'].items():
                criterion_elem = ET.SubElement(cpvs_elem, 'criterion')
                criterion_elem.set('name', criterion)
                criterion_elem.text = f"{cpv:.5f}"

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

        dom = minidom.parseString(full_xml)
        pretty_xml = dom.toprettyxml(indent="  ")

        # Убираем лишние пустые строки
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        formatted_xml = '\n'.join(lines)

        # Сохраняем файл
        with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
            f.write(formatted_xml)

        file_size = os.path.getsize(filepath)
        print(f"✅ Файл успешно сохранен: {filepath}")
        print(f"📏 Размер файла: {file_size:,} байт ({file_size / 1024:.1f} KB)")

        # Добавляем в список сгенерированных файлов
        self.generated_files.append(filepath)

        return filepath


