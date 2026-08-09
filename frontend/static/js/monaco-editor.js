/**
 * Monaco Editor Integration
 * Professional code editor with syntax highlighting and advanced features
 */

let editor = null;
let editorTheme = 'vs-light';
const EDITOR_CONFIG = {
    language: 'python',
    theme: editorTheme,
    fontSize: 14,
    fontFamily: "'Fira Code', monospace",
    tabSize: 4,
    insertSpaces: true,
    wordWrap: 'on',
    minimap: { enabled: true },
    scrollBeyondLastLine: false,
    automaticLayout: true,
    formatOnPaste: true,
    formatOnType: true
};

/**
 * Initialize Monaco Editor
 */
function initializeMonacoEditor() {
    // Load Monaco from CDN
    require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' } });

    require(['vs/editor/editor.main'], () => {
        editor = monaco.editor.create(document.getElementById('editor-container'), {
            value: '',
            language: EDITOR_CONFIG.language,
            theme: EDITOR_CONFIG.theme,
            fontSize: EDITOR_CONFIG.fontSize,
            fontFamily: EDITOR_CONFIG.fontFamily,
            tabSize: EDITOR_CONFIG.tabSize,
            insertSpaces: EDITOR_CONFIG.insertSpaces,
            wordWrap: EDITOR_CONFIG.wordWrap,
            minimap: EDITOR_CONFIG.minimap,
            scrollBeyondLastLine: EDITOR_CONFIG.scrollBeyondLastLine,
            automaticLayout: EDITOR_CONFIG.automaticLayout,
            formatOnPaste: EDITOR_CONFIG.formatOnPaste,
            formatOnType: EDITOR_CONFIG.formatOnType
        });

        // Setup autosave
        setupAutosave();

        // Setup keyboard shortcuts
        setupEditorShortcuts();

        // Setup theme toggle
        setupThemeToggle();
    });
}

/**
 * Setup autosave functionality
 */
function setupAutosave() {
    if (!editor) return;

    editor.onDidChangeModelContent(() => {
        const code = editor.getValue();
        saveToLocalStorage(code);
    });
}

/**
 * Setup keyboard shortcuts
 */
function setupEditorShortcuts() {
    if (!editor) return;

    // Ctrl/Cmd + Enter: Run code
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
        runCode();
    });

    // Ctrl/Cmd + Shift + Enter: Submit code
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.Enter, () => {
        submitCode();
    });

    // Ctrl/Cmd + Alt + F: Format code
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Alt | monaco.KeyCode.KeyF, () => {
        editor.getAction('editor.action.formatDocument').run();
    });

    // Ctrl/Cmd + /: Toggle comment
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Slash, () => {
        editor.getAction('editor.action.commentLine').run();
    });
}

/**
 * Setup theme toggle
 */
function setupThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleEditorTheme);
    }
}

/**
 * Toggle editor theme between light and dark
 */
function toggleEditorTheme() {
    if (!editor) return;

    editorTheme = editorTheme === 'vs-light' ? 'vs-dark' : 'vs-light';
    monaco.editor.setTheme(editorTheme);
    localStorage.setItem('editorTheme', editorTheme);
}

/**
 * Set editor language
 */
function setEditorLanguage(language) {
    if (!editor) return;

    const model = editor.getModel();
    monaco.editor.setModelLanguage(model, language);
    localStorage.setItem('editorLanguage', language);
}

/**
 * Set editor font size
 */
function setEditorFontSize(size) {
    if (!editor) return;

    editor.updateOptions({ fontSize: parseInt(size) });
    localStorage.setItem('editorFontSize', size);
}

/**
 * Get editor content
 */
function getEditorContent() {
    return editor ? editor.getValue() : '';
}

/**
 * Set editor content
 */
function setEditorContent(content) {
    if (editor) {
        editor.setValue(content);
    }
}

/**
 * Clear editor
 */
function clearEditor() {
    if (editor) {
        editor.setValue('');
    }
}

/**
 * Save code to local storage
 */
function saveToLocalStorage(code) {
    if (app.currentProblem) {
        const key = `problem_${app.currentProblem.id}_code`;
        localStorage.setItem(key, code);
    }
}

/**
 * Load code from local storage
 */
function loadFromLocalStorage() {
    if (app.currentProblem) {
        const key = `problem_${app.currentProblem.id}_code`;
        const code = localStorage.getItem(key);
        if (code) {
            setEditorContent(code);
        }
    }
}

/**
 * Get editor selection
 */
function getEditorSelection() {
    if (!editor) return null;

    const selection = editor.getSelection();
    const model = editor.getModel();
    return model.getValueInRange(selection);
}

/**
 * Add decoration to editor (highlight lines)
 */
function decorateEditorLine(lineNumber, className) {
    if (!editor) return;

    const decorations = [{
        range: new monaco.Range(lineNumber, 1, lineNumber, 1),
        options: {
            isWholeLine: true,
            className: className,
            glyphMarginClassName: className
        }
    }];

    editor.deltaDecorations([], decorations);
}

/**
 * Show inline error
 */
function showInlineError(lineNumber, message) {
    if (!editor) return;

    const model = editor.getModel();
    const markers = [{
        severity: monaco.MarkerSeverity.Error,
        startLineNumber: lineNumber,
        startColumn: 1,
        endLineNumber: lineNumber,
        endColumn: model.getLineLength(lineNumber) + 1,
        message: message
    }];

    monaco.editor.setModelMarkers(model, 'owner', markers);
}

/**
 * Clear inline errors
 */
function clearInlineErrors() {
    if (!editor) return;

    const model = editor.getModel();
    monaco.editor.setModelMarkers(model, 'owner', []);
}

/**
 * Show autocomplete suggestions
 */
function showAutocompleteSuggestions(suggestions) {
    if (!editor) return;

    // Monaco handles autocomplete automatically
    // This is a placeholder for custom suggestion handling
}

/**
 * Format code
 */
function formatCode() {
    if (!editor) return;

    editor.getAction('editor.action.formatDocument').run();
}

/**
 * Get code statistics
 */
function getCodeStatistics() {
    if (!editor) return null;

    const code = editor.getValue();
    const lines = code.split('\n');
    const characters = code.length;
    const words = code.split(/\s+/).length;

    return {
        lines: lines.length,
        characters: characters,
        words: words,
        nonEmptyLines: lines.filter(line => line.trim().length > 0).length
    };
}

/**
 * Export code as file
 */
function exportCode(filename = 'code.py') {
    const code = getEditorContent();
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(code));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

/**
 * Load theme preference from localStorage
 */
function loadThemePreference() {
    const savedTheme = localStorage.getItem('editorTheme');
    if (savedTheme) {
        editorTheme = savedTheme;
    }
}

// Initialize on document ready
document.addEventListener('DOMContentLoaded', () => {
    loadThemePreference();
    // Monaco initialization will be called when needed
});

// Export functions
window.initializeMonacoEditor = initializeMonacoEditor;
window.setEditorLanguage = setEditorLanguage;
window.setEditorFontSize = setEditorFontSize;
window.getEditorContent = getEditorContent;
window.setEditorContent = setEditorContent;
window.clearEditor = clearEditor;
window.formatCode = formatCode;
window.exportCode = exportCode;
window.getCodeStatistics = getCodeStatistics;
