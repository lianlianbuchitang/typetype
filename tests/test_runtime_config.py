import os
import subprocess
import sys
from pathlib import Path

from src.backend.models.dto.text_catalog_item import TextCatalogItem
from src.backend.config.runtime_config import RuntimeConfig


def test_runtime_config_from_dict_builds_sources_and_default_key():
    runtime_config = RuntimeConfig._from_dict(
        {
            "base_url": "https://example.com",
            "api_timeout": 12.5,
            "default_text_source_key": "remote",
            "text_sources": {
                "local": {
                    "label": "本地示例",
                    "local_path": "resources/texts/demo.txt",
                },
                "remote": {
                    "label": "远程示例",
                    "text_id": "remote-id",
                    "has_ranking": True,
                },
            },
        }
    )

    assert runtime_config.base_url == "https://example.com"
    assert runtime_config.api_timeout == 12.5
    assert runtime_config.default_text_source_key == "remote"

    local_source = runtime_config.get_text_source("local")
    assert local_source is not None
    assert local_source.label == "本地示例"
    assert local_source.local_path == "resources/texts/demo.txt"

    remote_source = runtime_config.get_text_source("remote")
    assert remote_source is not None
    assert remote_source.text_id == "remote-id"
    assert remote_source.has_ranking is True


def test_runtime_config_source_options_include_catalog_items():
    runtime_config = RuntimeConfig._from_dict(
        {
            "default_text_source_key": "builtin_demo",
            "text_sources": {
                "builtin_demo": {
                    "label": "内置示例",
                    "local_path": "resources/texts/builtin_demo.txt",
                }
            },
        }
    )

    runtime_config.update_catalog(
        [
            TextCatalogItem(
                text_id="cloud_001",
                label="云端文章",
                description="每日推荐",
                has_ranking=False,
            )
        ]
    )

    assert runtime_config.get_text_source_options() == [
        {"key": "builtin_demo", "label": "内置示例"},
        {"key": "cloud_001", "label": "云端文章"},
    ]


def test_backend_config_modules_import_with_src_only_pythonpath(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    isolated_home = tmp_path / "home"
    isolated_home.mkdir()

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from backend.config.runtime_config import RuntimeConfig; "
                "from backend.config.text_source_config import TextSourceEntry; "
                "from backend.models.dto.text_catalog_item import TextCatalogItem"
            ),
        ],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env={
            **os.environ,
            "PYTHONPATH": str(repo_root / "src"),
            "HOME": str(isolated_home),
        },
        check=False,
    )

    assert result.returncode == 0, result.stderr
