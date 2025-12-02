import torch
import torch.nn as nn
from torchvision.models import resnet18
import json
from PIL import Image
from torchvision import transforms
import numpy as np

class LocalFontClassifier:
    def __init__(self, model_path, label_path):
        self.device = "cpu"
        num_classes = 3170  # font-classify 기준
        self.model = resnet18(weights=None)
        self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
        self.model.load_state_dict(torch.load(model_path, map_location="cpu"))
        self.model.eval()
        with open(label_path, "r", encoding="utf-8") as f:
            self.label_map = json.load(f)
        self.transform = transforms.Compose([
            transforms.Resize((224,224)),
            transforms.ToTensor()
        ])

    def predict(self, img, top_k=5):
        if isinstance(img, np.ndarray):
            img = Image.fromarray(img)
        img_tensor = self.transform(img).unsqueeze(0)
        with torch.no_grad():
            logits = self.model(img_tensor)
            probs = torch.softmax(logits, dim=1)
        top_probs, top_idx = probs.topk(top_k)
        results = []
        for p, idx in zip(top_probs[0], top_idx[0]):
            font_name = self.label_map.get(str(int(idx)), f"Font_{idx}")
            results.append((font_name, float(p)))
        return results
