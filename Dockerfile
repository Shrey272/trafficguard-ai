# -----------------------------------
# Stage 1: Build the React Frontend
# -----------------------------------
FROM node:20-alpine as frontend-builder

WORKDIR /app/frontend

# Copy package files and install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# Copy the rest of the frontend source code and build
COPY frontend/ ./
RUN npm run build


# -----------------------------------
# Stage 2: Setup Python Backend
# -----------------------------------
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Copy compiled frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose the port
EXPOSE 8000

# Set working directory to backend where main.py lives
WORKDIR /app/backend

# Run the FastAPI server
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
