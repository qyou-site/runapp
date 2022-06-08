FROM python:3.8.13-slim

WORKDIR /pose

COPY . /pose

RUN apt-get update -q \
    && pip install --upgrade pip setuptools wheel  \
    && apt-get install ffmpeg libsm6 libxext6 git -y \
    && apt-get clean \
    && pip install -r requirements.txt --no-cache-dir \
    && rm -rf /var/lib/apt/lists/*



ENTRYPOINT ['python','main.py']
# ENTRYPOINT ['/bin/bash','-l','-c']

# CMD ['python', 'main.py']