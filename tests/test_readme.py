"""The examples in README.md must actually run and give the numbers shown."""

import doctest
import re
from pathlib import Path

README = (Path(__file__).parent.parent / "README.md").read_text(encoding="utf-8")


def test_readme_python_examples():
    blocks = re.findall(r"```python\n(.*?)```", README, re.S)
    assert blocks, "README should contain python examples"
    parser, runner = doctest.DocTestParser(), doctest.DocTestRunner(optionflags=doctest.ELLIPSIS)
    for i, block in enumerate(blocks):
        runner.run(parser.get_doctest(block, {}, f"README[{i}]", "README.md", 0))
    assert runner.failures == 0


def test_package_docstring_example():
    import lk_tax

    assert doctest.testmod(lk_tax).failed == 0
