FROM node:20-slim

WORKDIR /app

# Copy dependency files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Expose frontend port
EXPOSE 5173

# Start development server and expose to all network interfaces
CMD ["npm", "run", "dev", "--", "--host"]
