FROM node:16

# Ustawiamy katalog roboczy dla frontendu
WORKDIR /app

# Instalujemy pnpm globalnie
RUN npm install -g pnpm

# Kopiujemy pliki zależności (package.json oraz ewentualny pnpm-lock.yaml)
COPY frontend/package.json frontend/pnpm-lock.yaml* ./

# Instalujemy zależności przy pomocy pnpm
RUN pnpm install

# Kopiujemy cały kod frontendu
COPY frontend/ .

# Informujemy, że aplikacja będzie działać na porcie 3000
EXPOSE 3000

# Uruchamiamy aplikację
CMD ["pnpm", "dev"]
