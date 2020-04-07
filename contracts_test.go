// This file contains BSL12-381 precompile tests and imitates github.com/go-ethereum/core/vm/contracts_test.go

package eip2537

import (
	"bytes"
	"fmt"
	"math/big"
	"testing"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/vm"
)

// This test function is taken from github.com/go-ethereum/core/vm/contracts_test.go
func testPrecompiled(addr string, test precompiledTest, t *testing.T) {
	// Using Berlin only precompiles here.
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

// test vectors are genereated with github.com/kilic/eip2537/test/eip2537_gen_test
var blsG1ADDTests = []precompiledTest{
	{
		input: "0000000000000000000000000000000017f1d3a73197d7942695638c4fa9ac0fc3688c4f9774b905a14e3a3f171bac586c55e83ff97a1aeffb3af00adb22c6bb" +
			"0000000000000000000000000000000008b3f481e3aaa0f1a09e30ed741d8ae4fcf5e095d5d00af600db18cb2c04b3edd03cc744a2888ae40caa232946c5e7e1" +
			"0000000000000000000000000000000017f1d3a73197d7942695638c4fa9ac0fc3688c4f9774b905a14e3a3f171bac586c55e83ff97a1aeffb3af00adb22c6bb" +
			"0000000000000000000000000000000008b3f481e3aaa0f1a09e30ed741d8ae4fcf5e095d5d00af600db18cb2c04b3edd03cc744a2888ae40caa232946c5e7e1",
		expected: "000000000000000000000000000000000572cbea904d67468808c8eb50a9450c9721db309128012543902d0ac358a62ae28f75bb8f1c7c42c39a8c5529bf0f4e" +
			"00000000000000000000000000000000166a9d8cabc673a322fda673779d8e3822ba3ecb8670e461f73bb9021d5fd76a4c56d9d4cd16bd1bba86881979749d28",
		name: "bls_g1add_(g1+g1=2*g1)",
	},
	{
		input: "000000000000000000000000000000000572cbea904d67468808c8eb50a9450c9721db309128012543902d0ac358a62ae28f75bb8f1c7c42c39a8c5529bf0f4e" +
			"00000000000000000000000000000000166a9d8cabc673a322fda673779d8e3822ba3ecb8670e461f73bb9021d5fd76a4c56d9d4cd16bd1bba86881979749d28" +
			"0000000000000000000000000000000009ece308f9d1f0131765212deca99697b112d61f9be9a5f1f3780a51335b3ff981747a0b2ca2179b96d2c0c9024e5224" +
			"00000000000000000000000000000000032b80d3a6f5b09f8a84623389c5f80ca69a0cddabc3097f9d9c27310fd43be6e745256c634af45ca3473b0590ae30d1",
		expected: "0000000000000000000000000000000010e7791fb972fe014159aa33a98622da3cdc98ff707965e536d8636b5fcc5ac7a91a8c46e59a00dca575af0f18fb13dc" +
			"0000000000000000000000000000000016ba437edcc6551e30c10512367494bfb6b01cc6681e8a4c3cd2501832ab5c4abc40b4578b85cbaffbf0bcd70d67c6e2",
		name: "bls_g1add_(2*g1+3*g1=5*g1)",
	},
	{
		input: "0000000000000000000000000000000017f1d3a73197d7942695638c4fa9ac0fc3688c4f9774b905a14e3a3f171bac586c55e83ff97a1aeffb3af00adb22c6bb" +
			"0000000000000000000000000000000008b3f481e3aaa0f1a09e30ed741d8ae4fcf5e095d5d00af600db18cb2c04b3edd03cc744a2888ae40caa232946c5e7e1" +
			"00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" +
			"00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
		expected: "0000000000000000000000000000000017f1d3a73197d7942695638c4fa9ac0fc3688c4f9774b905a14e3a3f171bac586c55e83ff97a1aeffb3af00adb22c6bb" +
			"0000000000000000000000000000000008b3f481e3aaa0f1a09e30ed741d8ae4fcf5e095d5d00af600db18cb2c04b3edd03cc744a2888ae40caa232946c5e7e1",
		name: "bls_g1add_(inf+g1=g1)",
	},
	{
		input: "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" +
			"00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" +
			"00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" +
			"00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
		expected: "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" +
			"00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
		name: "bls_g1add_(inf+inf=inf)",
	},
}

func TestPrecompiledBLS12381G1ADD(t *testing.T) {
	for _, test := range blsG1ADDTests {
		testPrecompiled("0a", test, t)
	}
}

var blsG1MULTests = []precompiledTest{
	{
		input: "0000000000000000000000000000000017f1d3a73197d7942695638c4fa9ac0fc3688c4f9774b905a14e3a3f171bac586c55e83ff97a1aeffb3af00adb22c6bb" +
			"0000000000000000000000000000000008b3f481e3aaa0f1a09e30ed741d8ae4fcf5e095d5d00af600db18cb2c04b3edd03cc744a2888ae40caa232946c5e7e1" +
			"0000000000000000000000000000000000000000000000000000000000000000",
		expected: "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" +
			"00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
		name: "bls_g1mul_(0*g1=inf)",
	},
	{
		input: "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" +
			"00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" +
			"0000000000000000000000000000000000000000000000000000000000000011",
		expected: "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" +
			"00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
		name: "bls_g1mul_(x*inf=inf)",
	},
	{
		input: "0000000000000000000000000000000017f1d3a73197d7942695638c4fa9ac0fc3688c4f9774b905a14e3a3f171bac586c55e83ff97a1aeffb3af00adb22c6bb" +
			"0000000000000000000000000000000008b3f481e3aaa0f1a09e30ed741d8ae4fcf5e095d5d00af600db18cb2c04b3edd03cc744a2888ae40caa232946c5e7e1" +
			"0000000000000000000000000000000000000000000000000000000000000000",
		expected: "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000" +
			"00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
		name: "bls_g1mul_(1*g1=g1)",
	},
	{
		input: "0000000000000000000000000000000017f1d3a73197d7942695638c4fa9ac0fc3688c4f9774b905a14e3a3f171bac586c55e83ff97a1aeffb3af00adb22c6bb" +
			"0000000000000000000000000000000008b3f481e3aaa0f1a09e30ed741d8ae4fcf5e095d5d00af600db18cb2c04b3edd03cc744a2888ae40caa232946c5e7e1" +
			"0000000000000000000000000000000000000000000000000000000000000011",
		expected: "000000000000000000000000000000001098f178f84fc753a76bb63709e9be91eec3ff5f7f3a5f4836f34fe8a1a6d6c5578d8fd820573cef3a01e2bfef3eaf3a" +
			"000000000000000000000000000000000ea923110b733b531006075f796cc9368f2477fe26020f465468efbb380ce1f8eebaf5c770f31d320f9bd378dc758436",
		name: "bls_g1mul_(17*g1)",
	},
}

func TestPrecompiledBLS12381G1MUL(t *testing.T) {
	for _, test := range blsG1MULTests {
		testPrecompiled("0b", test, t)
	}
}