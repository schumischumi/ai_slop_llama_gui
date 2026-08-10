import pytest

from llama_gui.parser import HelpParser


def test_help_parser_basic():
    parser = HelpParser()
    help_text = """
    ----- common params -----
    -t, --threads N (default: 8)
    --cpu-strict
    --no-cpu-strict
    --model <model_name>
    --choices [a|b|c]
    --flag-only
    """
    groups = parser.parse(help_text)
    assert len(groups) == 1
    group = groups[0]
    assert group.name == "common_params"
    assert len(group.params) == 5
    
    # Check threads (int)
    threads = next(p for p in group.params if p.long_name == "threads")
    assert threads.param_type == "int"
    assert threads.default == "8"
    assert threads.has_value is True

    # Check cpu-strict (bool)
    cpu_strict = next(p for p in group.params if p.long_name == "cpu-strict")
    assert cpu_strict.param_type == "bool"
    assert cpu_strict.has_value is False

    # Check model (string)
    model = next(p for p in group.params if p.long_name == "model")
    assert model.param_type == "string"
    assert model.has_value is True

    # Check choices (choice)
    choices = next(p for p in group.params if p.long_name == "choices")
    assert choices.param_type == "choice"
    assert choices.choices == ["a", "b", "c"]

    # Check flag-only (flag)
    flag = next(p for p in group.params if p.long_name == "flag-only")
    assert flag.param_type == "flag"
    assert flag.has_value is False

if __name__ == "__main__":
    # Manual run
    import sys
    sys.exit(pytest.main([__file__]))
