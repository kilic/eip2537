'''
This script generates EIP2537 test vectors.
Notice that test vectors generated with this script does not target
underlying mathematical properties of BLS12-381 curve. Instead It is
mostly targeting a few expected results, parsing errors and error propagation.
Prints of vectors follows Go syntax.
'''

from py_ecc.bls12_381 import G1, G2, add, multiply, FQ, FQ2, Z1 as INFINITY1, Z1 as INFINITY2, curve_order, is_on_curve, b, b2, field_modulus

# encoded g1 point at infility
infinity_g1_encoded = 2 * ["{0:0{1}x}".format(0, 128)]

# encoded g2 point at infility
infinity_g2_encoded = 4 * ["{0:0{1}x}".format(0, 128)]

# zeros
ZERO48 = "{0:0{1}x}".format(0, 96)
ZERO64 = "{0:0{1}x}".format(0, 128)
ZERO96 = "{0:0{1}x}".format(0, 192)
ZERO128 = "{0:0{1}x}".format(0, 256)
ZERO256 = "{0:0{1}x}".format(0, 512)


# return invalid g1 point
def g1_point_is_not_on_curve():
  p = (
      FQ(1),
      FQ(1),
  )
  assert is_on_curve(p, b) is False
  return p


# return invalid g2 point
def g2_point_is_not_on_curve():
  p = (
      FQ2([1, 1]),
      FQ2([1, 1]),
  )
  assert is_on_curve(p, b2) is False
  return p


# return invalid field element that larger than modulus
def invalid_field_element():
  return field_modulus + 1


# return field order
def modulus():
  return field_modulus


#
'''

Expected Errors 
'errBLS12381_XXX_'

'''

# msg : "invalid input length"
ERROR_INVALID_INPUT_LENGHT = "errBLS12381InvalidInputLength"
# msg : "invalid field element top bytes"
ERROR_FIELD_ELEMENT_TOP_BYTES = "errBLS12381InvalidFieldElementTopBytes"
# msg : "invalid field element"
ERROR_INVALID_FIELD_ELEMENT = "errBLS12381InvalidFieldElement"
# msg : "point is not on curve"
POINT_G1_IS_NOT_ON_CURVE = "errBLS12381G1PointIsNotOnCurve"
# msg : "point is not on curve"
POINT_G2_IS_NOT_ON_CURVE = "errBLS12381G2PointIsNotOnCurve"

#
'''

Utilities

'''


# given list of strings ["a", "b", "c"] returns "a" + "b" + "c"
def concat_list(entries):
  res = ""
  for i, s in enumerate(entries):
    res += "\"{}\"".format(s)
    if i + 1 != len(entries):
      res += " +\n"
  return res


# encode 32 bytes scalar
def encode_scalar(e):
  return str("{0:0{1}x}".format(e, 64))


# encode 48 bytes field to element to 64 bytes
def encode_field_element(fe):
  padded = "{0:0{1}x}"
  if hasattr(fe, 'n'):
    return padded.format(fe.n, 128)
  return padded.format(fe, 128)


# encodes field elements into larger byte string than expected
def bad_encode_field_element_large(fe):
  padded = "{0:0{1}x}"
  if hasattr(fe, 'n'):
    return padded.format(fe.n, 130)
  return padded.format(fe, 130)


# encodes field elements into shorter byte string than expected
def bad_encode_field_element_short(fe):
  padded = "{0:0{1}x}"
  if hasattr(fe, 'n'):
    return padded.format(fe.n, 126)
  return padded.format(fe, 126)


# # encodes field element violating zero top bytes (top 16 bytes must be zeros)
# def bad_encode_field_element_top_bytes(fe):
#   return "{2:0{3}x}{0:0{1}x}".format(10, 96, 1, 32)


# encodes field element violating zero top bytes (top 16 bytes must be zeros)
def bad_encode_field_element_top_bytes(fe):
  padded = "{2:0{3}x}{0:0{1}x}"
  if fe is None:
    return padded.format(0, 96, 1, 32)
  return padded.format(fe.n, 96, 1, 32)


# encodes an invalid field element (that is larger than modulus)
def bad_encode_invalid_field_element():
  return encode_field_element(invalid_field_element())


# encodes 48 * 2 bytse g1 point to 256 bytes
def encode_g1_point(point):
  if point is INFINITY1:
    return infinity_g1_encoded
  x = encode_field_element(point[0])
  y = encode_field_element(point[1])
  return [x, y]


# encodes g1 point into larger byte string than expected
def bad_encode_g1_point_large(point):
  x = encode_field_element(point[0])
  y = bad_encode_field_element_large(point[1])
  return [x, y]


# encodes g1 point into shorter byte string than expected
def bad_encode_g1_point_short(point):
  x = encode_field_element(point[0])
  y = bad_encode_field_element_short(point[1])
  return [x, y]


# encodes g1 point with invalid field element
# note that this migth also violate the curve equation
def bad_encode_g1_point_invalid_field_element():
  x = ZERO64
  y = bad_encode_invalid_field_element()
  return [x, y]


# encodes g1 point violating field element zero top bytes
def bad_encode_g1_point_top_bytes(point):
  x = encode_field_element(point[0])
  y = bad_encode_field_element_top_bytes(point[1])
  return [x, y]


# encodes g1 point and scalar value pair into 128 + 32 bytes
def encode_g1_point_scalar_pair(p, e):
  return encode_g1_point(p) + [encode_scalar(e)]


# encodes g1 point and scalar value pair into shorher byte string than expected
def bad_encode_g1_point_scalar_pair_short(p, e):
  return bad_encode_g1_point_short(p) + [encode_scalar(e)]


# encodes g1 point and scalar value pair into larger byte string than expected
def bad_encode_g1_point_scalar_pair_large(p, e):
  return bad_encode_g1_point_large(p) + [encode_scalar(e)]


# encodes g1 point and scalar value pair violating zero top bytes of a field element
def bad_encode_g1_point_scalar_pair_top_bytes(p, e):
  return bad_encode_g1_point_top_bytes(p) + [encode_scalar(e)]


# encodes g1 point and scalar value pair with invalid field element
def bad_encode_g1_point_scalar_pair_invalid_field_element(e):
  return bad_encode_g1_point_invalid_field_element() + [encode_scalar(e)]


# encodes a g1 point that does not satisfy curve equation
def encode_g1_point_not_on_curve():
  return encode_g1_point(g1_point_is_not_on_curve())


# encodes a g2 point into 4 * 64 bytes
def encode_g2_point(point):
  if point is INFINITY2:
    return infinity_g2_encoded
  x0 = encode_field_element(point[0].coeffs[1])
  x1 = encode_field_element(point[0].coeffs[0])
  y0 = encode_field_element(point[1].coeffs[1])
  y1 = encode_field_element(point[1].coeffs[0])
  return [x0, x1, y0, y1]


# encodes g2 point into larger byte string than expected
def bad_encode_g2_point_large(point):
  x0 = encode_field_element(point[0].coeffs[1])
  x1 = encode_field_element(point[0].coeffs[0])
  y0 = encode_field_element(point[1].coeffs[1])
  y1 = bad_encode_field_element_large(point[1].coeffs[0])
  return [x0, x1, y0, y1]


# encodes g2 point into shorter byte string than expected
def bad_encode_g2_point_short(point):
  x0 = encode_field_element(point[0].coeffs[1])
  x1 = encode_field_element(point[0].coeffs[0])
  y0 = encode_field_element(point[1].coeffs[1])
  y1 = bad_encode_field_element_short(point[1].coeffs[0])
  return [x0, x1, y0, y1]


# encodes g2 point violating field element zero top bytes
def bad_encode_g2_point_invalid_field_element(point):
  x0 = encode_field_element(point[0].coeffs[1])
  x1 = encode_field_element(point[0].coeffs[0])
  y0 = encode_field_element(point[1].coeffs[1])
  y1 = bad_encode_invalid_field_element()
  return [x0, x1, y0, y1]


# encodes g2 point violating field element zero top bytes
def bad_encode_g2_point_top_bytes(point):
  x0 = encode_field_element(point[0].coeffs[1])
  x1 = encode_field_element(point[0].coeffs[0])
  y0 = encode_field_element(point[1].coeffs[1])
  y1 = bad_encode_field_element_top_bytes(point[1].coeffs[0])
  return [x0, x1, y0, y1]


# encodes g2 point and scalar value pair into 256 + 32 bytes
def encode_g2_point_scalar_pair(p, e):
  return encode_g2_point(p) + [encode_scalar(e)]


# encodes g2 point and scalar value pair into shorher byte string than expected
def bad_encode_g2_point_scalar_pair_short(p, e):
  return bad_encode_g2_point_short(p) + [encode_scalar(e)]


# encodes g2 point and scalar value pair into larger byte string than expected
def bad_encode_g2_point_scalar_pair_large(p, e):
  return bad_encode_g2_point_large(p) + [encode_scalar(e)]


# encodes g2 point and scalar value pair violating zero top bytes of a field element
def bad_encode_g2_point_scalar_pair_top_bytes(p, e):
  return bad_encode_g2_point_top_bytes(p) + [encode_scalar(e)]


# encodes g2 point and scalar value pair with invalid field element
def bad_encode_g1_point_scalar_pair_invalid_field_element(e):
  return bad_encode_g2_point_invalid_field_element() + [encode_scalar(e)]


# encodes a g2 point that does not satisfy curve equation
def encode_g2_point_not_on_curve():
  return encode_g2_point(g2_point_is_not_on_curve())


def make_vector(inputs, expecteds, name):
  return "{{\ninput:\n{},\nexpected:\n{},\nname: \"{}\",\n}},".format(
      concat_list(inputs), concat_list(expecteds), name)


def make_fail_vector(inputs, error, name):
  return "{{\ninput:\n{},\nexpectedError: {},\nname: \"{}\",\n}},".format(
      concat_list(inputs), error, name)


'''

Generate Tests

'''


# generates G1ADD happy case tests
def gen_G1ADD_tests():
  vectors = []

  # 1
  # G1 + G1 == 2 * G1
  name = "bls_g1add_(g1+g1=2*g1)"
  a = G1
  b = G1
  r = add(a, b)
  inputs = encode_g1_point(a) + encode_g1_point(b)
  expected = encode_g1_point(r)
  vectors.append(make_vector(inputs, expected, name))

  # 2
  # 3 * G1 + 2 * G1 == 5 * G1
  name = "bls_g1add_(2*g1+3*g1=5*g1)"
  a = multiply(G1, 2)
  b = multiply(G1, 3)
  r = add(a, b)
  inputs = encode_g1_point(a) + encode_g1_point(b)
  expected = encode_g1_point(r)
  vectors.append(make_vector(inputs, expected, name))

  # 3
  # inf + G1 == G1
  name = "bls_g1add_(inf+g1=g1)"
  inputs = encode_g1_point(G1) + encode_g1_point(INFINITY1)
  expected = encode_g1_point(G1)
  vectors.append(make_vector(inputs, expected, name))

  # 4
  # inf + inf == inf
  name = "bls_g1add_(inf+inf=inf)"
  inputs = encode_g1_point(INFINITY1) + encode_g1_point(INFINITY1)
  expected = encode_g1_point(INFINITY1)
  vectors.append(make_vector(inputs, expected, name))

  print("---------\nG1ADD\n---------\n")
  for v in vectors:
    print(v)

  return


# generates G1ADD failure tests
def gen_G1ADD_fail_tests():
  vectors = []

  # 1
  # Empty input
  name = "bls_g1add_empty_input"
  inputs = ['']
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 1
  # Short input
  name = "bls_g1add_short_input"
  inputs = bad_encode_g1_point_short(G1) + encode_g1_point(G1)
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 2
  # Large input
  name = "bls_g1add_large_input"
  inputs = bad_encode_g1_point_large(G1) + encode_g1_point(G1)
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 3
  # Violate top bytes
  name = "bls_g1add_violate_top_bytes"
  inputs = bad_encode_g1_point_top_bytes(G1) + encode_g1_point(G1)
  error = ERROR_FIELD_ELEMENT_TOP_BYTES
  vectors.append(make_fail_vector(inputs, error, name))

  # 4
  # Invalid field element
  name = "bls_g1add_invalid_field_element"
  inputs = bad_encode_g1_point_invalid_field_element() + encode_g1_point(G1)
  error = ERROR_INVALID_FIELD_ELEMENT
  vectors.append(make_fail_vector(inputs, error, name))

  # 5
  # Point is not on curve
  name = "bls_g1add_point_not_on_curve"
  inputs = encode_g1_point_not_on_curve() + encode_g1_point(G1)
  error = POINT_G1_IS_NOT_ON_CURVE
  vectors.append(make_fail_vector(inputs, error, name))

  print("---------\nG1ADD Failure\n---------\n")
  for v in vectors:
    print(v)

  return


# generates G1MUL happy case tests
def gen_G1MUL_tests():
  vectors = []

  # 1
  # 0 * G1 == inf
  name = "bls_g1mul_(0*g1=inf)"
  a = G1
  e = 0
  r = multiply(a, e)
  inputs = encode_g1_point_scalar_pair(a, e)
  expected = encode_g1_point(r)
  vectors.append(make_vector(inputs, expected, name))

  # 2
  # x * inf == inf
  name = "bls_g1mul_(x*inf=inf)"
  e = 17
  inputs = encode_g1_point_scalar_pair(INFINITY1, e)
  expected = encode_g1_point(INFINITY1)
  vectors.append(make_vector(inputs, expected, name))

  # 3
  # 1 * G1 == G1
  name = "bls_g1mul_(1*g1=g1)"
  a = G1
  e = 0
  r = multiply(a, e)
  inputs = encode_g1_point_scalar_pair(a, e)
  expected = encode_g1_point(r)
  vectors.append(make_vector(inputs, expected, name))

  # 4
  # 17 * G1
  name = "bls_g1mul_(17*g1)"
  a = G1
  e = 17
  r = multiply(a, e)
  inputs = encode_g1_point_scalar_pair(a, e)
  expected = encode_g1_point(r)
  vectors.append(make_vector(inputs, expected, name))

  print("---------\nG1MUL\n---------\n")
  for v in vectors:
    print(v)

  return


# generates G1MUL failure tests
def gen_G1MUL_fail_tests():
  vectors = []

  # 1
  # Empty input
  name = "bls_g1mul_empty_input"
  inputs = ['']
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 1
  # Short input
  name = "bls_g1mul_short_input"
  inputs = bad_encode_g1_point_scalar_pair_short(G1, 1)
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 2
  # Large input
  name = "bls_g1mul_large_input"
  inputs = bad_encode_g1_point_scalar_pair_large(G1, 1)
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 3
  # Violate top bytes
  name = "bls_g1mul_violate_top_bytes"
  inputs = bad_encode_g1_point_scalar_pair_top_bytes(G1, 1)
  error = ERROR_FIELD_ELEMENT_TOP_BYTES
  vectors.append(make_fail_vector(inputs, error, name))

  # 4
  # Invalid field element
  name = "bls_g1mul_invalid_field_element"
  inputs = bad_encode_g1_point_invalid_field_element()
  error = ERROR_INVALID_FIELD_ELEMENT
  vectors.append(make_fail_vector(inputs, error, name))

  # 5
  # Point is not on curve
  name = "bls_g1mul_point_not_on_curve"
  inputs = encode_g1_point_scalar_pair(g1_point_is_not_on_curve(), 1)
  error = POINT_G1_IS_NOT_ON_CURVE
  vectors.append(make_fail_vector(inputs, error, name))

  print("---------\nG1MUL Failure\n---------\n")
  for v in vectors:
    print(v)

  return


# generates G1MUL happy case tests
def gen_G1MULTIEXP_tests():
  vectors = []

  # 1
  # Single pair
  name = "bls_g1multiexp_single"
  a = G1
  e = 17
  r = multiply(a, e)
  inputs = encode_g1_point_scalar_pair(a, e)
  expected = encode_g1_point(r)
  vectors.append(make_vector(inputs, expected, name))

  # 1
  # Multiple pairs
  name = "bls_g1multiexp_multiple"
  bases = [G1, multiply(G1, 1001), multiply(G1, 1002)]
  scalars = [50, 51, 52]
  acc_result = INFINITY1
  acc_input = []
  for p, e in zip(bases, scalars):
    acc_result = add(multiply(p, e), acc_result)
    acc_input = acc_input + encode_g1_point_scalar_pair(p, e)
  print(acc_input)
  inputs = acc_input
  expected = encode_g1_point(acc_result)
  vectors.append(make_vector(inputs, expected, name))

  # 2
  # Larger set
  name = "bls_g1multiexp_larger"
  N, b, ez = 25, 1, 91
  e = ez
  acc_result = INFINITY1
  acc_input = []
  for _ in range(N):
    base = multiply(G1, b)
    acc_result = add(multiply(base, e), acc_result)
    acc_input = acc_input + encode_g1_point_scalar_pair(base, e)
    e = (e * ez) % curve_order
    b += 1
  inputs = acc_input
  expected = encode_g1_point(acc_result)
  vectors.append(make_vector(inputs, expected, name))

  print("---------\nG1MULTIEXP\n---------\n")
  for v in vectors:
    print(v)

  return


# generates G1MUL fail tests
def gen_G1MULTIEXP_fail_tests():
  vectors = []

  # 1
  # Empty input
  name = "bls_g1multiexp_empty_input"
  inputs = ['']
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 1
  # Short input
  name = "bls_g1multiexp_short_input"
  inputs = bad_encode_g1_point_scalar_pair_short(G1, 1)
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 2
  # Large input
  name = "bls_g1multiexp_large_input"
  inputs = bad_encode_g1_point_scalar_pair_large(G1, 1)
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 3
  # Invalid field element
  name = "bls_g1multiexp_invalid_field_element"
  inputs = bad_encode_g1_point_invalid_field_element()
  error = ERROR_INVALID_FIELD_ELEMENT
  vectors.append(make_fail_vector(inputs, error, name))

  # 4
  # Violate top bytes
  name = "bls_g1multiexp_violate_top_bytes"
  inputs = bad_encode_g1_point_scalar_pair_top_bytes(G1, 1)
  error = ERROR_FIELD_ELEMENT_TOP_BYTES
  vectors.append(make_fail_vector(inputs, error, name))

  # 5
  # Point is not on curve
  name = "bls_g1multiexp_point_not_on_curve"
  inputs = encode_g1_point_scalar_pair(g1_point_is_not_on_curve(), 1)
  error = POINT_G1_IS_NOT_ON_CURVE
  vectors.append(make_fail_vector(inputs, error, name))

  print("---------\nG1MULTIEXP Failure\n---------\n")
  for v in vectors:
    print(v)

  return


# generates G2ADD happy case tests
def gen_G2ADD_tests():
  vectors = []

  # 1
  # G2 + G2 == 2 * G2
  name = "bls_g2add_(g2+g2=2*g2)"
  a = G2
  b = G2
  r = add(a, b)
  inputs = encode_g2_point(a) + encode_g2_point(b)
  expected = encode_g2_point(r)
  vectors.append(make_vector(inputs, expected, name))

  # 2
  # 2 * G2 + 3 * G2 = 5 * G2
  name = "bls_g2add_(2*g2+3*g2=5*g2)"
  a = multiply(G2, 2)
  b = multiply(G2, 3)
  r = add(a, b)
  inputs = encode_g2_point(a) + encode_g2_point(b)
  expected = encode_g2_point(r)
  vectors.append(make_vector(inputs, expected, name))

  # 3
  # inf + G2 == G2
  name = "bls_g2add_(inf+g2=g2)"
  inputs = encode_g2_point(G2) + encode_g2_point(INFINITY2)
  expected = encode_g2_point(G2)
  vectors.append(make_vector(inputs, expected, name))

  # 4
  # inf + inf == inf
  name = "bls_g2add_(inf+inf=inf)"
  inputs = encode_g2_point(INFINITY2) + encode_g2_point(INFINITY2)
  expected = encode_g2_point(INFINITY2)
  vectors.append(make_vector(inputs, expected, name))

  print("---------\nG2ADD\n---------\n")
  for v in vectors:
    print(v)

  return


# generates G2ADD failure tests
def gen_G2ADD_fail_tests():
  vectors = []

  # 1
  # Empty input
  name = "bls_g2add_empty_input"
  inputs = ['']
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 1
  # Short input
  name = "bls_g2add_short_input"
  inputs = bad_encode_g2_point_short(G2) + encode_g2_point(G2)
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 2
  # Large input
  name = "bls_g2add_large_input"
  inputs = bad_encode_g2_point_large(G2) + encode_g2_point(G2)
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 3
  # Violate top bytes
  name = "bls_g2add_violate_top_bytes"
  inputs = bad_encode_g2_point_top_bytes(G2) + encode_g2_point(G2)
  error = ERROR_FIELD_ELEMENT_TOP_BYTES
  vectors.append(make_fail_vector(inputs, error, name))

  # 4
  # Invalid field element
  name = "bls_g2add_invalid_field_element"
  inputs = bad_encode_g2_point_invalid_field_element() + encode_g2_point(G2)
  error = ERROR_INVALID_FIELD_ELEMENT
  vectors.append(make_fail_vector(inputs, error, name))

  # 5
  # Point is not on curve
  name = "bls_g2add_point_not_on_curve"
  inputs = encode_g2_point_not_on_curve() + encode_g2_point(G2)
  error = POINT_G2_IS_NOT_ON_CURVE
  vectors.append(make_fail_vector(inputs, error, name))

  print("---------\nG2ADD Failure\n---------\n")
  for v in vectors:
    print(v)

  return


# generates G2MUL happy case tests
def gen_G2MUL_tests():
  vectors = []

  # 1
  # 0 * G2 == inf
  name = "bls_g2mul_(0*g2=inf)"
  a = G2
  e = 0
  r = multiply(a, e)
  inputs = encode_g2_point_scalar_pair(a, e)
  expected = encode_g2_point(r)
  vectors.append(make_vector(inputs, expected, name))

  # 2
  # x * inf == inf
  name = "bls_g2mul_(x*inf=inf)"
  e = 17
  inputs = encode_g2_point_scalar_pair(INFINITY2, e)
  expected = encode_g2_point(INFINITY2)
  vectors.append(make_vector(inputs, expected, name))

  # 3
  # 1 * G2 == G2
  name = "bls_g2mul_(1*g2=g2)"
  a = G2
  e = 0
  r = multiply(a, e)
  inputs = encode_g2_point_scalar_pair(a, e)
  expected = encode_g2_point(r)
  vectors.append(make_vector(inputs, expected, name))

  # 4
  # 17 * G2
  name = "bls_g2mul_(17*g2)"
  a = G2
  e = 17
  r = multiply(a, e)
  inputs = encode_g2_point_scalar_pair(a, e)
  expected = encode_g2_point(r)
  vectors.append(make_vector(inputs, expected, name))

  print("---------\nG2MUL\n---------\n")
  for v in vectors:
    print(v)

  return


# generates G2MUL failure tests
def gen_G2MUL_fail_tests():
  vectors = []

  # 1
  # Empty input
  name = "bls_g2mul_empty_input"
  inputs = ['']
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 1
  # Short input
  name = "bls_g2mul_short_input"
  inputs = bad_encode_g2_point_scalar_pair_short(G2, 1)
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 2
  # Large input
  name = "bls_g2mul_large_input"
  inputs = bad_encode_g2_point_scalar_pair_large(G2, 1)
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 3
  # Violate top bytes
  name = "bls_g2mul_violate_top_bytes"
  inputs = bad_encode_g2_point_scalar_pair_top_bytes(G2, 1)
  error = ERROR_FIELD_ELEMENT_TOP_BYTES
  vectors.append(make_fail_vector(inputs, error, name))

  # 4
  # Invalid field element
  name = "bls_g2mul_invalid_field_element"
  inputs = bad_encode_g2_point_invalid_field_element()
  error = ERROR_INVALID_FIELD_ELEMENT
  vectors.append(make_fail_vector(inputs, error, name))

  # 5
  # Point is not on curve
  name = "bls_g2mul_point_not_on_curve"
  inputs = encode_g2_point_scalar_pair(g2_point_is_not_on_curve(), 1)
  error = POINT_G2_IS_NOT_ON_CURVE
  vectors.append(make_fail_vector(inputs, error, name))

  print("---------\nG2MUL Failure\n---------\n")
  for v in vectors:
    print(v)

  return


# generates G2MULTIEXP happy case tests
def gen_G2MULTIEXP_tests():
  vectors = []

  # 1
  # Single pair
  name = "bls_g2multiexp_single"
  a = G2
  e = 17
  r = multiply(a, e)
  inputs = encode_g2_point_scalar_pair(a, e)
  expected = encode_g2_point(r)
  vectors.append(make_vector(inputs, expected, name))

  # 1
  # Multiple pairs
  name = "bls_g2multiexp_multiple"
  bases = [G2, multiply(G2, 1001), multiply(G2, 1002)]
  scalars = [50, 51, 52]
  acc_result = INFINITY2
  acc_input = []
  for p, e in zip(bases, scalars):
    x = multiply(p, e)
    acc_result = add(x, acc_result)
    acc_input = acc_input + encode_g2_point_scalar_pair(p, e)
  inputs = acc_input
  expected = encode_g2_point(acc_result)
  vectors.append(make_vector(inputs, expected, name))

  # 2
  # Larger set
  name = "bls_g2multiexp_larger"
  N, b, ez = 25, 1, 91
  e = ez
  acc_result = INFINITY2
  acc_input = []
  for _ in range(N):
    base = multiply(G2, b)
    acc_result = add(multiply(base, e), acc_result)
    acc_input = acc_input + encode_g2_point_scalar_pair(base, e)
    e = (e * ez) % curve_order
    b += 1
  inputs = acc_input
  expected = encode_g2_point(acc_result)
  vectors.append(make_vector(inputs, expected, name))

  print("---------\nG2MULTIEXP\n---------\n")
  for v in vectors:
    print(v)

  return


# generates G2MULTIEXP fail tests
def gen_G2MULTIEXP_fail_tests():
  vectors = []

  # 1
  # Empty input
  name = "bls_g2multiexp_empty_input"
  inputs = ['']
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 1
  # Short input
  name = "bls_g2multiexp_short_input"
  inputs = bad_encode_g2_point_scalar_pair_short(G2, 1)
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 2
  # Large input
  name = "bls_g2multiexp_large_input"
  inputs = bad_encode_g2_point_scalar_pair_large(G2, 1)
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 3
  # Violate top bytes
  name = "bls_g2multiexp_violate_top_bytes"
  inputs = bad_encode_g2_point_scalar_pair_top_bytes(G2, 1)
  error = ERROR_FIELD_ELEMENT_TOP_BYTES
  vectors.append(make_fail_vector(inputs, error, name))

  # 4
  # Invalid field element
  name = "bls_g2multiexp_invalid_field_element"
  inputs = bad_encode_g2_point_scalar_pair_large()
  error = ERROR_INVALID_FIELD_ELEMENT
  vectors.append(make_fail_vector(inputs, error, name))

  # 5
  # Point is not on curve
  name = "bls_g2multiexp_point_not_on_curve"
  inputs = encode_g2_point_scalar_pair(g2_point_is_not_on_curve(), 1)
  error = POINT_G2_IS_NOT_ON_CURVE
  vectors.append(make_fail_vector(inputs, error, name))

  print("---------\nG2MULTIEXP Failure\n---------\n")
  for v in vectors:
    print(v)

  return


# generates mapping to curve test vectors
# vectors are taken from ietf hash to curve draft version
# G.9.2.  BLS12381G1_XMD:SHA-256_SSWU_NU_
# https://tools.ietf.org/html/draft-irtf-cfrg-hash-to-curve-06#appendix-G.9.2
def gen_MAPPING_tests():
  vectors = []

  # 1
  # G1 expected
  name = "bls_mapping_g1_expected"
  inputs = [
      encode_field_element(
          0x0ccb6bda9b602ab82aae21c0291623e2f639648a6ada1c76d8ffb664130fd18d98a2cc6160624148827a9726678e7cd4
      )
  ]
  expected = [
      encode_field_element(
          0x115281bd55a4103f31c8b12000d98149598b72e5da14e953277def263a24bc2e9fd8fa151df73ea3800f9c8cbb9b245c
      ),
      encode_field_element(
          0x0796506faf9edbf1957ba8d667a079cab0d3a37e302e5132bd25665b66b26ea8556a0cfb92d6ae2c4890df0029b455ce
      )
  ]
  vectors.append(make_vector(inputs, expected, name))

  # 2
  # G2 expected
  name = "bls_mapping_g2_expected"
  inputs = [
      encode_field_element(
          0x094376a68cdc8f64bd981d59bf762f9b2960df6b135f6e09ceada2fe8d0000bbf04023492796c09f8ef04016a2e8365f
      ),
      encode_field_element(
          0x09367e3b485dda3925e82cc458e5009051281d3e442e94f9ef9feec44ee26375d6dc904dc1aa1f831f2aebd7b437ad12
      ),
  ]
  expected = [
      encode_field_element(
          0x04264ddf941f7c9ea5ad62027c72b194c6c3f62a92fcdb56ddc9de7990489af1f81c576e7f451c2cd416102253e040f0
      ),
      encode_field_element(
          0x170919c7845a9e623cef297e17484606a3eb2ae21ed8a21ff2b258861daefa3ac36955c0b374c6f4925868920d9c5f0b
      ),
      encode_field_element(
          0x02d03d852629f70563e3a653ccc2e114439f551a2fd87c8136eb205b84e22c3f40507beccdcdc52c921b69a57968ec7c
      ),
      encode_field_element(
          0x0ce03abe6c55ff0640b2b303440d88bd1a2b0cbfe3274b2802c1f58b1085e4dd8795c9c4d9c166d2f033e3c438e7f8a9
      ),
  ]
  vectors.append(make_vector(inputs, expected, name))

  print("---------\nMAPPING\n---------\n")
  for v in vectors:
    print(v)

  return


# generates mapping to curve failed test vectors
def gen_MAPPING_fail_tests():
  vectors = []

  # 1
  # Empty input
  name = "bls_mapping_empty_input"
  inputs = ['']
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 2
  # Unrecognized input (with length that is not equal to 64 or 128)
  name = "bls_mapping_unrecognized_input"
  inputs = ["1234"]
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 3
  # Invalid field element 1
  name = "bls_mapping_invalid_fq_element"
  inputs = [bad_encode_invalid_field_element()]
  error = ERROR_INVALID_FIELD_ELEMENT
  vectors.append(make_fail_vector(inputs, error, name))

  # 4
  # Invalid field element 1
  name = "bls_mapping_invalid_fq_element"
  inputs = [ZERO128, bad_encode_invalid_field_element()]
  error = ERROR_INVALID_FIELD_ELEMENT
  vectors.append(make_fail_vector(inputs, error, name))

  print("---------\nMAPPING Failure\n---------\n")
  for v in vectors:
    print(v)

  return


# generates mapping to curve failed test vectors
def gen_PAIRING_tests():
  vectors = []


def generate_vectors():
  print("eip2537 test vectors\n")

  #   gen_G1ADD_tests()
  #   gen_G1MUL_tests()
  #   gen_G1MULTIEXP_tests()

  gen_G1ADD_fail_tests()
  #   gen_G1MUL_fail_tests()
  #   gen_G1MULTIEXP_fail_tests()

  #   gen_G2ADD_tests()
  #   gen_G2MUL_tests()
  #   gen_G2MULTIEXP_tests()

  #   gen_G2ADD_fail_tests()
  #   gen_G2MUL_fail_tests()
  #   gen_G2MULTIEXP_fail_tests()

  # gen_MAPPING_tests()

  return


generate_vectors()
