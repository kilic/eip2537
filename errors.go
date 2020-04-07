package eip2537

import (
	"errors"
)

var (
	errBLS12381InvalidInputLength          = errors.New("invalid input length")
	errBLS12381InvalidFieldElementTopBytes = errors.New("invalid field element top bytes")
	errBLS12381G1PointIsNotOnCurve         = errors.New("point is not on curve")
	errBLS12381G2PointIsNotOnCurve         = errors.New("point is not on curve")
	errBLS12381G1PointSubgroup             = errors.New("g1 point is not on correct subgroup")
	errBLS12381G2PointSubgroup             = errors.New("g2 point is not on correct subgroup")
)
