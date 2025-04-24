import pytest
import pandas as pd
from utils.coin_utils import get_coin_choices, get_price_history

def test_get_coin_choices():
    choices = get_coin_choices()
    assert isinstance(choices, dict)
    assert len(choices) > 0
    for k, v in choices.items():
        assert isinstance(k, str)
        assert isinstance(v, str)
        assert '(' in v and ')' in v  # Should be 'Name (SYMBOL)'

def test_get_price_history():
    choices = get_coin_choices()
    asset_id = next(iter(choices.keys()))
    df = get_price_history(asset_id, days=10)
    assert isinstance(df, pd.DataFrame) or df is None
    # If DataFrame, check for expected columns
    if isinstance(df, pd.DataFrame):
        assert 'date' in df.columns or df.shape[1] > 0
