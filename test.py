from script_hardfloat_ieee import RecFNtoIEEE, RecFNtoIEEE_s2i

def test_f32_nan():
    payload = 0x1337
    recf32_nan = ((7 << 6) << 23) | payload
    ieeef32_nan = (255 << 23) | payload
    assert RecFNtoIEEE(recf32_nan, size=32) == ieeef32_nan
    assert RecFNtoIEEE_s2i(hex(recf32_nan), size=32) == ieeef32_nan

def test_f64_nan():
    payload = 0x1337
    recf64_nan = ((7 << 9) << 52) | payload
    ieeef64_nan = (2047 << 52) | payload
    assert RecFNtoIEEE(recf64_nan, size=64) == ieeef64_nan
    assert RecFNtoIEEE_s2i(hex(recf64_nan), size=64) == ieeef64_nan

def test_f32_inf():
    recf32_inf = ((6 << 6) << 23)
    ieeef32_inf = (255 << 23)
    assert RecFNtoIEEE(recf32_inf, size=32) == ieeef32_inf
    assert RecFNtoIEEE_s2i(hex(recf32_inf), size=32) == ieeef32_inf

def test_f64_inf():
    recf64_inf = ((6 << 9) << 52)
    ieeef64_inf = (2047 << 52)
    assert RecFNtoIEEE(recf64_inf, size=64) == ieeef64_inf
    assert RecFNtoIEEE_s2i(hex(recf64_inf), size=64) == ieeef64_inf

if __name__ == "__main__":
    # to run when no suitable verison of pytest is available
    test_f32_nan()
    test_f64_nan()

    test_f32_inf()
    test_f64_inf()
