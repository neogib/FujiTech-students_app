
FROM node:20

WORKDIR /app/frontend

# Użyj corepack zamiast npm -g pnpm (stabilniej i wersjonowalnie)
RUN corepack enable && corepack prepare pnpm@10.15.0 --activate

# Manifesty osobno (cache warstw)
COPY package.json pnpm-lock.yaml* ./

# Reszta źródeł
COPY . .

EXPOSE 3000

# Jeśli brakuje node_modules -> zainstaluj; potem odpal dev na wszystkich interfejsach
CMD ["/bin/sh","-lc","set -e; if [ ! -x node_modules/.bin/nuxt ]; then echo '→ Installing deps…'; pnpm install --frozen-lockfile; fi; exec pnpm dev"]

