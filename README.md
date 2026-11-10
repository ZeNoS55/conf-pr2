# Инструмент визуализации графа зависимостей .NET (NuGet)

Практическая работа № 2 по дисциплине "Конфигурационное управление".  
Вариант № 26.

## 1. Общее описание

Данный инструмент предназначен для визуализации графа зависимостей пакетов
платформы .NET (NuGet), включая транзитивные зависимости, выявление циклов,
фильтрацию и расчет порядка загрузки зависимостей.

В соответствии с требованиями задания:
- Пакетный менеджер: **.NET (NuGet)**.
- Источник параметров: **Опции командной строки (CLI)**.
- Получение зависимостей реализовано напрямую по протоколу NuGet v3 API
  (а также из локальных файлов `.nuspec` / файлов описания графов) без
  использования сторонних библиотек и пакетных менеджеров.
- Построение графа зависимостей реализовано на основе **нерекурсивного
  алгоритма поиска в ширину (BFS)**.
- Поддерживается ограничение максимальной глубины анализа.
- Поддерживается фильтрация пакетов по заданной подстроке.
- Реализована корректная обработка циклических зависимостей.
- Поддерживается тестовый режим работы с графами, где имена пакетов задаются
  заглавными латинскими буквами.
- Реализован расчет порядка загрузки пакетов (bottom-up / prerequisites first).
- Формируется графическое представление графа на языке PlantUML с выводом
  изображения на экран.

---

## 2. Описание всех функций и настроек

### 2.1. Настройки (параметры командной строки)

| Опция | Короткая | Тип | Описание |
|---|---|---|---|
| `--package` | `-p` | string | Имя анализируемого пакета (обязательный). |
| `--repo` | `-r` | string | URL NuGet API или путь к файлу тестового графа. |
| `--test-mode` | `-t` | flag | Включение режима работы с тестовым графом. |
| `--max-depth` | `-d` | int | Максимальная глубина анализа (>= 0). |
| `--filter` | `-f` | string | Подстрока для исключения пакетов из анализа. |
| `--stage` | `-s` | int | Номер этапа для демонстрации (1-5). |
| `--no-gui` | - | flag | Отключение авто-открытия окна изображения. |

### 2.2. Архитектура и функции модулей

1. **Модуль конфигурации (`src/config.py`)**:
   - `Config`: класс хранения параметров приложения.
   - `validate_package_name`: проверка непустого имени пакета и формата
     заглавных латинских букв в тестовом режиме.
   - `validate_repo`: валидация URL-схемы (http/https) или существования
     файла в тестовом режиме.
   - `validate_max_depth`: проверка неотрицательности глубины (>= 0).
   - `validate_config`: общая валидация конфигурации.
   - `format_config_kv`: форматирование параметров в формате "ключ-значение".

2. **Модуль CLI (`src/cli.py`)**:
   - `add_core_arguments`: регистрация базовых аргументов.
   - `add_optional_arguments`: регистрация параметров фильтрации и глубины.
   - `create_parser`: сборка парсера аргументов `argparse`.
   - `parse_arguments`: разбор аргументов командной строки и валидация.

3. **Модуль сбора данных (`src/collector.py`)**:
   - `fetch_json`: HTTP-запрос к REST API без внешних зависимостей.
   - `extract_deps_from_groups`: извлечение уникальных идентификаторов
     зависимостей из групп фреймворков NuGet.
   - `fetch_nuget_dependencies`: получение прямых зависимостей через NuGet v3
     Registration API (`/registration5-semver1/{package}/index.json`).
   - `parse_nuspec_content`: парсинг XML-манифестов `.nuspec`.
   - `parse_test_repo_json` / `parse_test_repo_text`: загрузка тестовых графов
     в форматах JSON и списков смежности.
   - `get_direct_dependencies`: единая точка доступа для извлечения прямых
     зависимостей пакета.

4. **Модуль графа (`src/graph.py`)**:
   - `GraphResult`: структура данных графа (список смежности, циклы, уровни).
   - `is_filtered_out`: проверка подстроки фильтрации.
   - `enqueue_child`: валидация потомка, детекция циклов и формирование шага.
   - `build_dependency_graph`: нерекурсивный BFS на очереди `deque` с учетом
     максимальной глубины, фильтрации и детектированием циклов.

5. **Модуль порядка загрузки (`src/order.py`)**:
   - `collect_graph_nodes`: сбор всех уникальных узлов графа.
   - `build_dependency_maps`: построение прямых и обратных связей узлов.
   - `compute_load_order`: вычисление порядка загрузки зависимостей
     (снизу вверх, от листьев к корневому пакету).
   - `format_load_order`: вывод порядка загрузки с диагностикой циклов.

6. **Модуль визуализации (`src/visualizer.py`)**:
   - `generate_plantuml_text`: трансляция графа в код диаграммы PlantUML.
   - `encode_plantuml`: сжатие zlib/deflate и кодирование в 64-символьный
     алфавит PlantUML URL.
   - `render_plantuml_to_png`: получение готового PNG через сервер рендеринга.
   - `display_image_on_screen`: открытие изображения в стандартном просмотрщике
     ОС (`os.startfile` на Windows / `open` / `xdg-open`).

7. **Главный модуль (`src/main.py`)**:
   - `run_stage1` ... `run_stage5`: пошаговые сценарии работы программы.
   - `main`: точка входа CLI.

---

## 3. Сборка проекта и запуск тестов

Проект реализован на языке Python 3 (рекомендуется Python 3.10+) и
использует только стандартную библиотеку. Дополнительная установка
сторонних пакетов не требуется.

### 3.1. Запуск через скрипты

- **Windows**:
  ```cmd
  run.bat --package Moq --max-depth 2
  ```

- **Linux / macOS**:
  ```bash
  chmod +x run.sh
  ./run.sh --package Moq --max-depth 2
  ```

### 3.2. Запуск тестов

Запуск всех модульных и интеграционных тестов:
```cmd
python -m unittest discover tests
```
или с подробным выводом:
```cmd
python -m unittest discover tests -v
```

---

## 4. Примеры использования

### 4.1. Демонстрация этапов на тестовых репозиториях

1. **Этап 1: Вывод настроек ключ-значение**:
   ```cmd
   python -m src.main -p A -r test_repos/diamond.json -t -s 1
   ```
   Вывод:
   ```text
   === Stage 1: Configuration ===
   package_name: A
   repo: test_repos/diamond.json
   test_mode: True
   max_depth: 5
   filter_substring: 
   ```

2. **Этап 2: Вывод прямых зависимостей пакета**:
   ```cmd
   python -m src.main -p A -r test_repos/diamond.json -t -s 2
   ```
   Вывод:
   ```text
   === Stage 2: Direct Dependencies for A ===
   - B
   - C
   ```

3. **Этап 3: Построение графа с помощью нерекурсивного BFS**:
   - Ромбовидный граф:
     ```cmd
     python -m src.main -p A -r test_repos/diamond.json -t -s 3
     ```
     Вывод:
     ```text
     === Stage 3: BFS Graph (Root: A) ===
     A -> ['B', 'C']
     B -> ['D']
     C -> ['D']
     D -> []
     ```
   - Циклический граф (`test_repos/cycle.json`):
     ```cmd
     python -m src.main -p A -r test_repos/cycle.json -t -s 3
     ```
     Вывод:
     ```text
     === Stage 3: BFS Graph (Root: A) ===
     A -> ['B']
     B -> ['C']
     C -> ['A']
     Detected cycles: [('C', 'A')]
     ```
   - Фильтрация пакетов (`test_repos/filtered.json` с фильтром `TEST`):
     ```cmd
     python -m src.main -p A -r test_repos/filtered.json -t -f TEST -s 3
     ```

4. **Этап 4: Порядок загрузки зависимостей**:
   ```cmd
   python -m src.main -p A -r test_repos/diamond.json -t -s 4
   ```
   Вывод:
   ```text
   === Stage 4: Package Load Order ===
   Package load order (bottom-up / prerequisites first):
   1. D
   2. B
   3. C
   4. A
   ```

5. **Этап 5: Визуализация в PlantUML**:
   ```cmd
   python -m src.main -p A -r test_repos/diamond.json -t -s 5 --no-gui
   ```

---

### 4.2. Демонстрация на реальных пакетах NuGet

Инструмент протестирован на 3 пакетах экосистемы .NET:

1. **Пакет 1: `Moq`**
   - Команда:
     ```cmd
     python -m src.main -p Moq -d 2 -s 5 --no-gui
     ```
   - Зависимости: `Castle.Core`, `System.Threading.Tasks.Extensions`.
   - Порядок загрузки:
     1. `System.Diagnostics.EventLog`
     2. `System.Reflection.Emit`
     3. `System.Runtime.CompilerServices.Unsafe`
     4. `Castle.Core`
     5. `System.Threading.Tasks.Extensions`
     6. `Moq`

2. **Пакет 2: `Microsoft.Extensions.Logging`**
   - Команда:
     ```cmd
     python -m src.main -p Microsoft.Extensions.Logging -d 1 -s 5 --no-gui
     ```
   - Прямые зависимости:
     - `Microsoft.Bcl.AsyncInterfaces`
     - `Microsoft.Extensions.DependencyInjection`
     - `Microsoft.Extensions.Logging.Abstractions`
     - `Microsoft.Extensions.Options`
     - `System.Diagnostics.DiagnosticSource`
     - `System.ValueTuple`

3. **Пакет 3: `Serilog.AspNetCore`**
   - Команда:
     ```cmd
     python -m src.main -p Serilog.AspNetCore -d 1 -s 5 --no-gui
     ```
   - Прямые зависимости:
     - `Serilog`
     - `Serilog.Extensions.Hosting`
     - `Serilog.Formatting.Compact`
     - `Serilog.Settings.Configuration`
     - `Serilog.Sinks.Console`
     - `Serilog.Sinks.Debug`
     - `Serilog.Sinks.File`

---

## 5. Сравнение с реальным менеджером пакетов и штатными средствами

### 5.1. Сравнение порядка загрузки зависимостей (Этап 4)

- **В разработанном инструменте**:
  Реализован строгий восходящий топологический порядок (bottom-up /
  post-order). Пакеты, не имеющие зависимостей (листья графа), загружаются
  первыми; по мере удовлетворения всех предварительных условий в очередь
  добавляются зависящие от них пакеты. При обнаружении циклов инструмент
  диагностирует обратные дуги и выводит предупреждение.
- **В пакетном менеджере NuGet (.NET)**:
  В .NET CLR сборки (`.dll`) загружаются в память виртуальной машины
  асинхронно/лениво через `AssemblyLoadContext` в момент первого обращения к
  типу из соответствующей сборки (JIT-компиляция метода).
  При сборке (`dotnet build`) компилятор Roslyn требует, чтобы все
  транзитивные ссылки были разрешены заранее на этапе `dotnet restore`.
  При конфликтах версий в ромбовидных зависимостях NuGet применяет правило
  **Nearest Wins** (побеждает версия на наименьшей глубине дерева).

### 5.2. Сравнение визуализации со штатными инструментами (Этап 5)

- **Штатные средства .NET**:
  - `dotnet list package --include-transitive` выводит текстовый список всех
    прямых и транзитивных зависимостей в терминал, но не строит графическую
    диаграмму связей.
  - Утилита `dotnet-depends` или плагины к Visual Studio (DGML Architecture
    Dependency Graph) строят плоские графы с большим количеством служебных
    системных узлов фреймворка.
- **Преимущества нашего решения**:
  - Наглядное представление структуры в виде PlantUML диаграммы.
  - Поддержка интерактивной фильтрации по подстроке (`--filter`) для
    отсечения служебных библиотек (например, `System.*`).
  - Четкое ограничение глубины анализа (`--max-depth`), позволяющее
    избежать перегрузки диаграммы.
  - Автоматическая визуализация циклических зависимостей пунктирными дугами.
