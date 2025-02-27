# AI Travel Assistant

Welcome to the AI Travel Assistant project! This application leverages multiple APIs to provide users with comprehensive travel assistance, including flight searches, weather updates, and points of interest in various cities.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [APIs Used](#apis-used)
- [Contributing](#contributing)
- [License](#license)

## Introduction

The AI Travel Assistant is designed to help users plan their trips efficiently by providing real-time information on flights, weather, and tourist attractions. The application integrates with several APIs to fetch and display relevant data based on user queries.

## Features

- **Flight Search**: Find the cheapest flights between cities on specified dates.
- **Weather Updates**: Get current weather information for any city.
- **Tourist Attractions**: Discover top points of interest near the city center.

## Installation

To get started with the AI Travel Assistant, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/SemanticKernel.git
    cd SemanticKernel
    ```

2. **Create a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    - Create a `.env` file in the root directory of the project.
    - Add your API keys to the `.env` file as follows:
        ```plaintext
        OPENAI_API_KEY=your_openai_api_key
        KIWI_API_KEY=your_kiwi_api_key
        OPENTRIPMAP_API_KEY=your_opentripmap_api_key
        OPENWEATHER_API_KEY=your_openweather_api_key
        ```

## Usage

To run the AI Travel Assistant, execute the following command:

```bash
python main.py