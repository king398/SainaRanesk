FROM nvcr.io/nvidia/pytorch:23.12-py3

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
RUN pip install flash-attn --no-build-isolation
RUN pip install  transformers accelerate datasets[audio]
#CMD python3 -m  flask run --host=0.0.0.0-