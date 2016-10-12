import os


def check_install():
    if os.path.exists('./install.db'):
        return False
    else:
        return True
