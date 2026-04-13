"""上传文本适配层。"""

import json
import os
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal, Slot

from ...utils.logger import log_info, log_warning

if TYPE_CHECKING:
    from ...integration.text_uploader import TextUploader

# 本地文本写入路径与配置文件路径
LOCAL_TEXTS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "..",
    "..",
    "..",
    "resources",
    "texts",
)
CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "..",
    "..",
    "..",
    "config",
    "config.json",
)


class UploadTextAdapter(QObject):
    """上传文本 Qt 适配层。

    职责：
    - 本地写入文本文件并更新 config.json 的 text_sources 配置
    - 调用 TextUploader 上传到云端
    - 信号通知上传结果
    """

    uploadFinished = Signal(bool, str)

    def __init__(
        self,
        text_uploader: "TextUploader",
        texts_dir: str | None = None,
        config_path: str | None = None,
    ):
        super().__init__()
        self._text_uploader = text_uploader
        self._texts_dir = os.path.abspath(texts_dir or LOCAL_TEXTS_DIR)
        self._config_path = os.path.abspath(config_path or CONFIG_PATH)

    @Slot(str, str, str)
    def upload_to_local(self, title: str, content: str, source_key: str) -> None:
        """写文件到本地并更新 config.json 的 text_sources 配置。"""
        try:
            os.makedirs(self._texts_dir, exist_ok=True)
            safe_title = title.replace("/", "_").replace("\\", "_")
            filename = f"{source_key}_{safe_title}.txt"
            file_path = os.path.join(self._texts_dir, filename)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            self._update_config(source_key, title, filename)

            log_info(f"[UploadTextAdapter] 本地保存成功: {file_path}")
            self.uploadFinished.emit(True, f"文本已保存到本地: {filename}")
        except Exception as e:
            log_warning(f"[UploadTextAdapter] 本地保存失败: {e}")
            self.uploadFinished.emit(False, f"本地保存失败: {e}")

    @Slot(str, str, str)
    def upload_to_cloud(self, title: str, content: str, source_key: str) -> None:
        """调用 TextUploader 上传到云端。"""
        try:
            result_id = self._text_uploader.upload(content, title, source_key)
            if result_id is not None:
                log_info(f"[UploadTextAdapter] 云端上传成功: id={result_id}")
                self.uploadFinished.emit(True, f"文本上传成功，ID: {result_id}")
            else:
                self.uploadFinished.emit(False, "上传失败：服务器未返回有效ID")
        except Exception as e:
            log_warning(f"[UploadTextAdapter] 云端上传异常: {e}")
            self.uploadFinished.emit(False, f"上传失败: {e}")

    def _update_config(self, source_key: str, title: str, filename: str) -> None:
        """更新 config.json 的 text_sources 配置。"""
        config_data = self._load_config_data()

        text_sources = config_data.get("text_sources", {})
        text_sources[source_key] = {
            "label": title,
            "local_path": f"resources/texts/{filename}",
        }
        config_data["text_sources"] = text_sources

        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)

        log_info(f"[UploadTextAdapter] config.json 已更新: source_key={source_key}")

    def _load_config_data(self) -> dict:
        """加载 config.json，若不存在则返回空字典。"""
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                log_warning("[UploadTextAdapter] config.json 读取失败，使用空配置")
        return {}
