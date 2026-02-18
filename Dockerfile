## ---- build stage ----
FROM python:3.12-slim AS build

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

## ---- runtime stage ----
FROM python:3.12-slim

WORKDIR /app

COPY --from=build /install /usr/local
COPY . .

EXPOSE 8000
CMD ["sh", "entrypoint.sh"]
