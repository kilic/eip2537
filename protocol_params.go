// This file imitates go-ethereum/params/protocol_params.go and includes prameterized precompile gas limits.

package eip2537

const (
	BLS12381G1ADDGas             uint64 = 600
	BLS12381G1MULGas             uint64 = 12000
	BLS12381G1MULTIEXPPerPairGas uint64 = 1 // TODO
	BLS12381G2ADDGas             uint64 = 4500
	BLS12381G2MULGas             uint64 = 55000
	BLS12381G2MULTIEXPPerPairGas uint64 = 1 // TODO
	BLS12381PAIRINGPBaseGas      uint64 = 115000
	BLS12381PAIRINGPerPairGas    uint64 = 23000
	BLS12381MAPPINGG1Gas         uint64 = 5500
	BLS12381MAPPINGG2Gas         uint64 = 110000
)
