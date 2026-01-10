import xml.etree.ElementTree as ET
import os
from typing import Dict, List, Any, Optional
from utils import Utils

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
            
            # Проверяем формат файла
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
                
                # Эксперты (из метаданных)
                experts_elem = metadata.find('experts')
                if experts_elem is not None and experts_elem.text:
                    experts_list = [
                        exp.strip() for exp in experts_elem.text.split(',') 
                        if exp.strip()
                    ]
                    data['metadata']['experts_list'] = experts_list
                
                # Дополнительные метаданные
                for child in metadata:
                    if child.tag not in ['alternatives', 'criteria', 'experts']:
                        data['metadata'][child.tag] = child.text
            
            # Читаем данные экспертов
            experts_root = root.find('experts')
            if experts_root is None:
                print("❌ Не найден элемент 'experts'")
                return None
            
            for expert_elem in experts_root.findall('expert'):
                expert_name = expert_elem.get('name')
                if not expert_name:
                    print("⚠️  Пропущен эксперт без имени")
                    continue
                
                # Вес эксперта
                try:
                    weight = float(expert_elem.get('weight', 0.5))
                except ValueError:
                    print(f"⚠️  Некорректный вес для эксперта {expert_name}, используется 0.5")
                    weight = 0.5
                
                # CPV значения
                cpvs = {}
                cpvs_elem = expert_elem.find('cpvs')
                if cpvs_elem is not None:
                    for cpv_elem in cpvs_elem.findall('criterion'):
                        crit_name = cpv_elem.get('name')
                        try:
                            cpv_value = float(cpv_elem.text) if cpv_elem.text else 0.0
                            cpvs[crit_name] = cpv_value
                        except ValueError:
                            print(f"⚠️  Некорректный CPV для {expert_name}/{crit_name}")
                            cpvs[crit_name] = 0.0
                
                # Предпочтения
                preferences = {}
                prefs_elem = expert_elem.find('preferences')
                if prefs_elem is not None:
                    for crit_elem in prefs_elem.findall('criterion'):
                        crit_name = crit_elem.get('name')
                        preferences[crit_name] = {}
                        
                        for group_elem in crit_elem.findall('group'):
                            group_str = group_elem.text.strip() if group_elem.text else ""
                            try:
                                pref_value = int(group_elem.get('preference', 1))
                            except ValueError:
                                print(f"⚠️  Некорректное значение предпочтения для {expert_name}/{crit_name}")
                                pref_value = 1
                            
                            if group_str:
                                preferences[crit_name][group_str] = pref_value
                
                # Сохраняем данные эксперта
                data['experts'][expert_name] = {
                    'weight': weight,
                    'cpvs': cpvs,
                    'preferences': preferences
                }
            
            # Проверяем целостность данных
            if not GDMXMLParser.validate_data(data):
                return None
            
            print(f"✅ Успешно загружено:")
            print(f"   Альтернативы: {len(data['alternatives'])} ({', '.join(data['alternatives'])})")
            print(f"   Критерии: {len(data['criteria'])} ({', '.join(data['criteria'])})")
            print(f"   Эксперты: {len(data['experts'])} ({', '.join(data['experts'].keys())})")
            
            return data
            
        except ET.ParseError as e:
            print(f"❌ Ошибка парсинга XML: {e}")
            return None
        except Exception as e:
            print(f"❌ Ошибка при чтении файла: {e}")
            return None
    
    @staticmethod
    def validate_data(data: Dict[str, Any]) -> bool:
        """Проверка целостности загруженных данных"""
        
        # Проверяем альтернативы
        if not data['alternatives']:
            print("❌ Нет альтернатив в файле")
            return False
        
        # Проверяем критерии
        if not data['criteria']:
            print("❌ Нет критериев в файле")
            return False
        
        # Проверяем экспертов
        if not data['experts']:
            print("❌ Нет данных об экспертах")
            return False
        
        # Проверяем каждого эксперта
        for expert_name, expert_data in data['experts'].items():
            # Проверяем CPV
            if not Utils.validate_cpvs(expert_data['cpvs'], data['criteria']):
                print(f"❌ Некорректные CPV для эксперта {expert_name}")
                return False
            
            # Проверяем предпочтения
            if not Utils.validate_preferences(expert_data['preferences'], data['alternatives']):
                print(f"❌ Некорректные предпочтения для эксперта {expert_name}")
                return False
        
        return True

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
        print(f"    {', '.join(data['alternatives'])}")
        
        print(f"\n  Критерии: {len(data['criteria'])}")
        print(f"    {', '.join(data['criteria'])}")
        
        print(f"\n  Эксперты: {len(data['experts'])}")
        for expert_name in data['experts'].keys():
            print(f"    • {expert_name}")
        
        print(f"\n👥 Детали по экспертам:")
        for expert_name, expert_data in data['experts'].items():
            print(f"\n  Эксперт: {expert_name}")
            print(f"    Вес: {expert_data['weight']}")
            
            print(f"    CPV:")
            for criterion, cpv in expert_data['cpvs'].items():
                print(f"      {criterion}: {cpv:.3f}")
            
            print(f"    Групп предпочтений:")
            total_groups = 0
            for criterion, groups in expert_data['preferences'].items():
                print(f"      {criterion}: {len(groups)} групп")
                total_groups += len(groups)
            print(f"    Всего: {total_groups} групп")