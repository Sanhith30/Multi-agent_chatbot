@echo off
echo 🚀 SunnyAI Production Deployment for Windows
echo ================================================

echo.
echo 📋 Step 1: Checking Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker not found. Please install Docker Desktop for Windows
    echo 📥 Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo ✅ Docker found

echo.
echo 📋 Step 2: Checking .env file...
if not exist ".env" (
    echo ❌ .env file not found
    echo 📝 Please edit .env file with your OpenAI API key
    pause
    exit /b 1
)
echo ✅ .env file exists

echo.
echo 📋 Step 3: Building Docker images...
docker-compose -f docker-compose.prod.yml build
if %errorlevel% neq 0 (
    echo ❌ Docker build failed
    pause
    exit /b 1
)
echo ✅ Docker images built successfully

echo.
echo 📋 Step 4: Starting production services...
docker-compose -f docker-compose.prod.yml up -d
if %errorlevel% neq 0 (
    echo ❌ Failed to start services
    pause
    exit /b 1
)

echo.
echo ⏳ Waiting for services to be ready...
timeout /t 30 /nobreak >nul

echo.
echo 🎉 Production deployment completed!
echo.
echo 📊 Access your application:
echo 🌐 Frontend: http://localhost:3001
echo 🔧 Backend API: http://localhost:8000
echo 📈 Grafana: http://localhost:3000 (admin/admin123)
echo 📊 Prometheus: http://localhost:9090
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your real OpenAI API key
echo 2. Test the application at http://localhost:3001
echo 3. Monitor performance at http://localhost:3000
echo.
pause