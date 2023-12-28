docker build -t chompt-webapp .
docker tag chompt-webapp registry.digitalocean.com/chompt-webapp/chompt-webapp:latest
docker push registry.digitalocean.com/chompt-webapp/chompt-webapp:latest