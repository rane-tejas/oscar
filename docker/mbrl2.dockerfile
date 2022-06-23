FROM nvidia/cuda:11.1.1-base-ubuntu18.04

# Install some basic utilities
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    sudo \
    git \
    bzip2 \
    libx11-6
#  && rm -rf /var/lib/apt/lists/*

# Create a working directory
RUN mkdir /app
WORKDIR /app

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' --shell /bin/bash user \
 && chown -R user:user /app
RUN echo "user ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-user
USER user

# All users can use /home/user as their home directory
ENV HOME=/home/user
RUN chmod 777 /home/user

# Install Miniconda and Python 3.7
ENV CONDA_AUTO_UPDATE_CONDA=false
ENV PATH=/home/user/miniconda/bin:$PATH
RUN curl -sLo ~/miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-py37_4.9.2-Linux-x86_64.sh \
 && chmod +x ~/miniconda.sh \
 && ~/miniconda.sh -b -p ~/miniconda \
 && rm ~/miniconda.sh \
 && conda clean -ya

# CUDA 11.1-specific steps
RUN conda install cudatoolkit=11.1 \
    -c pytorch -c nvidia \
     && conda clean -ya

# Set the default command to python3
# CMD ["python3"]

########################################################

ARG USER_NAME
ARG USER_PASSWORD
ARG USER_ID
ARG USER_GID

ENV DEBIAN_FRONTEND=noninteractive 

USER root

# Install dependencies
# COPY ./install_gym_dependencies.sh /tmp/install_gym_dependencies.sh
# RUN yes "Y" | /tmp/install_gym_dependencies.sh
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
 python3-pip \
 libglfw3-dev \
 python3-dev \
 libpython3.7 \
 build-essential \
 libxcursor-dev \
 libxrandr-dev \
 libxinerama-dev \
 libxi-dev \
 mesa-common-dev \
 zip \
 unzip \
 make \
 gcc-8 \
 g++-8 \
 vulkan-utils \
 mesa-vulkan-drivers \
 pigz \
#  git \
 libegl1 \
 git-lfs

# Force gcc 8 to avoid CUDA 10 build issues on newer base OS
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-8 8
RUN update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-8 8

# WAR for eglReleaseThread shutdown crash in libEGL_mesa.so.0 (ensure it's never detected/loaded)
# Can't remove package libegl-mesa0 directly (because of libegl1 which we need)
RUN rm /usr/lib/x86_64-linux-gnu/libEGL_mesa.so.0 /usr/lib/x86_64-linux-gnu/libEGL_mesa.so.0.0.0 /usr/share/glvnd/egl_vendor.d/50_mesa.json

COPY nvidia_icd.json /usr/share/vulkan/icd.d/nvidia_icd.json
COPY 10_nvidia.json /usr/share/glvnd/egl_vendor.d/10_nvidia.json

WORKDIR /opt/isaacgym

RUN useradd --create-home ${USER_NAME}

# copy gym repo to docker
COPY --chown=${USER_NAME} . .

# install gym modules
ENV PATH="/home/${USER_NAME}/.local/bin:$PATH"
RUN pwd
RUN ls
RUN cd isaacgym/python && pip install -q -e .

ENV NVIDIA_VISIBLE_DEVICES=all NVIDIA_DRIVER_CAPABILITIES=all

# COPY ./install_dependencies.sh /tmp/install_dependencies.sh
# RUN yes "Y" | /tmp/install_dependencies.sh
RUN pip install \
  comet_ml \
  einops \
  python-dev-tools \
  omegaconf \
  hydra \
  hydra-core \
  gym \
  ipdb \
  ray \
  tensorboardX \
  rl-games==1.1.3 \
  pyyaml>=5.3.1 \
  torch \
  torchvision


WORKDIR /home/$USER_NAME
RUN cd $WORKDIR

# # require no sudo pw in docker
# # RUN echo $USER_PASSWORD | sudo -S bash -c 'echo "'$USER_NAME' ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/docker-user' && printf "\n"

# # COPY ./install_pytorch.sh /tmp/install_pytorch.sh
# # RUN yes "Y" | /tmp/install_pytorch.sh

# # COPY ./install_more.sh /tmp/install_more.sh
# # RUN yes "Y" | /tmp/install_more.sh

# # # install director
# # COPY ./install_director.sh /tmp/install_director.sh
# # RUN yes "Y" | /tmp/install_director.sh

# # # visdom hotfix
# # COPY ./visdom_download_scripts.sh /tmp/visdom_download_scripts.sh
# # RUN yes "Y" | /tmp/visdom_download_scripts.sh

# # set the terminator inside the docker container to be a different color
# # RUN mkdir -p .config/terminator
# # COPY ./terminator_config .config/terminator/config
# # RUN chown $USER_NAME:$USER_NAME -R .config


# # # change ownership of everything to our user
# # RUN cd $WORKDIR && chown $USER_NAME:$USER_NAME -R .
# # RUN echo 'PS1="\[\033[42m\]\[\033[31m\]\u@\h:\w\$"' >> /home/$USER_NAME/.bashrc 
# # RUN echo 'use_pytorch_dense_correspondence' >> /home/$USER_NAME/.bashrc 

# # ENTRYPOINT bash -c "source ~/code/docker/entrypoint.sh && /bin/bash"
