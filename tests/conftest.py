import matplotlib.pyplot as plt
import pytest

import scifig as sf


@pytest.fixture(autouse=True)
def _style():
    sf.apply_style()
    yield
    plt.close("all")
