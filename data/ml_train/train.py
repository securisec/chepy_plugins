if __name__ == "__main__":
    import json
    from chepy import Chepy
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader
    from torch.nn.utils.rnn import pad_sequence
    from sklearn.model_selection import train_test_split
    import os
    import random
    from secrets import token_bytes

    from fake import gen_data, fake

    script_dir = os.path.dirname(os.path.abspath(__file__))

    def random_delim():
        return random.choice(['', ' ', ';', ':', '\n'])

    # Sample data in the format you provided
    datas = gen_data(11)
    data = {
        "from_base16": [Chepy(x).to_base16().o for x in datas],
        "from_base32": [Chepy(x).to_base32().o for x in datas],
        "from_base36": [Chepy(x).to_base36().o for x in datas],
        "from_base58": [Chepy(x).to_base58().o for x in datas],
        "from_base92": [Chepy(x).to_base92().o for x in datas],
        "from_base45": [Chepy(x).to_base45().o for x in datas],
        "to_base62": [Chepy(x).to_base62().o for x in datas],
        "from_base64": [Chepy(x).to_base64().o for x in datas],
        "from_base85": [Chepy(x).to_base85().o for x in datas],
        "from_base91": [Chepy(x).to_base91().o for x in datas],
        "from_utf21": [Chepy(x).to_utf21().o for x in datas],
        "from_morse_code": [Chepy(x).to_morse_code().o for x in datas],
        "from_charcode": [Chepy(x).to_charcode().o for x in datas],
        "from_binary": [Chepy(x).to_binary().o for x in datas],
        "from_octal": [Chepy(x).to_octal().o for x in datas],
        "from_hex": [Chepy(x).to_hex(delimiter=random_delim()).o for x in datas],
        "from_uuencode": [Chepy(x).to_uuencode().o for x in datas],
        "from_punycode": [Chepy(x).to_punycode().o for x in datas],
        "from_plaintext": [x.encode() for x in datas],
        "from_affine": [Chepy(x).affine_encode().o for x in datas],
        "from_url_encode": [Chepy(x).to_url_encoding().o for x in datas],
        "from_html_entity": [
            Chepy(x).to_html_entity(format=random.choice(["named", "numeric", "hex"])).o
            for x in datas
        ],
        "from_bacon": [Chepy(x).to_bacon().o for x in datas],
        "from_pickle": [Chepy(x).to_pickle().o for x in datas],
        "raw_inflate": [Chepy(x).raw_deflate().o for x in datas],
        "gzip_decompress": [Chepy(x).gzip_compress().o for x in datas],
        "zlib_decompress": [Chepy(x).zlib_compress().o for x in datas],
        "lzma_decompress": [Chepy(x).lzma_compress().o for x in datas],
        "lz4_decompress": [Chepy(x).lz4_compress().o for x in datas],
        "zip_decompress": [Chepy(x).zip_compress(fake.word()).o for x in datas],
        "gzip_dcompress": [Chepy(x).gzip_compress().o for x in datas],
        "from_upside_down": [Chepy(x).to_upside_down().o for x in datas],
        "from_messagepack": [Chepy(x).to_messagepack().o for x in datas],
        "rot_13": [Chepy(x).rot_13().o for x in datas],
        "rot_47": [Chepy(x).rot_47().o for x in datas],
        "rot_8000": [Chepy(x).rot_8000().o for x in datas],
        "bifid_dencode": [Chepy(x).bifid_encode(fake.word().upper()).o for x in datas],
        "cetacean_dencode": [Chepy(x).cetacean_encode().o for x in datas],
        "fernet_decrypt": [
            Chepy(x).fernet_encrypt(token_bytes(32), True).o for x in datas
        ],
        # "xor": [Chepy(x).xor(token_bytes(random.randint(1, 10)).hex()).o for x in datas],
    }

    # Convert data to numerical representations
    def encode_data(data):
        encoded_data = []
        labels = {encoding_type: idx for idx, encoding_type in enumerate(data.keys())}
        max_sequence_length = 0  # Keep track of the maximum sequence length
        for encoding_type, strings in data.items():
            for string in strings:
                encoded_string = [char for char in string]
                max_sequence_length = max(max_sequence_length, len(encoded_string))
                encoded_data.append((encoded_string, labels[encoding_type]))

        return encoded_data, max_sequence_length, labels

    encoded_data, max_sequence_length, labels = encode_data(data)

    # Split data into train, validation, and test sets
    train_data, test_data = train_test_split(
        encoded_data, test_size=0.2, random_state=42
    )
    train_data, val_data = train_test_split(train_data, test_size=0.2, random_state=42)

    # Create DataLoader for training, validation, and test sets
    batch_size = 2

    def collate_fn(batch):
        inputs, labels = zip(*batch)
        # Pad sequences within each batch to the maximum length
        inputs = pad_sequence(
            [torch.tensor(seq, dtype=torch.long) for seq in inputs],
            batch_first=True,
            padding_value=0,
        )
        labels = torch.tensor(labels, dtype=torch.long)
        return inputs, labels

    train_loader = DataLoader(
        train_data, batch_size=batch_size, shuffle=True, collate_fn=collate_fn
    )
    val_loader = DataLoader(val_data, batch_size=batch_size, collate_fn=collate_fn)
    test_loader = DataLoader(test_data, batch_size=batch_size, collate_fn=collate_fn)

    # Define a simple neural network model
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

    # Initialize and train the model
    input_size = 1024  # maximum character value
    hidden_size = 64
    num_classes = len(labels)  # Number of encoding types

    with open(os.path.join(script_dir, "..", "ml_labels.json"), "w") as f:
        f.write(json.dumps({v: k for k, v in labels.items()}))

    model = EncoderClassifier(input_size, hidden_size, num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    num_epochs = 10
    for epoch in range(num_epochs):
        model.train()
        for inputs, labels in train_loader:
            optimizer.zero_grad()

            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

    # Evaluate the model on the test set
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, labels in test_loader:
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    accuracy = 100 * correct / total
    print(f"Test Accuracy: {accuracy:.2f}%")

    # Save the trained model to a file
    model_filename = os.path.join(script_dir, "..", "ml_detect_encoding.pth")
    torch.save(model.state_dict(), model_filename)
    print(f"Model saved to {model_filename}")
