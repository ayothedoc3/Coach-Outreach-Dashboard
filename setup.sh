#!/bin/bash


set -e

echo "🚀 Setting up Coach Outreach Dashboard..."

check_requirements() {
    echo "📋 Checking requirements..."
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not installed."
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is required but not installed."
        exit 1
    fi
    
    if ! command -v poetry &> /dev/null; then
        echo "📦 Installing Poetry..."
        curl -sSL https://install.python-poetry.org | python3 -
        export PATH="$HOME/.local/bin:$PATH"
    fi
    
    echo "✅ Requirements check passed!"
}

setup_env() {
    echo "⚙️ Setting up environment variables..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "📝 Created .env file from template"
        echo "⚠️  Please edit .env with your actual credentials before running the application"
    else
        echo "✅ .env file already exists"
    fi
}

setup_backend() {
    echo "🔧 Setting up backend..."
    
    cd backend
    
    echo "📦 Installing Python dependencies..."
    poetry install
    
    mkdir -p ../data
    
    echo "✅ Backend setup complete!"
    cd ..
}

setup_frontend() {
    echo "🎨 Setting up frontend..."
    
    cd frontend
    
    echo "📦 Installing Node.js dependencies..."
    npm install
    
    echo "✅ Frontend setup complete!"
    cd ..
}

create_scripts() {
    echo "📜 Creating startup scripts..."
    
    cat > start-backend.sh << 'EOF'
#!/bin/bash
cd backend
echo "🚀 Starting backend server..."
poetry run python app/main.py
EOF
    chmod +x start-backend.sh
    
    cat > start-frontend.sh << 'EOF'
#!/bin/bash
cd frontend
echo "🚀 Starting frontend server..."
npm run dev
EOF
    chmod +x start-frontend.sh
    
    cat > start-all.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Coach Outreach Dashboard..."

echo "Starting backend..."
cd backend
poetry run python app/main.py &
BACKEND_PID=$!
cd ..

sleep 3

echo "Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ Both servers started!"
echo "📊 Frontend: http://localhost:5174"
echo "🔧 Backend: http://localhost:8001"
echo "🔑 Demo login: admin / admin"
echo ""
echo "Press Ctrl+C to stop all servers"

trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF
    chmod +x start-all.sh
    
    echo "✅ Startup scripts created!"
}

main() {
    echo "🎯 Coach Outreach Dashboard Setup"
    echo "=================================="
    
    check_requirements
    setup_env
    setup_backend
    setup_frontend
    create_scripts
    
    echo ""
    echo "🎉 Setup complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Edit .env file with your credentials"
    echo "2. Run ./start-all.sh to start both servers"
    echo "3. Open http://localhost:5174 in your browser"
    echo "4. Login with demo credentials: admin / admin"
    echo ""
    echo "📚 For more information, see README.md"
}

main "$@"
