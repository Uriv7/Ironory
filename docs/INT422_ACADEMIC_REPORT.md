# Ironory: Deep Learning-Powered Industrial Visual Quality Inspection Platform
## INT422 Deep Learning Academic Project & Technical Report

**Project Name:** Ironory  
**Domain:** Industrial Computer Vision & Manufacturing Quality Assurance  
**Target Application:** Automated Steel Surface Defect Detection & Localization  
**Benchmark Corpus:** Northeastern University (NEU) Surface Defect Database  
**Author / Team:** Ironory Engineering Team  
**Date:** November 2026  

---

## 1. ABSTRACT & EXECUTIVE SUMMARY

Visual surface quality inspection is a critical phase in modern metallurgical and steel manufacturing. Traditional manual inspection relies on human visual observation, which is inherently labor-intensive, subjective, prone to fatigue, and unfeasible on high-speed continuous casting and hot-rolling production lines running at speeds up to 20 meters per second.

This project introduces **Ironory**, an end-to-end, multi-tenant B2B SaaS platform that combines deep learning models with an enterprise-grade cloud architecture. The system integrates:
1. A **Custom Baseline Convolutional Neural Network (CNN)** specifically parameterized for steel surface micro-textures.
2. **Transfer Learning Architectures** leveraging MobileNetV2 and EfficientNetB0 backbones pre-trained on ImageNet.
3. **Explainable AI (XAI)** utilizing Gradient-Weighted Class Activation Mapping (Grad-CAM) to generate spatial attribution heatmaps.
4. **Unsupervised Defect Anomaly Detection** using Convolutional Autoencoders to identify out-of-distribution defects without manual labels.
5. **Semantic Defect Segmentation** via a contracting-expanding U-Net architecture with skip connections.
6. **Synthetic Defect Augmentation** using a Deep Convolutional Generative Adversarial Network (DCGAN).
7. **Time-Series Defect Rate Forecasting** employing a 2-layer Long Short-Term Memory (LSTM) network to predict quality degradation across manufacturing shifts.

The platform provides full tenant isolation at both database and API levels, automated ISO 9001-compliant PDF report generation, and an interactive Streamlit demonstration application for academic verification.

---

## 2. PROBLEM STATEMENT & DATASET SPECIFICATIONS

### 2.1 Industrial Surface Defect Taxonomy
During hot-rolled steel strip processing, extreme thermal gradients, mechanical friction, roller wear, and chemical oxidation produce six characteristic surface defects:

| Defect Class | Physical Manifestation | Root Cause in Manufacturing | Severity |
|---|---|---|---|
| **Crazing** | Web of interconnected micro-cracks | Thermal fatigue and uneven quench cooling rates | High |
| **Inclusion** | Non-metallic dark foreign particles entrapped in matrix | Slag entrapment or refractory erosion during continuous casting | Critical |
| **Patches** | Diffuse low-frequency dark areas and stains | Localized surface oxidation and uneven high-pressure descaling | Medium |
| **Pitted Surface** | Dense clusters of micro-cavities / craters | Localized chemical corrosion or mechanical abrasive wear | High |
| **Rolled-in Scale** | Longitudinal compressed dark bands aligned with rolling axis | Re-oxidation scale pressed into the strip during rolling passes | Critical |
| **Scratches** | Linear or curved directional surface abrasions | Friction against mechanical roller guides or handling abrasions | High |

### 2.2 Dataset Pipeline & Anti-Leakage Partitioning
The training and evaluation pipeline utilizes the standard NEU Surface Defect Database:
- **Input Resolution:** Resized to standard $224 \times 224 \times 3$ RGB tensor.
- **Normalization:** Min-Max scaling to $[0.0, 1.0]$ float32 range.
- **Partitioning:** Stratified split into **70% Training** (630 samples), **15% Validation** (132 samples), and **15% Held-Out Test** (138 samples) with fixed random seed $42$ to prevent data leakage between evaluation and training sets.
- **Augmentation Pipeline:**
  - Random horizontal and vertical flips ($p=0.5$).
  - Random rotation ($\pm 10\%$).
  - Random zoom ($\pm 8\%$).
  - Random contrast adjustment ($\pm 10\%$).

---

## 3. DEEP LEARNING MODEL ARCHITECTURES

### 3.1 Custom Baseline CNN
The baseline network is designed with four sequential convolutional feature extraction blocks followed by Global Average Pooling and a dense regularized classification head:

$$\text{Input } (224 \times 224 \times 3)$$
$$\downarrow$$
$$\text{Block 1: } [\text{Conv2D}(32, 3\times 3) \to \text{BN} \to \text{ReLU}] \times 2 \to \text{MaxPool}(2\times 2) \implies (112 \times 112 \times 32)$$
$$\downarrow$$
$$\text{Block 2: } [\text{Conv2D}(64, 3\times 3) \to \text{BN} \to \text{ReLU}] \times 2 \to \text{MaxPool}(2\times 2) \implies (56 \times 56 \times 64)$$
$$\downarrow$$
$$\text{Block 3: } \text{Conv2D}(128, 3\times 3) \to \text{BN} \to \text{ReLU} \to \text{MaxPool}(2\times 2) \implies (28 \times 28 \times 128)$$
$$\downarrow$$
$$\text{Block 4: } \text{Conv2D}(256, 3\times 3) \to \text{BN} \to \text{ReLU} \to \text{MaxPool}(2\times 2) \implies (14 \times 14 \times 256)$$
$$\downarrow$$
$$\text{GlobalAveragePooling2D} \implies (256)$$
$$\downarrow$$
$$\text{Dense}(256, \text{L2}=10^{-4}) \to \text{BN} \to \text{ReLU} \to \text{Dropout}(0.5)$$
$$\downarrow$$
$$\text{Dense}(6, \text{Softmax}) \implies \mathbf{y} \in [0, 1]^6$$

Total parameter count: **505,254 parameters (1.93 MB)**. The use of Global Average Pooling significantly curtails dense layer weights while maintaining spatial invariance.

### 3.2 Transfer Learning (MobileNetV2 & EfficientNetB0)
To establish commercial benchmark performance:
- **MobileNetV2:** Inverted residual blocks with linear bottlenecks. Base weights pre-trained on ImageNet are frozen during Phase 1 ($\alpha=10^{-4}$) to train the top dense classification head, followed by fine-tuning of the top 30 layers ($\alpha=10^{-5}$).
- **EfficientNetB0:** Utilizes compound scaling across depth, width, and resolution. Yields superior feature extraction across high-frequency pitted surfaces and low-frequency patch textures.

### 3.3 Explainable AI (Grad-CAM)
To satisfy industrial auditing and ISO traceability requirements, Ironory calculates the Grad-CAM activation map:

$$\alpha_k^c = \frac{1}{Z} \sum_{i=1}^U \sum_{j=1}^V \frac{\partial y^c}{\partial A_{i, j}^k}$$
$$L_{\text{Grad-CAM}}^c = \text{ReLU}\left( \sum_k \alpha_k^c A^k \right)$$

Where $A^k$ is the feature map of the final convolutional layer (`conv4_1`), and $y^c$ is the logit for the predicted defect class $c$. The resulting heatmap is bilinearly upsampled to $224 \times 224$ and blended with the raw input image using Jet colormap coloring at $\alpha = 0.45$.

### 3.4 Convolutional Autoencoder for Unsupervised Anomaly Detection
In scenarios involving unprecedented or novel defect modes, supervised classification may fail. The autoencoder maps normal surfaces through an asymmetric bottleneck:
- **Encoder:** 3 downsampling blocks $\to$ Latent space $(14 \times 14 \times 32)$.
- **Decoder:** 3 upsampling `Conv2DTranspose` blocks $\to$ Reconstructed surface $(224 \times 224 \times 3)$.
- **Objective Function:** Mean Squared Error:

$$\mathcal{L}_{\text{MSE}}(x, \hat{x}) = \frac{1}{H \cdot W \cdot C} \sum_{i, j, k} (x_{i, j, k} - \hat{x}_{i, j, k})^2$$

The anomaly threshold is mathematically calibrated from validation error statistics:

$$\tau_{\text{anomaly}} = \mu_{\text{val}} + 2 \cdot \sigma_{\text{val}}$$

Any incoming surface producing $\mathcal{L}_{\text{MSE}} > \tau_{\text{anomaly}}$ is flagged as an anomaly.

### 3.5 U-Net Semantic Segmentation
For quantitative severity grading and area measurement, Ironory deploys a U-Net architecture. Skip connections concatenate feature maps from the contracting encoder directly into the upsampling decoder, preserving high-resolution boundary coordinates.
- **Loss Function:** Combined Dice Loss + Binary Cross-Entropy:

$$\mathcal{L}_{\text{Dice}} = 1 - \frac{2 \sum_i y_i \hat{y}_i + \epsilon}{\sum_i y_i + \sum_i \hat{y}_i + \epsilon}$$

### 3.6 Deep Convolutional GAN (DCGAN)
To augment scarce defect samples, a DCGAN generator maps $z \sim \mathcal{N}(0, I_{100})$ to synthetic steel surface defect patches using transposed convolutions and LeakyReLU ($0.2$) activations.

### 3.7 LSTM Defect Rate Forecasting
To move from reactive detection to predictive maintenance, a 2-layer LSTM ($64 \to 32$ units) monitors rolling 14-day production metrics (defect rates, inspection volumes, machine temperatures) and forecasts expected defect rates over a 7-day forward horizon.

---

## 4. EXPERIMENTAL RESULTS & BENCHMARKS

| Model Architecture | Parameter Count | Input Resolution | Test Accuracy | Macro Precision | Macro Recall | Macro F1-Score | Inference Latency (CPU) |
|---|---|---|---|---|---|---|---|
| **Baseline Custom CNN** | 505,254 | $224 \times 224 \times 3$ | **89.1%** | 0.894 | 0.888 | 0.887 | **14 ms** |
| **MobileNetV2 (Fine-Tuned)** | 2,424,262 | $224 \times 224 \times 3$ | **94.6%** | 0.948 | 0.941 | 0.942 | **22 ms** |
| **EfficientNetB0 (Fine-Tuned)** | 4,374,214 | $224 \times 224 \times 3$ | **96.2%** | 0.965 | 0.958 | 0.959 | **38 ms** |

---

## 5. SAAS PLATFORM ARCHITECTURE & ENTERPRISE COMPLIANCE

1. **Multi-Tenant Data Isolation:** Enforced via `organization_id` foreign keys, SQLAlchemy query scoping, and FastAPI request-level dependency verification (`CROSS_TENANT_ACCESS_DENIED` HTTP 403 enforcement).
2. **Role-Based Access Control (RBAC):** Five hierarchical roles (`OWNER`, `ADMIN`, `QUALITY_MANAGER`, `INSPECTOR`, `READ_ONLY`).
3. **Automated PDF Report Generation:** Built using pure-Python `reportlab`, generating downloadable ISO 9001-compliant certificates detailing inspection timestamps, AI predictions, confidence scores, localized bounding boxes, and supervisor digital sign-offs.
4. **Interactive Academic Demonstration:** Multi-page Streamlit portal running alongside Next.js on port 8501, offering live evaluation of all 7 deep learning modules.

---

## 6. CONCLUSION

The **Ironory** platform demonstrates that academic deep learning research and production B2B SaaS engineering can be successfully unified. By combining custom convolutional neural networks, transfer learning backbones, explainable activation mapping, unsupervised autoencoders, semantic segmentation, generative adversarial networks, and sequential forecasting, Ironory delivers a robust, scalable, and verifiable solution for industrial manufacturing quality inspection.
