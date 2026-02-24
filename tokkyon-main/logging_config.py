"""
ロギング設定
"""
import logging
import os
import sys
from pathlib import Path
from datetime import datetime


def setup_logging():
    """アプリケーションロギングを設定"""

    # フォーマッター
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # コンソールハンドラー（常に有効）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # ルートロガー設定
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)

    # ファイルハンドラー（ローカル開発時のみ）
    if os.getenv("RAILWAY_ENVIRONMENT") is None:
        try:
            log_dir = Path(__file__).parent / "logs"
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / f"tokkyon_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception:
            pass

    # uvicornのログレベル調整
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return logging.getLogger("tokkyon")


# アプリケーションロガー
logger = setup_logging()
