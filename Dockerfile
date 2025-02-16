FROM node:15-stretch

RUN mkdir /usr/src
RUN mkdir /usr/src/goof
RUN mkdir /tmp/extracted_files

COPY . /usr/src/goof
WORKDIR /usr/src/goof

RUN npm update
RUN npm install

EXPOSE 3000

CMD ["npm", "start"]
