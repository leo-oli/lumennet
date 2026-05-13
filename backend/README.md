# LumenNet Backend

The backend service functions as the core inference engine for the LumenNet system.

## Overview
It manages the lifecycle of the pre-trained neural network and exposes a high-performance RESTful API for image processing tasks.

## Architecture
Built with FastAPI and ONNX Runtime, the backend handles:
- **Pre-processing:** Translates raw RGB inputs into normalized float32 tensors, applying dynamic padding to meet network architecture constraints.
- **Inference:** Executes the ONNX-optimized model efficiently on the CPU.
- **Post-processing:** Denormalizes and processes the resultant tensors back into standard RGB image formats for the end-user.
