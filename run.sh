#!/bin/bash
echo "Starting Langify Translation Comparison Tool..."
echo ""
echo "The web interface will open at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
streamlit run app.py --server.headless true
