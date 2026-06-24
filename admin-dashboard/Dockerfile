FROM node:20-alpine
WORKDIR /app
COPY package.json next.config.js tsconfig.json postcss.config.js tailwind.config.ts ./
COPY src ./src
RUN npm install
RUN npm run build
EXPOSE 3005
CMD ["npm", "run", "start", "--", "-p", "3005"]

