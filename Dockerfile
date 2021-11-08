FROM ubuntu:focal

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
	&& apt-get install -y vim curl git sudo

RUN useradd --user-group --create-home --shell /bin/bash foam ;\
	echo "foam ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

RUN curl -s https://dl.openfoam.com/add-debian-repo.sh | bash ;\
	apt-get install -y openfoam1912 openfoam1912-tutorials ;\
	rm -rf /var/lib/apt/lists/* ;\
	echo "source /usr/lib/openfoam/openfoam1912/etc/bashrc" >> ~foam/.bashrc ;\
	echo "export OMPI_MCA_btl_vader_single_copy_mechanism=none" >> ~foam/.bashrc

USER foam

SHELL ["/bin/bash", "-c"]

RUN	source /usr/lib/openfoam/openfoam1912/etc/bashrc ;\
	cd ~ ;\
	git clone https://github.com/turbinesFoam/turbinesFoam.git ;\
	cd turbinesFoam ;\
	./Allwmake
