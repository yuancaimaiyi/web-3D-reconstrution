FROM node:18
WORKDIR /frontend
RUN npm install -g npm
COPY package.json package-lock.json ./
RUN npm install

COPY . .
EXPOSE 3000
CMD [ "npm", "start" ]