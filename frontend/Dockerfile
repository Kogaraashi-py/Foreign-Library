 # novels-portable/frontend/Dockerfile

# ═══════════════════════════════════════════════════════
# STAGE 1: Build
# ═══════════════════════════════════════════════════════
FROM node:18-alpine AS build

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm ci --only=production

# Copiar código fuente
COPY . .

# Build de producción
RUN npm run build

# ═══════════════════════════════════════════════════════
# STAGE 2: Production
# ═══════════════════════════════════════════════════════
FROM nginx:alpine

# Copiar build desde stage anterior
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuración de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Comando
CMD ["nginx", "-g", "daemon off;"]
