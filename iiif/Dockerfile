FROM ubuntu:xenial
RUN apt-get update
RUN apt-get install -y -q --no-install-recommends build-essential cmake
RUN apt-get install -y -q --no-install-recommends libtiff5-dev
RUN apt-get install -y -q --no-install-recommends wget

RUN wget --no-check-certificate 'https://github.com/uclouvain/openjpeg/archive/v2.3.1.tar.gz'
RUN tar xvf v2.3.1.tar.gz
WORKDIR openjpeg-2.3.1
RUN mkdir bin
RUN cmake .
RUN make
RUN make install

RUN export USE_OPENJPEG=1
RUN printf "include /etc/ld.so.conf.d/*.conf\ninclude /usr/local/lib\n" > /etc/ld.so.conf && ldconfig

WORKDIR /
RUN wget --no-check-certificate 'https://sourceforge.net/projects/iipimage/files/IIP%20Server/iipsrv-1.1/iipsrv-1.1.tar.bz2'
RUN tar xvf iipsrv-1.1.tar.bz2
WORKDIR iipsrv-1.1
RUN ./configure --with-openjpeg=/openjpeg-2.3.1
RUN make
WORKDIR /

ENV URI_MAP="iiif=>IIIF"
RUN mkdir /var/log/iipsrv
ENV LOGFILE="/var/log/iipsrv/iipsrv.log"

CMD /iipsrv-1.1/src/iipsrv.fcgi --bind 0.0.0.0:9000
