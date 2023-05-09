FROM nginx:1.21-alpine

# remove default configuration and replace it with our own
RUN rm /etc/nginx/conf.d/default.conf
COPY default.conf.conf /etc/nginx/templates/default.conf.conf

RUN mkdir -p /etc/ssl/
COPY cert.pem /etc/ssl/cert.pem
COPY key.pem /etc/ssl/key.pem