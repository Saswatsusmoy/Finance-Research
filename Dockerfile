FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p data/agent_states

# Expose ports for API and Streamlit
EXPOSE 8000
EXPOSE 8501

# Create an entrypoint script
RUN echo '#!/bin/bash\n\
uvicorn src.api:app --host 0.0.0.0 --port 8000 & \n\
streamlit run app.py --server.port 8501 --server.address 0.0.0.0\n' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"] 