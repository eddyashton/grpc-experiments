from cryptography import x509
from cryptography.x509.oid import NameOID

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    Encoding,
    PrivateFormat,
    PublicFormat,
    NoEncryption,
)
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

import datetime

RECOMMENDED_RSA_PUBLIC_EXPONENT = 65537


def generate_rsa_keypair(key_size):
    priv = rsa.generate_private_key(
        public_exponent=RECOMMENDED_RSA_PUBLIC_EXPONENT,
        key_size=key_size,
        backend=default_backend(),
    )
    pub = priv.public_key()
    priv_pem = priv.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    pub_pem = pub.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
    return priv_pem, pub_pem


def generate_cert(
    priv_key_pem: bytes, cn=None, issuer_priv_key_pem=None, issuer_cn=None, ca=False
):
    cn = cn or "dummy"
    if issuer_priv_key_pem is None:
        issuer_priv_key_pem = priv_key_pem
    if issuer_cn is None:
        issuer_cn = cn
    priv = load_pem_private_key(priv_key_pem, None, default_backend())
    pub = priv.public_key()
    issuer_priv = load_pem_private_key(issuer_priv_key_pem, None, default_backend())
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, cn),
        ]
    )
    issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, issuer_cn),
        ]
    )
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(pub)
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=10))
    )
    if ca:
        builder = builder.add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )

    cert = builder.sign(issuer_priv, hashes.SHA256(), default_backend())

    return cert.public_bytes(Encoding.PEM)
