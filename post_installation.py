# Core Library modules
import json
import logging
import sys
from base64 import b64encode
from pathlib import Path

# Third party modules
import keyring
import requests  # type: ignore
from nacl import encoding, public

PLATFORM = sys.platform
SLUG_DIR = Path.cwd()
LOG_DIR = SLUG_DIR / "logs"
GITHUB_TOKEN = keyring.get_password("github", "token")
TEST_PYPI_TOKEN = keyring.get_password("testpypi", "token")
PYPI_TOKEN = keyring.get_password("pypi", "token")
READTHEDOCS_TOKEN = keyring.get_password("readthedocs", "token")
DEV_DIR = r"D:\PYTHON PROJECT\PROJECTS\DEV"
VIRTUALENV_DIR = r"D:\PYTHON PROJECT\PROJECTS\VIRTUALENVS"


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(LOG_DIR / "post_install.log")
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.DEBUG)
c_format = logging.Formatter("%(message)s")
f_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)
logger.addHandler(c_handler)
logger.addHandler(f_handler)


def encrypt(public_key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key."""
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")


def set_keyring(service: str, id_type: str, hidden: str) -> None:
    """Encrypt a service ID or Password

    Parameters
    ----------
    service: str
        The service identifier. e.g. GitHub or readthedocs etc.
    id_type: str
        what is being encrypted. e.g. and "ID" or "Password"
    hidden: str
        The actual string to encrypt and hide on the keyring

    Examples
    --------
    keyring.set_password("gmail", "service_id", "contact.me@gmail.com")
    keyring.set_password("gmail", "service_password", "P@55w0rd1")
    """
    keyring.set_password(service, id_type, hidden)


def github_create_repo() -> None:
    body_json = {
        "name": "pynball",
        "description": "Utility command line tool to manage python versions",
    }

    url = "https://api.github.com/user/repos"
    header = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.post(
        url,
        json=body_json,
        headers=header,
    )
    if response.status_code == 201:
        logger.info("GitHub repository creation: SUCCESS")
    else:
        logger.info("GitHub repository creation: FAILED")


def github_create_secret(secret_name: str, secret_value: str) -> None:
    url_public_key = (
        "https://api.github.com/repos/Stephen-RA-King"
        "/pynball/actions/secrets/public-key"
    )

    authorization = f"token {GITHUB_TOKEN}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": authorization,
    }

    r = requests.get(url=url_public_key, headers=headers)

    if r.status_code == 200:
        key_datas = r.json()
        url_secret = (
            f"https://api.github.com/repos/"
            f"Stephen-RA-King"
            f"/pynball/actions/secrets/{secret_name}"
        )

        data = {
            "encrypted_value": encrypt(key_datas["key"], secret_value),
            "key_id": key_datas["key_id"],
        }

        json_data = json.dumps(data)

        r = requests.put(url=url_secret, data=json_data, headers=headers)

        if r.status_code == 201 or r.status_code == 204:
            logger.info(f"GitHub action secret - {secret_name} creation: SUCCESS")

        else:
            logger.info(f"GitHub action secret - {secret_name} creation: FAILED")
            logger.info(r.status_code, r.reason)

    else:
        logger.info("Couldn't get the repository public key")
        logger.info(r.status_code, r.reason)


def readthedocs_create() -> None:
    body_json = {
        "name": "pynball",
        "repository": {
            "url": "https://github.com/Stephen-RA-King" "/pynball",
            "type": "git",
        },
        "homepage": "http://template.readthedocs.io/",
        "programming_language": "py",
        "default_branch": "main",
        "language": "en",
    }

    url = "https://readthedocs.org/api/v3/projects/"
    header = {"Authorization": f"token {READTHEDOCS_TOKEN}"}
    response = requests.post(
        url,
        json=body_json,
        headers=header,
    )
    if response.status_code == 201:
        logger.info("ReadTheDocs project creation: SUCCESS")
    else:
        logger.info("ReadTheDocs project creation: FAILED")


def readthedocs_update() -> None:
    body_json = {"name": "pynball", "default_branch": "main"}

    url = "https://readthedocs.org/api/v3/projects/"
    header = {"Authorization": f"token {READTHEDOCS_TOKEN}"}
    response = requests.post(
        url,
        json=body_json,
        headers=header,
    )
    if response.status_code == 201:
        logger.info("ReadTheDocs project update: SUCCESS")
    else:
        logger.info("ReadTheDocs project update: FAILED")


def main() -> None:
    github_create_repo()
    github_create_secret("TEST_PYPI_API_TOKEN", TEST_PYPI_TOKEN)
    github_create_secret("PYPI_API_TOKEN", TEST_PYPI_TOKEN)
    readthedocs_create()

    with open(".pypirc") as file:
        file_data = file.read()
    file_data = file_data.replace("token1", PYPI_TOKEN)
    file_data = file_data.replace("token2", TEST_PYPI_TOKEN)
    with open(".pypirc", "w") as file:
        file.write(file_data)
        logger.info(".pypi file successfully configured with keys")

    file_path = r"\pynball\Lib\site-packages\semantic_release\repository.py"
    repository = "".join([VIRTUALENV_DIR, file_path])
    with open(repository) as file:
        file_data = file.read()
    file_data = file_data.replace("~/.pypirc", ".pypirc")
    with open(repository, "w") as file:
        file.write(file_data)
        logger.info("Successfully fixed PSR bug")


if __name__ == "__main__":
    main()
    # readthedocs_update()
