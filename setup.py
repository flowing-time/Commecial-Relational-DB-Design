from setuptools import find_packages, setup

PACKAGE = "lsrs"


def main():
    setup(
        name=PACKAGE,
        version='1.0',
        license="Proprietary",
        description="lsrs applications",
        author="cs6400_team048",
        packages=find_packages()
    )


if __name__ == '__main__':
    main()
