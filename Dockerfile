FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Test environment and imports before trying the real app
CMD echo "=== Checking Python ===" && \
    python --version && \
    echo "=== Checking Env Vars ===" && \
    echo "SUPABASE_URL=$SUPABASE_URL" && \
    echo "SUPABASE_KEY=$SUPABASE_KEY" && \
    echo "=== Testing Supabase import ===" && \
    python -c "from supabase import create_client; print('Import OK')" && \
    echo "=== Running the app ===" && \
    flet run --web main.py --port $PORT 2>&1
