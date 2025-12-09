/**
 * SEO Engine Loading Overlay with Toast Notifications
 * Compatible with Django Unfold admin (HTMX-based)
 */
(function() {
    'use strict';

    // Actions that should show loading overlay (excludes instant actions like exports)
    const LOADING_ACTIONS = [
        'run_lighthouse_audit',
        'run_pagespeed_analysis',
        'generate_ai_analysis',
        'generate_ai_recommendations',
        'generate_combined_ai_analysis',
        'regenerate_ai_analysis',
        'run_sync',
        'process_uploads',
        'process_ubersuggest',
        'generate_ai_playbooks',
        'generate_blog_drafts',
        'generate_fix_recommendation',
        'apply_meta_to_page',
        'apply_to_matching_service',
        'approve_recommendations',
        'apply_recommendations',
        'generate_ai_meta'
    ];

    // Actions that return file downloads (don't show loading, they're instant)
    const DOWNLOAD_ACTIONS = [
        'export_analysis_markdown'
    ];

    // Loading messages for each action
    const LOADING_MESSAGES = {
        'run_lighthouse_audit': 'Running Lighthouse Audit... This may take 30-60 seconds per URL.',
        'run_pagespeed_analysis': 'Analyzing with PageSpeed Insights...',
        'generate_ai_analysis': 'Generating AI Analysis with ChatGPT... Results will appear in "AI Analysis" tab.',
        'generate_ai_recommendations': 'Generating AI Recommendations from PageSpeed data...',
        'generate_combined_ai_analysis': 'Generating COMBINED AI Analysis... Aggregating all data sources.',
        'regenerate_ai_analysis': 'Regenerating AI Analysis...',
        'run_sync': 'Syncing Search Console Data...',
        'process_uploads': 'Processing CSV Upload...',
        'process_ubersuggest': 'Processing Ubersuggest Export... Parsing keywords, competitors, and backlinks.',
        'generate_ai_playbooks': 'Generating AI Recommendations...',
        'generate_blog_drafts': 'Creating Blog Drafts with AI...',
        'generate_fix_recommendation': 'Generating Fix Recommendations...',
        'apply_meta_to_page': 'Applying Meta Kit to matching pages... Updating SEO settings.',
        'apply_to_matching_service': 'Smart matching keywords to services... Applying SEO recommendations.',
        'approve_recommendations': 'Approving selected recommendations...',
        'apply_recommendations': 'Applying SEO recommendations to pages...',
        'generate_ai_meta': 'Generating AI Meta Tags with ChatGPT... This may take a few seconds per page.'
    };

    let isLoading = false;
    let currentAction = null;

    // Inject styles
    function injectStyles() {
        if (document.getElementById('seo-loading-styles')) return;

        const style = document.createElement('style');
        style.id = 'seo-loading-styles';
        style.textContent = `
            /* Loading Overlay - Full Screen */
            #seo-loading-overlay {
                display: none;
                position: fixed;
                inset: 0;
                background: rgba(0, 0, 0, 0.8);
                backdrop-filter: blur(8px);
                z-index: 999999;
                justify-content: center;
                align-items: center;
                transition: opacity 0.2s ease;
            }
            #seo-loading-overlay.active {
                display: flex !important;
            }
            .seo-loading-content {
                text-align: center;
                color: white;
                padding: 2.5rem;
                max-width: 28rem;
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.98) 0%, rgba(15, 23, 42, 0.98) 100%);
                border-radius: 1rem;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .seo-loading-spinner {
                width: 3.5rem;
                height: 3.5rem;
                border: 3px solid rgba(255, 255, 255, 0.2);
                border-top-color: #f9cb07;
                border-radius: 50%;
                animation: seo-spin 0.8s linear infinite;
                margin: 0 auto 1.5rem;
            }
            @keyframes seo-spin {
                to { transform: rotate(360deg); }
            }
            .seo-loading-title {
                font-size: 1.25rem;
                font-weight: 600;
                margin-bottom: 0.75rem;
                color: #f8fafc;
            }
            .seo-loading-message {
                font-size: 0.875rem;
                color: #94a3b8;
                margin-bottom: 1rem;
                line-height: 1.6;
            }
            .seo-loading-warning {
                font-size: 0.75rem;
                color: #fbbf24;
                font-weight: 500;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
            }
            .seo-loading-warning svg {
                width: 1rem;
                height: 1rem;
            }
            body.seo-loading-active {
                overflow: hidden !important;
            }
            body.seo-loading-active * {
                pointer-events: none !important;
            }
            body.seo-loading-active #seo-loading-overlay,
            body.seo-loading-active #seo-loading-overlay * {
                pointer-events: auto !important;
            }

            /* Toast Container */
            #seo-toast-container {
                position: fixed;
                top: 1rem;
                right: 1rem;
                z-index: 1000000;
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
                max-width: 28rem;
                pointer-events: none;
            }
            #seo-toast-container > * {
                pointer-events: auto;
            }

            /* Toast Base */
            .seo-toast {
                display: flex;
                align-items: flex-start;
                gap: 0.75rem;
                padding: 1rem 1.25rem;
                border-radius: 0.75rem;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
                transform: translateX(120%);
                transition: transform 0.3s ease, opacity 0.3s ease;
                opacity: 0;
                border: 1px solid;
                position: relative;
            }
            .seo-toast.active {
                transform: translateX(0);
                opacity: 1;
            }
            .seo-toast.hiding {
                transform: translateX(120%);
                opacity: 0;
            }

            /* Toast Types */
            .seo-toast.success {
                background: linear-gradient(135deg, #065f46 0%, #047857 100%);
                border-color: #10b981;
                color: #ecfdf5;
            }
            .seo-toast.error {
                background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
                border-color: #ef4444;
                color: #fef2f2;
            }
            .seo-toast.warning {
                background: linear-gradient(135deg, #78350f 0%, #92400e 100%);
                border-color: #f59e0b;
                color: #fffbeb;
            }
            .seo-toast.info {
                background: linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%);
                border-color: #3b82f6;
                color: #eff6ff;
            }

            .seo-toast-icon { flex-shrink: 0; width: 1.25rem; height: 1.25rem; }
            .seo-toast.success .seo-toast-icon { color: #34d399; }
            .seo-toast.error .seo-toast-icon { color: #f87171; }
            .seo-toast.warning .seo-toast-icon { color: #fbbf24; }
            .seo-toast.info .seo-toast-icon { color: #60a5fa; }

            .seo-toast-content { flex: 1; min-width: 0; }
            .seo-toast-title { font-weight: 600; font-size: 0.875rem; margin-bottom: 0.25rem; }
            .seo-toast-message { font-size: 0.8125rem; opacity: 0.9; line-height: 1.4; }

            .seo-toast-close {
                flex-shrink: 0;
                padding: 0.25rem;
                margin: -0.25rem;
                cursor: pointer;
                opacity: 0.7;
                transition: opacity 0.2s;
                background: none;
                border: none;
                color: inherit;
            }
            .seo-toast-close:hover { opacity: 1; }
            .seo-toast-close svg { width: 1rem; height: 1rem; }

            .seo-toast-progress {
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 0 0 0.75rem 0.75rem;
                overflow: hidden;
            }
            .seo-toast-progress-bar {
                height: 100%;
                background: rgba(255, 255, 255, 0.6);
                width: 100%;
                animation: seo-progress 6s linear forwards;
            }
            @keyframes seo-progress {
                from { width: 100%; }
                to { width: 0%; }
            }
        `;
        document.head.appendChild(style);
    }

    // Create toast container
    function createToastContainer() {
        if (document.getElementById('seo-toast-container')) return;
        const container = document.createElement('div');
        container.id = 'seo-toast-container';
        document.body.appendChild(container);
    }

    // Icons
    const ICONS = {
        success: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>',
        error: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" /></svg>',
        warning: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" /></svg>',
        info: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" /></svg>',
        close: '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>'
    };

    // Show toast notification
    function showToast(type, title, message, autoClose = 6000) {
        createToastContainer();
        const container = document.getElementById('seo-toast-container');

        const toast = document.createElement('div');
        toast.className = `seo-toast ${type}`;

        toast.innerHTML = `
            <span class="seo-toast-icon">${ICONS[type] || ICONS.info}</span>
            <div class="seo-toast-content">
                <div class="seo-toast-title">${title}</div>
                ${message ? `<div class="seo-toast-message">${message}</div>` : ''}
            </div>
            <button class="seo-toast-close">${ICONS.close}</button>
            ${autoClose ? '<div class="seo-toast-progress"><div class="seo-toast-progress-bar"></div></div>' : ''}
        `;

        container.appendChild(toast);

        requestAnimationFrame(() => toast.classList.add('active'));

        const closeBtn = toast.querySelector('.seo-toast-close');
        closeBtn.addEventListener('click', () => removeToast(toast));

        if (autoClose) {
            setTimeout(() => removeToast(toast), autoClose);
        }

        return toast;
    }

    function removeToast(toast) {
        if (!toast || !toast.parentNode) return;
        toast.classList.remove('active');
        toast.classList.add('hiding');
        setTimeout(() => toast.remove(), 300);
    }

    // Create loading overlay
    function createOverlay() {
        if (document.getElementById('seo-loading-overlay')) return;

        const overlay = document.createElement('div');
        overlay.id = 'seo-loading-overlay';
        overlay.innerHTML = `
            <div class="seo-loading-content">
                <div class="seo-loading-spinner"></div>
                <h2 class="seo-loading-title">Processing...</h2>
                <p class="seo-loading-message">Please wait while we process your request.</p>
                <p class="seo-loading-warning">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                    </svg>
                    Do not close or navigate away
                </p>
            </div>
        `;
        document.body.appendChild(overlay);
    }

    // Show loading overlay
    function showLoading(action) {
        if (isLoading) return;
        isLoading = true;
        currentAction = action;

        createOverlay();
        const overlay = document.getElementById('seo-loading-overlay');
        const title = overlay.querySelector('.seo-loading-title');
        const message = overlay.querySelector('.seo-loading-message');

        title.textContent = 'Processing...';
        message.textContent = LOADING_MESSAGES[action] || 'Please wait while we process your request.';

        overlay.classList.add('active');
        document.body.classList.add('seo-loading-active');

        console.log('[SEO Loading] Showing loading for:', action);
    }

    // Hide loading overlay
    function hideLoading() {
        isLoading = false;
        currentAction = null;

        const overlay = document.getElementById('seo-loading-overlay');
        if (overlay) {
            overlay.classList.remove('active');
        }
        document.body.classList.remove('seo-loading-active');

        console.log('[SEO Loading] Hiding loading');
    }

    // Get selected action from form - check multiple possible selectors
    function getSelectedAction() {
        // Try different selectors that Unfold might use
        const selectors = [
            'select[name="action"]',
            '#changelist-form select[name="action"]',
            '.actions select[name="action"]',
            '[data-action-select]'
        ];

        for (const selector of selectors) {
            const actionSelect = document.querySelector(selector);
            if (actionSelect && actionSelect.value) {
                console.log('[SEO Loading] Found action:', actionSelect.value, 'via', selector);
                return actionSelect.value;
            }
        }

        return null;
    }

    // Check if items are selected - check multiple possible selectors
    function hasSelectedItems() {
        const selectors = [
            'input[name="_selected_action"]:checked',
            'input[type="checkbox"][name="_selected_action"]:checked',
            '.action-select:checked',
            'tr.selected input[type="checkbox"]:checked'
        ];

        for (const selector of selectors) {
            const checkboxes = document.querySelectorAll(selector);
            if (checkboxes.length > 0) {
                console.log('[SEO Loading] Found', checkboxes.length, 'selected items via', selector);
                return true;
            }
        }

        return false;
    }

    // Check if action should show loading
    function shouldShowLoading(action) {
        const shouldShow = LOADING_ACTIONS.includes(action);
        console.log('[SEO Loading] Action', action, 'should show loading:', shouldShow);
        return shouldShow;
    }

    // Handle form submission
    function handleFormSubmit(e) {
        const action = getSelectedAction();
        console.log('[SEO Loading] Form submit detected, action:', action);

        if (action && shouldShowLoading(action) && hasSelectedItems()) {
            showLoading(action);
        }
    }

    // Track processed messages to avoid duplicates
    let messagesProcessed = false;

    // Parse Django messages and show as toasts
    function parseAndShowMessages() {
        // Only process once per page load
        if (messagesProcessed) return;

        // Look for Unfold's message containers as well
        const messageSelectors = [
            'ul.messagelist',
            '.messagelist',
            '[data-messages]',
            '.messages'
        ];

        let messageList = null;
        for (const selector of messageSelectors) {
            messageList = document.querySelector(selector);
            if (messageList) break;
        }

        if (!messageList) return;

        const messages = messageList.querySelectorAll('li, .message');
        if (messages.length === 0) return;

        messagesProcessed = true;
        console.log('[SEO Loading] Found', messages.length, 'messages to convert to toasts');

        messages.forEach(msg => {
            let type = 'info';
            let text = msg.textContent.trim();

            if (!text || text.length < 3) return;

            // Determine message type from Django's classes
            if (msg.classList.contains('success')) {
                type = 'success';
            } else if (msg.classList.contains('error')) {
                type = 'error';
            } else if (msg.classList.contains('warning')) {
                type = 'warning';
            } else if (msg.classList.contains('info')) {
                type = 'info';
            }

            // Also check emoji prefixes
            if (text.includes('✅')) type = 'success';
            if (text.includes('❌')) type = 'error';
            if (text.includes('⚠️')) type = 'warning';

            // Clean up emoji prefixes
            const cleanText = text.replace(/^[✅❌⚠️ℹ️🚀🔗]\s*/, '');

            // Extract title and message
            let title = type.charAt(0).toUpperCase() + type.slice(1);
            let message = cleanText;

            const colonIndex = cleanText.indexOf(':');
            if (colonIndex > 0 && colonIndex < 50) {
                title = cleanText.substring(0, colonIndex);
                message = cleanText.substring(colonIndex + 1).trim();
            }

            showToast(type, title, message);
        });

        // Hide original message list
        messageList.style.display = 'none';
    }

    // Initialize
    function init() {
        console.log('[SEO Loading] Initializing v2...');

        injectStyles();
        createOverlay();
        createToastContainer();

        // Handle standard form submissions
        document.addEventListener('submit', function(e) {
            const form = e.target;
            if (form.id === 'changelist-form' || form.querySelector('select[name="action"]')) {
                handleFormSubmit(e);
            }
        }, true);

        // Handle button clicks (Go button) - more aggressive capturing
        document.addEventListener('click', function(e) {
            const button = e.target.closest('button[type="submit"], input[type="submit"], button.action-btn, [data-action-btn]');
            if (button) {
                const form = button.closest('form');
                if (form) {
                    const action = getSelectedAction();
                    if (action && shouldShowLoading(action) && hasSelectedItems()) {
                        console.log('[SEO Loading] Button click triggered loading for:', action);
                        showLoading(action);
                    }
                }
            }
        }, true);

        // Handle action select change - show toast preview
        document.addEventListener('change', function(e) {
            if (e.target.name === 'action') {
                const action = e.target.value;
                if (shouldShowLoading(action)) {
                    console.log('[SEO Loading] Action selected:', action, '- will show loading on submit');
                }
            }
        });

        // HTMX event handlers (Unfold uses HTMX)
        document.body.addEventListener('htmx:beforeRequest', function(e) {
            console.log('[SEO Loading] HTMX beforeRequest:', e.detail);
            const form = e.detail.elt.closest ? e.detail.elt.closest('form') : null;
            if (form) {
                const action = getSelectedAction();
                if (action && shouldShowLoading(action) && hasSelectedItems()) {
                    showLoading(action);
                }
            }
        });

        document.body.addEventListener('htmx:afterRequest', function(e) {
            console.log('[SEO Loading] HTMX afterRequest');
            setTimeout(hideLoading, 100);
        });

        document.body.addEventListener('htmx:afterSwap', function(e) {
            console.log('[SEO Loading] HTMX afterSwap');
            setTimeout(function() {
                hideLoading();
                messagesProcessed = false; // Allow re-processing after swap
                parseAndShowMessages();
            }, 100);
        });

        document.body.addEventListener('htmx:responseError', function(e) {
            hideLoading();
            showToast('error', 'Request Failed', 'An error occurred while processing your request.');
        });

        // Parse messages on load
        setTimeout(parseAndShowMessages, 300);

        // Handle page navigation
        window.addEventListener('beforeunload', function() {
            if (isLoading) {
                // Keep loading visible during navigation
            }
        });

        console.log('[SEO Loading] Initialized successfully. Registered actions:', LOADING_ACTIONS);
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Also run on page load
    window.addEventListener('load', function() {
        setTimeout(function() {
            hideLoading();
            parseAndShowMessages();
        }, 200);
    });

    // Expose globally for debugging and manual use
    window.SEOLoading = {
        show: showLoading,
        hide: hideLoading,
        toast: showToast,
        getAction: getSelectedAction,
        hasSelected: hasSelectedItems,
        actions: LOADING_ACTIONS
    };

})();
