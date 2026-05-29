from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from services.review_engine import ReviewEngine
from services.providers.factory import ProviderFactory
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize factory
provider_factory = ProviderFactory()


@app.route('/')
def index():
    """Serve the main page"""
    providers_info = provider_factory.get_available_providers()
    return render_template('index.html', providers=providers_info)


@app.route('/api/review', methods=['POST'])
def review_pr():
    """API endpoint to review a PR"""
    data = request.get_json()
    pr_url = data.get('pr_url', '')
    provider_id = data.get('provider', None)
    model = data.get('model', None)
    custom_config = data.get('custom_config', None)

    if not pr_url:
        return jsonify({'error': '请提供PR URL'}), 400

    logger.info(f'Reviewing PR: {pr_url} with provider: {provider_id}, model: {model}')

    try:
        review_engine = ReviewEngine(provider_id, model, custom_config)
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
    provider_id = data.get('provider', None)
    model = data.get('model', None)
    custom_config = data.get('custom_config', None)

    if not pr_url or not filename:
        return jsonify({'error': '请提供PR URL和文件名'}), 400

    try:
        review_engine = ReviewEngine(provider_id, model, custom_config)
        result = review_engine.get_file_deep_analysis(pr_url, filename)
        return jsonify(result)
    except Exception as e:
        logger.error(f'File analysis failed: {str(e)}')
        return jsonify({'error': f'分析失败: {str(e)}'}), 500


@app.route('/api/providers')
def get_providers():
    """Get available providers and models"""
    return jsonify(provider_factory.get_available_providers())


@app.route('/api/providers/test', methods=['POST'])
def test_provider():
    """Test a provider connection"""
    data = request.get_json()
    provider_id = data.get('provider')
    model = data.get('model')
    custom_config = data.get('custom_config')

    try:
        from services.providers.factory import ProviderFactory
        factory = ProviderFactory()
        provider = factory.create_provider(provider_id, model, custom_config)

        # Test with a simple prompt
        result = provider.analyze("Hello, respond with 'OK' if you receive this.", max_tokens=10)

        return jsonify({
            'success': True,
            'provider': provider.get_provider_name(),
            'model': provider.get_model_name(),
            'response': result[:100]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    providers = provider_factory.get_available_providers()
    return jsonify({
        'status': 'healthy',
        'github_configured': bool(Config.GITHUB_TOKEN),
        'providers': {name: info['available'] for name, info in providers.items()}
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
