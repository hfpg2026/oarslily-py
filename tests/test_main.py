def test_feature_one():
    assert feature_one() == expected_output_one

def test_feature_two():
    assert feature_two() == expected_output_two

def test_feature_three():
    assert feature_three() == expected_output_three

def test_edge_case():
    assert edge_case_function() == expected_edge_case_output

def test_error_handling():
    with pytest.raises(ExpectedException):
        error_handling_function()

[pytest]
testpaths = tests
addopts = -v --tb=short