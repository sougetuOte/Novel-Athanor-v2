"""セットアップ確認用のサンプルテスト."""


def test_sample() -> None:
    """セットアップ確認用のサンプルテスト."""
    assert 1 + 1 == 2


def test_import_src() -> None:
    """src パッケージがインポートできることを確認."""
    import src

    assert src.__version__ == "0.1.0"
