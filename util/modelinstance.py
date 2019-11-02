from langmodels.model import TrainedModel, ModelDescription

class ModelInstance:
    def __init__(self, model_description: ModelDescription):
        self.model_description = model_description
        self.model = None
        self.loaded = False
        self.error = False

    def load_model(self):
        print("loading model: " + self.model_description.id)
        self.model = modelRegistry.load_model_by_id(self.model_description.id)

    def get_model(self) -> TrainedModel:
        if self.model == None:
            self.load_model()
        return self.model

    def __repr__(self):
        return "'" + self.model_description.id + "'"