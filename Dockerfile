FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Build the Chroma collection at image build time so it's ready when the
# container starts (move this to a startup script if your data changes often)
RUN python data/generate_data.py && python -m app.ingest

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
