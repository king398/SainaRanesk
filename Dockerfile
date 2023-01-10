FROM paperspace/gradient-base:pt112-tf29-jax0314-py39-20220803
ENV TZ=Asia/Kolkata \
    DEBIAN_FRONTEND=noninteractive
RUN  apt-get -y update
RUN apt-get install -y ffmpeg wget
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
     /bin/bash ~/miniconda.sh -b -p /opt/conda

# Put conda in path so we can use conda activate
ENV PATH=$CONDA_DIR/bin:$PATH
WORKDIR /app
COPY . .
RUN conda install git
CMD nvidia-smi
CMD ["bash"]
RUN pip install -r requirements.txt
RUN wget https://openaipublic.azureedge.net/main/whisper/models/81f7c96c852ee8fc832187b0132e569d6c3065a3252ed18e56effd0b6a73e524/large-v2.pt -P /app/models
RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc |   tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" |   tee /etc/apt/sources.list.d/ngrok.list &&   apt update &&   apt install ngrok
RUN f=$(python -c 'import service_streamer as ss; print(ss.service_streamer.__file__)')
RUN echo "$f"

# Modify variable `WORKER_TIMEOUT` from $f with the desired value
RUN desired_value="1800" # Modify this variable

RUN  cat "$f" | grep "^WORKER_TIMEOUT" # Current value

# Modify the file
RUN sed -E -i "s/^WORKER_TIMEOUT = [0-9]+\$/WORKER_TIMEOUT = ${desired_value}/" "$f"