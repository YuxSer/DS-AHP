import sys
import os
from config import Config

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Главная функция программы"""

    # Проверяем зависимости
    if not check_dependencies():
        print("❌ Необходимые библиотеки не установлены")
        print("   Установите зависимости: pip install numpy pandas lxml")
        return

    print("\n" + "=" * 70)
    print("             СИСТЕМА ГРУППОВОГО ПРИНЯТИЯ РЕШЕНИЙ")
    print("                    DS/AHP-GDM v1.0")
    print("=" * 70)

    print("\n О СИСТЕМЕ:")
    print("  • Групповое принятие решений с несколькими экспертами")
    print("  • Объединение метода анализа иерархий и теории Демпстера-Шафера")
    print("  • Три правила комбинирования: Демпстера, Ягера и Адаптивное")
    print("  • Адаптивный выбор правил на основе уровня конфликта")

    # Создаем папку для результатов если нужно
    if not os.path.exists(Config.EXPORT_DIR):
        os.makedirs(Config.EXPORT_DIR)
        print(f" Создана папка для результатов: {Config.EXPORT_DIR}")

    # Запускаем меню
    try:
        from menu import Menu
        menu = Menu()
        menu.show_main_menu()

    except ImportError as e:
        print(f"❌ Ошибка импорта модулей: {e}")
        print("   Убедитесь, что все файлы находятся в одной директории")

    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()

def check_dependencies() -> bool:
    """Проверка необходимых зависимостей"""
    required = ['numpy', 'pandas', 'lxml']

    print("🔍 Проверка зависимостей...")

    missing = []
    for lib in required:
        try:
            __import__(lib)
            print(f"  ✅ {lib}")
        except ImportError:
            print(f"  ❌ {lib}")
            missing.append(lib)

    if missing:
        print(f"\n⚠️  Отсутствуют: {', '.join(missing)}")
        print("   Установите: pip install " + " ".join(missing))
        return False

    return True

if __name__ == "__main__":
    main()