from app.models.report import BaseBlock, ReportBlockType


def test_base_block_creation_defaults():
    block = BaseBlock(type=ReportBlockType.TEXT)

    assert block.id is not None
    assert isinstance(block.id.int, int)
    assert block.type is ReportBlockType.TEXT
    assert block.children == []


def test_base_block_with_children():
    child = BaseBlock(type=ReportBlockType.TEXT)
    parent = BaseBlock(type=ReportBlockType.SECTION, children=[child])

    assert len(parent.children) == 1
    assert parent.children[0].id == child.id
    assert parent.children[0].type == ReportBlockType.TEXT


def test_base_block_serialization_roundtrip():
    child = BaseBlock(type=ReportBlockType.TEXT)
    parent = BaseBlock(type=ReportBlockType.SECTION, children=[child])

    data = parent.model_dump()
    restored = BaseBlock(**data)

    assert restored.type == ReportBlockType.SECTION
    assert len(restored.children) == 1
    assert restored.children[0].type == ReportBlockType.TEXT
