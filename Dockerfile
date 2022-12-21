FROM paperspace/gradient-base:pt112-tf29-jax0314-py39-20220803
RUN  apt-get -y update
RUN apt-get install -y ffmpeg wget
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
     /bin/bash ~/miniconda.sh -b -p /opt/conda

# Put conda in path so we can use conda activate
ENV PATH=$CONDA_DIR/bin:$PATH
WORKDIR /app
COPY . .
ENV TZ=Asia/Kolkata \
    DEBIAN_FRONTEND=noninteractive
RUN conda install git
CMD nvidia-smi
CMD ["bash"]
RUN pip install -r requirements.txt
RUN wget https://openaipublic.azureedge.net/main/whisper/models/e4b87e7e0bf463eb8e6956e646f1e277e901512310def2c24bf0e11bd3c28e9a/large.pt -P /app/models
#CMD python3 -m  flask run --host=0.0.0.0



# Install miniconda


