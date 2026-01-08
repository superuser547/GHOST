# REQUIREMENTS

## 0. Document Purpose and Scope

This document consolidates **all functional requirements (ФТ)** and the **technical specification (ТЗ)** for the open-source project: a local web application for constructing and generating academic reports according to ГОСТ and НИТУ МИСИС formatting guidelines.

The document is intended to be stored as `REQUIREMENTS.md` in the root of the GitHub repository and used as the single source of truth for:

- Planning and implementation (by the developer and/or Codex/agents).
- Validation of behavior and UI.
- Future evolution (new presets, new features).

The project is designed as:

- **Open source** (no commercial libraries).
- **Fully offline** (no network/API calls at runtime).
- **Cross-platform** (Windows, macOS, Linux; or via Docker).


---

## 1. Functional Requirements (ФТ)

### 1.1. System Purpose

The system is a local (or Dockerized) web application that allows a user to:

- **Interactively assemble the structure of a report** according to ГОСТ/МИСИС using a set of predefined blocks in a visual UI.
- **Configure formatting parameters** (with a NITU MISIS preset as the default).
- **Generate final reports** in `.docx` (and `.pdf`) formats that strictly follow the selected formatting rules.
- **Automatically check and highlight structure/format violations** with errors and warnings, helping the user conform to ГОСТ/МИСИС rules.

The system operates **fully offline** and does **not** use any external network services (no LLMs, no HTTP APIs).


### 1.2. User Roles and Target Object

#### 1.2.1. Roles

For the initial version there is a single role:

- **User** – student, teacher, or report author, who:
  - Builds the report structure via the web UI.
  - Enters the content of blocks.
  - Adjusts report parameters (type of work, topic, personal data, etc.).
  - Launches export to DOCX/PDF.

No separate “admin” role or multi-user management is considered in this version.

#### 1.2.2. Target Object

The system’s output object is an **academic report**, including but not limited to:

- Practical work reports
- Laboratory work reports
- Essays (рефераты)
- Course work (курсовые работы)
- Other similar academic deliverables

The report must adhere to ГОСТ and internal NITU MISIS formatting rules (hereinafter: **Мисис-пресет**).


### 1.3. Primary Usage Scenarios

#### 1.3.1. Scenario: Create New Report

1. The user opens the application in the browser.
2. The user chooses “Create new report” (or it happens by default on first load).
3. The screen displays:
   - **Settings panel** (at the top) – report-level settings and title page parameters.
   - **Blocks panel** (left) – available block types that can be inserted.
   - **Report builder / constructor** (center) – interactive area where the report structure is built.
   - **Errors and Warnings panel** (right) – list of validation messages from ГОСТ/МИСИС rules.
4. The user sets general report parameters (type of work, discipline, topic, student and teacher data, etc.).
5. The user adds blocks to the report structure (via drag-and-drop or buttons).
6. The user fills in the content of each block.
7. The validation panel shows errors and warnings; the user fixes them.
8. The user triggers export to DOCX or PDF.

#### 1.3.2. Scenario: Configure Title Page

1. In the settings panel, the user selects the **type of work** (practical, laboratory, essay, course work, etc.).
2. The user enters/edits the following fields:
   - Student’s full name (ФИО студента).
   - Group number.
   - Semester number.
   - Training direction code (направление подготовки, e.g. “38.03.05”).
   - Training direction name (e.g. “Бизнес-информатика”).
   - Department name (кафедра).
   - Discipline name.
   - Report topic.
   - Work number (for practical/laboratory, if applicable).
   - Teacher’s full name (ФИО преподавателя).
   - Submission date.
3. These values are:
   - Used when generating the title page from the `.docx` template.
   - **Saved in the browser’s `localStorage`** and restored as defaults on the next app load.

#### 1.3.3. Scenario: Edit Report Structure

1. The left blocks panel displays the list of available block types (see 1.4).
2. The user can:
   - Drag blocks into the central builder area.
   - Insert blocks via click (e.g. adding to the end or at a position near the selected block).
   - Change the order of blocks (drag-and-drop or “move up/down” buttons).
   - Delete blocks.
   - Edit the contents of each block in a separate block editor.
3. The structure update is immediately reflected:
   - Visually in the builder.
   - In numbering (sections, figures, tables, appendices).
   - In validation results shown in the errors/warnings panel.

#### 1.3.4. Scenario: View and Fix ГОСТ/МИСИС Violations

1. The right side shows the **Errors and Warnings** panel.
2. On every significant change (or periodically with debounce) the system:
   - Runs validation rules over the current `Report` model.
   - Updates the lists:
     - **Errors** (critical violations that should not be present in the final document).
     - **Warnings** (undesirable or suspicious situations).
3. When the user clicks an error or warning:
   - The builder scrolls/focuses the corresponding block/element so the user can quickly fix it.

#### 1.3.5. Scenario: Export to DOCX

1. The user clicks “Export to Word (.docx)”.  
2. The system:
   - Takes the current report structure (JSON representation).
   - Validates the model (basic schema validation; optionally detailed structural validation).
   - Builds an intermediate representation (Markdown + YAML metadata) from the report.
   - Invokes Pandoc to convert Markdown → DOCX with a reference template `misis_reference.docx`.
   - The DOCX generation must include automatic **table of contents (TOC)** generation without requiring manual update in Word.
   - Ensures headings, sections, lists, tables, figures, references, and appendices meet МИСИС formatting rules.
3. The system returns the generated `.docx` file for download.
4. The resulting `.docx` is ready to use **without any manual “update fields” actions** in Word (TOC and page numbers are already correct).

#### 1.3.6. Scenario: Export to PDF

1. The user clicks “Export to PDF”.
2. The system:
   - Generates the DOCX as in 1.3.5, or directly uses Markdown with Pandoc to PDF.
   - Converts to PDF on the backend (using Pandoc and/or corresponding PDF engines).
   - Returns the PDF to the user for download.

The goal is for the PDF formatting to mirror the DOCX result as closely as possible.

#### 1.3.7. Scenario: Save and Load Report Projects

1. The user can save the entire report in a **project file** (e.g., `.report.json`):
   - This file contains the full `Report` model, including:
     - Meta information (settings, title page data).
     - Blocks and their contents.
     - Nested structure.
2. Later, the user can:
   - Load this project file.
   - Restore the report structure and content in the builder.
   - Make changes and re-export to DOCX/PDF.

Initial version: project save/load can be implemented purely on the frontend side (export/import of JSON), without backend storage.


### 1.4. Supported Block Types

The system must support the following **block types** (structural elements) in the report builder:

1. **Title Page** (`TITLE_PAGE`)
   - Generated automatically from user-entered meta data and a `.docx` title page template.
   - In the builder, may appear as a special block at the beginning of the document.
   - The user does not type content manually; they configure only metadata in the settings panel.

2. **Table of Contents (TOC)** (`TOC`)
   - Special block representing the report’s contents (СОДЕРЖАНИЕ).
   - One per report (in the МИСИС preset).
   - Usually placed immediately after the title page.
   - Generated automatically at export time via Pandoc’s `--toc` and heading hierarchy.

3. **Section** (`SECTION`)
   - Top-level section heading (level 1) such as:
     - “ВВЕДЕНИЕ”
     - “1 Постановка задачи”
     - “ЗАКЛЮЧЕНИЕ”
     - “СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ”
   - Properties:
     - `title: str`
     - `special_kind: Optional["INTRO", "CONCLUSION", "REFERENCES"]` – to distinguish special sections.
   - Can contain child blocks:
     - Subsections;
     - Text blocks;
     - Lists;
     - Tables;
     - Figures;
     - etc.

4. **Subsection** (`SUBSECTION`)
   - Subheadings of level 2 or 3.
   - Properties:
     - `level: 2 or 3`
     - `title: str`
   - Placed inside Sections or other Subsections.

5. **Text Block** (`TEXT`)
   - One or more paragraphs of plain text.
   - Properties:
     - `text: str`
   - Used for normal body text, conclusions, explanations, etc.

6. **List Block** (`LIST`)
   - Either bullet lists or numbered lists:
     - Bullet: marker is a **long dash** (`–`).
     - Numbered: format `1)`, `2)`, `3)` etc.
   - Properties:
     - `list_type: "bulleted" | "numbered"`
     - `items: list[str]`

7. **Table Block** (`TABLE`)
   - Properties:
     - `caption: str` – required, used for “Таблица N – Название таблицы”.
     - `rows: list[list[str]]` – 2D array (first row is usually the header).
   - Always accompanied by a caption, displayed above the table in the final document.

8. **Figure Block** (`FIGURE`)
   - Properties:
     - `caption: str` – required, used for “Рисунок N – Название рисунка”.
     - `file_name: str` – name/ID of the uploaded image file.
   - In the builder, may show a thumbnail preview and a caption field.

9. **References List Block** (`REFERENCES`)
   - Special block representing “СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ”.
   - Properties:
     - `items: list[str]` – textual references; strict ГОСТ content format is not enforced in the first version (only basic structure).

10. **Appendix Block** (`APPENDIX`)
    - Represents a separate appendix (e.g., “ПРИЛОЖЕНИЕ А”).
    - Properties:
      - `label: str` – letter index (“А”, “Б”, “В”, etc. without Ё, З, Й, О, Ч, Ъ, Ы, Ь).
      - `title: str` – title of the appendix.
      - `children: list[ReportBlock]` – content blocks within the appendix (text, tables, figures, etc.).

> **Formulas:** There is **no separate formula block** in the first version. Formulas are expected to be added by the user manually in Word, or omitted.


### 1.5. Settings Panel Requirements

The settings panel (top area in UI) must allow the user to configure:

1. **Preset Selection**
   - A list of formatting presets (initially only `MISIS`).
   - The default preset is **MISIS standard** (`misis_v1`).
   - The panel should show a short textual description of the preset (page margins, fonts, etc.) or at least its name.

2. **General Report Parameters**
   - Type of work:
     - Practical work (ПР), laboratory work (ЛР), essay, course work, etc.
   - Work number (for practical/laboratory if applicable).
   - Discipline name.
   - Report topic.

3. **Title Page Parameters**
   - Student’s full name (ФИО).
   - Group number.
   - Semester number.
   - Training direction code.
   - Training direction name.
   - Department name.
   - Teacher’s full name.
   - Submission date (date of completion or defense).

4. **Persistence to localStorage**
   - These settings must be automatically stored in `localStorage`:
     - All fields from the title page parameters;
     - Optionally: default type of work and discipline.
   - On page load, the application:
     - Reads values from `localStorage` (if available);
     - Pre-populates the settings panel with these values;
     - Allows the user to change them at any time.



### 1.6. Blocks Panel and Report Builder Requirements

#### 1.6.1. Blocks Panel

- Displays all available block types (Title Page, TOC, Section, Subsection, Text, List, Table, Figure, References, Appendix).
- For each block type, shows:
  - A name;
  - A short description.
- Interaction options:
  - Click to add a block of this type into the structure (e.g., at the end or relative to selected block).
  - Drag-and-drop to insert a block at a specific position in the builder.

#### 1.6.2. Report Builder (Constructor)

- Visual representation of the report’s structure as a list/tree of blocks:
  - Sections and subsections may be displayed with indentation for nesting.
  - Blocks can be reordered via drag-and-drop or explicit “move up/down” actions.
- For each block:
  - Clicking on it selects it and shows an editor for its properties/contents (BlockEditor).
  - The user can delete the block (with confirmation for important blocks).
- The builder must support nested structures:
  - Sections containing subsections and content blocks;
  - Appendices containing their own child blocks.

Changes in the builder must be immediately reflected in:

- The internal `Report` model in the frontend store.
- The numbering and validation state (after a slight debounce to avoid excessive calls).


### 1.7. Errors and Warnings Panel

#### 1.7.1. General Requirements

- The panel shows two groups:
  - **Errors** – violations of mandatory rules;
  - **Warnings** – potential or minor issues, recommended to fix but not strictly mandatory.
- Each entry includes:
  - `code` – a stable string identifier of the rule (e.g., `SECTION_ENDS_WITH_MEDIA`);
  - `message` – a human-readable description;
  - `block_id` – optional link to the related block.

#### 1.7.2. Validation Rules (Minimum Set)

The system must implement at least the following rules (as in 5.2 of ТЗ):

1. `REQUIRED_SECTIONS_PRESENT`
   - Checks presence of mandatory structural elements for the MISIS preset:
     - Title page;
     - Table of contents (СОДЕРЖАНИЕ);
     - Section “ВВЕДЕНИЕ”;
     - Section “ЗАКЛЮЧЕНИЕ”;
     - Section “СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ`.
   - Missing any of them → **error**.

2. `SECTION_ORDER`
   - Validates correct order of key sections:
     - “ВВЕДЕНИЕ” must appear before main body sections;
     - “ЗАКЛЮЧЕНИЕ” must appear after main body sections but before the references list;
     - “СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ” must be placed before any appendices.
   - Violations → **error**.

3. `SECTION_ENDS_WITH_MEDIA`
   - For each section (and possibly subsection treated as a section boundary), checks that the last child block is **not** a Figure, Table, or List.
   - If the last block is FIGURE, TABLE, or LIST, the rule returns an **error** indicating that a concluding text block is required.

4. `NON_EMPTY_LISTS`
   - Ensures that all List blocks have at least one item.
   - Empty lists → **error** or `warning` (minimum requirement: must be flagged).

5. `FIGURE_HAS_CAPTION`
   - Ensures all Figure blocks have a non-empty `caption`.
   - Missing/empty caption → **error**.

6. `TABLE_HAS_CAPTION`
   - Ensures all Table blocks have a non-empty `caption` (table name).
   - Missing/empty caption → **error**.

7. `APPENDIX_LABELS_UNIQUE`
   - Ensures that all Appendix labels (letters) are unique within a single report.
   - Duplicate labels → **error**.

8. `APPENDIX_LABELS_ORDER` (optional but desired in first version)
   - If implemented, ensures appendices follow alphabetical order (A, Б, В, … without Ё, З, Й, О, Ч, Ъ, Ы, Ь).
   - Out-of-order or invalid labels → `warning` or `error` as determined by the spec (at minimum `warning`).

9. `FIGURE_TABLE_NUMBERING_CONSISTENT`
   - Validates figure and table numbering for consistency:
     - no duplicate numbers;
     - no obvious gaps in numbering (1,2,4 – missing 3 → warning or error).
   - At minimum, the rule should detect duplicates and produce an **error**.

10. `REFERENCES_PRESENT_IF_NEEDED`
    - For certain work types under MISIS preset (e.g. practical/laboratory/essay):
      - If the report requires a references list, but the `REFERENCES` block is missing, this is an **error**.

11. `LIST_OF_REFERENCES_NOT_EMPTY`
    - If a `REFERENCES` block exists, check that `items` is not empty.
    - Empty references list → at least a `warning` (can be stricter if desired).

12. `REPORT_EMPTY_SPACE_LIMIT`
    - Попытка оценить долю пустого пространства на странице.
    - Если на странице более 25% пустого пространства → **warning** (рекомендательное требование, см. раздел 3.1).

13. `HEADING_SPACING_SCENARIOS`
    - Проверка допустимых сценариев интервалов вокруг заголовков (см. таблицу в разделе 3.3).
    - Нарушение обязательных интервалов → **error**.

14. `HEADING_NUMBERING_STYLE`
    - Проверка корректности многоуровневой нумерации (1 / 1.1 / 1.1.1) и привязки к стилям Heading 1/2/3.
    - Несоответствие схемы → **error**.

15. `LIST_MARKER_FORMAT`
    - Маркеры списков соответствуют нормативу (маркированный «–», нумерованный «1)», вложенный «а)»).
    - Несоответствие формату → **error** (или **warning** для вложенных/рекомендательных случаев).

16. `TABLE_REQUIREMENTS`
    - Таблица имеет шапку, выровнена по центру, без колонки «№ п/п».
    - Несоответствие → **error**.

17. `FIGURE_REQUIREMENTS`
    - Рисунок имеет подпись в формате `Рисунок X – Название` и размещён по центру.
    - Несоответствие → **error**.

18. `REFERENCES_LINKS_VALID`
    - Каждая ссылка в тексте вида `[N]` соответствует записи в списке источников.
    - Отсутствие соответствующей записи → **error**.

19. `REFERENCES_AGE_WARNING`
    - По методическим указаниям МИСИС источники старше 5 лет не рекомендуются.
    - Система помечает такие записи как **warning** и не блокирует экспорт (см. раздел 3.7).

Additional rules may be added in the future, but the above form the **minimum validation set** for the first release.


### 1.8. DOCX Export Requirements

#### 1.8.1. General Expectations

The generated `.docx` report must:

- Match the structure defined in the builder:
  - Title page;
  - Table of contents;
  - Sections and subsections (with headings);
  - Text blocks;
  - Lists;
  - Tables and figures with captions;
  - References list;
  - Appendices.
- Conform to the MISIS preset formatting, including (but not limited to):
  - Page margins;
  - Fonts and sizes;
  - Paragraph indentation and line spacing;
  - Heading styles;
  - List styles;
  - Table and figure captions.

#### 1.8.2. Headings and Numbering

- Headings of level 1, 2, 3 must be assigned appropriate Word styles (through the Pandoc `reference.docx` template).
- Multi-level numbering of headings (1, 1.1, 1.2, 2, 2.1, etc.) must be implemented via styles and numbering defined in `misis_reference.docx`.
- Section titles such as “ВВЕДЕНИЕ”, “ЗАКЛЮЧЕНИЕ”, “СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ” must appear as required by MISIS:
  - often uppercase, centered for some specific sections, etc. – these details are to be captured in the template.
- Подробные числовые параметры оформления и сценарии интервалов для заголовков перечислены в разделе 3.

#### 1.8.3. Figures and Tables Numbering

- Figures:
  - Numbered globally in the main text OR per section, as specified by the MISIS rules (implementation detail to be finalized in template).
  - Captions must follow format: `Рисунок N – Название рисунка`.
- Tables:
  - Similar numbering style;
  - Captions must follow format: `Таблица N – Название таблицы`.
- Appendices:
  - Figures and tables within appendices may use a prefix with the appendix label (e.g., `Рисунок А.1`), depending on the preset; the template and numbering scheme in the generator must reflect this.

#### 1.8.4. Table of Contents

- The DOCX must contain a **correct table of contents** (СОДЕРЖАНИЕ):
  - All relevant headings must appear in the TOC.
  - Page numbers must be correct and not require manual update in Word.

- Implementation is done via Pandoc:
  - The Markdown document uses heading levels.
  - Pandoc is invoked with `--toc` and reference doc that properly formats the TOC.
  - The resulting docx must already contain a static or properly updated TOC, such that the user does not need to press Ctrl+A → F9.

#### 1.8.5. File Name

- When exporting, the backend must generate a file name based on report meta:
  - Student last name (or full name in Latin or transliterated form),
  - Group number,
  - Discipline abbreviation (or code),
  - Work type abbreviation (e.g., `PR`, `LR`),
  - Work number.
- Нормативный формат имени файла (по методичке МИСИС):

  ```text
  {StudentLastNameLatin}_{Group}_{DisciplineAbbrev}_{WorkTypeShort}№{WorkNumber}.{ext}
  ```

  Пример: `Ivanov_BBI-24-3_TOiP_PR№1.docx`.

- Фактический формат имени файла, используемый приложением:

  ```text
  {StudentLastNameLatin}_{Group}_{DisciplineAbbrev}_{WorkTypeShort}{WorkNumber}.{ext}
  ```

  Пример: `Ivanov_BBI-24-3_TOiP_PR1.docx`.

- Приложение по умолчанию использует формат **без символа №** для совместимости с разными файловыми системами.
  Пользователь может вручную переименовать файл в нормативный формат с `№` перед номером работы.
- Discipline abbreviation and `WorkTypeShort` normalization rules must be specified in code (e.g., mapping to MISIS abbreviations or a simplified standard).
- Разделители — только подчёркивания `_`, без пробелов и дефисов между блоками формата.


### 1.9. PDF Export Requirements

- When exporting to PDF:
  - The system must generate the PDF locally (on the backend) using Pandoc and/or appropriate PDF engine.
  - The PDF must faithfully represent formatting from DOCX/MISIS template (page size, margins, fonts, layout).
- PDF generation must **not** rely on any external online services (no API calls).


### 1.10. Project Save and Load

- Users must be able to:
  - Save current report state as a JSON file:
    - Contains the full `Report` structure (all blocks, meta, nested blocks).
    - Recommended extension: `.report.json`.
  - Load previously saved JSON to restore the editing state.

- For the first version:
  - Save/Load can be implemented purely in the frontend:
    - Save: “Download JSON” (using a Blob and `URL.createObjectURL`).
    - Load: “Upload JSON” and parse it in the browser.
  - Backend does not need persistent storage of projects.


### 1.11. Constraints and Exclusions

1. **Formulas**
   - No dedicated formula block or formula generation.
   - No automatic creation of Word OMML formulas.
   - Users may insert formulas manually in Word after export if needed.

2. **Antiplagiarism and External Integrations**
   - No integration with antiplagiarism systems.
   - No integration with any external academic platforms or LMS.

3. **AI / LLM**
   - No usage of ChatGPT/DeepSeek or any LLM models in the first version.
   - No automatic segmentation of text into blocks using AI (future possibility, but strictly out-of-scope for this version).

4. **Commercial Libraries**
   - No Aspose, Spire, or any paid/proprietary libraries.
   - Only open-source tools are used (Pandoc, Python, Node.js ecosystem, etc.).

> Дополнительно: конкретные ограничения по оформлению и вне scope (формулы, антиплагиат и др.) закреплены в разделе 3.10.


---

## 2. Technical Specification (ТЗ)

### 2.1. Overall Architecture

The system is implemented as a **client–server web application**:

- **Frontend**: TypeScript + React + Vite SPA.
- **Backend**: FastAPI (Python 3.11+).
- **Document generation engine**: Pandoc with a configured `reference.docx` template for MISIS.

The app runs locally in the user’s environment:

- Directly via `uvicorn` and `npm` scripts;
- Or via Docker (`docker-compose` bringing up frontend + backend).

The system is designed to be:

- Offline: no external HTTP requests.
- Open source: all components and libraries are free or open source.


### 2.2. Technology Stack

#### 2.2.1. Backend

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Web server**: uvicorn
- **Key libraries**:
  - `fastapi`
  - `uvicorn[standard]`
  - `pydantic` / `pydantic-settings`
  - `python-docx` (optional, for tests or utility inspection of generated DOCX)
  - `pytest`, `pytest-asyncio` for testing
  - Standard library modules:
    - `pathlib`, `tempfile`, `subprocess`, `uuid`, `datetime`

- **External tool**:
  - **Pandoc** for document conversion:
    - Markdown → DOCX with `--reference-doc` and `--toc`.
    - Markdown → PDF (via built-in or specified PDF engine, such as `wkhtmltopdf`, `pdflatex`, etc., depending on configuration).

#### 2.2.2. Frontend

- **Language**: TypeScript
- **Framework**: React
- **Build tool**: Vite
- **Key libraries**:
  - `react`, `react-dom`
  - Drag-and-drop library (e.g., `@dnd-kit/core` or `react-beautiful-dnd`)
  - State management:
    - Either React Context + `useReducer` or a small store library (e.g., `zustand`)
  - HTTP client:
    - `fetch` (native) or `axios` (if desired)

- **Tooling**:
  - ESLint + Prettier for linting and formatting.


### 2.3. Deployment Modes

Two main modes should be supported:

1. **Local Development Mode**:
   - Backend:
     - Run with `uvicorn app.main:app --reload`.
   - Frontend:
     - Run with `npm run dev` (Vite dev server).
   - The frontend dev server proxies `/api` requests to the backend.

2. **Docker / Production Mode**:
   - `backend` image:
     - Python + FastAPI + Pandoc installed.
   - `frontend` image:
     - Built React app (static files) served either:
       - by a lightweight HTTP server (e.g., `nginx`, `caddy`, `serve`), or
       - by the backend app itself via static files route.
   - `docker-compose.yml` defines two services:
     - `backend` (exposes API port, e.g., 8000),
     - `frontend` (exposes port, e.g., 4173 or 80).


### 2.4. Backend Structure

A recommended directory layout:

```text
backend/
  app/
    main.py             # FastAPI entry point
    core/
      config.py         # app settings (pydantic-settings)
      logging.py        # logging configuration (optional)
    api/
      v1/
        reports.py      # /api/v1/reports/* routes
        presets.py      # /api/v1/presets/* routes
    models/
      report.py         # Pydantic models: Report, ReportMeta, ReportBlock, etc.
      validation.py     # Pydantic models: ValidationIssue, ValidationResult
    services/
      validation/
        engine.py       # orchestrates validation rules
        rules.py        # individual validation rules implementations
      generation/
        builder.py      # builds Markdown (and YAML) from Report
        pandoc_runner.py# wraps Pandoc CLI calls
      projects/
        storage.py      # optional if backend handles project files
    assets/
      templates/
        misis_reference.docx  # main reference template for Pandoc
      samples/
        ...                    # example reports/documents (for tests)
  tests/
    ...
  pyproject.toml / requirements.txt
```


### 2.5. Data Model (Backend)

#### 2.5.1. ReportMeta

```python
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import date

class WorkType(str, Enum):
    PRACTICE = "practice"
    LAB = "lab"
    ESSAY = "essay"
    COURSE = "course"
    OTHER = "other"

class ReportMeta(BaseModel):
    preset: str = "misis_v1"

    work_type: WorkType
    work_number: Optional[int]

    discipline: str
    topic: str

    student_full_name: str
    group: str
    semester: str
    direction_code: str
    direction_name: str
    department: str
    teacher_full_name: str
    submission_date: date
```

#### 2.5.2. Block Types

```python
from uuid import UUID, uuid4
from typing import List, Optional, Literal, Union

class ReportBlockType(str, Enum):
    TITLE_PAGE = "title_page"
    TOC = "toc"
    SECTION = "section"
    SUBSECTION = "subsection"
    TEXT = "text"
    LIST = "list"
    TABLE = "table"
    FIGURE = "figure"
    REFERENCES = "references"
    APPENDIX = "appendix"
```

Each block has a common base:

```python
class BaseBlock(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: ReportBlockType
    children: List["BaseBlock"] = []
```

Then specific subtypes can be defined, e.g.:

```python
class SectionBlock(BaseBlock):
    type: Literal[ReportBlockType.SECTION]
    title: str
    special_kind: Optional[Literal["INTRO", "CONCLUSION", "REFERENCES"]] = None

class SubsectionBlock(BaseBlock):
    type: Literal[ReportBlockType.SUBSECTION]
    level: Literal[2, 3]
    title: str

class TextBlock(BaseBlock):
    type: Literal[ReportBlockType.TEXT]
    text: str

class ListBlock(BaseBlock):
    type: Literal[ReportBlockType.LIST]
    list_type: Literal["bulleted", "numbered"]
    items: List[str]

class TableBlock(BaseBlock):
    type: Literal[ReportBlockType.TABLE]
    caption: str
    rows: List[List[str]]

class FigureBlock(BaseBlock):
    type: Literal[ReportBlockType.FIGURE]
    caption: str
    file_name: str

class ReferencesBlock(BaseBlock):
    type: Literal[ReportBlockType.REFERENCES]
    items: List[str]

class AppendixBlock(BaseBlock):
    type: Literal[ReportBlockType.APPENDIX]
    label: str
    title: str
    children: List[BaseBlock] = []
```

The main `Report` model:

```python
class Report(BaseModel):
    meta: ReportMeta
    blocks: List[BaseBlock]
```

> Note: actual implementation may use `Union[...]` for blocks or a discriminated union pattern, but logically it must cover all the listed properties.

#### 2.5.3. Validation Models

```python
class ValidationIssueLevel(str, Enum):
    ERROR = "error"
    WARNING = "warning"

class ValidationIssue(BaseModel):
    code: str
    level: ValidationIssueLevel
    message: str
    block_id: Optional[UUID] = None

class ValidationResult(BaseModel):
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]
```


### 2.6. REST API Endpoints

#### 2.6.1. `GET /api/v1/presets`

- **Purpose**: Get the list of available formatting presets.
- **Response (200)**:

```json
[
  {
    "id": "misis_v1",
    "name": "МИСИС (стандартный)",
    "description": "Пресет оформления отчетов по методическим указаниям НИТУ МИСИС."
  }
]
```

#### 2.6.2. `GET /api/v1/presets/{preset_id}`

- **Purpose**: Get detailed information about a specific preset (optional but recommended).
- **Response (200)**:
  - JSON with extended metadata: page margins, base font, headings style notes, etc.

#### 2.6.3. `POST /api/v1/reports/validate`

- **Purpose**: Validate a report according to MISIS preset rules.
- **Request Body**: `Report` JSON.
- **Response (200)**: `ValidationResult`

```json
{
  "errors": [
    {
      "code": "SECTION_ENDS_WITH_MEDIA",
      "level": "error",
      "message": "Раздел '1 Теоретическая часть' заканчивается рисунком. После рисунка должен идти текст.",
      "block_id": "uuid-xxxx"
    }
  ],
  "warnings": [
    {
      "code": "REFERENCES_MISSING",
      "level": "warning",
      "message": "В отчете отсутствует раздел 'СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ'.",
      "block_id": null
    }
  ]
}
```


#### 2.6.4. `POST /api/v1/reports/export/docx`

- **Purpose**: Generate a DOCX report.
- **Request Body**: `Report` JSON.
- **Response (200)**:
  - Binary stream of `.docx` file with content type:
    - `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
  - `Content-Disposition` header with generated file name.

#### 2.6.5. `POST /api/v1/reports/export/pdf`

- **Purpose**: Generate a PDF report.
- **Request Body**: `Report` JSON.
- **Response (200)**:
  - Binary stream of `.pdf` file with content type:
    - `application/pdf`
  - `Content-Disposition` header with generated file name.


#### 2.6.6. Project Save/Load Endpoints (Optional)

To keep backend simple in v1, **project save/load may be implemented purely client-side**. If backend endpoints are added later, they can be:

- `POST /api/v1/reports/project/save` – accept `Report` and return it as a downloadable JSON file.
- `POST /api/v1/reports/project/load` – accept an uploaded JSON file and validate/normalize the `Report` structure.

In v1, these endpoints are **not required** by this ТЗ.


### 2.7. Document Generation Module

#### 2.7.1. Overview

Document generation happens in `services/generation`:

1. **builder.py** – converts `Report` into an intermediate **Markdown + YAML** representation.
2. **pandoc_runner.py** – calls Pandoc to convert Markdown to DOCX/PDF using MISIS reference template.


#### 2.7.2. Builder: Markdown + YAML Metadata

**YAML metadata section** (at the top of the Markdown file):

```yaml
---
title: "Практическая работа №4"
author: "Иванов Иван Иванович"
institute: "НИТУ МИСИС"
department: "Кафедра ..."
discipline: "Технологические основы производства"
work_type: "Практическая работа"
work_number: 4
group: "ББИ-24-3"
semester: "2"
direction_code: "38.03.05"
direction_name: "Бизнес-информатика"
teacher: "Петров Петр Петрович"
submission_date: "2025-03-15"
...
---
```

These fields will be used in the Word template (`misis_reference.docx`) to:

- Fill the title page (via Pandoc template fields).
- Potentially fill headers/footers (if needed).

**Markdown body**:

- Built from `Report.blocks`:

  - **Title Page**:
    - Controlled by the template and YAML metadata; may not require explicit Markdown content.

  - **TOC**:
    - Pandoc will generate the table of contents automatically with `--toc`, so explicit TOC block in Markdown may be omitted or replaced with a special marker section if needed.

  - **Sections and Subsections**:
    - Level 1: `# ВВЕДЕНИЕ`, `# 1 Постановка задачи`, etc.
    - Level 2: `## 1.1 Подраздел`, etc.
    - Level 3: `### 1.1.1 Подподраздел`.

  - **Text Blocks**:
    - Rendered as paragraphs separated by blank lines.

  - **Lists**:
    - Bulleted: `-` or `-` with long dash in text (visual style managed by template).
    - Numbered: `1) item`, `2) item`, etc.

  - **Tables**:
    - Represented with Pandoc table syntax (pipe tables or simple tables).
    - Captions placed above the table as a paragraph with appropriate pattern (e.g. `Таблица 1 – Название`), and/or using Pandoc attributes for proper captioning via `pandoc-crossref` in future.

  - **Figures**:
    - Images inserted via `![caption](path/to/image)` or using Pandoc’s extended attributes.
    - Captions should follow the MISIS pattern.

  - **References List**:
    - Rendered as a section heading and a list of sources.

  - **Appendices**:
    - For each appendix:
      - A top-level heading: `# ПРИЛОЖЕНИЕ А` (or corresponding label).
      - A subheading for the appendix title, if required.
      - Child blocks rendered as usual (text, tables, figures).


#### 2.7.3. Pandoc Runner

`pandoc_runner.py` must:

- Provide functions:

  ```python
  def generate_docx_from_markdown(md_path: Path, output_path: Path, reference_doc: Path) -> None: ...
  def generate_pdf_from_markdown(md_path: Path, output_path: Path, reference_doc: Path) -> None: ...
  ```

- Build the Pandoc command:
  - For DOCX:

    ```bash
    pandoc input.md       --reference-doc=assets/templates/misis_reference.docx       --toc       -o output.docx
    ```

  - For PDF (example):

    ```bash
    pandoc input.md       --reference-doc=assets/templates/misis_reference.docx       --toc       -o output.pdf
    ```

- Use `subprocess.run` with proper error handling:
  - Capture stderr/stdout;
  - Return appropriate errors through FastAPI if Pandoc fails.

`misis_reference.docx` must be:

- A manually prepared Word template with:
  - Correct margins, fonts, spacing;
  - Styles for normal text and headings;
  - Styles for figure/table captions;
  - Possibly a pre-defined title page that uses YAML metadata fields.

This template is crucial to ensure MISIS/GOST conformity.


### 2.8. Validation Engine

#### 2.8.1. Structure

`services/validation` must contain:

- `rules.py` – individual rules, each a function:

  ```python
  def rule_section_ends_with_media(report: Report) -> List[ValidationIssue]: ...
  ```

- `engine.py` – orchestrator that:

  - Holds a registry of rules;
  - Runs all rules for a given `Report`:
  
    ```python
    def validate_report(report: Report) -> ValidationResult:
        issues = []
        issues.extend(rule_required_sections_present(report))
        issues.extend(rule_section_order(report))
        issues.extend(rule_section_ends_with_media(report))
        ...
        return ValidationResult(
            errors=[i for i in issues if i.level == ValidationIssueLevel.ERROR],
            warnings=[i for i in issues if i.level == ValidationIssueLevel.WARNING],
        )
    ```

#### 2.8.2. Implemented Rules

The rules listed in **1.7.2** (ФТ) must be implemented here, with logic that maps exactly to those descriptions.


### 2.9. Frontend Structure and UI

#### 2.9.1. Project Structure

Example layout:

```text
frontend/
  src/
    main.tsx
    App.tsx
    api/
      client.ts        # Axios/fetch setup
      reports.ts       # Functions to call backend endpoints
    store/
      reportStore.ts   # Report state: meta + blocks
    components/
      Layout/
        AppLayout.tsx
      SettingsPanel/
        SettingsPanel.tsx
      BlocksPanel/
        BlocksPanel.tsx
      ReportBuilder/
        ReportBuilder.tsx
        BlockItem.tsx
        BlockEditor.tsx
      ValidationPanel/
        ValidationPanel.tsx
    types/
      report.ts        # TS interfaces mirroring Pydantic models
      validation.ts
  index.html
  vite.config.ts
  package.json
```

#### 2.9.2. Core Components

- **SettingsPanel**:
  - Renders fields for `ReportMeta`.
  - Synchronizes selected fields with `localStorage` (load on mount, save on change).

- **BlocksPanel**:
  - Shows block type palette:
    - Title page;
    - TOC;
    - Section;
    - Subsection;
    - Text;
    - List;
    - Table;
    - Figure;
    - References;
    - Appendix.
  - On click or drag, creates new block and inserts into the report structure.

- **ReportBuilder**:
  - Displays hierarchical structure of `Report.blocks`.
  - Supports:
    - selection of block;
    - editing of block properties via `BlockEditor`;
    - drag-and-drop to reorder blocks;
    - operations to move up/down, delete.

- **BlockEditor**:
  - Contextual editor for the selected block type:
    - For Text: multiline text editor;
    - For List: list of items with add/remove;
    - For Table: editable grid or at least rows/cols structure;
    - For Figure: file picker (or link) + caption;
    - For Section/Subsection: title input, special kind selector; etc.

- **ValidationPanel**:
  - Displays lists of errors and warnings from `/reports/validate`.
  - On click of an issue, focuses corresponding block in `ReportBuilder`.


### 2.10. State Management

- A central store (or React Context + reducer) must hold `Report`:

  ```ts
  interface ReportMeta { ... }
  interface ReportBlock { ... }
  interface Report { meta: ReportMeta; blocks: ReportBlock[]; }
  ```

- Actions:
  - set meta fields;
  - add block;
  - update block;
  - move block;
  - delete block;
  - set full report (for loading a project).

- The front-end should trigger validation:
  - either automatically on change with throttling/debouncing;
  - or on explicit user action “Revalidate”.


### 2.11. Non-Functional Requirements

#### 2.11.1. Portability

- The application must run on:
  - Windows 10+;
  - macOS (current stable versions);
  - Linux (common distributions).
- Docker-based deployment is recommended to smooth over OS differences.

#### 2.11.2. Performance

- Target report size:
  - Up to ~50–100 pages of text;
  - Several dozen figures and tables.
- Validation and UI updates:
  - Should feel instant or near-instant (<200–300 ms) for typical size reports.
- Export to DOCX/PDF:
  - Expected to take seconds, but not minutes, at target sizes.


#### 2.11.3. Security

- No external network communication at runtime:
  - No calls to online APIs;
  - No data exfiltration.
- File uploads (e.g., images):
  - Are kept local to the environment;
  - Must not be sent to external services.
- Temporary files (Markdown, intermediate DOCX/PDF) should be cleaned up after use.


#### 2.11.4. Code Quality

- Backend:
  - Type-hinted Python;
  - Code formatted with `black` (or equivalent);
  - Linting with `ruff` or `flake8`.
- Frontend:
  - TypeScript with strict type checking;
  - ESLint + Prettier for consistent style.


### 2.12. Testing and Acceptance

#### 2.12.1. Backend Unit Tests

- Validate:
  - `services/validation` rules (with various synthetic `Report` examples).
  - `services/generation/builder.py` – expected Markdown output for given `Report` samples.
  - `pandoc_runner.py` – correct Pandoc command invocation (using mocks).

- For DOCX:
  - Use sample `Report` → generate `.docx` via Pandoc.
  - Parse the result with `python-docx` or XML:
    - Verify headings exist with expected text;
    - Check some style properties (e.g., that headings use expected style names);
    - Check presence of table and figure captions with correct text.

#### 2.12.2. Integration Tests

- End-to-end tests:
  - Generate a minimal report (intro, 1 section, conclusion, references).
  - Call `/reports/export/docx`.
  - Ensure response is non-empty, valid DOCX.
  - Optionally use CLI tools or libraries to open/inspect the docx and confirm it is not corrupted.

- Similar tests for `/reports/export/pdf`:
  - Validate that PDFs are generated and not empty.


#### 2.12.3. Acceptance Criteria

The system is accepted when:

1. A user can:
   - Build a typical MISIS-compliant report from scratch in the UI;
   - Export it to DOCX and PDF;
   - Open them in Word/LibreOffice and visually confirm compliance with MISIS formatting.

2. Key misis/ГОСТ requirements are met:
   - Page margins, fonts, sizes, line spacing, paragraph indentation;
   - Heading formatting and structure;
   - List formatting;
   - Table and figure handling (captions, numbering);
   - Required sections and their order;
   - Proper table of contents with correct page numbers.

3. The system runs correctly on Windows and macOS (or in Docker) without requiring an internet connection.


### 2.13. Limitations

- **Formulas**:
  - No automatic support.
  - Users must add formulas manually in Word if needed.

- **Antiplagiarism**:
  - No integration with antiplagiarism or university systems.

- **AI Features**:
  - No automatic segmentation of a full-text report into blocks using AI.
  - No LLM-based text generation or processing.

- **Commercial Libraries**:
  - No Aspose/Spire or similar. Only Pandoc and open-source tools.

> Детализированные ограничения по оформлению и scope проекта указаны в разделе 3.10.


---

## 3. Числовые параметры и форматирование МИСИС (нормативные требования)

Раздел фиксирует **все числовые параметры и специальные правила оформления** по методическим материалам НИТУ МИСИС и образцам.  
Чтобы требования были однозначны, каждое правило классифицируется как:

- **Обязательное при генерации** — приложение должно сформировать документ строго по этим параметрам.
- **Проверки/подсветка** — приложение обязано валидировать и показывать ошибки/предупреждения в UI.
- **Рекомендации (на совести пользователя)** — методичка требует, но авто‑контроль может быть ограничен; система показывает warning или только текстовую рекомендацию.

### 3.1. Параметры страницы и ориентация

**Обязательное при генерации**

- Формат страницы: **A4**.
- Поля для книжной ориентации (основное тело отчёта):
  - Левое: **3,0 см**
  - Правое: **1,5 см**
  - Верхнее: **2,0 см**
  - Нижнее: **2,0 см**
- Поля для альбомной ориентации (страницы с широкими таблицами/рисунками):
  - Левое: **2,0 см**
  - Правое: **2,0 см**
  - Верхнее: **2,0 см**
  - Нижнее: **2,0 см**
- Переключение ориентации допускается только для страниц с широкими объектами (таблицы/рисунки).

**Проверки/подсветка**

- Валидация соответствия полей и ориентации страниц требованиям, включая проверку, что альбомные страницы применяются только при необходимости.

### 3.2. Нумерация страниц и «≤ 25% пустого места»

**Обязательное при генерации**

- Нумерация страниц начинается с **первой страницы отчёта**.
- Если присутствует титульный лист и содержание:
  - номера на титульном листе и странице содержания **не отображаются**;
  - фактический вывод номеров начинается с **первой страницы введения**.
- Положение номера страницы: **снизу по центру**.

**Проверки/подсветка**

- Если на странице более **25% пустого пространства**, система должна попытаться это обнаружить и выдать **warning**.

**Рекомендации**

- При невозможности точной автоматической оценки пустого пространства выводится текстовое предупреждение без блокировки экспорта.

### 3.3. Заголовки и структура разделов

**Обязательное при генерации**

- Заголовки уровней 1/2/3: **Times New Roman, 12 pt**, межстрочный интервал **1,5**.
- Заголовки структурных разделов набираются **ПРОПИСНЫМИ**:
  - «СОДЕРЖАНИЕ», «ВВЕДЕНИЕ», «ЗАКЛЮЧЕНИЕ», «СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ», «ПРИЛОЖЕНИЕ».
- Многоуровневая нумерация:
  - Уровень 1: `1`, `2`, `3`, …
  - Уровень 2: `1.1`, `1.2`, …
  - Уровень 3: `1.1.1`, …
  - Нумерация реализуется **многоуровневым списком Word**, связанным со стилями Heading 1/2/3.
  - Выравнивание номера по позиции **1,25 см**, после номера — **пробел**.
- Между заголовком и следующим текстом/подзаголовком **не допускаются пустые абзацы**.

**Интервалы вокруг заголовков (сценарии)**

| Сценарий | Интервал до | Интервал после |
| --- | --- | --- |
| Заголовок в начале страницы → сразу текст | 0 pt | 24 pt |
| Заголовок в начале страницы → сразу подзаголовок | 0 pt | 0 pt |
| Заголовок среди текста → сразу подзаголовок | 24 pt | 0 pt |
| Заголовок среди текста → сразу текст | 24 pt | 24 pt |

**Проверки/подсветка**

- Проверять соблюдение таблицы сценариев интервалов и отсутствие пустых абзацев между заголовками и текстом.
- Проверять корректность многоуровневой нумерации и связь стилей Heading 1/2/3.

### 3.4. Списки

**Обязательное при генерации**

- Общие параметры абзаца списков:
  - Шрифт: **Times New Roman, 12 pt**.
  - Выравнивание: **по ширине**.
  - Отступы слева/справа: **0 см**.
  - Первая строка: **0 см**.
  - Межстрочный интервал: **1,5**.
  - Интервалы до/после: **0 pt**.
- Маркированный список:
  - Маркер: **длинное тире «–» (код 190)**.
  - Положение маркера: **0 см**.
  - Отступ текста: **1,25 см**.
  - Символ после маркера: **пробел**.
- Нумерованный список:
  - Формат: **`1)`**, `2)`, `3)` (цифра + закрывающая скобка).
  - Положение номера: **0 см**.
  - Отступ текста: **1,25 см**.
  - Символ после номера: **табуляция**.
- Внутритекстовые и вложенные перечисления:
  - Основной формат: **строчные русские буквы с закрывающей скобкой** (`а)`, `б)`, `в)` …).
  - Запрещённые буквы: **ё, э, й, о, ч, ъ, ы, ь**.
  - Допускается использование арабских цифр со скобкой (`1)`, `2)`, …) при вложенности уровня 2+ или в случаях, когда перечисление содержит числовые значения и буквенная схема создаёт неоднозначность.

**Проверки/подсветка**

- Неверные маркеры и нумерация (не «–», не `1)` и т. п.) → **error**.
- Неверная схема вложенных списков (отсутствие буквенного/цифрового формата) → **warning** или **error** (по уровню критичности).

### 3.5. Таблицы

**Обязательное при генерации**

- Выравнивание таблицы: **по центру страницы**.
- Основной текст отчёта оформляется **Times New Roman 12 pt, межстрочный 1,5** (см. требования к основному тексту).
  Внутри таблиц применяются отдельные параметры:
  - Шрифт содержимого таблиц (шапка и строки): **Times New Roman, 10 pt**.
  - Межстрочный интервал внутри таблиц: **одинарный (1,0)**.
  - Выравнивание текста в ячейках по умолчанию: **по левому краю**.
  - Допускается **выравнивание по центру** для заголовков столбцов/строк при необходимости.
- Подпись к таблице:
  - Формат: **`Таблица X – Название`**.
  - Шрифт: **Times New Roman, 12 pt**.
  - Выравнивание: **по левому краю**.
  - Интервалы до/после: **0 pt**.
  - Межстрочный интервал: **1,5**.
- Текст после таблицы:
  - Интервал перед первым абзацем: **6 pt**.
- Запреты и особенности:
  - Таблица **не должна** содержать отдельную колонку «№ п/п».
  - Таблица **не должна** вставляться как изображение.
  - Таблица **обязана** иметь шапку.
  - Для таблиц, переходящих на следующую страницу:
    - На новой странице первая строка: **«Продолжение таблицы X»**;
    - Далее **повторяется шапка**.

**Проверки/подсветка**

- Таблица без шапки, с колонкой «№ п/п», либо оформленная как изображение → **error**.
- Отсутствие строки «Продолжение таблицы X» при переносе на новую страницу → **warning**.

### 3.6. Рисунки

**Обязательное при генерации**

- Выравнивание рисунка: **по центру страницы**.
- Подпись к рисунку:
  - Формат: **`Рисунок X – Название`**.
  - Шрифт: **Times New Roman, 12 pt**.
  - Межстрочный интервал: **1,5**.
  - Интервалы до/после: **0 pt**.
  - Выравнивание подписи: **по центру**.
- Рисунок не должен нарушать поля страницы (не «прижат» к краям).

**Проверки/подсветка**

- Отсутствие подписи или нарушение формата подписи → **error**.
- Раздел, заканчивающийся рисунком без поясняющего текста → **error**.

### 3.7. Список использованных источников и ссылки

**Обязательное при генерации**

- Ссылки в тексте оформляются как **`[1]`, `[2]`, …**.
- Каждая ссылка должна соответствовать записи в списке источников.
- Оформление списка источников:
  - Шрифт: **Times New Roman, 12 pt**.
  - Выравнивание: **по ширине**.
  - Первая строка: **1,25 см**.
  - Межстрочный интервал: **1,5**.
  - Интервалы до/после: **0 pt**.

**Проверки/подсветка**

- Ссылка в тексте без соответствующей записи в списке → **error**.

**Рекомендации**

- По методическим указаниям МИСИС год издания источников, как правило, **не должен превышать 5 лет**.
- Приложение не блокирует использование более старых источников, но:
  - помечает такие записи как **warning** при вводе/редактировании;
  - отображает предупреждение в панели ошибок/предупреждений;
  - ответственность за соблюдение 5‑летнего ограничения остаётся на пользователе.

### 3.8. Приложения

**Обязательное при генерации**

- Приложения нумеруются буквами русского алфавита: **А, Б, В, …**, без букв **Ё, З, Й, О, Ч, Ъ, Ы, Ь**.
- Заголовок приложения:
  - Формат: **«ПРИЛОЖЕНИЕ А»**, **капсом**, **полужирным**, **по центру**.
  - При наличии названия: **«ПРИЛОЖЕНИЕ А – Название»**.
- Нумерация элементов внутри приложений:
  - Рисунки: **«Рисунок А.1 – …»**, **«Рисунок А.2 – …»**.
  - Таблицы: **«Таблица А.1 – …»**, **«Таблица А.2 – …»**.
- В содержании приложения отображаются с указанием **буквы и названия**.

**Проверки/подсветка**

- Неверная буква (из запрещённого набора) или дубликат буквы → **error**.

### 3.9. Содержание (оглавление)

**Обязательное при генерации**

- Заголовок «СОДЕРЖАНИЕ»:
  - **ПРОПИСНЫМИ**, **полужирный**, **Times New Roman 12 pt**, **по центру**.
  - Интервал после: **24 pt**.
  - Межстрочный интервал: **1,5**.
- Если Word/TOC по умолчанию генерирует заголовок «Оглавление», приложение должно **заменять на «СОДЕРЖАНИЕ»** (через стили, Pandoc или пост‑обработку).
- Стили строк оглавления (TOC 1/2/3):
  - Шрифт: **Times New Roman, 12 pt**.
  - Межстрочный интервал: **1,5**.
  - Интервалы до/после: **0 pt**.
  - Отступы слева:
    - TOC 1: **0 см**,
    - TOC 2: **1,25 см**,
    - TOC 3: **2,5 см**.

**Проверки/подсветка**

- Заголовок «Оглавление» вместо «СОДЕРЖАНИЕ» → **error**.

### 3.10. Ограничения по scope (сознательно не реализуется на первом этапе)

- **Формулы**: автоматическое оформление, размещение и нумерация формул не реализуются. Пользователь оформляет формулы вручную в Word.
- **Антиплагиат**: проверка на антиплагиат и требования к проценту оригинальности полностью вне ответственности приложения.
- **Сложные нестандартные сценарии**:
  - сложные многоуровневые структуры таблиц/рисунков;
  - специфические требования кафедр или индивидуальные шаблоны;
  - нестандартные приложения;
  Эти сценарии допускаются, но **не проверяются автоматически**.  
  Ответственность за соответствие ГОСТ/МИСИС в таких случаях лежит на пользователе.


End of REQUIREMENTS document.
