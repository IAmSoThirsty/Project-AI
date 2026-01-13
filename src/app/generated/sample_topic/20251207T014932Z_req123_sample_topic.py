# Test-first style: include a companion test stub

def impl_sample_topic():
    # implementation goes here
    return True

# companion test (to be moved to tests/ by integrator)
def test_impl_sample_topic():
    assert impl_sample_topic() is True
