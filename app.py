from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
from services.review_engine import ReviewEngine
from services.providers.factory import ProviderFactory
from config import Config
import logging
import json

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


@app.route('/api/review/stream', methods=['POST'])
def review_pr_stream():
    """API endpoint to review a PR with streaming progress"""
    data = request.get_json()
    pr_url = data.get('pr_url', '')
    provider_id = data.get('provider', None)
    model = data.get('model', None)
    custom_config = data.get('custom_config', None)

    if not pr_url:
        return jsonify({'error': '请提供PR URL'}), 400

    def generate():
        review_engine = ReviewEngine(provider_id, model, custom_config)
        for event in review_engine.review_pr_stream(pr_url):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/comment', methods=['POST'])
def post_comment():
    """API endpoint to post analysis as GitHub comment"""
    data = request.get_json()
    pr_url = data.get('pr_url', '')
    analysis = data.get('analysis', {})
    comment_type = data.get('type', 'review')
    provider_id = data.get('provider', None)
    model = data.get('model', None)
    custom_config = data.get('custom_config', None)

    if not pr_url or not analysis:
        return jsonify({'error': '请提供PR URL和分析结果'}), 400

    try:
        review_engine = ReviewEngine(provider_id, model, custom_config)
        result = review_engine.post_comment(pr_url, analysis, comment_type)
        return jsonify(result)
    except Exception as e:
        logger.error(f'Comment failed: {str(e)}')
        return jsonify({'error': f'评论失败: {str(e)}'}), 500


@app.route('/api/export', methods=['POST'])
def export_result():
    """API endpoint to export analysis result"""
    data = request.get_json()
    result = data.get('result', {})
    format = data.get('format', 'markdown')
    provider_id = data.get('provider', None)
    model = data.get('model', None)
    custom_config = data.get('custom_config', None)

    if not result:
        return jsonify({'error': '请提供分析结果'}), 400

    try:
        review_engine = ReviewEngine(provider_id, model, custom_config)
        content = review_engine.export_result(result, format)

        if format == 'html':
            return Response(
                content,
                mimetype='text/html',
                headers={'Content-Disposition': 'attachment; filename=review-report.html'}
            )
        elif format == 'json':
            return Response(
                content,
                mimetype='application/json',
                headers={'Content-Disposition': 'attachment; filename=review-report.json'}
            )
        else:
            return Response(
                content,
                mimetype='text/markdown',
                headers={'Content-Disposition': 'attachment; filename=review-report.md'}
            )
    except Exception as e:
        logger.error(f'Export failed: {str(e)}')
        return jsonify({'error': f'导出失败: {str(e)}'}), 500


@app.route('/api/cache/stats')
def cache_stats():
    """Get cache statistics"""
    try:
        review_engine = ReviewEngine()
        stats = review_engine.get_cache_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear cache"""
    data = request.get_json() or {}
    older_than_hours = data.get('older_than_hours', 24)

    try:
        review_engine = ReviewEngine()
        review_engine.clear_cache(older_than_hours)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
