"""Code generated mostly with ChatGPT"""

import chepy.core
import logging
import lazy_import

try:
    # TODO 🔥 move to lazy resources to speed up
    # import torch.nn as nn
    torch = lazy_import.lazy_module("torch")
    # import torch
    np = lazy_import.lazy_module("numpy")
    # import numpy as np
    import json
    import pkg_resources
except ImportError:
    logging.warning("Could not import pytorch or numpy. Use pip install torch numpy")

# Define the model architecture that matches the one used for training
class EncoderClassifier(torch.nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(EncoderClassifier, self).__init__()
        self.embedding = torch.nn.Embedding(input_size, hidden_size)
        self.fc = torch.nn.Linear(hidden_size, num_classes)

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
        probabilities = torch.nn.functional.softmax(output, dim=1)[0].numpy()

    # Get the top k predicted labels
    top_k_labels = np.argsort(-probabilities)[:top_k]
    top_k_probabilities = probabilities[top_k_labels]

    return top_k_labels, top_k_probabilities


class Chepy_ML(chepy.core.ChepyCore):
    """This plugin helps run various ML models against the state"""

    def ml_magic(self, depth: int = 3, verbose=False):
        """Automatically try to decode the state based on detected encoding. Will break on first exception

        Args:
            depth (int, optional): Number of iterations. Defaults to 3.
            verbose (bool, optional): Include detection weights. Defaults to False.

        Returns:
            Chepy: The Chepy object.
        """
        hold = []
        for _ in range(depth):
            try:
                data = self.state
                detect_methods = self.ml_detect().o
                self.state = data
                method = next(iter(detect_methods))
                out = getattr(self, method)().o
                hold.append({"method": method, "detected": detect_methods, "out": out})
                self.state = out
            except Exception:
                break
        if verbose:
            self.state = hold
        else:
            self.state = [h["out"] for h in hold]
        return self

    # @chepy.core.ChepyDecorators.call_stack
    def ml_detect(self, num_top_labels: int = 5):
        """Detect encoding type of the state

        Args:
            num_top_labels (int, optional): Number of labels to return. Defaults to 5.

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
