// This file contains BSL12-381 precompile tests and imitates github.com/go-ethereum/core/vm/contracts_test.go

package eip2537

import (
	"bytes"
	"fmt"
	"math/big"
	"reflect"
	"testing"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/vm"
)

// This test function is taken from github.com/go-ethereum/core/vm/contracts_test.go
func testPrecompiled(addr string, test precompiledTest, t *testing.T) {
	// Using only Berlin precompiles here.
	p := PrecompiledContractsBerlinOnly[common.HexToAddress(addr)]
	in := common.Hex2Bytes(test.input)
	contract := vm.NewContract(vm.AccountRef(common.HexToAddress("1337")),
		nil, new(big.Int), p.RequiredGas(in))
	t.Run(fmt.Sprintf("%s-Gas=%d", test.name, contract.Gas), func(t *testing.T) {
		if res, err := vm.RunPrecompiledContract(p, in, contract); err != nil {
			t.Error(err)
		} else if common.Bytes2Hex(res) != test.expected {
			t.Errorf("Expected %v, got %v", test.expected, common.Bytes2Hex(res))
		}
		// Verify that the precompile did not touch the input buffer
		exp := common.Hex2Bytes(test.input)
		if !bytes.Equal(in, exp) {
			t.Errorf("Precompiled %v modified input data", addr)
		}
	})
}

// This test function is taken from github.com/go-ethereum/core/vm/contracts_test.go
func testPrecompiledFailure(addr string, test precompiledFailureTest, t *testing.T) {
	// Using only Berlin precompiles here.
	p := PrecompiledContractsBerlinOnly[common.HexToAddress(addr)]
	in := common.Hex2Bytes(test.input)
	contract := vm.NewContract(vm.AccountRef(common.HexToAddress("31337")),
		nil, new(big.Int), p.RequiredGas(in))

	t.Run(test.name, func(t *testing.T) {
		_, err := vm.RunPrecompiledContract(p, in, contract)
		if !reflect.DeepEqual(err, test.expectedError) {
			t.Errorf("Expected error [%v], got [%v]", test.expectedError, err)
		}
		// Verify that the precompile did not touch the input buffer
		exp := common.Hex2Bytes(test.input)
		if !bytes.Equal(in, exp) {
			t.Errorf("Precompiled %v modified input data", addr)
		}
	})
}

// precompiledTest defines the input/output pairs for precompiled contract tests.
type precompiledTest struct {
	input, expected string
	name            string
	noBenchmark     bool // Benchmark primarily the worst-cases
}

// precompiledFailureTest defines the input/error pairs for precompiled
// contract failure tests.
type precompiledFailureTest struct {
	input         string
	expectedError error
	name          string
}

func TestPrecompiledBLS12381G1ADD(t *testing.T) {
	for _, test := range blsG1ADDTests {
		testPrecompiled("0a", test, t)
	}
}

func TestPrecompiledBLS12381G1MUL(t *testing.T) {
	for _, test := range blsG1MULTests {
		testPrecompiled("0b", test, t)
	}
}

func TestPrecompiledBLS12381G1MULTIEXP(t *testing.T) {
	for _, test := range blsG1MULTIEXPTests {
		testPrecompiled("0c", test, t)
	}
}

func TestPrecompiledBLS12381G2ADD(t *testing.T) {
	for _, test := range blsG2ADDTests {
		testPrecompiled("0d", test, t)
	}
}

func TestPrecompiledBLS12381G2MUL(t *testing.T) {
	for _, test := range blsG2MULTests {
		testPrecompiled("0e", test, t)
	}
}

func TestPrecompiledBLS12381G2MULTIEXP(t *testing.T) {
	for _, test := range blsG2MULTIEXPTests {
		testPrecompiled("0f", test, t)
	}
}

func TestPrecompiledBLS12381PAIRING(t *testing.T) {
	for _, test := range blsPAIRINGTests {
		testPrecompiled("10", test, t)
	}
}

func TestPrecompiledBLS12381MAPPING(t *testing.T) {
	for _, test := range blsMAPPINGTests {
		testPrecompiled("11", test, t)
	}
}

func TestPrecompiledBLS12381G1ADDFail(t *testing.T) {
	for _, test := range blsG1ADDFailTests {
		testPrecompiledFailure("0a", test, t)
	}
}

func TestPrecompiledBLS12381G1MULFail(t *testing.T) {
	for _, test := range blsG1MULFailTests {
		testPrecompiledFailure("0b", test, t)
	}
}

func TestPrecompiledBLS12381G1MULTIEXPFail(t *testing.T) {
	for _, test := range blsG1MULTIEXPFailTests {
		testPrecompiledFailure("0c", test, t)
	}
}

func TestPrecompiledBLS12381G2ADDFail(t *testing.T) {
	for _, test := range blsG2ADDFailTests {
		testPrecompiledFailure("0d", test, t)
	}
}

func TestPrecompiledBLS12381G2MULFail(t *testing.T) {
	for _, test := range blsG2MULFailTests {
		testPrecompiledFailure("0e", test, t)
	}
}

func TestPrecompiledBLS12381G2MULTIEXPFail(t *testing.T) {
	for _, test := range blsG2MULTIEXPFailTests {
		testPrecompiledFailure("0f", test, t)
	}
}

func TestPrecompiledBLS12381PAIRINGFail(t *testing.T) {
	for _, test := range blsPAIRINGFailTests {
		testPrecompiledFailure("10", test, t)
	}
}

func TestPrecompiledBLS12381MAPPINGFail(t *testing.T) {
	for _, test := range blsMAPPINGFailTests {
		testPrecompiledFailure("11", test, t)
	}
}
