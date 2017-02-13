FROM nginx:alpine

ADD . /etc/nginx/

# RUN apt-get install apache2-utils
# RUN apk add --update mini_httpd && rm -rf /var/cache/apk/*
RUN apk add --update apache2-utils && rm -rf /var/cache/apk/*
RUN htpasswd -b -c /etc/nginx/.htpasswd admin scrapyd
