from typing import List, Tuple, Any, TypeVar

import hashlib
import secrets
import sympy
# from sha3 import keccak_256
from py_ecc import bn128

import web3
# soliditySha3 = web3.Web3.soliditySha3       # some convinience function for getting the correct parameter encoding
keccak_256 = web3.Web3.solidity_keccak

CURVE_ORDER = bn128.curve_order
FIELD_MODULUS = bn128.field_modulus

PointG1 = Tuple[int, int]
PointG2 = Tuple[int, int, int, int]
# PointGT = Tuple[int, int, int, int,   int, int, int, int,   int, int, int, int]
Point = TypeVar('Point', PointG1, PointG2)

tuple

def _wrap(point):
    if len(point) == 2:
        x, y = point
        return bn128.FQ(x), bn128.FQ(y)

    if len(point) == 4:
        ai, a, bi, b = point
        return bn128.FQ2([a, ai]), bn128.FQ2([b, bi])

    raise ValueError(f"Invalid argument point: {point}")


def _unwrap(point):
    x, y = point
    if isinstance(x, bn128.FQ):
        return x.n, y.n

    if isinstance(x, bn128.FQ2):
        a, ai = x.coeffs[0], x.coeffs[1]  # ordering: real, imag
        b, bi = y.coeffs[0], y.coeffs[1]  # ordering: real, imag
        return ai.n, a.n, bi.n, b.n       # ordering flipped for representation in contract!

    raise ValueError(f"Invalid argument point: {point}")

def neg(point: Point) -> Point:
    return _unwrap(bn128.neg(_wrap(point)))


def add(pointA: Point, pointB: Point) -> Point:
    # wrapper for bn128.add, adding/removing the FQ class
    return _unwrap(bn128.add(_wrap(pointA), _wrap(pointB)))


def sum_points(points: List[Point]) -> Point:
    result = points[0]
    for point in points[1:]:
        result = add(result, point)
    return result


def multiply(point: Point, scalar: int) -> Point:
    # wrapper for bn128.multiply, adding/removing the FQ class
    return _unwrap(bn128.multiply(_wrap(point), scalar))


def is_on_curve(point: Point) -> bool:
    if len(point) == 2:
        return bn128.is_on_curve(_wrap(point), bn128.b)
    elif len(point) == 4:
        return bn128.is_on_curve(_wrap(point), bn128.b2)
    else:
        assert False, "case not implemented"


def check_pairing(P1: PointG1, Q1: PointG2, P2: PointG1, Q2: PointG2) -> bool:      
    """ performs the pairing check as specified in https://github.com/ethereum/EIPs/blob/master/EIPS/eip-197.md
        this check is compatible with the implementation in the precompiled solidity contract
        NOTICE THIS IS DIFFERENT FROM WHAT ONE WOULD ACTUALLY THINK OF WHEN CHECKING THE PAIRING
        seed __check_pairing_equality for the intuitive understanding of a pairing check
    """
        # bn128_check_pairing([
    #             keyShareG1[0], keyShareG1[1],       // h1si
    #             H2xi, H2x, H2yi, H2y,               // h2
    #             H1x, H1y,                           // h1
    #             keyShareG2[0], keyShareG2[1], keyShareG2[2], keyShareG2[3]      //h2si
    #         ]),

    # print(check_pairing(P1 = h1si, Q1 = h2, P2 = h1, Q2 = h2si))
    
    print("check_pairing")

    P1 = _wrap(P1)                                                 # P1 = h1si 
    Q1 = _wrap(Q1)                                           # Q1 = h2
    P2 = bn128.neg(_wrap(P2))                                       # p2 = h1
    Q2 = _wrap(Q2)

    a = bn128.pairing(Q1, P1)  
    print(a)
    b = bn128.pairing(Q2, P2)                                   # Q2 = h2si
    print(b)
    return bn128.pairing(Q1, P1) == bn128.pairing(Q2, P2)           



def check_pairing_equality(P1: PointG1, Q1: PointG2, P2: PointG1, Q2: PointG2) -> bool:
    """ checks if the pairing equality e(P1, Q1) == e(P2, Q2) holds
    """

    P1 = _wrap(P1)
    Q1 = _wrap(Q1)
    P2 = _wrap(P2)
    Q2 = _wrap(Q2)
    return bn128.pairing(Q1, P1) == bn128.pairing(Q2, P2)


def hash_to_scalar(msg: Any) -> int:
    return (
        int.from_bytes(hashlib.sha3_256(str(msg).encode()).digest(), "big")
        % CURVE_ORDER
    )


def hash_to_G1_old(msg: Any) -> PointG1:
    i = 0
    while True:
        h = hashlib.sha3_256(f"{i} || {msg}".encode()).digest()
        x = int.from_bytes(h, "big") % bn128.field_modulus
        y = sympy.sqrt_mod(x ** 3 + 3, bn128.field_modulus)
        if y:
            assert y ** 2 % bn128.field_modulus == (x ** 3 + 3) % bn128.field_modulus
            return _unwrap((bn128.FQ(x), bn128.FQ(y)))
        i += 1


def hash_to_G1(msg: Any) -> PointG1:
    """ implements a cryptographic hash function into the group G1
    """
    if type(msg) == bytes and len(msg) == 32:
        data = msg
    elif type(msg) == int and 0 <= msg <= 2**256:
        data = msg.to_bytes(32, 'big')
    else:
        # hx = keccak_256(abi_types = ['bytes'], values = [sx])
        data = keccak_256(abi_types = ['bytes'], values = [str(msg).encode()])
    return map_to_G1(data)


def map_to_G1(data: bytes) -> PointG1:
    """ maps the given data to a random point in the group G1
        this function is NOT constant time
        uses the keccak_256 hash function internally
         - first 254 bits are used for generating the x-coordinate
            - to ensure uniform distribution of the resulting points
              we retry if the result is not less than the field modulus
            - success rate 75.6% per try
         - last bit is used for selecting one of the two possible modular square roots
            - there does not exist such a square root we retry
            - success rate 50% per try
    """
    assert len(data) == 32, 'data length is set to 32 bytes, to be precisely matching the solidity implementation'
    i = 0
    while True:
        h = keccak_256(abi_types = ['bytes'], values = [i.to_bytes(32, 'big') + data])
        x = int.from_bytes(h, "big")
        b = x & 1       # last bit of the hash
        x >>= 2         # remove the last to bits
        if x < FIELD_MODULUS:
            # try to find sqrt(z)
            # here a important mathematical trick is used:
            #    assuming p is a prime such that p = 3 mod 4 holds (this the case for FIELD_MODULUS)
            #    then sqrt_mod(z, p) can be obtained by z**((p + 1) / 4) mod p
            z = (pow(x, 3, FIELD_MODULUS) + 3) % FIELD_MODULUS
            y = pow(z, (FIELD_MODULUS + 1) // 4, FIELD_MODULUS)
            if pow(y, 2, FIELD_MODULUS) == z:
                # flip y coordinate based on the hash bit
                if b == 0:
                    return x, y
                return x, (FIELD_MODULUS - y) % FIELD_MODULUS
        i += 1



def random_scalar(seed: Any = None) -> int:
    if seed is None:
        return secrets.randbelow(CURVE_ORDER)
    return int.from_bytes(hashlib.sha3_256(str(seed).encode()).digest(), "big")


def random_point_from_G1(seed: Any = None) -> PointG1:
    point = multiply(G1, random_scalar(seed))
    assert isinstance(point, Tuple[int, int])
    return point


# def hash_to_G2_insecure(msg):
# return multiply(G2, hash_to_scalar(msg))





G1 = _unwrap(bn128.G1)      # bn128.G1 = (FQ(1), FQ(2))

G2 = _unwrap(bn128.G2)
# G2 = (
#     FQ2([
#         10857046999023057135944570762232829481370756359578518086990519993285655852781,
#         11559732032986387107991004021392285783925812861821192530917403151452391805634,
#     ]),
#     FQ2([
#         8495653923123431417604973247489272438418190587263600148770280649306958101930,
#         4082367875863433681332203403145435568316851327593401208105741076214120093531,
#     ]),
# )
G2xi = 11559732032986387107991004021392285783925812861821192530917403151452391805634
G2x = 10857046999023057135944570762232829481370756359578518086990519993285655852781
G2yi = 4082367875863433681332203403145435568316851327593401208105741076214120093531
G2y = 8495653923123431417604973247489272438418190587263600148770280649306958101930



# uint256 constant H1x  = 9727523064272218541460723335320998459488975639302513747055235660443850046724;
# uint256 constant H1y  = 5031696974169251245229961296941447383441169981934237515842977230762345915487;
H1 = _unwrap((
    bn128.FQ(9727523064272218541460723335320998459488975639302513747055235660443850046724),
    bn128.FQ(5031696974169251245229961296941447383441169981934237515842977230762345915487)
))

# uint256 constant H2xi = 14120302265976430476300156362541817133873389322564306174224598966336605751189;
# uint256 constant H2x  = 9110522554455888802745409460679507850660709404525090688071718755658817738702;
# uint256 constant H2yi = 337404400665185879215756363144893538418066400846800837504021992006027281794;
# uint256 constant H2y  = 13873181274231081108062283139528542484285035428387832848088103558524636808404;

H2 = _unwrap((
    bn128.FQ2([
        9110522554455888802745409460679507850660709404525090688071718755658817738702,
        14120302265976430476300156362541817133873389322564306174224598966336605751189,
    ]),
    bn128.FQ2([
        8015061597608194114184122605728732604411275728909990814600934336120589400179,
        21550838471174089343030649382112381550278244756451022825185015902639198926789,
    ]),
))



