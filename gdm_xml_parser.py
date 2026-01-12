import xml.etree.ElementTree as ET
import os
from typing import Dict, List, Any, Optional

class GDMXMLParser:

    @staticmethod
    def parse_gdm_xml(file_path: str) -> Optional[Dict[str, Any]]:
        if not os.path.exists(file_path):
            print(f"❌ Файл {file_path} не найден!")
            return None

        try:
            print(f"\n Чтение GDM XML файла: {file_path}")
            tree = ET.parse(file_path)
            root = tree.getroot()

            if root.tag != 'ds_ahp_gdm_analysis':
                print("❌ Неверный формат XML файла. Ожидается 'ds_ahp_gdm_analysis'")
                return None

            # Инициализируем структуру данных
            data = {
                'alternatives': [],
                'criteria': [],
                'experts': {},
                'metadata': {}
            }

            # Читаем метаданные
            metadata = root.find('metadata')
            if metadata is not None:
                # Альтернативы
                alts_elem = metadata.find('alternatives')
                if alts_elem is not None and alts_elem.text:
                    data['alternatives'] = [
                        alt.strip() for alt in alts_elem.text.split(',')
                        if alt.strip()
                    ]

                # Критерии
                criteria_elem = metadata.find('criteria')
                if criteria_elem is not None and criteria_elem.text:
                    data['criteria'] = [
                        crit.strip() for crit in criteria_elem.text.split(',')
                        if crit.strip()
                    ]

                # Информация о генерации
                gen_info = metadata.find('generation_info')
                if gen_info is not None:
                    data['metadata']['generation_info'] = {
                        'timestamp': gen_info.get('timestamp', ''),
                        'n_alternatives': gen_info.get('n_alternatives', ''),
                        'n_criteria': gen_info.get('n_criteria', ''),
                        'n_experts': gen_info.get('n_experts', ''),
                        'weight_distribution': gen_info.get('weight_distribution', ''),
                        'generator': gen_info.get('generator', '')
                    }

            # Читаем данные экспертов
            experts_root = root.find('experts')
            if experts_root is not None:
                for expert_elem in experts_root.findall('expert'):
                    expert_name = expert_elem.get('name', 'Unknown')

                    # Вес эксперта
                    try:
                        weight_str = expert_elem.get('weight', '0.5').strip()
                        weight = float(weight_str)
                    except (ValueError, TypeError):
                        weight = 0.5

                    # CPV значения
                    cpvs = {}
                    cpvs_elem = expert_elem.find('cpvs')
                    if cpvs_elem is not None:
                        for cpv_elem in cpvs_elem.findall('criterion'):
                            crit_name = cpv_elem.get('name', '')
                            try:
                                cpv_text = cpv_elem.text.strip() if cpv_elem.text else "0.0"
                                cpv_value = float(cpv_text)
                                cpvs[crit_name] = cpv_value
                            except (ValueError, TypeError):
                                cpvs[crit_name] = 0.0

                    # Предпочтения
                    preferences = {}
                    prefs_elem = expert_elem.find('preferences')
                    if prefs_elem is not None:
                        for crit_elem in prefs_elem.findall('criterion'):
                            crit_name = crit_elem.get('name', '')
                            preferences[crit_name] = {}

                            for group_elem in crit_elem.findall('group'):
                                group_str = group_elem.text.strip() if group_elem.text else ""
                                try:
                                    pref_value_str = group_elem.get('preference', '1').strip()
                                    pref_value = int(pref_value_str)
                                except (ValueError, TypeError):
                                    pref_value = 1

                                if group_str:
                                    preferences[crit_name][group_str] = pref_value

                    # Сохраняем данные эксперта
                    data['experts'][expert_name] = {
                        'weight': weight,
                        'cpvs': cpvs,
                        'preferences': preferences
                    }

            print(f"✅ Успешно загружено:")
            print(f"   Альтернативы: {len(data['alternatives'])}")
            print(f"   Критерии: {len(data['criteria'])}")
            print(f"   Экспертов: {len(data['experts'])}")

            return data

        except ET.ParseError as e:
            print(f"❌ Ошибка парсинга XML: {e}")
            return None
        except Exception as e:
            print(f"❌ Ошибка при чтении файла: {e}")
            return None

    @staticmethod
    def print_data_summary(data: Dict[str, Any]):
        """Вывод сводки по загруженным данным"""
        if not data:
            print("❌ Нет данных для отображения")
            return

        print("\n" + "=" * 60)
        print("СВОДКА ЗАГРУЖЕННЫХ ДАННЫХ")
        print("=" * 60)

        print(f"\n Общая информация:")
        print(f"  Альтернативы: {len(data['alternatives'])}")
        if len(data['alternatives']) <= 10:
            print(f"    {', '.join(data['alternatives'])}")
        else:
            print(f"    {', '.join(data['alternatives'][:5])}...")

        print(f"\n  Критерии: {len(data['criteria'])}")
        if len(data['criteria']) <= 10:
            print(f"    {', '.join(data['criteria'])}")
        else:
            print(f"    {', '.join(data['criteria'][:5])}...")

        print(f"\n  Эксперты: {len(data['experts'])}")
        if len(data['experts']) <= 10:
            for expert_name in data['experts'].keys():
                print(f"    • {expert_name}")
        else:
            expert_names = list(data['experts'].keys())
            for expert_name in expert_names[:5]:
                print(f"    • {expert_name}")
            print(f"    ...")

        # Информация о генерации
        if 'generation_info' in data['metadata']:
            print(f"\n📊 Информация о генерации:")
            gen_info = data['metadata']['generation_info']

            if 'timestamp' in gen_info and gen_info['timestamp']:
                try:
                    dt_str = gen_info['timestamp']
                    if 'T' in dt_str:
                        dt_str = dt_str.split('T')[0]
                    print(f"  Дата создания: {dt_str}")
                except:
                    pass

            params_to_show = ['n_alternatives', 'n_criteria', 'n_experts', 'weight_distribution']
            for key in params_to_show:
                if key in gen_info and gen_info[key]:
                    display_name = {
                        'n_alternatives': 'Альтернатив',
                        'n_criteria': 'Критериев',
                        'n_experts': 'Экспертов',
                        'weight_distribution': 'Распределение весов'
                    }.get(key, key)
                    print(f"  {display_name}: {gen_info[key]}")


