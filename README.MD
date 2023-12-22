# HW 2


1. Install poetry and activate its environment:

    ```bash
    pip install poetry
    poetry shell

2. Build package:

    ```bash
    poetry build

3. Build image in a docker:

    ```bash
    docker build -t bot-assistant-app-2 . 

4. Run container in a docker from previously build image (Start Bot):

    ```bash
    docker run -it --rm bot-assistant-app-2
