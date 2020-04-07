from py_ecc.bls12_381 import G1, G2, add, multiply, FQ, Z1 as INFINITY1, Z1 as INFINITY2, curve_order

infinity_g1_encoded = 2 * ["{0:0{1}x}".format(0, 128)]
infinity_g2_encoded = 4 * ["{0:0{1}x}".format(0, 128)]


def concat_list(entries):
  res = ""
  for i, s in enumerate(entries):
    res += "\"{}\"".format(s)
    if i + 1 != len(entries):
      res += " +\n"
  return res


def encode_field_element(fe: FQ):
  return "{0:0{1}x}".format(fe.n, 128)


def encode_g1_point(point):
  if point is INFINITY1:
    return infinity_g1_encoded
  x = encode_field_element(point[0])
  y = encode_field_element(point[1])
  return [x, y]


def encode_scalar(e):
  return str("{0:0{1}x}".format(e, 64))


def encode_g1_point_scalar_pair(p, e):
  return encode_g1_point(p) + [encode_scalar(e)]


def make_vector(inputs, expecteds, name):
  return "{{\ninput:\n{},\nexpected:\n{},\nname: \"{}\",\n}},".format(
      concat_list(inputs), concat_list(expecteds), name)


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
  # G1 + G1 == 2 * G1
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


# generates G1MUL happy case tests
def gen_G1MULTIEXP_tests():
  vectors = []

  # 1
  # single pair
  name = "bls_g1multiexp_single"
  a = G1
  e = 17
  r = multiply(a, e)
  inputs = encode_g1_point_scalar_pair(a, r)
  expected = encode_g1_point(r)
  vectors.append(make_vector(inputs, expected, name))

  # 1
  # multiple pairs
  name = "bls_g1multiexp_multiple"
  bases = [G1, multiply(G1, 1001), multiply(G1, 1002)]
  scalars = [50, 51, 52]
  acc_result = INFINITY1
  acc_input = ""
  for p, e in zip(bases, scalars):
    acc_result = add(multiply(p, e), acc_result)
    acc_input += encode_g1_point_scalar_pair(p, r)
  inputs = acc_input
  expected = encode_g1_point(acc_result)
  vectors.append(make_vector(inputs, expected, name))

  # 2
  # larger set
  name = "bls_g1multiexp_larger"
  N, b, ez = 100, 1, 91
  e = ez
  bases, scalars = [], []
  acc_input = ""
  acc_result = ""
  for _ in range(N):
    base = multiply(G1, b)
    acc_result = add(multiply(base, e), acc_result)
    acc_input += encode_g1_point_scalar_pair(base, e)
    e = (e * ez) % curve_order
    b += 1
  inputs = acc_input
  expected = encode_g1_point(acc_result)
  vectors.append(make_vector(inputs, expected, name))

  return vectors


def generate_vectors():
  print("eip2537 test vectors\n")
  gen_G1ADD_tests()
  gen_G1MUL_tests()


generate_vectors()
