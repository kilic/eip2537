// This file contains BSL12-381 precompile tests and imitates github.com/go-ethereum/core/vm/contracts.go

package eip2537

import (
	"math/big"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/vm"
	bls12381 "github.com/kilic/bls12-381"
)

// PrecompiledContractsBerlinOnly contains the set of pre-compiled contracts
// which are considered to be added in Berlin HF.
var PrecompiledContractsBerlinOnly = map[common.Address]vm.PrecompiledContract{
	common.BytesToAddress([]byte{0x0a}): &bls12381G1ADD{},
	common.BytesToAddress([]byte{0x0b}): &bls12381G1MUL{},
	common.BytesToAddress([]byte{0x0c}): &bls12381G1MULTIEXP{},
	common.BytesToAddress([]byte{0x0d}): &bls12381G2ADD{},
	common.BytesToAddress([]byte{0x0e}): &bls12381G2MUL{},
	common.BytesToAddress([]byte{0x0f}): &bls12381G2MULTIEXP{},
	common.BytesToAddress([]byte{0x10}): &bls12381PAIRING{},
	common.BytesToAddress([]byte{0x11}): &bls12381MAPG1{},
	common.BytesToAddress([]byte{0x12}): &bls12381MAPG2{},
}

type bls12381G1ADD struct{}

// RequiredGas returns the gas required to execute the pre-compiled contract.
func (c *bls12381G1ADD) RequiredGas(input []byte) uint64 {
	return BLS12381G1ADDGas
}

func (c *bls12381G1ADD) Run(input []byte) ([]byte, error) {
	return runBLS12381G1ADD(input)
}

// runBLS12381G1ADD implements EIP-2537 G1ADD precompile logic.
// > G1 addition call expects `256` bytes as an input that is interpreted as byte concatenation of two G1 points (`128` bytes each).
// > Output is an encoding of addition operation result - single G1 point (`128` bytes).
func runBLS12381G1ADD(in []byte) ([]byte, error) {
	if len(in) != 256 {
		return nil, errBLS12381InvalidInputLength
	}
	var err error
	var p0, p1 *bls12381.PointG1

	// Initialize G1
	g := bls12381.NewG1()

	// Decode G1 point p_0
	if p0, err = decodeG1Point(g, in[:128]); err != nil {
		return nil, err
	}
	// Decode G1 point p_1
	if p1, err = decodeG1Point(g, in[128:]); err != nil {
		return nil, err
	}

	// Compute r = p_0 + p_1
	r := g.New()
	g.Add(r, p0, p1)

	// Encode G1 point, outRaw is 96 bytes,
	// we must encode G1 point to 128 bytes.
	return encodeG1Point(g, r), nil
}

type bls12381G1MUL struct{}

// RequiredGas returns the gas required to execute the pre-compiled contract.
func (c *bls12381G1MUL) RequiredGas(input []byte) uint64 {
	return BLS12381G1MULGas
}

func (c *bls12381G1MUL) Run(input []byte) ([]byte, error) {
	return runBLS12381G1MUL(input)
}

// runBLS12381G1MUL implements EIP-2537 G1MUL precompile logic.
// > G1 multiplication call expects `160` bytes as an input that is interpreted as byte concatenation of encoding of G1 point (`128` bytes) and encoding of a scalar value (`32` bytes).
// > Output is an encoding of multiplication operation result - single G1 point (`128` bytes).
func runBLS12381G1MUL(in []byte) ([]byte, error) {
	if len(in) != 160 {
		return nil, errBLS12381InvalidInputLength
	}
	var err error
	var p0 *bls12381.PointG1

	// Initialize G1
	g := bls12381.NewG1()

	// Decode G1 point
	if p0, err = decodeG1Point(g, in[:128]); err != nil {
		return nil, err
	}
	// Decode scalar value
	e := new(big.Int).SetBytes(in[128:])

	// Compute r = p_0 + p_1
	r := g.New()
	g.MulScalar(r, p0, e)

	// Encode G1 point, outRaw is 96 bytes,
	// we must encode G1 point to 128 bytes.
	return encodeG1Point(g, r), nil
}

type bls12381G1MULTIEXP struct{}

// RequiredGas returns the gas required to execute the pre-compiled contract.
func (c *bls12381G1MULTIEXP) RequiredGas(input []byte) uint64 {
	return uint64(len(input)/160) * BLS12381G1MULTIEXPPerPairGas
}

func (c *bls12381G1MULTIEXP) Run(input []byte) ([]byte, error) {
	return runG1MULTIEXP(input)
}

// runG1MULTIEXP implements EIP-2537 G1MULTIEXP precompile logic.
// G1 multiplication call expects `160*k` bytes as an input that is interpreted as byte concatenation of `k` slices each of them being a byte concatenation of encoding of G1 point (`128` bytes) and encoding of a scalar value (`32` bytes).
// Output is an encoding of multiexponentiation operation result - single G1 point (`128` bytes).
func runG1MULTIEXP(in []byte) ([]byte, error) {
	k := len(in) / 160
	if len(in) != k*160 || k == 0 {
		return nil, errBLS12381InvalidInputLength
	}
	var err error
	points := make([]*bls12381.PointG1, k)
	scalars := make([]*big.Int, k)

	// Initialize G1
	g := bls12381.NewG1()

	// Decode point scalar pairs
	for i := 0; i < k; i++ {
		off := 160 * i
		t0, t1, t2 := off, off+128, off+160
		// Decode G1 point
		if points[i], err = decodeG1Point(g, in[t0:t1]); err != nil {
			return nil, err
		}
		// Decode scalar value
		scalars[i] = new(big.Int).SetBytes(in[t1:t2])
	}

	// Compute r = e_0 * p_0 + e_0 * p_0 + ... + e_(k-1) * p_(k-1)
	r := g.New()
	_, _ = g.MultiExp(r, points, scalars)

	// Encode G1 point, outRaw is 96 bytes,
	// we must encode G1 point to 128 bytes.
	return encodeG1Point(g, r), nil
}

type bls12381G2ADD struct{}

// RequiredGas returns the gas required to execute the pre-compiled contract.
func (c *bls12381G2ADD) RequiredGas(input []byte) uint64 {
	return BLS12381G2ADDGas
}

func (c *bls12381G2ADD) Run(input []byte) ([]byte, error) {
	return runBLS12381G2ADD(input)
}

// runBLS12381G2ADD implements EIP-2537 G2ADD precompile logic.
// > G2 addition call expects `512` bytes as an input that is interpreted as byte concatenation of two G2 points (`256` bytes each).
// > Output is an encoding of addition operation result - single G2 point (`256` bytes).
func runBLS12381G2ADD(in []byte) ([]byte, error) {
	if len(in) != 512 {
		return nil, errBLS12381InvalidInputLength
	}
	var err error
	var p0, p1 *bls12381.PointG2

	// Initialize G2
	g := bls12381.NewG2(nil)
	r := g.New()

	// Decode G2 point p_0
	if p0, err = decodeG2Point(g, in[:256]); err != nil {
		return nil, err
	}
	// Decode G2 point p_1
	if p1, err = decodeG2Point(g, in[256:]); err != nil {
		return nil, err
	}

	// Compute r = p_0 + p_1
	g.Add(r, p0, p1)

	// Encode G2 point, outRaw is 192 bytes,
	// we must encode G2 point to 256 bytes.
	return encodeG2Point(g, r), nil
}

type bls12381G2MUL struct{}

// RequiredGas returns the gas required to execute the pre-compiled contract.
func (c *bls12381G2MUL) RequiredGas(input []byte) uint64 {
	return BLS12381G2MULGas
}

func (c *bls12381G2MUL) Run(input []byte) ([]byte, error) {
	return runBLS12381G2MUL(input)
}

// runBLS12381G2MUL implements EIP-2537 G2MUL precompile logic.
// > G2 multiplication call expects `288` bytes as an input that is interpreted as byte concatenation of encoding of G2 point (`256` bytes) and encoding of a scalar value (`32` bytes).
// > Output is an encoding of multiplication operation result - single G2 point (`256` bytes).
func runBLS12381G2MUL(in []byte) ([]byte, error) {
	if len(in) != 288 {
		return nil, errBLS12381InvalidInputLength
	}
	var err error
	var p0 *bls12381.PointG2

	// Initialize G2
	g := bls12381.NewG2(nil)

	// Decode G2 point
	if p0, err = decodeG2Point(g, in[:256]); err != nil {
		return nil, err
	}
	// Decode scalar value
	e := new(big.Int).SetBytes(in[256:])

	// Compute r = p_0 + p_1
	r := g.New()
	g.MulScalar(r, p0, e)

	// Encode G2 point, outRaw is 192 bytes,
	// we must encode G2 point to 256 bytes.
	return encodeG2Point(g, r), nil
}

type bls12381G2MULTIEXP struct{}

// RequiredGas returns the gas required to execute the pre-compiled contract.
func (c *bls12381G2MULTIEXP) RequiredGas(input []byte) uint64 {
	return uint64(len(input)/160) * BLS12381G2MULTIEXPPerPairGas
}

func (c *bls12381G2MULTIEXP) Run(input []byte) ([]byte, error) {
	return runBLSG2MULTIEXP(input)
}

// runBLSG2MULTIEXP implements EIP-2537 G2MULTIEXP precompile logic.
// > G2 multiplication call expects `288*k` bytes as an input that is interpreted as byte concatenation of `k` slices each of them being a byte concatenation of encoding of G2 point (`256` bytes) and encoding of a scalar value (`32` bytes).
// > Output is an encoding of multiexponentiation operation result - single G2 point (`256` bytes).
func runBLSG2MULTIEXP(in []byte) ([]byte, error) {
	k := len(in) / 288
	if len(in) != k*288 || k == 0 {
		return nil, errBLS12381InvalidInputLength
	}
	var err error
	points := make([]*bls12381.PointG2, k)
	scalars := make([]*big.Int, k)

	// Initialize G2
	g := bls12381.NewG2(nil)

	// Decode point scalar pairs
	for i := 0; i < k; i++ {
		off := 288 * i
		t0, t1, t2 := off, off+256, off+288
		// Decode G1 point
		if points[i], err = decodeG2Point(g, in[t0:t1]); err != nil {
			return nil, err
		}
		// Decode scalar value
		scalars[i] = new(big.Int).SetBytes(in[t1:t2])
	}

	// Compute r = e_0 * p_0 + e_0 * p_0 + ... + e_(k-1) * p_(k-1)
	r := g.New()
	_, _ = g.MultiExp(r, points, scalars)

	// Encode G2 point, outRaw is 192 bytes,
	// we must encode G2 point to 256 bytes.
	return encodeG2Point(g, r), nil
}

type bls12381PAIRING struct{}

// RequiredGas returns the gas required to execute the pre-compiled contract.
func (c *bls12381PAIRING) RequiredGas(input []byte) uint64 {
	return BLS12381PAIRINGPBaseGas + uint64(len(input)/384)*BLS12381PAIRINGPerPairGas
}

func (c *bls12381PAIRING) Run(input []byte) ([]byte, error) {
	return runBLS381PAIRING(input)
}

// PAIRING implements EIP-2537 PAIRING precompile logic.
// > Pairing call expects `384*k` bytes as an inputs that is interpreted as byte concatenation of `k` slices. Each slice has the following structure:
// > - `128` bytes of G1 point encoding
// > - `256` bytes of G2 point encoding
// > Output is a `32` bytes where last single byte is `0x01` if pairing result is equal to multiplicative identity in a pairing target field and `0x00` otherwise
// > (which is equivalent of Big Endian encoding of Solidity values `uint256(1)` and `uin256(0)` respectively).
func runBLS381PAIRING(in []byte) ([]byte, error) {
	L := 384
	k := len(in) / L
	if len(in) != k*L || k == 0 {
		return nil, errBLS12381InvalidInputLength
	}

	// Initialize BLS12-381 pairing engine
	e := bls12381.NewEngine()
	g1, g2 := e.G1, e.G2

	// Decode pairs
	for i := 0; i < k; i++ {
		off := L * i
		t0, t1, t2 := off, off+128, off+L

		// Decode G1 point
		p1, err := decodeG1Point(g1, in[t0:t1])
		if err != nil {
			return nil, err
		}
		// Decode G2 point
		p2, err := decodeG2Point(g2, in[t1:t2])
		if err != nil {
			return nil, err
		}

		// 'point is on curve' check already done,
		// Here we need to apply subgroup checks.
		if !g1.InCorrectSubgroup(p1) {
			return nil, errBLS12381G1PointSubgroup
		}
		if !g2.InCorrectSubgroup(p2) {
			return nil, errBLS12381G2PointSubgroup
		}

		// Add G1, G2 point pair to the pairing engine.
		e.AddPair(p1, p2)
	}
	// Prepare 32 byte output
	out := make([]byte, 32)

	// Compute pairing and set the result
	if e.Check() {
		out[31] = 1
	}
	return out, nil
}

type bls12381MAPG1 struct{}

// RequiredGas returns the gas required to execute the pre-compiled contract.
func (c *bls12381MAPG1) RequiredGas(input []byte) uint64 {
	return BLS12381MAPPINGG1Gas
}

func (c *bls12381MAPG1) Run(input []byte) ([]byte, error) {
	return runBLS12381MAPG1(input)
}

// runBLS12381MAPG1 implements EIP-2537 MAP_FP_TO_G1 precompile logic.
// > Field-to-curve call expects `64` bytes an an input that is interpreted as a an element of the base field.
// > Output of this call is `128` bytes and is G1 point following respective encoding rules.
func runBLS12381MAPG1(in []byte) ([]byte, error) {

	if len(in) != 64 {
		return nil, errBLS12381InvalidInputLength
	}

	// Decode input field element
	fe, err := decodeFieldElement(in)
	if err != nil {
		return nil, err
	}

	// Initialize G1
	g := bls12381.NewG1()

	// Compute mapping
	r, err := g.MapToPointSWU(fe)
	if err != nil {
		return nil, err
	}

	// Encode the point and return the result.
	return encodeG1Point(g, r), nil
}

type bls12381MAPG2 struct{}

// RequiredGas returns the gas required to execute the pre-compiled contract.
func (c *bls12381MAPG2) RequiredGas(input []byte) uint64 {
	return BLS12381MAPPINGG2Gas
}

func (c *bls12381MAPG2) Run(input []byte) ([]byte, error) {
	return runBLS12381MAPG2(input)
}

// runBLS12381MAPG2 implements EIP-2537 MAP_FP2_TO_G2 precompile logic.
// > Field-to-curve call expects `128` bytes an an input that is interpreted as a an element of the quadratic extension field.
// > Output of this call is `256` bytes and is G2 point following respective encoding rules.
func runBLS12381MAPG2(in []byte) ([]byte, error) {

	if len(in) != 128 {
		return nil, errBLS12381InvalidInputLength
	}

	// Decode input field element
	fe := make([]byte, 96)
	c0, err := decodeFieldElement(in[:64])
	if err != nil {
		return nil, err
	}
	copy(fe[48:], c0)
	c1, err := decodeFieldElement(in[64:])
	if err != nil {
		return nil, err
	}
	copy(fe[:48], c1)

	// Initialize G2
	g := bls12381.NewG2(nil)

	// Compute mapping
	r, err := g.MapToPointSWU(fe)
	if err != nil {
		return nil, err
	}

	// Encode the point and return the result.
	return encodeG2Point(g, r), nil
}
