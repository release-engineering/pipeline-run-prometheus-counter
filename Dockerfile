FROM registry.access.redhat.com/ubi8/ubi:latest

WORKDIR /src
RUN dnf install -y \
    --setopt=deltarpm=0 \
    --setopt=install_weak_deps=false \
    --setopt=tsflags=nodocs \
    httpd \
    mod_ssl \
    python3-mod_wsgi \
    python3-pip\
    && dnf clean all
RUN mkdir -p /data && chown -R apache:apache /data
COPY . .
COPY ./docker/httpd.conf /etc/httpd/conf/httpd.conf
RUN pip3 install -r requirements.txt --no-deps --require-hashes
RUN pip3 install . --no-deps
ENV PRPC_DB_PATH=/data/prpc.db
VOLUME /data
EXPOSE 8080
CMD ["/usr/sbin/httpd", "-DFOREGROUND"]
