'''
This script generates EIP2537 test vectors.
Notice that test vectors generated with this script does not target
underlying mathematical properties of BLS12-381 curve. Instead It is
mostly targeting a few expected results, parsing errors and error propagation.
Prints of vectors follows Go syntax.
'''

from py_ecc.bls12_381 import G1, G2, add, multiply, FQ, FQ2, Z1 as INFINITY1, Z1 as INFINITY2, curve_order, is_on_curve, b, b2, field_modulus, neg
from py_ecc.utils import prime_field_inv as inv
import csv

# encoded g1 point at infility
infinity_g1_encoded = 2 * ["{0:0{1}x}".format(0, 128)]

# encoded g2 point at infility
infinity_g2_encoded = 4 * ["{0:0{1}x}".format(0, 128)]

ZERO32 = "{0:0{1}x}".format(0, 64)
ZERO48 = "{0:0{1}x}".format(0, 96)
ZERO64 = "{0:0{1}x}".format(0, 128)
ZERO96 = "{0:0{1}x}".format(0, 192)
ZERO128 = "{0:0{1}x}".format(0, 256)
ZERO256 = "{0:0{1}x}".format(0, 512)
ONE32 = "{0:0{1}x}".format(1, 64)


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


# subgroup check g1
def g1_is_in_correct_subgroup(p):
  return multiply(p, curve_order) is INFINITY1


# subgroup check g2
def g2_is_in_correct_subgroup(p):
  return multiply(p, curve_order) is INFINITY2


# return g1 point that is on curve but not in correct subgroup
def g1_point_not_in_correct_subgroup():
  one = FQ.one()
  x = FQ.one()

  # expected point
  # (4, 1630892974828014537729259858097113969650871260980656934049590190201941782487224876496582135785777461178964897591404)
  while True:
    y = x * x * x + b
    y = sqrt1(y)
    if y is not None:
      p = (x, y)
      assert is_on_curve(p, b)
      assert g1_is_in_correct_subgroup((x, y)) is False
      return p
    x += one


# return g2 point that is on curve but not in correct subgroup
def g2_point_not_in_correct_subgroup():
  one = FQ2.one()
  x = FQ2.one()
  # expected point
  # ((2, 0), (188995492400578496451910581292546059920654572609832469388872107051048741028892423057992033888655218419282460458611, 434381874456081807472298918693162486998243066160460423017297172308631992219110538691921044767658182807847155297615))
  while True:
    y = x * x * x + b2
    y = sqrt2(y)
    if y is not None:
      p = (x, y)
      assert is_on_curve(p, b2)
      assert g2_is_in_correct_subgroup(p) is False
      return p
    x += one


# Constants that we need for calculating square root
P = field_modulus
P_MINUS3_OVER4 = ((P - 3) * inv(4, P)) % P
P_MINUS1_OVER2 = ((P - 1) * inv(2, P)) % P
P_PLUS1_OVER4 = ((P + 1) * inv(4, P)) % P


# returns a for given a ** 2 if such fq element exists otherwise return None
# https://eprint.iacr.org/2012/685.pdf
# algoritm 2
def sqrt1(a):
  x = a**P_PLUS1_OVER4
  return x if x * x == a else None


# test sqrt 2
def test_sqrt1():
  a0 = FQ(7)
  aa = a0 * a0
  a1 = sqrt1(aa)
  assert aa == a1 * a1


# returns a for given a ** 2 if such fq2 element exists otherwise return None
# https://eprint.iacr.org/2012/685.pdf
# algoritm 9
def sqrt2(a):
  a1 = a**P_MINUS3_OVER4
  alpha = a1 * a1 * a
  x0 = a1 * a
  if alpha == FQ2([-1, 0]):
    return FQ2((x0.coeffs[1], x0.coeffs[0]))
  alpha = alpha + FQ2.one()
  alpha = alpha**P_MINUS1_OVER2
  x = alpha * x0
  return x if x * x == a else None


# test sqrt 1
def test_sqrt2():
  a0 = FQ2([field_modulus - 10, field_modulus - 11])
  aa = a0 * a0
  a1 = sqrt2(aa)
  assert aa == a1 * a1


# test sqrt implementations above
test_sqrt1()
test_sqrt2()

# Expected Errors 'errBLS12381_XXX_'

# msg : "invalid input length"
ERROR_INVALID_INPUT_LENGHT = "errBLS12381InvalidInputLength"
# msg : "invalid field element top bytes"
ERROR_FIELD_ELEMENT_TOP_BYTES = "errBLS12381InvalidFieldElementTopBytes"
# msg : "invalid field element"
ERROR_INVALID_FIELD_ELEMENT = "errBLS12381InvalidFieldElement"
# msg : "point is not on curve"
ERROR_POINT_G1_IS_NOT_ON_CURVE = "errBLS12381G1PointIsNotOnCurve"
# msg : "point is not on curve"
ERROR_POINT_G2_IS_NOT_ON_CURVE = "errBLS12381G2PointIsNotOnCurve"
# msg : "g1 point is not on correct subgroup"
ERROR_POINT_G1_SUBGROUP = "errBLS12381G1PointSubgroup"
# msg : "g2 point is not on correct subgroup"
ERROR_POINT_G2_SUBGROUP = "errBLS12381G2PointSubgroup"

# Utilities


# given list of strings ["a", "b", "c"] returns "a" + "b" + "c"
def concat_list(entries):
  res = ""
  for i, s in enumerate(entries):
    res += "\"{}\"".format(s)
    if i + 1 != len(entries):
      res += " +\n"
  return res


# encode scalar into 32 bytes
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
def bad_encode_g1_point_large():
  x = encode_field_element(G1[0])
  y = bad_encode_field_element_large(G1[1])
  return [x, y]


# encodes g1 point into shorter byte string than expected
def bad_encode_g1_point_short():
  x = encode_field_element(G1[0])
  y = bad_encode_field_element_short(G1[1])
  return [x, y]


# encodes g1 point with invalid field element
# note that this migth also violate the curve equation
def bad_encode_g1_point_invalid_field_element():
  x = encode_field_element(G1[0])
  y = bad_encode_invalid_field_element()
  return [x, y]


# encodes g1 point violating field element zero top bytes
def bad_encode_g1_point_top_bytes():
  x = encode_field_element(G1[0])
  y = bad_encode_field_element_top_bytes(G1[1])
  return [x, y]


# encodes g1 point and scalar value pair into 128 + 32 bytes
def encode_g1_point_scalar_pair(p, e):
  return encode_g1_point(p) + [encode_scalar(e)]


# encodes g1 point and scalar value pair into shorher byte string than expected
def bad_encode_g1_point_scalar_pair_short():
  return bad_encode_g1_point_short() + [encode_scalar(7)]


# encodes g1 point and scalar value pair into larger byte string than expected
def bad_encode_g1_point_scalar_pair_large():
  return bad_encode_g1_point_large() + [encode_scalar(7)]


# encodes g1 point and scalar value pair violating zero top bytes of a field element
def bad_encode_g1_point_scalar_pair_top_bytes():
  return bad_encode_g1_point_top_bytes() + [encode_scalar(7)]


# encodes g1 point and scalar value pair with invalid field element
def bad_encode_g1_point_scalar_pair_invalid_field_element():
  return bad_encode_g1_point_invalid_field_element() + [encode_scalar(7)]


# encodes a g1 point that does not satisfy curve equation
def encode_g1_point_not_on_curve():
  return encode_g1_point(g1_point_is_not_on_curve())


# encodes a g2 point into 4 * 64 bytes
def encode_g2_point(point):
  if point is INFINITY2:
    return infinity_g2_encoded
  x0 = encode_field_element(point[0].coeffs[0])
  x1 = encode_field_element(point[0].coeffs[1])
  y0 = encode_field_element(point[1].coeffs[0])
  y1 = encode_field_element(point[1].coeffs[1])
  return [x0, x1, y0, y1]


# encodes g2 point into larger byte string than expected
def bad_encode_g2_point_large():
  x0 = encode_field_element(G2[0].coeffs[0])
  x1 = encode_field_element(G2[0].coeffs[1])
  y0 = encode_field_element(G2[1].coeffs[0])
  y1 = bad_encode_field_element_large(G2[1].coeffs[1])
  return [x0, x1, y0, y1]


# encodes g2 point into shorter byte string than expected
def bad_encode_g2_point_short():
  x0 = encode_field_element(G2[0].coeffs[0])
  x1 = encode_field_element(G2[0].coeffs[1])
  y0 = encode_field_element(G2[1].coeffs[0])
  y1 = bad_encode_field_element_short(G2[1].coeffs[1])
  return [x0, x1, y0, y1]


# encodes g2 point violating field element zero top bytes
def bad_encode_g2_point_invalid_field_element():
  x0 = encode_field_element(G2[0].coeffs[0])
  x1 = encode_field_element(G2[0].coeffs[1])
  y0 = encode_field_element(G2[1].coeffs[0])
  y1 = bad_encode_invalid_field_element()
  return [x0, x1, y0, y1]


# encodes g2 point violating field element zero top bytes
def bad_encode_g2_point_top_bytes():
  x0 = encode_field_element(G2[0].coeffs[0])
  x1 = encode_field_element(G2[0].coeffs[1])
  y0 = encode_field_element(G2[1].coeffs[0])
  y1 = bad_encode_field_element_top_bytes(G2[1].coeffs[1])
  return [x0, x1, y0, y1]


# encodes g2 point and scalar value pair into 256 + 32 bytes
def encode_g2_point_scalar_pair(p, e):
  return encode_g2_point(p) + [encode_scalar(e)]


# encodes g2 point and scalar value pair into shorher byte string than expected
def bad_encode_g2_point_scalar_pair_short():
  return bad_encode_g2_point_short() + [encode_scalar(7)]


# encodes g2 point and scalar value pair into larger byte string than expected
def bad_encode_g2_point_scalar_pair_large():
  return bad_encode_g2_point_large() + [encode_scalar(7)]


# encodes g2 point and scalar value pair violating zero top bytes of a field element
def bad_encode_g2_point_scalar_pair_top_bytes():
  return bad_encode_g2_point_top_bytes() + [encode_scalar(7)]


# encodes g2 point and scalar value pair with invalid field element
def bad_encode_g2_point_scalar_pair_invalid_field_element():
  return bad_encode_g2_point_invalid_field_element() + [encode_scalar(7)]


# encodes a g2 point that does not satisfy curve equation
def encode_g2_point_not_on_curve():
  return encode_g2_point(g2_point_is_not_on_curve())


# encodes g1 point and g2 point pair into 256 + 128 bytes
def encode_g1_point_g2_point_pair(p1, p2):
  return encode_g1_point(p1) + encode_g2_point(p2)


def make_vector(inputs, expecteds, name):
  return "{{\ninput:\n{},\nexpected:\n{},\nname: \"{}\",\n}},".format(
      concat_list(inputs), concat_list(expecteds), name)


def make_matter_vectors(op_name):
  vectors = []
  with open("./matter/{}.csv".format(op_name), newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for i, row in enumerate(reader):
      name = "matter_{}_{}".format(op_name, i)
      v = make_vector([row['input']], [row['result']], name)
      vectors.append(v)
  return vectors


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

  # append matter vectors
  vectors = vectors + make_matter_vectors('g1_add')

  generated = "\nvar blsG1ADDTests = []precompiledTest{{\n{}\n}}".format(
      "\n".join(vectors))

  return generated


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
  inputs = bad_encode_g1_point_short() + encode_g1_point(G1)
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 2
  # Large input
  name = "bls_g1add_large_input"
  inputs = bad_encode_g1_point_large() + encode_g1_point(G1)
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 3
  # Violate top bytes
  name = "bls_g1add_violate_top_bytes"
  inputs = bad_encode_g1_point_top_bytes() + encode_g1_point(G1)
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
  error = ERROR_POINT_G1_IS_NOT_ON_CURVE
  vectors.append(make_fail_vector(inputs, error, name))

  generated = "\nvar blsG1ADDFailTests = []precompiledFailureTest{{\n{}\n}}".format(
      "\n".join(vectors))

  return generated


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

  # append matter vectors
  vectors = vectors + make_matter_vectors('g1_mul')

  generated = "\nvar blsG1MULTests = []precompiledTest{{\n{}\n}}".format(
      "\n".join(vectors))

  return generated


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
  inputs = bad_encode_g1_point_scalar_pair_short()
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 2
  # Large input
  name = "bls_g1mul_large_input"
  inputs = bad_encode_g1_point_scalar_pair_large()
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 3
  # Violate top bytes
  name = "bls_g1mul_violate_top_bytes"
  inputs = bad_encode_g1_point_scalar_pair_top_bytes()
  error = ERROR_FIELD_ELEMENT_TOP_BYTES
  vectors.append(make_fail_vector(inputs, error, name))

  # 4
  # Invalid field element
  name = "bls_g1mul_invalid_field_element"
  inputs = bad_encode_g1_point_scalar_pair_invalid_field_element()
  error = ERROR_INVALID_FIELD_ELEMENT
  vectors.append(make_fail_vector(inputs, error, name))

  # 5
  # Point is not on curve
  name = "bls_g1mul_point_not_on_curve"
  inputs = encode_g1_point_scalar_pair(g1_point_is_not_on_curve(), 1)
  error = ERROR_POINT_G1_IS_NOT_ON_CURVE
  vectors.append(make_fail_vector(inputs, error, name))

  generated = "\nvar blsG1MULFailTests = []precompiledFailureTest{{\n{}\n}}".format(
      "\n".join(vectors))

  return generated


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

  # append matter vectors
  vectors = vectors + make_matter_vectors('g1_multiexp')

  generated = "\nvar blsG1MULTIEXPTests = []precompiledTest{{\n{}\n}}".format(
      "\n".join(vectors))

  return generated


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
  inputs = bad_encode_g1_point_scalar_pair_short()
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 2
  # Large input
  name = "bls_g1multiexp_large_input"
  inputs = bad_encode_g1_point_scalar_pair_large()
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 3
  # Invalid field element
  name = "bls_g1multiexp_invalid_field_element"
  inputs = bad_encode_g1_point_scalar_pair_invalid_field_element()
  error = ERROR_INVALID_FIELD_ELEMENT
  vectors.append(make_fail_vector(inputs, error, name))

  # 4
  # Violate top bytes
  name = "bls_g1multiexp_violate_top_bytes"
  inputs = bad_encode_g1_point_scalar_pair_top_bytes()
  error = ERROR_FIELD_ELEMENT_TOP_BYTES
  vectors.append(make_fail_vector(inputs, error, name))

  # 5
  # Point is not on curve
  name = "bls_g1multiexp_point_not_on_curve"
  inputs = encode_g1_point_scalar_pair(g1_point_is_not_on_curve(), 1)
  error = ERROR_POINT_G1_IS_NOT_ON_CURVE
  vectors.append(make_fail_vector(inputs, error, name))

  generated = "\nvar blsG1MULTIEXPFailTests = []precompiledFailureTest{{\n{}\n}}".format(
      "\n".join(vectors))

  return generated


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

  # append matter vectors
  vectors = vectors + make_matter_vectors('g2_add')

  generated = "\nvar blsG2ADDTests = []precompiledTest{{\n{}\n}}".format(
      "\n".join(vectors))

  return generated


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
  inputs = bad_encode_g2_point_short() + encode_g2_point(G2)
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 2
  # Large input
  name = "bls_g2add_large_input"
  inputs = bad_encode_g2_point_large() + encode_g2_point(G2)
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 3
  # Violate top bytes
  name = "bls_g2add_violate_top_bytes"
  inputs = bad_encode_g2_point_top_bytes() + encode_g2_point(G2)
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
  error = ERROR_POINT_G2_IS_NOT_ON_CURVE
  vectors.append(make_fail_vector(inputs, error, name))

  generated = "\nvar blsG2ADDFailTests = []precompiledFailureTest{{\n{}\n}}".format(
      "\n".join(vectors))

  return generated


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

  # append matter vectors
  vectors = vectors + make_matter_vectors('g2_mul')

  generated = "\nvar blsG2MULTests = []precompiledTest{{\n{}\n}}".format(
      "\n".join(vectors))

  return generated


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
  inputs = bad_encode_g2_point_scalar_pair_short()
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 2
  # Large input
  name = "bls_g2mul_large_input"
  inputs = bad_encode_g2_point_scalar_pair_large()
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 3
  # Violate top bytes
  name = "bls_g2mul_violate_top_bytes"
  inputs = bad_encode_g2_point_scalar_pair_top_bytes()
  error = ERROR_FIELD_ELEMENT_TOP_BYTES
  vectors.append(make_fail_vector(inputs, error, name))

  # 4
  # Invalid field element
  name = "bls_g2mul_invalid_field_element"
  inputs = bad_encode_g2_point_scalar_pair_invalid_field_element()
  error = ERROR_INVALID_FIELD_ELEMENT
  vectors.append(make_fail_vector(inputs, error, name))

  # 5
  # Point is not on curve
  name = "bls_g2mul_point_not_on_curve"
  inputs = encode_g2_point_scalar_pair(g2_point_is_not_on_curve(), 1)
  error = ERROR_POINT_G2_IS_NOT_ON_CURVE
  vectors.append(make_fail_vector(inputs, error, name))

  generated = "\nvar blsG2MULFailTests = []precompiledFailureTest{{\n{}\n}}".format(
      "\n".join(vectors))

  return generated


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

  # append matter vectors
  vectors = vectors + make_matter_vectors('g2_multiexp')

  generated = "\nvar blsG2MULTIEXPTests = []precompiledTest{{\n{}\n}}".format(
      "\n".join(vectors))

  return generated


# generates G2MULTIEXP fail tests
def gen_G2MULTIEXP_fail_tests():
  vectors = []

  # 1
  # Empty input
  name = "bls_g2multiexp_empty_input"
  inputs = ['']
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 2
  # Short input
  name = "bls_g2multiexp_short_input"
  inputs = bad_encode_g2_point_scalar_pair_short()
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 3
  # Large input
  name = "bls_g2multiexp_large_input"
  inputs = bad_encode_g2_point_scalar_pair_large()
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 4
  # Violate top bytes
  name = "bls_g2multiexp_violate_top_bytes"
  inputs = bad_encode_g2_point_scalar_pair_top_bytes()
  error = ERROR_FIELD_ELEMENT_TOP_BYTES
  vectors.append(make_fail_vector(inputs, error, name))

  # 5
  # Invalid field element
  name = "bls_g2multiexp_invalid_field_element"
  inputs = bad_encode_g2_point_scalar_pair_invalid_field_element()
  error = ERROR_INVALID_FIELD_ELEMENT
  vectors.append(make_fail_vector(inputs, error, name))

  # 5
  # Point is not on curve
  name = "bls_g2multiexp_point_not_on_curve"
  inputs = encode_g2_point_scalar_pair(g2_point_is_not_on_curve(), 1)
  error = ERROR_POINT_G2_IS_NOT_ON_CURVE
  vectors.append(make_fail_vector(inputs, error, name))

  generated = "\nvar blsG2MULTIEXPFailTests = []precompiledFailureTest{{\n{}\n}}".format(
      "\n".join(vectors))

  return generated


# generates mapping fp to g1 test vectors
def gen_MAPG1_tests():
  vectors = []

  # vectors are taken from ietf hash to curve draft version 6
  # G.9.2.  BLS12381G1_XMD:SHA-256_SSWU_NU_
  # https://tools.ietf.org/html/draft-irtf-cfrg-hash-to-curve-06#appendix-G.9.2
  name = "bls_mapg1_expected"
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

  # append matter vectors
  vectors = vectors + make_matter_vectors('fp_to_g1')

  generated = "\nvar blsMAPG1Tests = []precompiledTest{{\n{}\n}}".format(
      "\n".join(vectors))

  return generated


# generates mapping fp2 to g2 test vectors
def gen_MAPG2_tests():
  vectors = []

  # vectors are taken from ietf hash to curve draft version 6
  # G.9.2.  BLS12381G1_XMD:SHA-256_SSWU_NU_
  # https://tools.ietf.org/html/draft-irtf-cfrg-hash-to-curve-06#appendix-G.9.2
  name = "bls_mapg2_expected"
  inputs = [
      encode_field_element(
          0x09367e3b485dda3925e82cc458e5009051281d3e442e94f9ef9feec44ee26375d6dc904dc1aa1f831f2aebd7b437ad12
      ),
      encode_field_element(
          0x094376a68cdc8f64bd981d59bf762f9b2960df6b135f6e09ceada2fe8d0000bbf04023492796c09f8ef04016a2e8365f
      ),
  ]
  expected = [
      encode_field_element(
          0x170919c7845a9e623cef297e17484606a3eb2ae21ed8a21ff2b258861daefa3ac36955c0b374c6f4925868920d9c5f0b
      ),
      encode_field_element(
          0x04264ddf941f7c9ea5ad62027c72b194c6c3f62a92fcdb56ddc9de7990489af1f81c576e7f451c2cd416102253e040f0
      ),
      encode_field_element(
          0x0ce03abe6c55ff0640b2b303440d88bd1a2b0cbfe3274b2802c1f58b1085e4dd8795c9c4d9c166d2f033e3c438e7f8a9
      ),
      encode_field_element(
          0x02d03d852629f70563e3a653ccc2e114439f551a2fd87c8136eb205b84e22c3f40507beccdcdc52c921b69a57968ec7c
      ),
  ]
  vectors.append(make_vector(inputs, expected, name))

  # append matter vectors
  vectors = vectors + make_matter_vectors('fp2_to_g2')

  generated = "\nvar blsMAPG2Tests = []precompiledTest{{\n{}\n}}".format(
      "\n".join(vectors))

  return generated


# generates mapping to curve failed test vectors
def gen_MAPG1_fail_tests():
  vectors = []

  # 1
  # Empty input
  name = "bls_mapg1_empty_input"
  inputs = ['']
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 2
  # Short input
  name = "bls_mapg1_short_input"
  inputs = [ZERO64[2:]]
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 3
  # Violate top bytes
  name = "bls_mapg1_top_bytes"
  inputs = [bad_encode_field_element_top_bytes(None)]
  error = ERROR_FIELD_ELEMENT_TOP_BYTES
  vectors.append(make_fail_vector(inputs, error, name))

  # 4
  # Invalid field element
  name = "bls_mapg1_invalid_fq_element"
  inputs = [bad_encode_invalid_field_element()]
  error = ERROR_INVALID_FIELD_ELEMENT
  vectors.append(make_fail_vector(inputs, error, name))

  generated = "\nvar blsMAPG1FailTests = []precompiledFailureTest{{\n{}\n}}".format(
      "\n".join(vectors))

  return generated


# generates mapping to curve failed test vectors
def gen_MAPG2_fail_tests():
  vectors = []

  # 1
  # Empty input
  name = "bls_mapg2_empty_input"
  inputs = ['']
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 2
  # Short input
  name = "bls_mapg2_short_input"
  inputs = [ZERO64, ZERO64[2:]]
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 3
  # Violate top bytes
  name = "bls_mapg2_top_bytes"
  inputs = [ZERO64, bad_encode_field_element_top_bytes(None)]
  error = ERROR_FIELD_ELEMENT_TOP_BYTES
  vectors.append(make_fail_vector(inputs, error, name))

  # 4
  # Invalid field element
  name = "bls_mapg2_invalid_fq_element"
  inputs = [ZERO64, bad_encode_invalid_field_element()]
  error = ERROR_INVALID_FIELD_ELEMENT
  vectors.append(make_fail_vector(inputs, error, name))

  generated = "\nvar blsMAPG2FailTests = []precompiledFailureTest{{\n{}\n}}".format(
      "\n".join(vectors))

  return generated


# generates mapping to curve failed test vectors
def gen_PAIRING_tests():
  vectors = []

  # 1
  # Two pair checks true
  # e(2 * G1, 3 * G2) == e(6 * G1, G2)
  name = "bls_pairing_e(2*G1,3*G2)=e(6*G1,G2)"
  a0 = multiply(G1, 2)
  a1 = multiply(G2, 3)
  b0 = multiply(G1, 6)
  b1 = neg(G2)
  inputs = encode_g1_point(a0) + encode_g2_point(a1) + encode_g1_point(
      b0) + encode_g2_point(b1)
  expected = [ONE32]
  vectors.append(make_vector(inputs, expected, name))

  # 2
  # Two pair checks false
  # e(2 * G1, 3 * G2) == e(5 * G1, G2)
  name = "bls_pairing_e(2*G1,3*G2)=e(5*G1,G2)"
  a0 = multiply(G1, 2)
  a1 = multiply(G2, 3)
  b0 = multiply(G1, 5)
  b1 = neg(G2)
  inputs = encode_g1_point(a0) + encode_g2_point(a1) + encode_g1_point(
      b0) + encode_g2_point(b1)
  expected = [ZERO32]
  vectors.append(make_vector(inputs, expected, name))

  # 3
  # Ten pair checks true
  name = "bls_pairing_10paircheckstrue"
  N, s1, s2 = 10, 11, 21
  inputs = []
  acc_result = 0
  for _ in range(N - 1):
    a1 = multiply(G1, s1)
    a2 = multiply(G2, s2)
    acc_result += s1 * s2
    s1 += 1
    s2 += 1
    inputs = inputs + encode_g1_point_g2_point_pair(a1, a2)
  a1 = multiply(G1, acc_result)
  a2 = neg(G2)
  inputs = inputs + encode_g1_point_g2_point_pair(a1, a2)
  expected = [ONE32]
  vectors.append(make_vector(inputs, expected, name))

  # 4
  # Ten pair checks false
  name = "bls_pairing_10pairchecksfalse"
  N, s1, s2 = 10, 11, 21
  inputs = []
  acc_result = 0
  for _ in range(N - 1):
    a1 = multiply(G1, s1)
    a2 = multiply(G2, s2)
    acc_result += s1 * s2
    s1 += 1
    s2 += 1
    inputs = inputs + encode_g1_point_g2_point_pair(a1, a2)
  a1 = multiply(G1, acc_result)
  # same vector with #3 but omiting negation at the end
  a2 = G2
  inputs = inputs + encode_g1_point_g2_point_pair(a1, a2)
  expected = [ZERO32]
  vectors.append(make_vector(inputs, expected, name))

  # append matter vectors
  vectors = vectors + make_matter_vectors('pairing')

  generated = "\nvar blsPAIRINGTests = []precompiledTest{{\n{}\n}}".format(
      "\n".join(vectors))

  return generated


def gen_PAIRING_fail_tests():
  vectors = []

  # 1
  # Empty input
  name = "bls_pairing_empty_input"
  inputs = ['']
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 2
  # Extra data
  name = "bls_pairing_extra_data"
  inputs = encode_g1_point(G1) + encode_g2_point(G2) + encode_g1_point(
      G1) + bad_encode_g2_point_large()
  error = ERROR_INVALID_INPUT_LENGHT
  vectors.append(make_fail_vector(inputs, error, name))

  # 3
  # Invalid field element
  name = "bls_pairing_invalid_field_element"
  inputs = encode_g1_point(G1) + encode_g2_point(G2) + encode_g1_point(
      G1) + bad_encode_g2_point_invalid_field_element()
  error = ERROR_INVALID_FIELD_ELEMENT
  vectors.append(make_fail_vector(inputs, error, name))

  # 4
  # Violate top bytes
  name = "bls_pairing_top_bytes"
  inputs = encode_g1_point(G1) + encode_g2_point(G2) + encode_g1_point(
      G1) + bad_encode_g2_point_top_bytes()
  error = ERROR_FIELD_ELEMENT_TOP_BYTES
  vectors.append(make_fail_vector(inputs, error, name))

  # 5
  # G1 Point is not on curve
  name = "bls_pairing_g1_not_on_curve"
  inputs = encode_g1_point(G1) + encode_g2_point(G2) + encode_g1_point(
      g1_point_is_not_on_curve()) + encode_g2_point(G2)
  error = ERROR_POINT_G1_IS_NOT_ON_CURVE
  vectors.append(make_fail_vector(inputs, error, name))

  # 6
  # G2 Point is not on curve
  name = "bls_pairing_g2_not_on_curve"
  inputs = encode_g1_point(G1) + encode_g2_point(G2) + encode_g1_point(
      G1) + encode_g2_point(g2_point_is_not_on_curve())
  error = ERROR_POINT_G2_IS_NOT_ON_CURVE
  vectors.append(make_fail_vector(inputs, error, name))

  # 7
  # G1 Point is not in correct subgroup
  name = "bls_pairing_g1_not_in_correct_subgroup"
  inputs = encode_g1_point(G1) + encode_g2_point(G2) + encode_g1_point(
      g1_point_not_in_correct_subgroup()) + encode_g2_point(G2)
  error = ERROR_POINT_G1_SUBGROUP
  vectors.append(make_fail_vector(inputs, error, name))

  # 8
  # G1 Point is not in correct subgroup
  name = "bls_pairing_g2_not_in_correct_subgroup"
  inputs = encode_g1_point(G1) + encode_g2_point(G2) + encode_g1_point(
      G1) + encode_g2_point(g2_point_not_in_correct_subgroup())
  error = ERROR_POINT_G2_SUBGROUP
  vectors.append(make_fail_vector(inputs, error, name))

  generated = "\nvar blsPAIRINGFailTests = []precompiledFailureTest{{\n{}\n}}".format(
      "\n".join(vectors))

  return generated


def generate_vectors():

  f = open("../vectors_test.go", "w+")
  f.write("package eip2537\n")
  f.write(gen_G1ADD_tests())
  f.write(gen_G1MUL_tests())
  f.write(gen_G1MULTIEXP_tests())
  f.write(gen_G2ADD_tests())
  f.write(gen_G2MUL_tests())
  f.write(gen_G2MULTIEXP_tests())
  f.write(gen_PAIRING_tests())
  f.write(gen_MAPG1_tests())
  f.write(gen_MAPG2_tests())

  f.write(gen_G1ADD_fail_tests())
  f.write(gen_G1MUL_fail_tests())
  f.write(gen_G1MULTIEXP_fail_tests())
  f.write(gen_G2ADD_fail_tests())
  f.write(gen_G2MUL_fail_tests())
  f.write(gen_G2MULTIEXP_fail_tests())
  f.write(gen_PAIRING_fail_tests())
  f.write(gen_MAPG1_fail_tests())
  f.write(gen_MAPG2_fail_tests())
  f.close()

  return


generate_vectors()
