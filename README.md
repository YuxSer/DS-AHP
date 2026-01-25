# DS/AHP-GDM: Adaptive Group Decision Making Framework

[![Версия Python](https://img.shields.io/badge/python-3.8+-blue.svg)]()
[![Лицензия](https://img.shields.io/badge/license-MIT-blue.svg)]()

DS/AHP-GDM — это гибридная система для многокритериального группового принятия решений, объединяющая метод анализа иерархий (AHP) и теорию Демпстера-Шафера с адаптивным механизмом комбинирования свидетельств.

## Ключевые особенности
- Адаптивное переключение между правилами комбинирования (Демпстер/Ягер) на основе уровня конфликта
- Учет различной важности экспертов через механизм дисконтирования Бейнона
- Поддержка группового анализа с несколькими экспертами, критериями и альтернативами
- Генерация реалистичных тестовых данных для экспериментов
- Интервальная оценка альтернатив через функции доверия и правдоподобия


## Установка и запуск
```bash
# Клонирование репозитория
git clone https://github.com/YuxSer/DS-AHP.git
cd DS-AHP

# Установка зависимостей
pip install -r requirements.txt

# Запуск системы
python main.py
```



## Структура проекта
```text
DS-AHP-GDM/
│
├── main.py                 # Точка входа в программу
├── config.py               # Конфигурационные параметры системы
├── menu.py                 # Текстовый пользовательский интерфейс
│
├── gdm_analyzer.py         # Главный анализатор GDM (координация работы)
├── expert_manager.py       # Управление экспертами и BOE вычисления
├── combination_rules.py    # Реализация правил комбинирования
├── belief_plausibility.py  # Расчет Belief и Plausibility функций
│
├── xml_data_generator.py   # Генератор XML тестовых данных
├── gdm_xml_parser.py       # Парсер XML файлов формата GDM
├── export_formats.py       # Экспорт результатов в различные форматы
├── utils.py                # Вспомогательные функции и утилиты
│
├── requirements.txt        # Список зависимостей Python
├── input_data/             # Директория с входными данными для экспериментов
├── results/                # Директория с результатми экспериментов
└── README.md               # Документация проекта
```
## Результаты экспериментов

Для проведения экспериментов был разработан генератор входных данных в формате XML, который позволяет создавать тестовые наборы данных с заданным количеством альтернатив, критериев и экспертов. Генератор позволяет задавать различные распределения весов экспертов (равномерное, убывающее, случайное) и создаёт реалистичные парные сравнения альтернатив по каждому критерию для каждого эксперта. Это позволяет моделировать различные сценарии группового принятия решений с различным уровнем согласованности мнений экспертов.

Для валидации предложенного адаптивного подхода было проведено 11 экспериментов с различными конфигурациями. Каждый эксперимент повторялся 10 раз для статистической значимости. Результаты повторных экспериментов оказались абсолютно идентичными. Результаты сравнивались по трём правилам комбинирования.

Входные данные находятся в директории input_data. В названии xml файлов указано количество, альтернатив, экспертов и критериев. Все результаты эксперимнтов находятся в директории results.

Проведённые эксперименты показали, что правило Демпстера даёт наиболее «уверенные» результаты с наибольшими оценками, но может быть чувствительно к конфликтам между экспертами. Правило Ягера более консервативно, перераспределяя конфликт в неопределённость, что приводит к снижению оценок альтернатив. Адаптивное правило, по сравнению с использованием только метода Ягера, обладает большей разрешающей способностью при низком уровне конфликта (не будучи излишне консервативным), а по сравнению с использованием только метода Демпстера — правило более устойчиво к конфликтам и менее склонно к выдаче экстремальных результатов.

## Технологии

- Python 3.8+ — основной язык реализации

- NumPy — математические вычисления и работа с матрицами

- Pandas — обработка структурированных данных

- lxml — парсинг и генерация XML файлов

## Участники

- Основными разработчиками являются С.Е.Юшков и Ц.Цай, студенты ИКНК СПбПУ.
- Руководитель и соавтор проекта - В.А.Пархоменко, старший преподаватель ИКНК СПбПУ.

## Гарантии

Разработчики не дают никаких гарантий по поводу использования данного программного обеспечения.

## Лицензия

Это программа открыта для использования и распростаняется под лицензией MIT.

# DS/AHP-GDM: Adaptive Group Decision Making Framework

[![Версия Python](https://img.shields.io/badge/python-3.8+-blue.svg)]()
[![Лицензия](https://img.shields.io/badge/license-MIT-blue.svg)]()

DS/AHP-GDM is a hybrid system for multi-criteria group decision making that combines the Analytic Hierarchy Process (AHP) and Dempster-Shafer theory with an adaptive evidence combination mechanism.

## Key Features

- Adaptive switching between combination rules (Dempster/Yager) based on conflict level
- Accounting for varying expert importance through Beynon's discounting mechanism
- Support for group analysis with multiple experts, criteria, and alternatives
- Generation of realistic test data for experiments
- Interval evaluation of alternatives through belief and plausibility functions

## Installation and Launch
```bash
# Clone repository
git clone https://github.com/YuxSer/DS-AHP.git
cd DS-AHP

# Install dependencies
pip install -r requirements.txt

# Launch system
python main.py
```

## Project Structure
```text
DS-AHP-GDM/
│
├── main.py                 # Program entry point
├── config.py               # System configuration parameters
├── menu.py                 # Text-based user interface
│
├── gdm_analyzer.py         # Main GDM analyzer (work coordination)
├── expert_manager.py       # Expert management and BPA calculations
├── combination_rules.py    # Implementation of combination rules
├── belief_plausibility.py  # Calculation of Belief and Plausibility functions
│
├── xml_data_generator.py   # XML test data generator
├── gdm_xml_parser.py       # GDM format XML file parser
├── export_formats.py       # Export results to various formats
├── utils.py                # Utility functions
│
├── requirements.txt        # Python dependencies list
├── input_data/             # Directory with input data for experiments
├── results/                # Directory with experiment results
└── README.md               # Project documentation
```

## Experiment Results

For conducting experiments, an XML input data generator was developed that allows creating test datasets with specified numbers of alternatives, criteria, and experts. The generator allows setting various expert weight distributions (uniform, decreasing, random) and creates realistic pairwise comparisons of alternatives for each criterion for each expert. This enables modeling various group decision-making scenarios with different levels of expert opinion consistency.

To validate the proposed adaptive approach, 11 experiments with different configurations were conducted. Each experiment was repeated 10 times for statistical significance. The results of repeated experiments were absolutely identical. Results were compared across three combination rules.

Input data is located in the input_data directory. The XML file names indicate the number of alternatives, experts, and criteria. All experiment results are located in the results directory.

The conducted experiments showed that Dempster's rule gives the most "confident" results with the highest scores but can be sensitive to conflicts between experts. Yager's rule is more conservative, redistributing conflict into uncertainty, which leads to lower alternative scores. Compared to using only Yager's method, the adaptive rule has greater resolving power at low conflict levels (without being overly conservative), and compared to using only Dempster's method, the rule is more robust to conflicts and less prone to producing extreme results.

## Technologies

- Python 3.8+ — main implementation language

- NumPy — mathematical computations and matrix operations

- Pandas — structured data processing

- lxml — XML file parsing and generation

## Contributors

- The main developers are S.E. Iushkov and C. Cai, students of SPbPU ICSC.
- Project supervisor and co-author - V.A. Parkhomenko, senior lecturer at SPbPU ICSC.

## Warranty

The developers provide no warranty regarding the use of this software.

## License

This program is open for use and distributed under the MIT license.
