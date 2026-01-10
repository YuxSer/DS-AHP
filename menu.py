import os
from config import Config
from gdm_analyzer import GDMAnalyzer
from xml_data_generator import XMLDataGenerator

generator = XMLDataGenerator()


class Menu:
    """Текстовое меню для взаимодействия с пользователем"""

    def __init__(self):
        """Инициализация меню"""
        self.analyzer = None
        self.current_file = None

    def show_main_menu(self):
        """Главное меню программы"""
        while True:
            print("\n" + "=" * 70)
            print("             СИСТЕМА ГРУППОВОГО ПРИНЯТИЯ РЕШЕНИЙ")
            print("                    DS/AHP-GDM v1.0")
            print("=" * 70)

            print("\nГЛАВНОЕ МЕНЮ:")
            print("1. Загрузить данные из XML файла")
            print("2. Настройки анализа")
            print("3. Запустить анализ")
            print("4. Сгенерировать новые данные (XML)")
            print("5. Выход")

            choice = input("\nВыберите пункт меню (0-4): ").strip()

            if choice == "1":
                self.load_data_from_xml()
            elif choice == "2":
                self.settings_menu()
            elif choice == "3":
                self.run_analysis()
            elif choice == "4":
                self.generate_custom_data(generator)
            elif choice == "5":
                print("Выход из программы...")
                break
            else:
                print("❌ Неверный выбор! Попробуйте снова.")

    def load_data_from_xml(self):
        """Загрузка данных из XML файла"""
        print("\n" + "=" * 50)
        print("ЗАГРУЗКА ДАННЫХ ИЗ XML ФАЙЛА")
        print("=" * 50)

        while True:
            file_path = input("\nВведите путь к XML файлу: ").strip()

            if not file_path:
                print("❌ Путь не может быть пустым!")
                continue

            if not os.path.exists(file_path):
                print(f"❌ Файл '{file_path}' не найден!")

                retry = input("Попробовать снова? (y/n): ").strip().lower()
                if retry not in ['y', 'yes', 'д', 'да']:
                    break
                continue

            # Проверяем расширение файла
            if not file_path.lower().endswith('.xml'):
                print("⚠️  Файл не имеет расширения .xml")

                proceed = input("Все равно загрузить? (y/n): ").strip().lower()
                if proceed not in ['y', 'yes', 'д', 'да']:
                    continue

            try:
                # Создаем анализатор
                self.analyzer = GDMAnalyzer()

                # Загружаем данные
                success = self.analyzer.load_data_from_xml(file_path)

                if success:
                    self.current_file = file_path
                    print(f"\n✅ Данные успешно загружены из: {file_path}")
                    break
                else:
                    print("❌ Не удалось загрузить данные из файла")

            except Exception as e:
                print(f"❌ Ошибка при загрузке файла: {e}")

            retry = input("\nПопробовать другой файл? (y/n): ").strip().lower()
            if retry not in ['y', 'yes', 'д', 'да']:
                break


    def settings_menu(self):
        """Меню настроек"""
        if not self.analyzer:
            print("❌ Сначала загрузите данные!")
            return

        while True:
            print("\n" + "=" * 40)
            print("          НАСТРОЙКИ АНАЛИЗА")
            print("=" * 40)

            print("\nТекущие настройки:")
            print(f"  1. Правило комбинирования: {Config.COMBINATION_RULE_NAMES[self.analyzer.combination_rule]}")

            if self.analyzer.combination_rule == Config.COMBINATION_RULE_ADAPTIVE:
                threshold = self.analyzer.conflict_threshold or Config.DEFAULT_CONFLICT_THRESHOLD
                print(f"     (Порог конфликта: X = {threshold})")

            print(f"  2. Коэффициент пессимизма: {self.analyzer.pessimism_coefficient}")

            print("\nВыберите настройку для изменения:")
            print("1. Изменить правило комбинирования")
            print("2. Изменить коэффициент пессимизма")

            if self.analyzer.combination_rule == Config.COMBINATION_RULE_ADAPTIVE:
                print("3. Настроить порог адаптивного правила")
                print("4. Назад в главное меню")
                max_choice = 4
            else:
                print("3. Назад в главное меню")
                max_choice = 3

            choice = input(f"\nВыберите вариант (1-{max_choice}): ").strip()

            if choice == "1":
                self.change_combination_rule()
            elif choice == "2":
                self.change_pessimism_coefficient()
            elif choice == "3" and self.analyzer.combination_rule == Config.COMBINATION_RULE_ADAPTIVE:
                self.configure_adaptive_rule()
            elif choice == str(max_choice):
                break
            else:
                print("❌ Неверный выбор!")

    def change_combination_rule(self):
        """Изменение правила комбинирования"""
        print("\n--- Правило комбинирования свидетельств ---")

        print(f"\n1. {Config.COMBINATION_RULE_NAMES[Config.COMBINATION_RULE_DEMPSTER]}")
        print(f"   {Config.COMBINATION_RULE_DESCRIPTIONS[Config.COMBINATION_RULE_DEMPSTER]}")

        print(f"\n2. {Config.COMBINATION_RULE_NAMES[Config.COMBINATION_RULE_YAGER]}")
        print(f"   {Config.COMBINATION_RULE_DESCRIPTIONS[Config.COMBINATION_RULE_YAGER]}")

        print(f"\n3. {Config.COMBINATION_RULE_NAMES[Config.COMBINATION_RULE_ADAPTIVE]}")
        print(f"   {Config.COMBINATION_RULE_DESCRIPTIONS[Config.COMBINATION_RULE_ADAPTIVE]}")

        choice = input("\nВыберите правило (1-3): ").strip()

        if choice == "1":
            self.analyzer.set_combination_rule(Config.COMBINATION_RULE_DEMPSTER)
        elif choice == "2":
            self.analyzer.set_combination_rule(Config.COMBINATION_RULE_YAGER)
        elif choice == "3":
            self.analyzer.set_combination_rule(Config.COMBINATION_RULE_ADAPTIVE)
            self.configure_adaptive_rule()
        else:
            print("❌ Неверный выбор!")

    def change_pessimism_coefficient(self):
        """Изменение коэффициента пессимизма"""
        print("\n--- Коэффициент пессимизма ---")
        print(f"Текущее значение: {self.analyzer.pessimism_coefficient}")
        print(f"Диапазон: {Config.MIN_PESSIMISM_COEFFICIENT} - {Config.MAX_PESSIMISM_COEFFICIENT}")
        print("\nγ = 1: полный пессимизм (учитываем только нижнюю границу)")
        print("γ = 0: полный оптимизм (учитываем только верхнюю границу)")
        print("γ = 0.5: нейтральный подход (по умолчанию)")

        while True:
            try:
                new_coef = float(input(f"\nВведите новый коэффициент пессимизма: "))

                if self.analyzer.set_pessimism_coefficient(new_coef):
                    break
                else:
                    print(f"❌ Коэффициент должен быть в диапазоне "
                          f"[{Config.MIN_PESSIMISM_COEFFICIENT}, {Config.MAX_PESSIMISM_COEFFICIENT}]!")

            except ValueError:
                print("❌ Введите числовое значение!")

            retry = input("Попробовать снова? (y/n): ").lower()
            if retry not in ['y', 'yes', 'д', 'да']:
                break

    def configure_adaptive_rule(self):
        """Настройка адаптивного правила"""
        if self.analyzer.combination_rule != Config.COMBINATION_RULE_ADAPTIVE:
            return

        print("\n--- Настройка адаптивного правила ---")
        print(f"Текущий порог: X = {self.analyzer.conflict_threshold or Config.DEFAULT_CONFLICT_THRESHOLD}")
        print(f"Диапазон: {Config.MIN_CONFLICT_THRESHOLD} - {Config.MAX_CONFLICT_THRESHOLD}")
        print("\nПринцип работы:")
        print("  • Если конфликт K < X → используется правило Демпстера")
        print("  • Если конфликт K >= X → используется правило Ягера")
        print(f"\nРекомендации:")
        print("  • X = 0.1-0.3: чувствительное правило (чаще Ягер)")
        print("  • X = 0.4-0.6: умеренное правило (по умолчанию 0.4)")
        print("  • X = 0.7-0.9: консервативное правило (чаще Демпстер)")

        change = input("\nИзменить порог X? (y/n): ").strip().lower()

        if change in ['y', 'yes', 'д', 'да']:
            while True:
                try:
                    new_threshold = float(input(f"\nВведите новый порог X: "))

                    if self.analyzer.set_conflict_threshold(new_threshold):
                        break
                    else:
                        print(f"❌ Порог должен быть в диапазоне "
                              f"[{Config.MIN_CONFLICT_THRESHOLD}, {Config.MAX_CONFLICT_THRESHOLD}]!")

                except ValueError:
                    print("❌ Введите числовое значение!")

                retry = input("Попробовать снова? (y/n): ").lower()
                if retry not in ['y', 'yes', 'д', 'да']:
                    break

    def run_analysis(self):
        """Запуск анализа"""
        if not self.analyzer:
            print("❌ Сначала загрузите данные!")
            return

        print("\n" + "=" * 50)
        print("ЗАПУСК АНАЛИЗА DS/AHP-GDM")
        print("=" * 50)

        print(f"\n📋 Параметры анализа:")
        print(f"  • Правило комбинирования: {Config.COMBINATION_RULE_NAMES[self.analyzer.combination_rule]}")
        print(f"  • Коэффициент пессимизма: {self.analyzer.pessimism_coefficient}")

        # Спросить о скорректированных BOE
        use_adjusted = input("\nИспользовать скорректированные BOE (учет важности экспертов)? (y/n): ").strip().lower()
        use_adjusted_boe = use_adjusted in ['y', 'yes', 'д', 'да']

        print(f"\n🚀 Запуск анализа...")

        # Запускаем анализ
        optimal = self.analyzer.run_analysis(use_adjusted_boe=use_adjusted_boe)

        if optimal:
            print(f"\n✅ Анализ завершен!")
            print(f"🏆 Оптимальная альтернатива: {optimal}")

        else:
            print("\n❌ Анализ завершился с ошибкой")

    def generate_custom_data(self, generator: XMLDataGenerator):
        """Ручная настройка параметров генерации"""
        print("\n" + "=" * 70)
        print("НАСТРОЙКА ПАРАМЕТРОВ ГЕНЕРАЦИИ")
        print("=" * 70)

        try:
            # Количество альтернатив
            while True:
                try:
                    n_alts = int(input("\nКоличество альтернатив (1-100): ").strip())
                    if 1 <= n_alts <= 100:
                        break
                    else:
                        print("❌ Введите число от 1 до 100")
                except ValueError:
                    print("❌ Введите целое число")

            # Количество критериев
            while True:
                try:
                    n_criteria = int(input("Количество критериев (1-10): ").strip())
                    if 1 <= n_criteria <= 10:
                        break
                    else:
                        print("❌ Введите число от 1 до 10")
                except ValueError:
                    print("❌ Введите целое число")

            # Количество экспертов
            while True:
                try:
                    n_experts = int(input("Количество экспертов (1-10): ").strip())
                    if 1 <= n_experts <= 10:
                        break
                    else:
                        print("❌ Введите число от 1 до 10")
                except ValueError:
                    print("❌ Введите целое число")

            # Распределение весов
            print("\n📊 Распределение весов экспертов:")
            print("  1. Равномерное (все веса = 1.0)")
            print("  2. Убывающее (от 1.0 до 0.2)")
            print("  3. Случайное (0.3 - 1.0)")

            weight_choice = input("Выберите распределение (1-3): ").strip()

            if weight_choice == "1":
                weight_dist = "equal"
            elif weight_choice == "2":
                weight_dist = "decreasing"
            else:
                weight_dist = "uniform"

            # Директория для сохранения
            output_dir = input(f"\nДиректория для сохранения (по умолчанию: generated_xml): ").strip()
            if not output_dir:
                output_dir = "generated_xml"

            # Генерация
            print(f"\n🚀 Запуск генерации с параметрами:")
            print(f"  • Альтернатив: {n_alts}")
            print(f"  • Критериев: {n_criteria}")
            print(f"  • Экспертов: {n_experts}")
            print(f"  • Распределение весов: {weight_dist}")

            dataset, xml_file = generator.generate_dataset(
                n_alternatives=n_alts,
                m_criteria=n_criteria,
                k_experts=n_experts,
                weight_distribution=weight_dist,
                output_dir=output_dir
            )

            # Предлагаем загрузить
            load = input(f"\n📥 Загрузить сгенерированный файл? (y/n): ").strip().lower()

            if load in ['y', 'yes', 'д', 'да']:
                self.analyzer = GDMAnalyzer()
                if self.analyzer.load_data_from_xml(xml_file):
                    self.current_file = xml_file
                    print(f"✅ Файл успешно загружен")
                else:
                    print("❌ Не удалось загрузить файл")

        except Exception as e:
            print(f"❌ Ошибка: {e}")
