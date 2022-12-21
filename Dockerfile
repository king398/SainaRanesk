FROM ubuntu:20.04
RUN yes| unminimize

    # Set ENV variables
ENV LANG C.UTF-8
ENV SHELL=/bin/bash
ENV DEBIAN_FRONTEND=noninteractive

ENV APT_INSTALL="apt-get install -y --no-install-recommends"
ENV PIP_INSTALL="python3 -m pip --no-cache-dir install --upgrade"
ENV GIT_CLONE="git clone --depth 10"


# ==================================================================
# Tools
# ------------------------------------------------------------------
RUN apt-get update && \
        $APT_INSTALL \
        apt-utils \
        gcc \
        make \
        pkg-config \
        apt-transport-https \
        build-essential \
        ca-certificates \
        wget \
        rsync \
        git \
        vim \
        mlocate \
        libssl-dev \
        curl \
        openssh-client \
        unzip \
        unrar \
        zip \
        csvkit \
        emacs \
        joe \
        jq \
        dialog \
        man-db \
        manpages \
        manpages-dev \
        manpages-posix \
        manpages-posix-dev \
        nano \
        iputils-ping \
        sudo \
        ffmpeg \
        libsm6 \
        libxext6 \
        libboost-all-dev \
        cifs-utils \
        software-properties-common


# ==================================================================
# Python
# ------------------------------------------------------------------

    #Based on https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa

    # Adding repository for python3.9 \
RUN add-apt-repository ppa:deadsnakes/ppa -y && \
$APT_INSTALL \
        python3.9 \
        python3.9-dev \
        python3.9-venv \
        python3-distutils-extra

 # Add symlink so python and python3 commands use same python3.9 executable
RUN ln -s /usr/bin/python3.9 /usr/local/bin/python3 && \
        ln -s /usr/bin/python3.9 /usr/local/bin/python



RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.9
ENV PATH=$PATH:/root/.local/bin
RUN wget https://developer.download.nvidia.com/compute/cuda/11.6.2/local_installers/cuda_11.6.2_510.47.03_linux.run && \
        bash cuda_11.6.2_510.47.03_linux.run --silent --toolkit && \
        rm cuda_11.6.2_510.47.03_linux.run
ENV PATH=$PATH:/usr/local/cuda-11.6/bin
ENV LD_LIBRARY_PATH=/usr/local/cuda-11.6/lib64

    # Installing CUDNN
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin && \
        mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600 && \
        apt-get install dirmngr -y && \
        apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub && \
        add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /" && \
        apt-get update && \
        apt-get install libcudnn8=8.4.1.*-1+cuda11.6 -y && \
        apt-get install libcudnn8-dev=8.4.1.*-1+cuda11.6 -y && \
        rm /etc/apt/preferences.d/cuda-repository-pin-600 \
RUN $PIP_INSTALL torch==1.12.1 torchvision==0.13.1 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu116 && \
# Install base utilities
RUN  apt-get -y update


# Install miniconda
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
     /bin/bash ~/miniconda.sh -b -p /opt/conda

# Put conda in path so we can use conda activate
ENV PATH=$CONDA_DIR/bin:$PATH

RUN PIP_INSTALL jupyterlab==3.4.6 && \


# ==================================================================
# Additional Python Packages
# ------------------------------------------------------------------

 $PIP_INSTALL \
        numpy==1.23.4 \
        scipy==1.9.2 \
        pandas==1.5.0 \
        cloudpickle==2.2.0 \
        scikit-image==0.19.3 \
        scikit-learn==1.1.2 \
        matplotlib==3.6.1 \
        ipython==8.5.0 \
        ipykernel==6.16.0 \
        ipywidgets==8.0.2 \
        cython==0.29.32 \
        tqdm==4.64.1 \
        gdown==4.5.1 \
        xgboost==1.6.2 \
        pillow==9.2.0 \
        seaborn==0.12.0 \
        sqlalchemy==1.4.41 \
        spacy==3.4.1 \
        nltk==3.7 \
        boto3==1.24.90 \
        tabulate==0.9.0 \
        future==0.18.2 \
        gradient==2.0.6 \
        jsonify==0.5 \
        opencv-python==4.6.0.66 \
        sentence-transformers==2.2.2 \
        wandb==0.13.4 \
        awscli==1.25.91


# ==================================================================
# Installing JRE and JDK
# ------------------------------------------------------------------

RUN $APT_INSTALL \
        default-jre \
        default-jdk


# ==================================================================
# CMake
# ------------------------------------------------------------------

RUN $GIT_CLONE https://github.com/Kitware/CMake ~/cmake && \
        cd ~/cmake && \
        ./bootstrap && \
        make -j"$(nproc)" install


# ==================================================================
# Node.js and Jupyter Notebook Extensions
# ------------------------------------------------------------------

RUN curl -sL https://deb.nodesource.com/setup_16.x | bash  && \
        $APT_INSTALL nodejs  && \
        $PIP_INSTALL jupyter_contrib_nbextensions jupyterlab-git && \
        jupyter contrib nbextension install --user


# ==================================================================
# Startup
# ------------------------------------------------------------------

EXPOSE 8888 6006
WORKDIR /app
COPY . .
ENV TZ=Asia/Kolkata \
    DEBIAN_FRONTEND=noninteractive
RUN conda install git
CMD nvidia-smi
CMD ["bash"]
RUN pip install -r requirements.txt
RUN wget https://openaipublic.azureedge.net/main/whisper/models/e4b87e7e0bf463eb8e6956e646f1e277e901512310def2c24bf0e11bd3c28e9a/large.pt -P /app/models
RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc |  tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" |  tee /etc/apt/sources.list.d/ngrok.list &&  apt update &&  apt install ngrok
CMD jupyter lab --allow-root --ip=0.0.0.0 --no-browser --ServerApp.trust_xheaders=True --ServerApp.disable_check_xsrf=False --ServerApp.allow_remote_access=True --ServerApp.allow_origin='*' --ServerApp.allow_credentials=True

