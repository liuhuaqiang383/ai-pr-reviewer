// DOM Elements
const reviewForm = document.getElementById('reviewForm');
const prUrlInput = document.getElementById('prUrl');
const submitBtn = document.getElementById('submitBtn');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const aiProvider = document.getElementById('aiProvider');
const aiModel = document.getElementById('aiModel');

// API Base URL
const API_BASE = '';

// Models configuration
const MODELS = {
    claude: {
        'claude-haiku-4-20250514': 'Claude Haiku (快速)',
        'claude-sonnet-4-20250514': 'Claude Sonnet (平衡)',
        'claude-opus-4-20250514': 'Claude Opus (高质量)'
    },
    openai: {
        'gpt-4o': 'GPT-4o (推荐)',
        'gpt-4o-mini': 'GPT-4o Mini (快速)',
        'gpt-4-turbo': 'GPT-4 Turbo',
        'gpt-3.5-turbo': 'GPT-3.5 Turbo (经济)'
    },
    gemini: {
        'gemini-1.5-pro': 'Gemini 1.5 Pro (推荐)',
        'gemini-1.5-flash': 'Gemini 1.5 Flash (快速)',
        'gemini-1.0-pro': 'Gemini 1.0 Pro'
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    reviewForm.addEventListener('submit', handleSubmit);
    setupFilterButtons();
    setupProviderSelection();
    updateModelOptions();
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

        // Make API call with provider and model
        const response = await fetch(`${API_BASE}/api/review`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pr_url: prUrl,
                provider: getSelectedProvider(),
                model: getSelectedModel()
            })
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
}

function updateModelOptions() {
    const provider = aiProvider.value;
    const models = MODELS[provider] || {};

    // Clear current options
    aiModel.innerHTML = '';

    // Add new options
    Object.entries(models).forEach(([value, label]) => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = label;
        aiModel.appendChild(option);
    });
}

function getSelectedProvider() {
    return aiProvider.value;
}

function getSelectedModel() {
    return aiModel.value;
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
