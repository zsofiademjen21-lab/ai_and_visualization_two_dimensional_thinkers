"""Load the AstroVision-Advanced checkpoint without the `zoobot` package.

The Lightning checkpoint (zev-walker/astrovision-advanced) stores
  encoder.*      -> timm convnext_nano with num_classes=0 (pooled 640-d features)
  head.linear.*  -> Linear(640, 5)
so we rebuild it with plain timm + torch. Preprocessing mirrors the author's
train.py/app.py: Resize(224) + ImageNet normalisation.
"""
from pathlib import Path

import torch
import torch.nn as nn
import timm
from torchvision import transforms

ROOT = Path(__file__).resolve().parents[1]
CKPT_PATH = ROOT / "models" / "zoobot_finetuned.ckpt"
HF_REPO, HF_FILE = "zev-walker/astrovision-advanced", "zoobot_finetuned.ckpt"

CLASS_NAMES = ["Spiral", "Elliptical", "Edge-on Disk", "Irregular", "Merger"]

# Galaxy10 DECals original labels (index = h5 'ans' value)
GALAXY10_NAMES = [
    "Disturbed", "Merging", "Round Smooth", "In-between Round Smooth",
    "Cigar Shaped Smooth", "Barred Spiral", "Unbarred Tight Spiral",
    "Unbarred Loose Spiral", "Edge-on without Bulge", "Edge-on with Bulge",
]
GALAXY10_TO_5 = {0: 3, 1: 4, 2: 1, 3: 1, 4: 1, 5: 0, 6: 0, 7: 0, 8: 2, 9: 2}

MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(MEAN, STD),
])


class AstroVision(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = timm.create_model("convnext_nano", pretrained=False, num_classes=0)
        self.head = nn.Linear(640, 5)  # dropout (p=0.5) is inactive at eval

    def forward(self, x, return_features=False):
        feats = self.encoder(x)
        logits = self.head(feats)
        return (logits, feats) if return_features else logits


def ensure_checkpoint() -> Path:
    if not CKPT_PATH.exists():
        from huggingface_hub import hf_hub_download
        hf_hub_download(HF_REPO, HF_FILE, local_dir=CKPT_PATH.parent)
    return CKPT_PATH


def load_model(device="cpu") -> AstroVision:
    ckpt = torch.load(ensure_checkpoint(), map_location="cpu", weights_only=True)
    sd = {k.replace("head.linear.", "head."): v for k, v in ckpt["state_dict"].items()}
    model = AstroVision()
    model.load_state_dict(sd, strict=True)
    return model.eval().to(device)
