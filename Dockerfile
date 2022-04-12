FROM ruby:2.5.7
MAINTAINER Webmaster Team "Tilak Thimmappa"

RUN apt-get update
RUN apt-get install -y git imagemagick libpq-dev libncurses5-dev libffi-dev curl build-essential libssl-dev libreadline6-dev zlib1g-dev zlib1g libsqlite3-dev libmagickwand-dev libqtwebkit-dev libqt4-dev libreadline-dev libxslt-dev

COPY . /weby
WORKDIR /weby
COPY ./config/database.yml.example /weby/config/database.yml
COPY ./config/secrets.yml.example /weby/config/secrets.yml
RUN gem install bundler
RUN bundle check || bundle install

RUN bundle exec rake assets:precompile --trace
# CMD export SECRET_KEY_BASE=`bundle exec rake secret`
EXPOSE 3000
RUN chmod +x entrypoint
CMD ["./entrypoint"]
# CMD rails s -b 0.0.0.0 -p 3000
# docker run -it -p $PORT:$PORT -e SECRET_KEY_BASE=$SECRET_KEY_BASE -e PG_DB=$PG_DB -e PG_USER=$PG_USER -e PG_PASS=$PG_PASS -e PG_HOST=$PG_HOST -e PG_PORT=$PG_PORT -e PORT=$PORT faraohh/weby:latest
