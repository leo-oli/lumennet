# LumenNet: Deep Learning Low-Light Image Enhancement

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.14+-blue.svg?logo=python)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg?logo=docker)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-blue.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![ONNX](https://img.shields.io/badge/ONNX-Runtime-blue.svg?logo=onnx)](https://onnxruntime.ai/)

LumenNet is an image enhancement pipeline designed to recover structural details and accurate colors from underexposed, low-light photographs. It utilizes a deep learning approach to simulate high-ISO noise reduction and dynamic range expansion typical of modern computational photography.

- [LumenNet: Deep Learning Low-Light Image Enhancement](#lumennet-deep-learning-low-light-image-enhancement)
  - [Results](#results)
    - [Visual Results](#visual-results)
    - [Quantitative Results](#quantitative-results)
  - [The Problem Statement](#the-problem-statement)
  - [System Architecture](#system-architecture)
  - [Model Architecture](#model-architecture)
  - [Training Methodology](#training-methodology)
  - [Deployment Instructions](#deployment-instructions)
    - [Configuration](#configuration)
    - [Direct API Usage](#direct-api-usage)
  - [License](#license)

## Results

### Visual Results

Below is an example of the model's performance on the validation set.

| Low Light Input                                           | Model Prediction                                                | Ground Truth                                         |
|-----------------------------------------------------------|-----------------------------------------------------------------|------------------------------------------------------|
| ![Input](model_training/plots/low_light_input_22.png.png) | ![Prediction](model_training/plots/model_prediction_22.png.png) | ![Target](model_training/plots/gt_target_22.png.png) |

*Sample images are sourced from the LOL-Dataset[^1], originally introduced in the paper "Deep Retinex Decomposition for Low-Light Enhancement"[^2].*

### Quantitative Results

Evaluated on the 15-image held-out validation split of the LOL-Dataset. Early stopping (patience of 10 epochs monitoring validation PSNR) halted training at Epoch 26, retaining the Epoch 16 checkpoint for ONNX export.

| Checkpoint           | Train Loss | Val Loss | Train PSNR | Val PSNR     | Val SSIM   |
|----------------------|------------|----------|------------|--------------|------------|
| **Best Epoch (16)**  | 0.1793     | 0.1984   | 19.38 dB   | **19.16 dB** | **0.7672** |
| **Final Epoch (26)** | 0.1654     | 0.2124   | 20.18 dB   | 18.20 dB     | 0.7629     |

## The Problem Statement

Photography in low-light conditions presents two fundamental challenges:

1. **Signal-to-Noise Ratio (SNR) collapse:** Sensor noise overwhelms the actual image data.
2. **Color Space Distortion:** In extreme low light, RGB channels compress and desaturate, making it mathematically difficult to enhance brightness without causing chromatic shifts or severe desaturation.

## System Architecture

LumenNet provides a decoupled microservice architecture:

- **Backend:** A FastAPI-based REST API that executes an ONNX-optimized model.
- **Frontend:** A Gradio-based web interface that provides an interactive slider to compare raw inputs with the AI-enhanced outputs.

```mermaid
flowchart LR
    subgraph offline_zone["Offline Pipeline"]
        subgraph train_layer["Model Training"]
            training["PyTorch Lightning<br/>U-Net and Kornia LAB"]
        end
        subgraph artifact_layer["Model Artifact"]
            artifact("ONNX Model")
        end
    end

    subgraph runtime_zone["Docker Compose Stack"]
        subgraph backend_layer["Backend, Port 8000"]
            backend["FastAPI and NumPy<br/>ONNX CPU Runtime"]
        end
        subgraph frontend_layer["Frontend, Port 7860"]
            frontend["Gradio Web UI<br/>HTTP Client"]
        end
    end

    user(["End-User Browser"])

    train_layer -->|"Export"| artifact_layer
    artifact_layer -->|"Load"| backend_layer
    backend_layer <-->|"HTTP /enhance"| frontend_layer
    frontend_layer <--> user
```

Project structure:

```text
lumennet/
├── backend/          # FastAPI REST API, NumPy padding wrapper, and ONNX CPU runtime
├── frontend/         # Gradio web interface and decoupled httpx API client
├── model_training/   # PyTorch Lightning training notebook, ONNX export, and plots
└── compose.yaml      # Multi-container Docker Compose orchestration
```

## Model Architecture

The core of LumenNet is a **U-Net architecture featuring a MobileNetV2 backbone**.

- **Encoder:** Transfer Learning is employed utilizing a pre-trained MobileNetV2 as an encoder to extract robust hierarchical spatial features.
- **Decoder:** A U-Net decoder is used to reconstruct the image from the encoded features.
- **Color Processing (The LAB Strategy):** To circumvent the desaturation and color-bleeding phenomena common in standard U-Nets, LumenNet operates conceptually within the **LAB color space**.
  - The model primarily focuses on the **L (Lightness)** channel to predict illumination adjustments.
  - The **A and B (Color)** channels are preserved and proportionally scaled based on the predicted luminance changes, preserving original chromaticity while clamping gain to prevent shadow noise amplification.
- **Inference Efficiency:** The network is exported to ONNX format, facilitating efficient execution on CPU-only infrastructure without necessitating expensive GPU resources.

## Training Methodology

- **Dataset:** The model was trained on the **LOL-Dataset (LOw-Light dataset)**[^1], consisting of 485 paired low-light and normal-light image samples (from the paper *"Deep Retinex Decomposition for Low-Light Enhancement"*[^2]).
- **Objective Function:** Optimization relies on a hybrid loss function combining:
  - **L1 Loss:** For pixel-wise intensity accuracy.
  - **SSIM (Structural Similarity) Loss:** To ensure structural edges and textures are rigorously maintained.
- **Optimization Strategy:** Trained via transfer learning with weight decay to mitigate overfitting on the small dataset, utilizing a Cosine Annealing learning rate scheduler to ensure stable convergence.

## Deployment Instructions

LumenNet is containerized using Docker. To launch the full stack, ensure [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/) are installed, then execute the following command from the project root:

```bash
docker compose up -d --build
```

Upon successful build and initialization, the interfaces are accessible at:

- **Graphical User Interface (GUI):** `http://localhost:7860`
- **API Documentation (Swagger UI):** `http://localhost:8000/docs`

### Configuration

Ports can be customized by defining `BACKEND_PORT` (default: `8000`) and `FRONTEND_PORT` (default: `7860`) in a `.env` file at the project root before starting the stack.

### Direct API Usage

You can call the enhancement endpoint directly without using the Gradio UI:

```bash
curl -X POST "http://localhost:8000/enhance" \
  -F "file=@path/to/dark_image.png" \
  --output enhanced.png
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

[^1]: RAKSHIT, Soumik. *LOw-Light Dataset*. Online. 2022. [Accessed 13 May 2026]. Available from: <https://www.kaggle.com/datasets/soumikrakshit/lol-dataset>.
[^2]: WEI, Chen, WANG, Wenjing, YANG, Wenhan and LIU, Jiaying. *Deep Retinex Decomposition for Low-Light Enhancement*. Online. 1. 2018. arXiv. [Accessed 13 May 2026]. DOI: <https://doi.org/10.48550/arXiv.1808.04560>.
