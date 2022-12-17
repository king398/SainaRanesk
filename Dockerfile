FROM pytorch/pytorch
RUN  apt-get -y update
RUN apt-get install -y ffmpeg wget
WORKDIR /app
COPY . .
ENV TZ=Asia/Kolkata \
    DEBIAN_FRONTEND=noninteractive
RUN conda install git
CMD nvidia-smi
CMD ["bash"]
RUN pip install -r requirements.txt
RUN wget https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt -P /app/models
#CMD python3 -m  flask run --host=0.0.0.0

