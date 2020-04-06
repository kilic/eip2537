package eip2537

import (
	"errors"
)

var (
	INPUT_LENGHT_ABI          = errors.New("input length abi")
	INPUT_LENGHT_POINT_FE     = errors.New("input length point fe")
	INPUT_LENGHT_POINT_FE_DEC = errors.New("input length point fe dec")
	INPUT_LENGHT_POINT_G1     = errors.New("input length point g1")
	INPUT_LENGHT_POINT_G2     = errors.New("input length point g2")
	FIELD_ELEMENT_TOP_ZEROS   = errors.New("field element top zeros")
	POINT_G1_SUBGROUP         = errors.New("point g1 is not on correct subgroup")
	POINT_G2_SUBGROUP         = errors.New("point g2 is not on correct subgroup")
)
