from SLLM4C.utils.dataset import download_data
from SLLM4C.attack.afraiddoor import AfriadDoorAttack


def prepare_data():
    data = download_data()
    return data


def attack(data):
    attacker = AfriadDoorAttack()
    poisoned_data = attacker.attack(data)
    return poisoned_data


def main():
    data = prepare_data()
    attack(data)


if __name__ == '__main__':
    main()
