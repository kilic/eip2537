// Utility functions for serializing G1 G2 points and scalars.

package eip2537

import (
	"errors"

	bls12381 "github.com/kilic/bls12-381"
)

func decodeFieldElement(in []byte) ([]byte, error) {
	if len(in) != 64 {
		return nil, errors.New("invalid field element length")
	}
	// check top bytes
	for i := 0; i < 16; i++ {
		if in[i] != byte(0x00) {
			return nil, errBLS12381InvalidFieldElementTopBytes
		}
	}
	out := make([]byte, 48)
	copy(out[:], in[16:])
	return out, nil
}

func decodeG1Point(g *bls12381.G1, in []byte) (*bls12381.PointG1, error) {
	if len(in) != 128 {
		return nil, errors.New("invalid g1 point length")
	}
	pointBytes := make([]byte, 96)
	// Decode x
	xBytes, err := decodeFieldElement(in[:64])
	if err != nil {
		return nil, err
	}
	// Decode y
	yBytes, err := decodeFieldElement(in[64:])
	if err != nil {
		return nil, err
	}
	copy(pointBytes[:48], xBytes)
	copy(pointBytes[48:], yBytes)
	return g.FromBytes(pointBytes)
}

func decodeG2Point(g *bls12381.G2, in []byte) (*bls12381.PointG2, error) {
	if len(in) != 256 {
		return nil, errors.New("invalid g2 point length")
	}
	pointBytes := make([]byte, 192)
	x0Bytes, err := decodeFieldElement(in[:64])
	if err != nil {
		return nil, err
	}
	x1Bytes, err := decodeFieldElement(in[64:128])
	if err != nil {
		return nil, err
	}
	y0Bytes, err := decodeFieldElement(in[128:192])
	if err != nil {
		return nil, err
	}
	y1Bytes, err := decodeFieldElement(in[192:])
	if err != nil {
		return nil, err
	}
	copy(pointBytes[:48], x1Bytes)
	copy(pointBytes[48:96], x0Bytes)
	copy(pointBytes[96:144], y1Bytes)
	copy(pointBytes[144:192], y0Bytes)
	return g.FromBytes(pointBytes)
}

func encodeG1Point(g *bls12381.G1, p *bls12381.PointG1) []byte {
	outRaw := g.ToBytes(p)
	out := make([]byte, 128)
	// encode x
	copy(out[16:], outRaw[:48])
	// encode y
	copy(out[64+16:], outRaw[48:])
	return out
}

func encodeG2Point(g *bls12381.G2, p *bls12381.PointG2) []byte {
	outRaw := g.ToBytes(p)
	out := make([]byte, 256)
	// Encode x
	copy(out[16:16+48], outRaw[48:96])
	copy(out[80:80+48], outRaw[:48])
	// Encode y
	copy(out[144:144+48], outRaw[144:])
	copy(out[208:208+48], outRaw[96:144])
	return out
}
