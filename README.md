# **My Solution for Sainya Ranakshetram AI challenge**

# 1. How to View my Solution

## A. README.md

This is a README.md file for my solution for sainya-ranakshetram ai challenge. This README.md file is written in
markdown format. You can read more about Markdown format [here](https://guides.github.com/features/mastering-markdown/).
There are Two ways in which you can read this README.md file

### Option 1: Read this README.md file on using grip ( GitHub markdown previewer)

To render this readme.md , open the terminal and cd into this directory and run the following command in a bash shell:

```console
$ grip
```

which will give the following output:

```console
* Serving Flask app 'grip.app'
* Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
* Running on http://localhost:6419
Press CTRL+C to quit
```

Click on the link http://localhost:6419 to view the rendered README.md file.

Incase you are running this solution on a remote server, you can forward the port 6419 to a remote tunnel using
cloud-flared tunneling service.
To do so, run the following command in a bash shell:

```console
$ cloudflared tunnel --url http://localhost:6419
```

this will give the following output:

```console
2022-12-22T11:28:34Z INF Thank you for trying Cloudflare Tunnel. Doing so, without a Cloudflare account, is a quick way to experiment and try it out. However, be aware that these account-less Tunnels have no uptime guarantee. If you intend to use Tunnels in production you should use a pre-created named tunnel by following: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps
2022-12-22T11:28:34Z INF Requesting new quick Tunnel on trycloudflare.com...
2022-12-22T11:28:36Z INF +--------------------------------------------------------------------------------------------+
2022-12-22T11:28:36Z INF |  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
2022-12-22T11:28:36Z INF |  Url Here (unique url will be created here every time)                                             |
2022-12-22T11:28:36Z INF +--------------------------------------------------------------------------------------------+
2022-12-22T11:28:36Z INF Version 2022.12.1
2022-12-22T11:28:36Z INF GOOS: linux, GOVersion: go1.19.3, GoArch: amd64
2022-12-22T11:28:36Z INF cloudflared will not automatically update if installed by a package manager.
2022-12-22T11:28:36Z INF Generated Connector ID: a3eea567-7fe4-4f24-bbab-eaba6e003265
2022-12-22T11:28:36Z INF Initial protocol quic
2022-12-22T11:28:36Z INF ICMP proxy will use 10.42.32.18 as source for IPv4
2022-12-22T11:28:36Z INF ICMP proxy will use :: as source for IPv6
2022-12-22T11:28:36Z INF Starting metrics server on 127.0.0.1:42055/metrics

```

The Url Here area will have your unique url. Click on the link to view the rendered README.md file.

### Option 2: Convert this README.

You can open a rendered pdf of README.md By opening the file README.pdf in this directory.

## B. Video

You can also view the video of my solution [here](https://youtu.be/1Z4Z2Z2Z2Z2) ## ADD vidoe link here

# 2. How to Run my soltion

## Step 1 : Make sure All requirements are installed

### Docker

To check this run the following command in a bash shell

```console
$ docker --version
```

If this command runs successfully then you have docker installed on your system. If not then install docker on your
system using the following command

```console
$ bash install_docker.sh
```

Which will install docker on your system

### Compute Requirements

This Repo requires an Nvidia GPU with a minimum of 10GB of memory to run to fit the transcription model.

## Step 2 : Clone the Docker container

To clone the docker container run the following command in a bash shell

```console
$ sudo docker pull mithilaidocker/audiotranscribe:master
```

## Step 3 : Run the Docker container

To run the docker container run the following command in a bash shell

```console
sudo docker run --gpus all --ipc=host --ulimit memlock=-1 --net="host" --ulimit stack=67108864 -it -v "/home/":/home \
--rm mithilaidocker/audiotranscribe:master
```

By running this command you will enter the docker container.

## Step 4 : Run the Solution

To Run the flask app for the solution run the following command in a bash shell.(Make sure you are in the `/app` dir)

```console
root@xx:/app#  python -m flask run --host= 0.0.0.0
```

This will run the flask app which contains the solution. it will give the following output

```
* Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
* Running on all addresses (0.0.0.0)
* Running on http://127.0.0.1:5000
* Running on http://10.42.32.18:5000
Press CTRL+C to quit
```

If you are running on the same machine as the server then you can access the solution at http://127.0.0.1:5000
In case you running this solution on a remote server you will need to forward the port 5000 to your local machine. To do
this
we can use cloudfared tunnel (_already installed on the docker image_) to forward the port 5000 to our local machine. To
do this run the following command in a bash shell

```console
$ cloudflared tunnel --url http://127.0.0.1:5000
```

This will Give the following output

```console
2022-12-22T11:28:34Z INF Thank you for trying Cloudflare Tunnel. Doing so, without a Cloudflare account, is a quick way to experiment and try it out. However, be aware that these account-less Tunnels have no uptime guarantee. If you intend to use Tunnels in production you should use a pre-created named tunnel by following: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps
2022-12-22T11:28:34Z INF Requesting new quick Tunnel on trycloudflare.com...
2022-12-22T11:28:36Z INF +--------------------------------------------------------------------------------------------+
2022-12-22T11:28:36Z INF |  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
2022-12-22T11:28:36Z INF |  Url Here (unique url will be created here every time)                                             |
2022-12-22T11:28:36Z INF +--------------------------------------------------------------------------------------------+
2022-12-22T11:28:36Z INF Version 2022.12.1
2022-12-22T11:28:36Z INF GOOS: linux, GOVersion: go1.19.3, GoArch: amd64
2022-12-22T11:28:36Z INF Settings: map[protocol:quic url:http://127.0.0.1:5000]
2022-12-22T11:28:36Z INF cloudflared will not automatically update if installed by a package manager.
2022-12-22T11:28:36Z INF Generated Connector ID: a3eea567-7fe4-4f24-bbab-eaba6e003265
2022-12-22T11:28:36Z INF Initial protocol quic
2022-12-22T11:28:36Z INF ICMP proxy will use 10.42.32.18 as source for IPv4
2022-12-22T11:28:36Z INF ICMP proxy will use :: as source for IPv6
2022-12-22T11:28:36Z INF Starting metrics server on 127.0.0.1:42055/metrics
```

Click on the link in the area of the output that says `Url Here` to view the solution. You will have your own unique url
every time
**_NOTE:_** The Cloudflare tunnel is only a quick way to access the solution. It is not a production ready solution. If
you want to use this solution in production you should use a pre-created named tunnel by
following: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps



## Step 5 : How to use the Flask App
Upon opening the url you will be greeted with the following page

![img.png](https://camo.githubusercontent.com/383351ab74835d389498c5efbb9e85d45259da22e89ea2dbc92540c5c84a0322/68747470733a2f2f692e6962622e636f2f686d4a735248422f53637265656e73686f742d66726f6d2d323032322d31322d32322d31372d31372d35392e706e67)




