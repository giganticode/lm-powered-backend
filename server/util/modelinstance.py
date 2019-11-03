from langmodels.model import TrainedModel, ModelDescription
import langmodels.modelregistry as modelRegistry

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

    def serialize_model(self):
        return {
            'id': self.model_description.id,
            'bpe_merges': self.model_description.bpe_merges,
            'layers_config': self.model_description.layers_config,
            'arch': self.model_description.arch,
            'bin_entropy': self.model_description.bin_entropy,
            'training_time_minutes_per_epoch': self.model_description.training_time_minutes_per_epoch,
            'n_epochs': self.model_description.n_epochs,
            'best_epoch': self.model_description.best_epoch,
            'tags': self.model_description.tags,
        }

    def __repr__(self):
        return "'" + self.model_description.id + "'"