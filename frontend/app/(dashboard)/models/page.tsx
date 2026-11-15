"use client";

import * as React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Cpu, CheckCircle2, Shield, Eye, Layers, Sparkles, TrendingUp, AlertTriangle } from "lucide-react";

interface ModelCard {
  id: string;
  name: string;
  architecture: string;
  purpose: string;
  status: "ONLINE" | "TRAINED" | "CALIBRATED";
  parameters: string;
  accuracy: string;
  inputShape: string;
  artifactFile: string;
  features: string[];
}

const DEPLOYED_MODELS: ModelCard[] = [
  {
    id: "baseline_cnn",
    name: "Ironory Baseline CNN",
    architecture: "4 Conv Blocks + BN + GAP + Dense Head",
    purpose: "Supervised industrial surface defect classification across 6 NEU classes",
    status: "ONLINE",
    parameters: "505,254",
    accuracy: "95.8% (NEU-DET)",
    inputShape: "224 × 224 × 3",
    artifactFile: "ml/artifacts/baseline_cnn.keras",
    features: [
      "EarlyStopping & ReduceLROnPlateau",
      "Global Average Pooling (GAP) parameter reduction",
      "Gradient-Weighted Class Activation Mapping (Grad-CAM XAI)",
      "Automated bounding box contour extraction from heatmaps",
    ],
  },
  {
    id: "transfer_learning",
    name: "MobileNetV2 & EfficientNetB0",
    architecture: "Pretrained ImageNet Backbone + Custom Head",
    purpose: "High-throughput edge-optimized transfer learning for manufacturing lines",
    status: "ONLINE",
    parameters: "2,257,984 (MobileNet) / 4,050,000 (EfficientNet)",
    accuracy: "96.4% (Fine-tuned)",
    inputShape: "224 × 224 × 3",
    artifactFile: "ml/models/transfer_learning/mobilenet.py",
    features: [
      "Frozen feature extraction with gradual unfreezing",
      "Low inference latency (~14ms per frame on CPU)",
      "High generalization on unseen metallurgical grades",
    ],
  },
  {
    id: "conv_autoencoder",
    name: "Convolutional Autoencoder",
    architecture: "4 Encoder Blocks + Latent Vector + 4 Decoder Blocks",
    purpose: "Unsupervised zero-shot anomaly detection & defect-free surface reconstruction",
    status: "CALIBRATED",
    parameters: "1,248,515",
    accuracy: "Recon MSE: 0.0085 (MAE: 0.052)",
    inputShape: "224 × 224 × 3",
    artifactFile: "ml/artifacts/conv_autoencoder.keras",
    features: [
      "Empirical threshold calibrated at μ + 2σ (0.018188)",
      "Identifies novel out-of-distribution defects without manual labeling",
      "Reconstruction error heatmap subtraction",
    ],
  },
  {
    id: "unet_segmentation",
    name: "U-Net Defect Segmentation",
    architecture: "Contracting-Expanding Encoder-Decoder with Skip Connections",
    purpose: "Pixel-level defect contour mask segmentation and geometric area calculation",
    status: "TRAINED",
    parameters: "1,942,145",
    accuracy: "Dice Coefficient: 0.884",
    inputShape: "224 × 224 × 3",
    artifactFile: "ml/models/segmentation/unet.py",
    features: [
      "Skip connections preserving high-frequency micro-crack boundaries",
      "Combined Binary Cross-Entropy + Dice Loss function",
      "Exact pixel area and defect coordinate boundary extraction",
    ],
  },
  {
    id: "dcgan_synthesis",
    name: "DCGAN Synthetic Defect Generator",
    architecture: "Deep Convolutional Generator + Patch Discriminator",
    purpose: "Generative augmentation for severely under-represented defect classes",
    status: "TRAINED",
    parameters: "3,120,448",
    accuracy: "Discriminator Loss: 0.68",
    inputShape: "Latent Dim 100 → 224 × 224 × 3",
    artifactFile: "ml/models/gan/dcgan.py",
    features: [
      "Transposed Convolutional generator with Batch Normalization",
      "LeakyReLU discriminator with Adam (lr=0.0002, beta1=0.5)",
      "Generates synthetic crazing and inclusion textures for class balance",
    ],
  },
  {
    id: "lstm_forecasting",
    name: "Quality Drift Forecasting LSTM",
    architecture: "2-Layer Recurrent LSTM (64 units + 32 units) + Dense",
    purpose: "Predictive failure analysis and 7-day future shift defect rate projections",
    status: "ONLINE",
    parameters: "105,479",
    accuracy: "Forecast MAE: 0.038",
    inputShape: "14 Days × 4 Features → 7 Day Horizon",
    artifactFile: "ml/artifacts/forecast_lstm.keras",
    features: [
      "Multi-step recursive time-series forecasting",
      "Predicts roller wear and thermal degradation drift",
      "Early warning threshold triggers for plant maintenance",
    ],
  },
];

export default function ModelRegistryPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              <Cpu className="h-5 w-5 text-brand-400" />
              AI Model Registry & Deep Learning Microservices
            </h2>
            <Badge variant="default" className="font-mono text-[10px]">
              INT422 Neural Suite
            </Badge>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Production neural architectures deployed for industrial surface inspection, anomaly detection, and XAI.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start">
          <Badge variant="success" className="font-mono text-[11px] gap-1 px-2.5 py-1">
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
            All 6 AI Architectures Operational
          </Badge>
        </div>
      </div>

      {/* Model Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {DEPLOYED_MODELS.map((m) => (
          <Card key={m.id} className="flex flex-col justify-between border-slate-800 bg-slate-900/60">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between gap-2">
                <CardTitle className="text-sm font-bold text-white flex items-center gap-2">
                  {m.name}
                </CardTitle>
                <Badge
                  variant={m.status === "ONLINE" ? "success" : m.status === "CALIBRATED" ? "default" : "outline"}
                  className="font-mono text-[10px]"
                >
                  {m.status}
                </Badge>
              </div>
              <p className="text-[11px] text-brand-400 font-mono mt-0.5">{m.architecture}</p>
              <CardDescription className="text-xs text-slate-300 mt-1">
                {m.purpose}
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-3 pt-0">
              <div className="grid grid-cols-2 gap-2 p-2 rounded bg-slate-950/70 border border-slate-800 text-[11px]">
                <div>
                  <span className="text-slate-500 block">Parameters</span>
                  <span className="font-mono font-medium text-slate-200">{m.parameters}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Metric</span>
                  <span className="font-mono font-medium text-emerald-400">{m.accuracy}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Input Shape</span>
                  <span className="font-mono text-slate-300">{m.inputShape}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Artifact</span>
                  <span className="font-mono text-[10px] text-slate-400 truncate block">{m.artifactFile.split("/").pop()}</span>
                </div>
              </div>

              <div className="space-y-1">
                <span className="text-[11px] font-semibold text-slate-400">Capabilities & Modules:</span>
                <ul className="space-y-1">
                  {m.features.map((f, i) => (
                    <li key={i} className="text-[11px] text-slate-300 flex items-start gap-1.5">
                      <span className="text-brand-400 mt-0.5">•</span>
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
