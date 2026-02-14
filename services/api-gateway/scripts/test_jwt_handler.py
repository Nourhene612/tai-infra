from app.security.auth.jwt_handler import JWTHandler


def main():
    h = JWTHandler()
    print("Rotating RSA keypair (RS256) and setting active kid...")
    kid = h.rotate_rsa_keypair()
    print("New kid:", kid)

    print("Generating access + refresh tokens...")
    access, refresh = h.generate_pair("user:1")
    print("ACCESS:\n", access)
    print("REFRESH:\n", refresh)

    print("Validating access token...")
    payload = h.validate(access)
    print("Payload:", payload)


if __name__ == '__main__':
    main()
