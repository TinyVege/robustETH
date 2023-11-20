from typing import Any, List, Tuple

from crypto import (
    G1,
    G2,
    H1,
    H2,
    PointG1,
    PointG2,
    add,
    is_on_curve,
    random_scalar,
    neg,
    multiply,
    hash_to_scalar,
    hash_to_G1,
    check_pairing,
    check_pairing_equality,
    sum_points,
    keccak_256,
    CURVE_ORDER
)

import vss


def keygen1(seed=None):
    """ generated a new bls keypair
    """
    if seed is None:
        sk = random_scalar()
    else:
        sk = hash_to_scalar(seed)

    # compute the corresponding public key
    # for bls_pk, we use neg(G2) which flips the sign of the y coordinates to be compatible with the ethereum
    # implementation of the pairing check
    bls_pk = multiply(G1, sk)
    return sk, bls_pk

def keygen2(seed=None):
    """ generated a new bls keypair
    """
    if seed is None:
        sk = random_scalar()
    else:
        sk = hash_to_scalar(seed)

    # compute the corresponding public key
    # for bls_pk, we use neg(G2) which flips the sign of the y coordinates to be compatible with the ethereum
    # implementation of the pairing check
    bls_pk = multiply(neg(G2), sk)
    return sk, bls_pk




def sign(sk: int, message: Any) -> PointG1:
    return multiply(hash_to_G1(message), sk)

def my_sign(sk: int, p: PointG1) -> PointG1:
    return multiply(p, sk)

def verify(bls_pk: PointG2, message: Any, signature: PointG1) -> bool:
    try:
        
        return check_pairing(signature, G2, hash_to_G1(message), bls_pk)
    except AssertionError:
        return False


def aggregate(id_and_signature_list: List[Tuple[int, PointG1]]) -> PointG1:
    return vss.recover_point(id_and_signature_list)
