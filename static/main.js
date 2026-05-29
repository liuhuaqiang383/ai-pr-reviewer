// DOM Elements
const reviewForm = document.getElementById('reviewForm');
const prUrlInput = document.getElementById('prUrl');
const submitBtn = document.getElementById('submitBtn');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const aiProvider = document.getElementById('aiProvider');
const aiModel = document.getElementById('aiModel');
const customConfigBtn = document.getElementById('customConfigBtn');
const customConfigModal = document.getElementById('customConfigModal');

// API Base URL
const API_BASE = '';

// Providers data (will be fetched from API)
let providersData = {};

// Custom config
let customConfig = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    reviewForm.addEventListener('submit', handleSubmit);
    setupFilterButtons();
    setupProviderSelection();
    loadProviders();
});

// Form Submission
async function handleSubmit(e) {
    e.preventDefault();

    const prUrl = prUrlInput.value.trim();
    if (!prUrl) return;

    // Show loading
    showLoading();
    disableSubmit();

    try {
        // Simulate progress steps
        animateLoadingSteps();

        // Build request body
        const requestBody = {
            pr_url: prUrl,
            provider: getSelectedProvider(),
            model: getSelectedModel()
        };

        // Add custom config if using custom provider
        if (getSelectedProvider() === 'custom') {
            const config = getCustomConfig();
            if (!config) {
                throw new Error('请先配置自定义AI提供商');
            }
            requestBody.custom_config = config;
        }

        // Make API call
        const response = await fetch(`${API_BASE}/api/review`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        // Display results
        displayResults(data);

    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
        enableSubmit();
    }
}

// Loading States
function showLoading() {
    loadingSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
}

function hideLoading() {
    loadingSection.classList.add('hidden');
}

function animateLoadingSteps() {
    const steps = document.querySelectorAll('.step');
    let currentStep = 0;

    const interval = setInterval(() => {
        if (currentStep < steps.length) {
            steps[currentStep].classList.add('active');
            if (currentStep > 0) {
                steps[currentStep - 1].classList.remove('active');
                steps[currentStep - 1].classList.add('completed');
            }
            currentStep++;
        } else {
            clearInterval(interval);
        }
    }, 2000);
}

// Submit Button States
function disableSubmit() {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>分析中...</span>';
}

function enableSubmit() {
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="fas fa-magic"></i> <span>开始分析</span>';
}

// Display Results
function displayResults(data) {
    resultsSection.classList.remove('hidden');

    // PR Info
    displayPRInfo(data.pr_info, data.statistics);

    // Risk Level
    displayRiskLevel(data.analysis);

    // Summary
    displaySummary(data.analysis);

    // Issues
    displayIssues(data.analysis);

    // Suggestions
    displaySuggestions(data.analysis);

    // Highlights
    displayHighlights(data.analysis);

    // Checklist
    displayChecklist(data.analysis);

    // Files
    displayFiles(data.files_changed);

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Display PR Info
function displayPRInfo(prInfo, stats) {
    document.getElementById('prTitle').textContent = prInfo.title;
    document.getElementById('prAuthor').textContent = prInfo.author;
    document.getElementById('prBranch').textContent = `${prInfo.base_branch} ← ${prInfo.head_branch}`;
    document.getElementById('prLink').href = prInfo.url;

    document.getElementById('statFiles').textContent = stats.total_files;
    document.getElementById('statAdditions').textContent = `+${stats.total_additions}`;
    document.getElementById('statDeletions').textContent = `-${stats.total_deletions}`;
}

// Display Risk Level
function displayRiskLevel(analysis) {
    const riskBadge = document.getElementById('riskBadge');
    const riskDescription = document.getElementById('riskDescription');

    const riskLevel = analysis.risk_level || 'medium';
    riskBadge.textContent = riskLevel.toUpperCase();
    riskBadge.className = `risk-badge ${riskLevel}`;

    const riskDescriptions = {
        low: '此PR风险较低，变更较为安全。',
        medium: '此PR存在一定风险，建议仔细审查。',
        high: '此PR风险较高，需要重点关注潜在问题。',
        critical: '此PR存在严重风险，强烈建议详细审查后再合并。'
    };

    riskDescription.textContent = riskDescriptions[riskLevel] || '请查看详细分析。';
}

// Display Summary
function displaySummary(analysis) {
    const summaryContent = document.getElementById('summaryContent');
    summaryContent.textContent = analysis.summary || '暂无总结';
}

// Display Issues
function displayIssues(analysis) {
    const issuesList = document.getElementById('issuesList');
    const issues = analysis.issues || [];

    if (issues.length === 0) {
        issuesList.innerHTML = '<p style="color: var(--text-secondary); text-align: center;">未发现明显问题</p>';
        return;
    }

    issuesList.innerHTML = issues.map(issue => `
        <div class="issue-item ${issue.severity || 'info'}" data-severity="${issue.severity || 'info'}">
            <div class="issue-header">
                <span class="issue-severity ${issue.severity || 'info'}">${getSeverityLabel(issue.severity)}</span>
                <span class="issue-category">${issue.category || '其他'}</span>
            </div>
            ${issue.file ? `<div class="issue-file"><i class="fas fa-file-code"></i> ${issue.file}${issue.line ? `:${issue.line}` : ''}</div>` : ''}
            <div class="issue-description">${issue.description || ''}</div>
            ${issue.suggestion ? `<div class="issue-suggestion"><i class="fas fa-lightbulb"></i> ${issue.suggestion}</div>` : ''}
        </div>
    `).join('');
}

// Display Suggestions
function displaySuggestions(analysis) {
    const suggestionsList = document.getElementById('suggestionsList');
    const suggestions = analysis.suggestions || [];

    if (suggestions.length === 0) {
        suggestionsList.innerHTML = '<p style="color: var(--text-secondary); text-align: center;">暂无建议</p>';
        return;
    }

    suggestionsList.innerHTML = suggestions.map(suggestion => `
        <div class="suggestion-item">
            <i class="fas fa-check-circle"></i>
            <span>${suggestion}</span>
        </div>
    `).join('');
}

// Display Highlights
function displayHighlights(analysis) {
    const highlightsList = document.getElementById('highlightsList');
    const highlights = analysis.highlights || [];

    if (highlights.length === 0) {
        highlightsList.innerHTML = '<p style="color: var(--text-secondary); text-align: center;">暂无亮点</p>';
        return;
    }

    highlightsList.innerHTML = highlights.map(highlight => `
        <div class="highlight-item">
            <i class="fas fa-star" style="color: var(--warning-color);"></i>
            <span>${highlight}</span>
        </div>
    `).join('');
}

// Display Checklist
function displayChecklist(analysis) {
    const checklist = document.getElementById('checklist');
    const items = analysis.checklist || [];

    if (items.length === 0) {
        checklist.innerHTML = '<p style="color: var(--text-secondary); text-align: center;">暂无检查项</p>';
        return;
    }

    checklist.innerHTML = items.map((item, index) => `
        <div class="checklist-item">
            <input type="checkbox" id="check-${index}">
            <label for="check-${index}">${item}</label>
        </div>
    `).join('');
}

// Display Files
function displayFiles(files) {
    const filesList = document.getElementById('filesList');

    if (!files || files.length === 0) {
        filesList.innerHTML = '<p style="color: var(--text-secondary); text-align: center;">无文件变更</p>';
        return;
    }

    filesList.innerHTML = files.map(file => `
        <div class="file-item">
            <span class="file-name">${file.filename}</span>
            <div class="file-stats">
                <span class="file-additions">+${file.additions}</span>
                <span class="file-deletions">-${file.deletions}</span>
                <span class="file-status">${file.status}</span>
            </div>
        </div>
    `).join('');
}

// Filter Buttons
function setupFilterButtons() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Filter issues
            const filter = btn.dataset.filter;
            filterIssues(filter);
        });
    });
}

function filterIssues(filter) {
    document.querySelectorAll('.issue-item').forEach(item => {
        if (filter === 'all' || item.dataset.severity === filter) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// Provider Selection
function setupProviderSelection() {
    aiProvider.addEventListener('change', updateModelOptions);
    customConfigBtn.addEventListener('click', openCustomConfig);
}

async function loadProviders() {
    try {
        const response = await fetch(`${API_BASE}/api/providers`);
        providersData = await response.json();
        populateProviders();
    } catch (error) {
        console.error('Failed to load providers:', error);
        // Fallback to default options
        aiProvider.innerHTML = '<option value="openai">OpenAI</option>';
    }
}

function populateProviders() {
    aiProvider.innerHTML = '';

    // Add custom config option first
    const customOption = document.createElement('option');
    customOption.value = 'custom';
    customOption.textContent = '⚡ 自定义配置';
    aiProvider.appendChild(customOption);

    // Add available providers
    Object.entries(providersData).forEach(([id, info]) => {
        const option = document.createElement('option');
        option.value = id;
        option.textContent = `${info.available ? '●' : '○'} ${info.name}`;
        option.disabled = !info.available;
        aiProvider.appendChild(option);
    });

    // Select first available provider
    const firstAvailable = Object.entries(providersData).find(([_, info]) => info.available);
    if (firstAvailable) {
        aiProvider.value = firstAvailable[0];
    }

    updateModelOptions();
}

function updateModelOptions() {
    const provider = aiProvider.value;
    aiModel.innerHTML = '';

    if (provider === 'custom') {
        // Show custom config modal
        openCustomConfig();
        return;
    }

    const providerInfo = providersData[provider];
    if (!providerInfo) return;

    const models = providerInfo.models || [];
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        aiModel.appendChild(option);
    });
}

function getSelectedProvider() {
    return aiProvider.value;
}

function getSelectedModel() {
    return aiModel.value;
}

function getCustomConfig() {
    return customConfig;
}

// Custom Config Modal
function openCustomConfig() {
    customConfigModal.classList.remove('hidden');
}

function closeCustomConfig() {
    customConfigModal.classList.add('hidden');
    // Reset to previous selection if custom not applied
    if (!customConfig) {
        const firstAvailable = Object.entries(providersData).find(([_, info]) => info.available);
        if (firstAvailable) {
            aiProvider.value = firstAvailable[0];
            updateModelOptions();
        }
    }
}

async function testCustomConfig() {
    const config = getCustomConfigFromForm();
    const resultDiv = document.getElementById('customTestResult');

    try {
        const response = await fetch(`${API_BASE}/api/providers/test`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ custom_config: config })
        });

        const data = await response.json();

        resultDiv.classList.remove('hidden', 'success', 'error');
        if (data.success) {
            resultDiv.classList.add('success');
            resultDiv.innerHTML = `<i class="fas fa-check-circle"></i> 连接成功！模型: ${data.model}`;
        } else {
            resultDiv.classList.add('error');
            resultDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${data.error}`;
        }
    } catch (error) {
        resultDiv.classList.remove('hidden', 'success', 'error');
        resultDiv.classList.add('error');
        resultDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> 测试失败: ${error.message}`;
    }
}

function applyCustomConfig() {
    customConfig = getCustomConfigFromForm();

    // Update UI to show custom config is active
    aiProvider.value = 'custom';

    // Add custom model to select
    aiModel.innerHTML = '';
    const option = document.createElement('option');
    option.value = customConfig.model;
    option.textContent = `${customConfig.model} (自定义)`;
    aiModel.appendChild(option);

    closeCustomConfig();

    // Show success message
    showNotification('自定义配置已应用', 'success');
}

function getCustomConfigFromForm() {
    return {
        name: document.getElementById('customName').value || 'Custom LLM',
        type: document.getElementById('customType').value,
        base_url: document.getElementById('customBaseUrl').value,
        api_key: document.getElementById('customApiKey').value,
        model: document.getElementById('customModel').value || 'default'
    };
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `<i class="fas fa-${type === 'success' ? 'check' : 'info'}-circle"></i> ${message}`;
    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Helpers
function getSeverityLabel(severity) {
    const labels = {
        critical: '严重',
        warning: '警告',
        info: '信息',
        error: '错误'
    };
    return labels[severity] || '信息';
}

function showError(message) {
    resultsSection.classList.remove('hidden');
    resultsSection.innerHTML = `
        <div class="result-card" style="text-align: center; color: var(--error-color);">
            <i class="fas fa-exclamation-circle" style="font-size: 3rem; margin-bottom: 1rem;"></i>
            <h3>分析失败</h3>
            <p>${message}</p>
            <button onclick="location.reload()" style="margin-top: 1rem; padding: 0.75rem 1.5rem; background: var(--primary-color); color: white; border: none; border-radius: var(--radius-md); cursor: pointer;">
                重试
            </button>
        </div>
    `;
}
