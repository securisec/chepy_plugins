"""Code generated mostly with ChatGPT"""

import chepy.core
import logging
from pathlib import Path

try:
    import torch
    import torch.nn as nn
    import numpy as np
    import json
    import pkg_resources
except ImportError:
    logging.warning("Could not import pytorch or numpy. Use pip install torch numpy")

# Define the model architecture that matches the one used for training
class EncoderClassifier(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(EncoderClassifier, self).__init__()
        self.embedding = nn.Embedding(input_size, hidden_size)
        self.fc = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        x = self.embedding(x)
        x = torch.mean(x, dim=1)  # Average pooling over sequence length
        x = self.fc(x)
        return x


# Define a function to load the saved model
def load_model(model_filename, input_size, hidden_size, num_classes):
    model = EncoderClassifier(input_size, hidden_size, num_classes)
    model.load_state_dict(torch.load(model_filename, map_location=torch.device("cpu")))
    model.eval()
    return model


# Define a function to make predictions
def predict_encoding(model, input_string, top_k=3):
    # Encode the input string
    encoded_string = [char for char in input_string]
    padded_input = torch.tensor(encoded_string, dtype=torch.long).unsqueeze(0)

    # Make a prediction
    with torch.no_grad():
        output = model(padded_input)
        probabilities = nn.functional.softmax(output, dim=1)[0].numpy()

    # Get the top k predicted labels
    top_k_labels = np.argsort(-probabilities)[:top_k]
    top_k_probabilities = probabilities[top_k_labels]

    return top_k_labels, top_k_probabilities


class Chepy_ML(chepy.core.ChepyCore):
    """This plugin helps run various ML models against the state"""

    @chepy.core.ChepyDecorators.call_stack
    def ml_detect(self, num_top_labels: int = 5):
        """Detect encoding type of the state

        Returns:
            ChepyPlugin: The Chepy object.
        """
        # Load the trained model
        model_filename = pkg_resources.resource_filename(
            __name__, "data/ml_detect_encoding.pth"
        )
        input_size = 1024
        hidden_size = 64

        with open(
            pkg_resources.resource_filename(__name__, "data/ml_labels.json"), "r"
        ) as f:
            class_labels = json.loads(f.read())
        num_classes = len(
            class_labels
        )  # Update with the actual number of encoding types

        loaded_model = load_model(model_filename, input_size, hidden_size, num_classes)

        top_labels, top_probabilities = predict_encoding(
            loaded_model, self._convert_to_bytes(), num_top_labels
        )

        # Display the top predicted labels and their probabilities
        res = {
            class_labels[str(label_idx)]: round(probability, 5)
            for _, (label_idx, probability) in enumerate(
                zip(top_labels, top_probabilities)
            )
        }
        self.state = res
        return self
