from src.services.calculator import AuraCalculatorService

def test_calculator():
    calc = AuraCalculatorService()
    res = calc.calculate(100, 80.0, 1, 2)
    assert "aura_score" in res
    assert res["aura_score"] <= 10000
    assert res["aura_score"] >= -5000
