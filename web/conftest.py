"""pytest 的公共配置：解决 main.py 里 `import config` 找不到的问题。

main.py 在 web/ 目录，config.py 在项目根目录。
pytest 运行时会先加载本文件，把项目根目录加进 sys.path，
这样测试文件里 `import main` 才能成功。
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # study-log/
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
