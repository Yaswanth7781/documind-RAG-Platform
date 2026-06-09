FROM node:22-alpine
WORKDIR /app
COPY UniGuard-AI-Frontend/package*.json ./
RUN npm install
COPY UniGuard-AI-Frontend/ ./
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
