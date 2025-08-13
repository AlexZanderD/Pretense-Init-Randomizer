🇷🇺
# 📝 Руководство пользователя: Zone Randomizer

## Введение

Zone Randomizer — это удобный инструмент для DCS-миссий, который автоматически изменяет оборонительные системы в зонах. С помощью этого скрипта вы можете добавить реиграбельности вашим миссиям, меняя состав противовоздушной обороны (ПВО), пехоты и других статических объектов без ручного редактирования каждого файла.

---

## Как это работает?

Программа анализирует файл `init.lua` вашей миссии, ищет в нём блоки описания зон, а затем производит следующие действия:

1.  **Определение режима миссии**: Скрипт проверяет, является ли миссия **"Cold War"** (`Config.isColdWar = true`) или **"Modern"** (`Config.isColdWar = false`). От этого зависит, какие именно юниты будут использоваться для рандомизации.
2.  **Анализ зон**: Программа просматривает каждую зону, определённую в `init.lua`, и считывает её имя.
3.  **Определение класса юнита**: На основе имени зоны (например, `palmyra-sam-red`) скрипт определяет класс юнита (**`sam`**). Это правило имеет **наивысший приоритет**. Если в имени зоны нет явной метки класса, скрипт использует информацию о классе из внутреннего конфига.
4.  **Рандомизация**: Программа выбирает случайный юнит из заранее определённого пула, который соответствует классу (**`sam`**), стороне (**`red`**) и режиму миссии.
5.  **Замена**: Исходный юнит заменяется на выбранный случайным образом.
6.  **Настройка Offmap Supply**: В конце работы скрипт также рандомизирует номера для `offmap-supply` для обеих сторон, придерживаясь определённого алгоритма для обеспечения баланса.

---

## Как пользоваться программой

1.  **Подготовьте файл**: Убедитесь, что ваш файл `init.lua` находится в папке миссии.
2.  **Запустите скрипт**: Запустите файл `randomizer.py` (или скомпилированный исполняемый файл).
3.  **Выберите файл**: В появившемся окне выберите файл `init.lua` вашей миссии.
4.  **Ожидайте**: Программа автоматически обработает файл и перезапишет его.
5.  **Готово!**: Появится сообщение, подтверждающее успешное завершение работы.

---

## Важные правила именования

Чтобы скрипт работал правильно, критически важно использовать унифицированный формат именования зон в вашем файле `init.lua`.

**Формат именования**: `[ИмяЗоны]-[КлассЮнита]-[Сторона]`

* `[ИмяЗоны]` – любое уникальное имя, например, `airfield`, `city`, `palmyra`.
* `[КлассЮнита]` – метка, по которой скрипт определяет класс юнита. Используйте одну из следующих:
    * `sam` (зенитно-ракетные комплексы, например SA-2, SA-10, Patriot)
    * `airdef` (системы ПВО малой и средней дальности, например SA-6, SA-9, Roland)
    * `shorad` (комплексы ближнего действия)
    * `aaa` (зенитная артиллерия)
    * `infantry` или `garrison` (пехота)
    * `ewr` (радиолокационная станция раннего предупреждения)
* `[Сторона]` – `red` или `blue`.

**Примеры корректного именования**:

* `presets.defenses.blue.patriot:extend({ name = 'palmyra-airdef-blue' }),` (Скрипт увидит `-airdef-` и заменит `patriot` на `roland` или `rapier`).
* `presets.defenses.red.sa10:extend({ name = 'airfield-airdef-red' }),` (Скрипт увидит `-airdef-` и заменит `sa10` на `sa6`, `sa9` или другую доступную систему).
* `presets.defenses.blue.hawk:extend({ name = 'coast-sam-blue' }),` (Скрипт увидит `-sam-` и заменит `hawk` на другой доступный SAM-комплекс).

---

## Дополнительные возможности и настройки

Программа имеет встроенный словарь `DEFAULT_CONFIG`, в котором определены классы, стороны и режимы Cold War для каждого юнита. Если вы хотите добавить новый юнит или изменить его классификацию, вам нужно отредактировать этот словарь.

**Пример добавления нового юнита**:
Если вы хотите добавить новый зенитный комплекс, найдите соответствующий класс в `DEFAULT_CONFIG` и добавьте его в список `variants`:

```json
{ 
    "prefix": "sa", 
    "side": "red", 
    "class": "sam", 
    "coldwar": "both", 
    "variants": {
        "red": [
            {"id": "sa2",  "coldwar": "true"},
            {"id": "sa3",  "coldwar": "true"},
            // ...
            {"id": "new_sa", "coldwar": "false"} // <-- Добавлен новый юнит
        ]
    }
}
```

🇺🇸
# 📝 Zone Randomizer User Guide

## Introduction

Zone Randomizer is a convenient tool for DCS missions that automatically changes defensive systems within mission zones. This script adds replayability to your missions by randomizing the composition of air defenses (SAM, AAA), infantry, and other static objects without the need for manual file editing.

---

## How It Works

The program analyzes your mission's `init.lua` file, searches for zone definition blocks, and then performs the following steps:

1.  **Mission Mode Detection**: The script checks if the mission is in **"Cold War"** mode (`Config.isColdWar = true`) or **"Modern"** mode (`Config.isColdWar = false`). This setting determines which specific units will be used for randomization.
2.  **Zone Analysis**: The program scans each zone defined in `init.lua` and reads its name.
3.  **Unit Class Determination**: Based on the zone's name (e.g., `palmyra-sam-red`), the script determines the unit's class (**`sam`**). This rule has the **highest priority**. If the zone name does not have a class tag, the script uses the class information from its internal configuration.
4.  **Randomization**: The program selects a random unit from a pre-defined pool that matches the correct class (**`sam`**), side (**`red`**), and mission mode.
5.  **Replacement**: The original unit is replaced with the randomly selected one.
6.  **Offmap Supply Configuration**: The script also randomizes the `offmap-supply` numbers for both sides, following a specific algorithm to maintain balance.

---

## How to Use the Program

1.  **Prepare Your File**: Make sure your `init.lua` file is located in the mission folder.
2.  **Run the Script**: Launch the `randomizer.py` file (or the compiled executable).
3.  **Select Your File**: In the window that appears, select the `init.lua` file for your mission.
4.  **Wait**: The program will automatically process and overwrite the file.
5.  **Done!**: A message will pop up confirming successful completion.

---

## Critical Naming Conventions

For the script to work correctly, it is crucial to use a consistent naming format for zones in your `init.lua` file.

**Naming Format**: `[ZoneName]-[UnitClass]-[Side]`

* `[ZoneName]` – Any unique name, for example, `airfield`, `city`, `palmyra`.
* `[UnitClass]` – The tag that the script uses to determine the unit's class. Use one of the following:
    * `sam` (Surface-to-air missile systems, e.g., SA-2, SA-10, Patriot)
    * `airdef` (Short- and medium-range air defense systems, e.g., SA-6, SA-9, Roland)
    * `shorad` (Short-range air defense)
    * `aaa` (Anti-aircraft artillery)
    * `infantry` or `garrison` (Infantry)
    * `ewr` (Early warning radar)
* `[Side]` – `red` or `blue`.

**Correct Naming Examples**:

* `presets.defenses.blue.patriot:extend({ name = 'palmyra-airdef-blue' }),` (The script will see `-airdef-` and replace `patriot` with `roland` or `rapier`).
* `presets.defenses.red.sa10:extend({ name = 'airfield-airdef-red' }),` (The script will see `-airdef-` and replace `sa10` with `sa6`, `sa9`, or another available system).
* `presets.defenses.blue.hawk:extend({ name = 'coast-sam-blue' }),` (The script will see `-sam-` and replace `hawk` with another available SAM system).

---

## Advanced Customization and Configuration

The program has an internal `DEFAULT_CONFIG` dictionary that defines the classes, sides, and Cold War compatibility for each unit. If you want to add a new unit or change its classification, you will need to edit this dictionary.

**Example of adding a new unit**:
If you want to add a new SAM system, find the corresponding class in `DEFAULT_CONFIG` and add it to the `variants` list:

```json
{ 
    "prefix": "sa", 
    "side": "red", 
    "class": "sam", 
    "coldwar": "both", 
    "variants": {
        "red": [
            {"id": "sa2",  "coldwar": "true"},
            {"id": "sa3",  "coldwar": "true"},
            // ...
            {"id": "new_sa", "coldwar": "false"} // <-- New unit added
        ]
    }
}
```
