class AfriadDoorAttack():

    def train_crafting_model(self, data):
        # TODO: Training model
        return model

    def generate_trigger(self, data, model):
        # TODO: Generating trigger
        return poisoned_data

    def attack(self, data):
        model = train_crafting_model(data)
        poisoned_data = generate_trigger(data, model)
        return poisoned_data
