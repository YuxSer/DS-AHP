import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple
from config import Config


class ExportFormats:
    """Экспорт результатов в различные форматы"""

    def __init__(self, export_dir: str = None):

        if export_dir is None:
            export_dir = Config.EXPORT_DIR

        self.export_dir = export_dir
        self._create_export_directory()

    def _create_export_directory(self):
        """Создание директории для экспорта"""
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
            print(f"📁 Создана директория для результатов: {self.export_dir}")

    def generate_filename(self, prefix: str = "results",
                          extension: str = "") -> str:

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if extension:
            if not extension.startswith('.'):
                extension = '.' + extension
            filename = f"{prefix}_{timestamp}{extension}"
        else:
            filename = f"{prefix}_{timestamp}"

        return os.path.join(self.export_dir, filename)

    # ==================== ЭКСПОРТ В XML ====================

    def export_to_xml(self, results: Dict[str, Any],
                      expert_data: Dict[str, Any],
                      filename: str = None) -> str:
        if filename is None:
            filename = self.generate_filename("gdm_results", "xml")

        try:
            # Создаем корневой элемент
            root = ET.Element('ds_ahp_gdm_results')

            # Метаданные
            metadata = ET.SubElement(root, 'metadata')

            timestamp_elem = ET.SubElement(metadata, 'timestamp')
            timestamp_elem.text = datetime.now().isoformat()

            analysis_type = ET.SubElement(metadata, 'analysis_type')
            analysis_type.text = 'DS/AHP-GDM'

            # Информация о задаче
            task_info = ET.SubElement(metadata, 'task_info')

            alternatives_elem = ET.SubElement(task_info, 'alternatives')
            alternatives_elem.text = ', '.join(expert_data.get('alternatives', []))

            criteria_elem = ET.SubElement(task_info, 'criteria')
            criteria_elem.text = ', '.join(expert_data.get('criteria', []))

            experts_elem = ET.SubElement(task_info, 'experts_count')
            experts_elem.text = str(len(expert_data.get('experts', {})))

            # Оптимальная альтернатива
            optimal = results.get('optimal_alternative', '')
            if optimal:
                optimal_elem = ET.SubElement(metadata, 'optimal_alternative')
                optimal_elem.text = optimal

            # Информация об экспертах
            experts_info = ET.SubElement(root, 'experts_info')
            for exp_name, exp_data in expert_data.get('experts', {}).items():
                exp_elem = ET.SubElement(experts_info, 'expert')
                exp_elem.set('name', exp_name)
                exp_elem.set('weight', f"{exp_data.get('weight', 0):.3f}")
                exp_elem.set('discount_rate',
                             f"{exp_data.get('discount_rate', 0):.3f}")

            # Ранжирование альтернатив
            ranking = results.get('ranking', [])
            if ranking:
                ranking_elem = ET.SubElement(root, 'ranking')

                for i, (alt, score) in enumerate(ranking, 1):
                    rank_elem = ET.SubElement(ranking_elem, 'alternative')
                    rank_elem.set('rank', str(i))
                    rank_elem.set('name', alt)
                    rank_elem.set('score', f"{score:.6f}")

                    # Интервалы доверия
                    intervals = results.get('intervals', {})
                    alt_set = frozenset([alt])
                    if alt_set in intervals:
                        bel, pl = intervals[alt_set]
                        rank_elem.set('belief', f"{bel:.6f}")
                        rank_elem.set('plausibility', f"{pl:.6f}")
                        rank_elem.set('interval', f"[{bel:.4f}, {pl:.4f}]")

                    if alt == optimal:
                        rank_elem.set('optimal', 'true')

            # Функции доверия и правдоподобия
            belief = results.get('belief_functions', {})
            plausibility = results.get('plausibility_functions', {})

            if belief and plausibility:
                functions_elem = ET.SubElement(root, 'belief_plausibility_functions')

                # Только для одиночных альтернатив
                for alt in expert_data.get('alternatives', []):
                    alt_set = frozenset([alt])
                    if alt_set in belief and alt_set in plausibility:
                        func_elem = ET.SubElement(functions_elem, 'alternative')
                        func_elem.set('name', alt)
                        func_elem.set('belief', f"{belief[alt_set]:.6f}")
                        func_elem.set('plausibility', f"{plausibility[alt_set]:.6f}")

            # Форматируем XML
            xml_string = ET.tostring(root, encoding='unicode', method='xml')
            xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
            full_xml = xml_declaration + xml_string

            dom = minidom.parseString(full_xml)
            pretty_xml = dom.toprettyxml(indent="  ")

            # Убираем лишние пустые строки
            lines = [line for line in pretty_xml.split('\n') if line.strip()]
            formatted_xml = '\n'.join(lines)

            # Сохраняем
            with open(filename, 'w', encoding='utf-8', newline='\n') as f:
                f.write(formatted_xml)

            print(f"✅ Результаты экспортированы в XML: {filename}")
            return filename

        except Exception as e:
            print(f"❌ Ошибка при экспорте в XML: {e}")
            return None

    # ==================== ЭКСПОРТ В JSON ====================

    def export_to_json(self, results: Dict[str, Any],
                       expert_data: Dict[str, Any],
                       filename: str = None) -> str:

        if filename is None:
            filename = self.generate_filename("gdm_results", "json")

        try:
            export_data = {
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'analysis_type': 'DS/AHP-GDM',
                    'version': '1.0'
                },
                'task_info': {
                    'alternatives': expert_data.get('alternatives', []),
                    'criteria': expert_data.get('criteria', []),
                    'experts_count': len(expert_data.get('experts', {}))
                },
                'experts_info': {},
                'results': {
                    'optimal_alternative': results.get('optimal_alternative', ''),
                    'ranking': [],
                    'intervals': {},
                    'scores': results.get('scores', {})
                }
            }

            # Информация об экспертах
            for exp_name, exp_data in expert_data.get('experts', {}).items():
                export_data['experts_info'][exp_name] = {
                    'weight': exp_data.get('weight', 0),
                    'discount_rate': exp_data.get('discount_rate', 0)
                }

            # Ранжирование
            ranking = results.get('ranking', [])
            export_data['results']['ranking'] = [
                {
                    'rank': i,
                    'alternative': alt,
                    'score': float(score)
                }
                for i, (alt, score) in enumerate(ranking, 1)
            ]

            # Интервалы
            intervals = results.get('intervals', {})
            for alt in expert_data.get('alternatives', []):
                alt_set = frozenset([alt])
                if alt_set in intervals:
                    bel, pl = intervals[alt_set]
                    export_data['results']['intervals'][alt] = {
                        'belief': float(bel),
                        'plausibility': float(pl),
                        'interval': f"[{bel:.4f}, {pl:.4f}]",
                        'width': float(pl - bel)
                    }

            # Сохраняем
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            print(f"✅ Результаты экспортированы в JSON: {filename}")
            return filename

        except Exception as e:
            print(f"❌ Ошибка при экспорте в JSON: {e}")
            return None


    def export_to_all_formats(self, results: Dict[str, Any],
                              expert_data: Dict[str, Any],
                              base_filename: str = None) -> Dict[str, str]:

        if base_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"gdm_results_{timestamp}"
            base_path = os.path.join(self.export_dir, base_filename)
        else:
            base_path = os.path.join(self.export_dir, base_filename)

        export_files = {}

        # Экспорт в XML
        xml_file = self.export_to_xml(results, expert_data, f"{base_path}.xml")
        if xml_file:
            export_files['xml'] = xml_file

        # Экспорт в JSON
        json_file = self.export_to_json(results, expert_data, f"{base_path}.json")
        if json_file:
            export_files['json'] = json_file


        # Вывод информации
        if export_files:
            print(f"\n📁 Все файлы сохранены в папке: {self.export_dir}/")
            print(f"📄 Экспортированные файлы:")
            for format_name, file_path in export_files.items():
                filename = os.path.basename(file_path)
                print(f"  • {format_name.upper()}: {filename}")

        return export_files