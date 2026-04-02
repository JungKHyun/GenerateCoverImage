import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add aiModel dropdown to UI
ai_model_html = """                <div class="input-group">
                    <label for="aiModel">생성 모델</label>
                    <select id="aiModel" class="prompt-input">
                        <option value="gemini-2.5-flash">Gemini 2.5 Flash Preview Image</option>
                        <option value="gemini-3.0-pro">Gemini 3 Pro Image</option>
                        <option value="gemini-3.1-flash">Gemini 3.1 Flash Image</option>
                        <option value="imagen-3.0-generate-001">Imagen 3.0 Generate 001</option>
                    </select>
                </div>
"""
# insert inside category-block of "API 설정" after apiKey
html = html.replace('</div>\n\n            <!-- 브랜드 & 기업 -->', '</div>\n\n            <!-- AI 모델 선택 -->\n' + ai_model_html + '            <!-- 브랜드 & 기업 -->')

# 2. Add <option value="other"> and hidden inputs to all other selects
selects_to_mod = ['brandTone', 'mood', 'audienceLevel', 'audienceContext', 'style', 'subject', 'negativeSpace', 'colorPalette']
for sel_id in selects_to_mod:
    pattern = r'(<select id="' + sel_id + '".*?>.*?)(</select>)'
    def repl(m):
        content = m.group(1)
        if '<option value="other">' not in content:
            content += '                        <option value="other">기타 (직접 입력)</option>\n                    '
        return content + '</select>\n                    <input type="text" id="' + sel_id + 'Other" class="prompt-input" placeholder="직접 입력..." style="display: none; margin-top: 0.5rem;" />'
    html = re.sub(pattern, repl, html, flags=re.DOTALL)

# 3. Modify buildState
build_state_orig = """            return {
                brandText: getVal('brandText').trim(),
                industry: getVal('industry') === 'other' ? getVal('industryOther').trim() : getVal('industry'),
                brandTone: getVal('brandTone'),
                mood: getVal('mood'),
                audienceLevel: getVal('audienceLevel'),
                audienceContext: getVal('audienceContext'),
                style: getVal('style'),
                subject: getVal('subject'),
                negativeSpace: getVal('negativeSpace'),
                colorPalette: getVal('colorPalette'),
                background: getVal('background') === 'other' ? getVal('backgroundOther').trim() : getVal('background'),
                quality: getMulti('qualityGroup'),
                negative: getMulti('negativeGroup'),
                aspectRatio: getVal('aspectRatio')
            };"""

build_state_new = """            return {
                brandText: getVal('brandText').trim(),
                industry: getVal('industry') === 'other' ? getVal('industryOther').trim() : getVal('industry'),
                brandTone: getVal('brandTone') === 'other' ? getVal('brandToneOther').trim() : getVal('brandTone'),
                mood: getVal('mood') === 'other' ? getVal('moodOther').trim() : getVal('mood'),
                audienceLevel: getVal('audienceLevel') === 'other' ? getVal('audienceLevelOther').trim() : getVal('audienceLevel'),
                audienceContext: getVal('audienceContext') === 'other' ? getVal('audienceContextOther').trim() : getVal('audienceContext'),
                style: getVal('style') === 'other' ? getVal('styleOther').trim() : getVal('style'),
                subject: getVal('subject') === 'other' ? getVal('subjectOther').trim() : getVal('subject'),
                negativeSpace: getVal('negativeSpace') === 'other' ? getVal('negativeSpaceOther').trim() : getVal('negativeSpace'),
                colorPalette: getVal('colorPalette') === 'other' ? getVal('colorPaletteOther').trim() : getVal('colorPalette'),
                background: getVal('background') === 'other' ? getVal('backgroundOther').trim() : getVal('background'),
                quality: getMulti('qualityGroup'),
                negative: getMulti('negativeGroup'),
                aspectRatio: getVal('aspectRatio')
            };"""
html = html.replace(build_state_orig, build_state_new)

# 4. Modify event listeners
old_listeners = """        // Event listener for Industry 'Other' toggle
        const industrySelect = document.getElementById('industry');
        const industryOtherInput = document.getElementById('industryOther');
        industrySelect.addEventListener('change', (e) => {
            if (e.target.value === 'other') {
                industryOtherInput.style.display = 'block';
                industryOtherInput.focus();
            } else {
                industryOtherInput.style.display = 'none';
                industryOtherInput.value = ''; // clear the hidden input
            }
        });

        // Event listener for Background 'Other' toggle
        const backgroundSelect = document.getElementById('background');
        const backgroundOtherInput = document.getElementById('backgroundOther');
        backgroundSelect.addEventListener('change', (e) => {
            if (e.target.value === 'other') {
                backgroundOtherInput.style.display = 'block';
                backgroundOtherInput.focus();
            } else {
                backgroundOtherInput.style.display = 'none';
                backgroundOtherInput.value = ''; // clear the hidden input
            }
        });"""

new_listeners = """        // Event listener for all 'Other' toggles
        const otherFields = [
            'industry', 'brandTone', 'mood', 'audienceLevel', 'audienceContext', 
            'style', 'subject', 'negativeSpace', 'colorPalette', 'background'
        ];

        otherFields.forEach(field => {
            const selectEl = document.getElementById(field);
            const otherInput = document.getElementById(field + 'Other');
            if(selectEl && otherInput) {
                selectEl.addEventListener('change', (e) => {
                    if (e.target.value === 'other') {
                        otherInput.style.display = 'block';
                        otherInput.focus();
                    } else {
                        otherInput.style.display = 'none';
                        otherInput.value = ''; // clear the hidden input
                        updatePrompts();
                    }
                });
            }
        });"""
html = html.replace(old_listeners, new_listeners)

# 5. Fix API generation endpoint and request body
api_fetch_old = """            // Use Google AI Studio Endpoint
            const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict`;
            
            const requestBody = {
                instances: [
                    { prompt: positivePrompt }
                ],
                parameters: {
                    sampleCount: 1,
                    aspectRatio: state.aspectRatio,
                }
            };

            // 부정 프롬프트가 있을 때만 추가
            if (negativePrompt) {
                requestBody.parameters.negativePrompt = negativePrompt;
            }

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'x-goog-api-key': apiKey,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestBody)
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    console.error("API Error details:", errorData);
                    
                    if (response.status === 400) throw new Error("프롬프트가 거절되었거나 형식이 잘못되었습니다.");
                    if (response.status === 401 || response.status === 403) throw new Error("API Key가 유효하지 않거나 권한이 없습니다.");
                    if (response.status === 429) throw new Error("요청 한도를 초과했습니다. 잠시 후 시도해주세요.");
                    
                    // 상세 에러가 있는 경우 추가
                    let detailMsg = errorData.error?.message ? ` - ${errorData.error.message}` : "";
                    throw new Error(`API 오류가 발생했습니다 (${response.status})${detailMsg}`);
                }

                const data = await response.json();
                
                if (data.predictions && data.predictions.length > 0 && data.predictions[0].bytesBase64Encoded) {
                    const base64Data = data.predictions[0].bytesBase64Encoded;
                    const mimeType = data.predictions[0].mimeType || 'image/png';
                    const dataUrl = `data:${mimeType};base64,${base64Data}`;"""

api_fetch_new = """            const aiModel = document.getElementById('aiModel').value || 'gemini-3.0-pro';
            const isGemini = aiModel.includes('gemini');
            
            // Build endpoints and request body based on model type
            let endpoint = '';
            let requestBody = {};
            
            if (isGemini) {
                endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${aiModel}:generateContent?key=${apiKey}`;
                
                let promptText = positivePrompt;
                if (negativePrompt) promptText += "\\nNegative prompt: " + negativePrompt;
                
                requestBody = {
                    "contents": [{
                        "parts": [{"text": promptText}]
                    }],
                    "generationConfig": {
                        "responseModalities": ["IMAGE"]
                    }
                };
            } else {
                endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${aiModel}:predict?key=${apiKey}`;
                
                requestBody = {
                    instances: [
                        { prompt: positivePrompt }
                    ],
                    parameters: {
                        sampleCount: 1,
                        aspectRatio: state.aspectRatio,
                    }
                };
                if (negativePrompt) {
                    requestBody.parameters.negativePrompt = negativePrompt;
                }
            }

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestBody)
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    console.error("API Error details:", errorData);
                    let detailMsg = errorData.error?.message ? ` - ${errorData.error.message}` : "";
                    throw new Error(`API 오류가 발생했습니다 (${response.status})${detailMsg}`);
                }

                const data = await response.json();
                let base64Data = null;
                let mimeType = 'image/jpeg';
                
                if (isGemini) {
                    // Extract from generateContent response geometry
                    if (data.candidates && data.candidates[0].content && data.candidates[0].content.parts[0].inlineData) {
                        const inline = data.candidates[0].content.parts[0].inlineData;
                        base64Data = inline.data;
                        mimeType = inline.mimeType;
                    }
                } else {
                    // Extract from predict response
                    if (data.predictions && data.predictions.length > 0 && data.predictions[0].bytesBase64Encoded) {
                        base64Data = data.predictions[0].bytesBase64Encoded;
                        mimeType = data.predictions[0].mimeType || 'image/png';
                    }
                }
                
                if (base64Data) {
                    const dataUrl = `data:${mimeType};base64,${base64Data}`;"""
                    
html = html.replace(api_fetch_old, api_fetch_new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
