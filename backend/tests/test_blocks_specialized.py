from app.models.report import (
    AppendixBlock,
    FigureBlock,
    ListBlock,
    ReferencesBlock,
    ReportBlockType,
    SectionBlock,
    SubsectionBlock,
    TableBlock,
    TextBlock,
)


def test_section_block_basic():
    block = SectionBlock(
        title="ВВЕДЕНИЕ",
        special_kind="INTRO",
    )

    assert block.type is ReportBlockType.SECTION
    assert block.title == "ВВЕДЕНИЕ"
    assert block.special_kind == "INTRO"
    assert block.children == []


def test_subsection_block_basic():
    block = SubsectionBlock(
        level=2,
        title="1.1 Подраздел",
    )

    assert block.type is ReportBlockType.SUBSECTION
    assert block.level == 2
    assert block.title.startswith("1.1")


def test_text_block_basic():
    block = TextBlock(
        text="Это простой текстовый блок.",
    )

    assert block.type is ReportBlockType.TEXT
    assert "текстовый блок" in block.text


def test_list_block_basic():
    block = ListBlock(
        list_type="numbered",
        items=["Раз", "Два", "Три"],
    )

    assert block.type is ReportBlockType.LIST
    assert block.list_type == "numbered"
    assert block.items == ["Раз", "Два", "Три"]


def test_table_block_basic():
    block = TableBlock(
        caption="Таблица 1 – Пример",
        rows=[
            ["Колонка 1", "Колонка 2"],
            ["1", "2"],
        ],
    )

    assert block.type is ReportBlockType.TABLE
    assert block.caption.startswith("Таблица 1")
    assert len(block.rows) == 2
    assert block.rows[0][0] == "Колонка 1"


def test_figure_block_basic():
    block = FigureBlock(
        caption="Рисунок 1 – Схема",
        file_name="figure1.png",
    )

    assert block.type is ReportBlockType.FIGURE
    assert block.caption.startswith("Рисунок 1")
    assert block.file_name.endswith(".png")


def test_references_block_basic():
    block = ReferencesBlock(
        items=[
            "ГОСТ 7.0.5-2008",
            "Методические указания НИТУ МИСИС, 2024.",
        ],
    )

    assert block.type is ReportBlockType.REFERENCES
    assert len(block.items) == 2


def test_appendix_block_basic():
    child = TextBlock(text="Содержимое приложения.")
    block = AppendixBlock(
        label="А",
        title="Дополнительные материалы",
        children=[child],
    )

    assert block.type is ReportBlockType.APPENDIX
    assert block.label == "А"
    assert block.title.startswith("Дополнительные")
    assert len(block.children) == 1
    assert isinstance(block.children[0], TextBlock)


def test_block_roundtrip_serialization():
    block = SectionBlock(
        title="ЗАКЛЮЧЕНИЕ",
        special_kind="CONCLUSION",
        children=[
            TextBlock(text="Тут делаются выводы."),
        ],
    )

    data = block.model_dump()
    restored = SectionBlock(**data)

    assert restored.title == "ЗАКЛЮЧЕНИЕ"
    assert restored.special_kind == "CONCLUSION"
    assert len(restored.children) == 1
    assert restored.children[0].type == ReportBlockType.TEXT
