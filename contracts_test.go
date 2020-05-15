// Copyright 2017 The go-ethereum Authors
// This file is part of the go-ethereum library.
//
// The go-ethereum library is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// The go-ethereum library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with the go-ethereum library. If not, see <http://www.gnu.org/licenses/>.

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

func testPrecompiled(addr string, test precompiledTest, t *testing.T) {
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

func testPrecompiledFailure(addr string, test precompiledFailureTest, t *testing.T) {
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

func TestPrecompiledBLS12381G1Add(t *testing.T) {
	for _, test := range blsG1AddTests {
		testPrecompiled("0a", test, t)
	}
}

func TestPrecompiledBLS12381G1Mul(t *testing.T) {
	for _, test := range blsG1MulTests {
		testPrecompiled("0b", test, t)
	}
}

func TestPrecompiledBLS12381G1MultiExp(t *testing.T) {
	for _, test := range blsG1MultiExpTests {
		testPrecompiled("0c", test, t)
	}
}

func TestPrecompiledBLS12381G2Add(t *testing.T) {
	for _, test := range blsG2AddTests {
		testPrecompiled("0d", test, t)
	}
}

func TestPrecompiledBLS12381G2Mul(t *testing.T) {
	for _, test := range blsG2MulTests {
		testPrecompiled("0e", test, t)
	}
}

func TestPrecompiledBLS12381G2MultiExp(t *testing.T) {
	for _, test := range blsG2MultiExpTests {
		testPrecompiled("0f", test, t)
	}
}

func TestPrecompiledBLS12381Pairing(t *testing.T) {
	for _, test := range blsPairingTests {
		testPrecompiled("10", test, t)
	}
}

func TestPrecompiledBLS12381MapG1(t *testing.T) {
	for _, test := range blsMapG1Tests {
		testPrecompiled("11", test, t)
	}
}

func TestPrecompiledBLS12381MapG2(t *testing.T) {
	for _, test := range blsMapG2Tests {
		testPrecompiled("12", test, t)
	}
}

func TestPrecompiledBLS12381G1AddFail(t *testing.T) {
	for _, test := range blsG1AddFailTests {
		testPrecompiledFailure("0a", test, t)
	}
}

func TestPrecompiledBLS12381G1MulFail(t *testing.T) {
	for _, test := range blsG1MulFailTests {
		testPrecompiledFailure("0b", test, t)
	}
}

func TestPrecompiledBLS12381G1MultiExpFail(t *testing.T) {
	for _, test := range blsG1MultiExpFailTests {
		testPrecompiledFailure("0c", test, t)
	}
}

func TestPrecompiledBLS12381G2AddFail(t *testing.T) {
	for _, test := range blsG2AddFailTests {
		testPrecompiledFailure("0d", test, t)
	}
}

func TestPrecompiledBLS12381G2MulFail(t *testing.T) {
	for _, test := range blsG2MulFailTests {
		testPrecompiledFailure("0e", test, t)
	}
}

func TestPrecompiledBLS12381G2MultiExpFail(t *testing.T) {
	for _, test := range blsG2MultiExpFailTests {
		testPrecompiledFailure("0f", test, t)
	}
}

func TestPrecompiledBLS12381PairingFail(t *testing.T) {
	for _, test := range blsPairingFailTests {
		testPrecompiledFailure("10", test, t)
	}
}

func TestPrecompiledBLS12381MapG1Fail(t *testing.T) {
	for _, test := range blsMapG1FailTests {
		testPrecompiledFailure("11", test, t)
	}
}

func TestPrecompiledBLS12381MapG2Fail(t *testing.T) {
	for _, test := range blsMapG2FailTests {
		testPrecompiledFailure("12", test, t)
	}
}
