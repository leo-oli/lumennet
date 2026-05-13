# LumenNet Frontend

The frontend service provides an interactive graphical user interface for the LumenNet system. 

## Overview
Built with Gradio, it allows users to upload underexposed photographs and view enhancements in real-time through an interactive before-and-after slider.

## Architecture
This service is lightweight and abstracts the model complexity. It is strictly responsible for:
- Image serialization and deserialization.
- Orchestrating HTTP requests to the backend inference API.
- Rendering the user interface.
