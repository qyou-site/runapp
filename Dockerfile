FROM python:3.8.13-slim

WORKDIR /pose

COPY . /poseopencv-python==3.4.13.47
    && pip install -r requirements.txt --no-cache-dir \
    && rm -rf /var/lib/apt/lists/*



ENTRYPOINT ['python','main.py']
# ENTRYPOINT ['/bin/bash','-l','-c']

# CMD ['python', 'main.py']