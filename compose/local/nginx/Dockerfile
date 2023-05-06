FROM nginx:1.21-alpine

# remove default configuration and replace it with our own
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.https.conf /etc/nginx/conf.d/default.conf

RUN mkdir -p /etc/ssl/
COPY example.dev.crt /etc/ssl/example.dev.crt
COPY example.dev.key /etc/ssl/example.dev.key