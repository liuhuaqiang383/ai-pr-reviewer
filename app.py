from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from services.review_engine import ReviewEngine
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize review engine
review_engine = ReviewEngine()


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/review', methods=['POST'])
def review_pr():
    """API endpoint to review a PR"""
    data = request.get_json()
    pr_url = data.get('pr_url', '')

    if not pr_url:
        return jsonify({'error': '请提供PR URL'}), 400

    logger.info(f'Reviewing PR: {pr_url}')

    try:
        result = review_engine.review_pr(pr_url)
        return jsonify(result)
    except Exception as e:
        logger.error(f'Review failed: {str(e)}')
        return jsonify({'error': f'审查失败: {str(e)}'}), 500


@app.route('/api/analyze-file', methods=['POST'])
def analyze_file():
    """API endpoint for deep file analysis"""
    data = request.get_json()
    pr_url = data.get('pr_url', '')
    filename = data.get('filename', '')

    if not pr_url or not filename:
        return jsonify({'error': '请提供PR URL和文件名'}), 400

    try:
        result = review_engine.get_file_deep_analysis(pr_url, filename)
        return jsonify(result)
    except Exception as e:
        logger.error(f'File analysis failed: {str(e)}')
        return jsonify({'error': f'分析失败: {str(e)}'}), 500


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'github_configured': bool(Config.GITHUB_TOKEN),
        'claude_configured': bool(Config.CLAUDE_API_KEY)
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
