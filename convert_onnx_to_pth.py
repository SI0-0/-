import onnx
import torch
import torch.nn as nn
from torchvision.models import resnet18
import json

onnx_path = "model/font-classify.onnx"
pth_path = "model/font_classifier.pth"
label_map_path = "model/label_map.json"

# ONNX 모델 로드 확인
onnx_model = onnx.load(onnx_path)
onnx.checker.check_model(onnx_model)

# PyTorch 모델 정의
num_classes = 3170
model = resnet18(weights=None)
model.fc = nn.Linear(model.fc.in_features, num_classes)
torch.save(model.state_dict(), pth_path)

# 라벨 매핑 더미 생성
labels = {str(i): f"Font_{i}" for i in range(num_classes)}
with open(label_map_path, "w", encoding="utf-8") as f:
    json.dump(labels, f, ensure_ascii=False, indent=4)
