const app = document.getElementById('app');

if (!app) {
  throw new Error('App root not found');
}

app.innerHTML = `
  <main style="max-width: 1100px; margin: 0 auto; padding: 24px; font-family: sans-serif; color: #1f2937;">
    <header style="display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap;">
      <div>
        <h1 style="margin: 0; font-size: 28px;">Voice Draft Studio</h1>
        <p style="margin: 6px 0 0; color: #6b7280;">口述メモから要点抽出、ブログ/クラファン本文に整形する流れを試せます。</p>
      </div>
      <div style="padding: 8px 12px; border-radius: 999px; background: #eef2ff; color: #4338ca; font-size: 14px;">MVP / Local Demo</div>
    </header>

    <section style="margin-top: 24px; display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 20px;">
      <div style="padding: 16px; border: 1px solid #e5e7eb; border-radius: 16px; background: white; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
        <h2 style="margin: 0 0 8px; font-size: 18px;">1. 口述内容を入力</h2>
        <p style="margin: 0 0 12px; color: #6b7280; font-size: 14px;">マイクに向かって話すか、直接書き込んで下書きとして保存します。</p>
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
          <button id="micBtn" style="padding: 10px 14px; border: none; border-radius: 10px; background: #dc2626; color: white; cursor: pointer;">🎤 音声入力を開始</button>
          <span id="micStatus" style="font-size: 13px; color: #6b7280;"></span>
        </div>
        <div id="timeline" style="display: none; max-height: 180px; overflow-y: auto; margin-bottom: 10px; padding: 10px; background: #f8fafc; border-radius: 10px; border: 1px solid #e5e7eb;"></div>
        <div id="interimText" style="display: none; margin-bottom: 10px; padding: 8px 12px; color: #9ca3af; font-size: 14px; font-style: italic;"></div>
        <textarea id="rawText" rows="8" style="width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 10px; font-size: 14px; resize: vertical;" placeholder="ここに話した内容が溜まっていきます。直接入力・編集もできます。">今日は子どもたちが楽しく学べるプログラミング教室でした。保護者の方に学びの楽しさを伝えることができました。</textarea>
        <div style="margin-top: 12px;">
          <button id="createDraftBtn" style="padding: 10px 14px; border: none; border-radius: 10px; background: #2563eb; color: white; cursor: pointer;">下書きとして保存</button>
        </div>
        <pre id="draftResult" style="margin-top: 12px; white-space: pre-wrap; background: #f8fafc; padding: 12px; border-radius: 10px; font-size: 12px; min-height: 80px;"></pre>
      </div>

      <div style="padding: 16px; border: 1px solid #e5e7eb; border-radius: 16px; background: white; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
        <h2 style="margin: 0 0 8px; font-size: 18px;">2. 要点抽出</h2>
        <p style="margin: 0 0 12px; color: #6b7280; font-size: 14px;">入力済みの原稿から、要点と引用候補を整理します。</p>
        <button id="extractBtn" disabled style="padding: 10px 14px; border: none; border-radius: 10px; background: #6b7280; color: white; cursor: not-allowed;">要点抽出を実行</button>
        <pre id="extractResult" style="margin-top: 12px; white-space: pre-wrap; background: #f8fafc; padding: 12px; border-radius: 10px; font-size: 12px; min-height: 120px;"></pre>
      </div>
    </section>

    <section style="margin-top: 20px; padding: 16px; border: 1px solid #e5e7eb; border-radius: 16px; background: white; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
      <h2 style="margin: 0 0 8px; font-size: 18px;">3. 生成結果の編集</h2>
      <p style="margin: 0 0 12px; color: #6b7280; font-size: 14px;">ブログ用またはクラファン用に整形した本文を確認できます。</p>
      <div style="display: flex; gap: 8px; flex-wrap: wrap;">
        <button id="blogBtn" disabled style="padding: 10px 14px; border: none; border-radius: 10px; background: #6b7280; color: white; cursor: not-allowed;">ブログ生成</button>
        <button id="crowdfundingBtn" disabled style="padding: 10px 14px; border: none; border-radius: 10px; background: #6b7280; color: white; cursor: not-allowed;">クラファン生成</button>
      </div>
      <pre id="generateResult" style="margin-top: 12px; white-space: pre-wrap; background: #f8fafc; padding: 12px; border-radius: 10px; font-size: 12px; min-height: 140px;"></pre>
    </section>

    <section style="margin-top: 20px; padding: 16px; border: 1px solid #e5e7eb; border-radius: 16px; background: white; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
      <h2 style="margin: 0 0 8px; font-size: 18px;">4. 挿絵生成</h2>
      <p style="margin: 0 0 12px; color: #6b7280; font-size: 14px;">要点からDALL-E用プロンプトのたたき台を作り、編集してから画像を生成します。生成後、使う画像をクリックして選択してください。</p>
      <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-bottom: 10px;">
        <select id="imageType" style="padding: 9px 10px; border: 1px solid #d1d5db; border-radius: 10px; font-size: 14px;">
          <option value="illustration">イメージ画像風</option>
          <option value="slide">スライド風</option>
        </select>
        <button id="promptDraftBtn" disabled style="padding: 10px 14px; border: none; border-radius: 10px; background: #6b7280; color: white; cursor: not-allowed;">プロンプトたたき台を生成</button>
      </div>
      <textarea id="imagePrompt" rows="4" style="width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 10px; font-size: 14px; resize: vertical;" placeholder="ここにDALL-E用プロンプト（英語）が入ります。自由に編集してから生成してください。"></textarea>
      <div style="margin-top: 10px; display: flex; gap: 8px; align-items: center;">
        <button id="imageBtn" disabled style="padding: 10px 14px; border: none; border-radius: 10px; background: #6b7280; color: white; cursor: not-allowed;">画像を生成（3枚）</button>
        <span id="imageStatus" style="font-size: 13px; color: #6b7280;"></span>
      </div>
      <div id="imageGrid" style="margin-top: 12px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;"></div>
      <p id="selectedImage" style="margin: 10px 0 0; font-size: 13px; color: #6b7280;"></p>
    </section>
  </main>
`;

let draftId: string | null = null;
let extractedPoints: string | null = null;
let generatedBody: string | null = null;

const draftResult = document.getElementById('draftResult') as HTMLPreElement;
const extractResult = document.getElementById('extractResult') as HTMLPreElement;
const generateResult = document.getElementById('generateResult') as HTMLPreElement;
const extractBtn = document.getElementById('extractBtn') as HTMLButtonElement;
const blogBtn = document.getElementById('blogBtn') as HTMLButtonElement;
const crowdfundingBtn = document.getElementById('crowdfundingBtn') as HTMLButtonElement;
const promptDraftBtn = document.getElementById('promptDraftBtn') as HTMLButtonElement;
const imageBtn = document.getElementById('imageBtn') as HTMLButtonElement;
const imageTypeSelect = document.getElementById('imageType') as HTMLSelectElement;
const imagePromptArea = document.getElementById('imagePrompt') as HTMLTextAreaElement;
const imageStatus = document.getElementById('imageStatus') as HTMLSpanElement;
const imageGrid = document.getElementById('imageGrid') as HTMLDivElement;
const selectedImage = document.getElementById('selectedImage') as HTMLParagraphElement;

const setButtonState = (button: HTMLButtonElement, enabled: boolean) => {
  button.disabled = !enabled;
  button.style.background = enabled ? '#2563eb' : '#6b7280';
  button.style.cursor = enabled ? 'pointer' : 'not-allowed';
};

// --- 音声入力 (Web Speech API) ---
const micBtn = document.getElementById('micBtn') as HTMLButtonElement;
const micStatus = document.getElementById('micStatus') as HTMLSpanElement;
const timeline = document.getElementById('timeline') as HTMLDivElement;
const interimText = document.getElementById('interimText') as HTMLDivElement;
const rawTextArea = document.getElementById('rawText') as HTMLTextAreaElement;

const SpeechRecognitionImpl =
  (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

let recognizing = false;

const addTimelineChip = (text: string) => {
  timeline.style.display = 'block';
  const chip = document.createElement('div');
  chip.textContent = text;
  chip.style.cssText =
    'padding: 8px 12px; margin-top: 6px; background: white; border: 1px solid #e5e7eb; border-radius: 10px; font-size: 14px; opacity: 0; transition: opacity 0.4s;';
  timeline.appendChild(chip);
  requestAnimationFrame(() => { chip.style.opacity = '1'; });
  // 少し経ったら「過去の発話」として薄くする
  setTimeout(() => { chip.style.opacity = '0.55'; }, 5000);
  timeline.scrollTop = timeline.scrollHeight;
};

const appendToRawText = (text: string) => {
  const current = rawTextArea.value.trim();
  rawTextArea.value = current ? `${current}\n${text}` : text;
};

if (!SpeechRecognitionImpl) {
  micBtn.disabled = true;
  micBtn.style.background = '#6b7280';
  micBtn.style.cursor = 'not-allowed';
  micStatus.textContent = 'このブラウザは音声認識に未対応です（Chrome / Edge を使ってください）';
} else {
  const recognition = new SpeechRecognitionImpl();
  recognition.lang = 'ja-JP';
  recognition.continuous = true;
  recognition.interimResults = true;

  recognition.onresult = (event: any) => {
    let interim = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const result = event.results[i];
      const transcript = result[0].transcript.trim();
      if (result.isFinal && transcript) {
        addTimelineChip(transcript);
        appendToRawText(transcript);
      } else {
        interim += result[0].transcript;
      }
    }
    interimText.style.display = interim ? 'block' : 'none';
    interimText.textContent = interim;
  };

  recognition.onerror = (event: any) => {
    if (event.error === 'not-allowed') {
      recognizing = false;
      micBtn.textContent = '🎤 音声入力を開始';
      micStatus.textContent = 'マイクの使用が許可されていません。ブラウザの設定を確認してください。';
    }
  };

  // Chromeは沈黙が続くと自動停止するため、録音中なら再開する
  recognition.onend = () => {
    if (recognizing) {
      recognition.start();
    } else {
      interimText.style.display = 'none';
      micStatus.textContent = '';
    }
  };

  micBtn.addEventListener('click', () => {
    if (recognizing) {
      recognizing = false;
      recognition.stop();
      micBtn.textContent = '🎤 音声入力を開始';
      micBtn.style.background = '#dc2626';
      micStatus.textContent = '';
    } else {
      recognizing = true;
      recognition.start();
      micBtn.textContent = '⏹ 停止';
      micBtn.style.background = '#1f2937';
      micStatus.textContent = '聞き取り中... 話した内容が下のテキストに追加されます';
    }
  });
}

const api = async (path: string, options?: RequestInit) => {
  const response = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Request failed');
  }
  return data;
};

(document.getElementById('createDraftBtn') as HTMLButtonElement).addEventListener('click', async () => {
  const rawText = (document.getElementById('rawText') as HTMLTextAreaElement).value;
  draftResult.textContent = '作成中...';

  try {
    const data = await api('/drafts', {
      method: 'POST',
      body: JSON.stringify({ raw_text: rawText, author: 'browser-user', tenant_id: 'aiaruku', tags: ['demo'] }),
    });
    draftId = data.draft_id;
    draftResult.textContent = JSON.stringify(data, null, 2);
    setButtonState(extractBtn, true);
    setButtonState(blogBtn, true);
    setButtonState(crowdfundingBtn, true);
  } catch (error) {
    draftResult.textContent = error instanceof Error ? error.message : 'Error';
  }
});

extractBtn.addEventListener('click', async () => {
  if (!draftId) {
    extractResult.textContent = '先に下書きを作成してください';
    return;
  }

  try {
    const data = await api(`/drafts/${draftId}/extract`, {
      method: 'POST',
      body: JSON.stringify({ draft_id: draftId, tenant_id: 'aiaruku' }),
    });
    extractResult.textContent = JSON.stringify(data, null, 2);
    extractedPoints = data.extracted_points;
    setButtonState(promptDraftBtn, true);
  } catch (error) {
    extractResult.textContent = error instanceof Error ? error.message : 'Error';
  }
});

// --- 挿絵生成 ---
promptDraftBtn.addEventListener('click', async () => {
  if (!extractedPoints) {
    imageStatus.textContent = '先に要点抽出を実行してください';
    return;
  }

  imageStatus.textContent = 'プロンプト生成中...';
  promptDraftBtn.disabled = true;
  try {
    const data = await api('/generate/image/prompt-draft', {
      method: 'POST',
      body: JSON.stringify({
        extracted_points: extractedPoints,
        image_type: imageTypeSelect.value,
        tenant_id: 'aiaruku',
        body_text: generatedBody,
      }),
    });
    imagePromptArea.value = data.prompt;
    imageStatus.textContent = 'プロンプトを編集してから「画像を生成」を押してください';
    setButtonState(imageBtn, true);
  } catch (error) {
    imageStatus.textContent = error instanceof Error ? error.message : 'Error';
  } finally {
    promptDraftBtn.disabled = false;
    setButtonState(promptDraftBtn, true);
  }
});

imageBtn.addEventListener('click', async () => {
  const prompt = imagePromptArea.value.trim();
  if (!prompt) {
    imageStatus.textContent = 'プロンプトを入力してください';
    return;
  }

  imageStatus.textContent = '画像生成中...（30秒〜1分ほどかかります）';
  setButtonState(imageBtn, false);
  imageGrid.innerHTML = '';
  selectedImage.textContent = '';

  try {
    const data = await api('/generate/image', {
      method: 'POST',
      body: JSON.stringify({
        prompt,
        image_type: imageTypeSelect.value,
        draft_id: draftId,
        tenant_id: 'aiaruku',
        n: 3,
      }),
    });

    const aspectRatio = imageTypeSelect.value === 'slide' ? '3 / 2' : '1';
    for (const image of data.images) {
      const img = document.createElement('img');
      img.src = image.image_url;
      // ぼかし→クリア演出: 読み込み完了までぼかし、届いた瞬間にクリアへ
      img.style.cssText =
        `width: 100%; aspect-ratio: ${aspectRatio}; object-fit: cover; border-radius: 12px; border: 3px solid transparent; cursor: pointer; filter: blur(12px); transition: filter 0.6s, border-color 0.2s;`;
      img.addEventListener('load', () => { img.style.filter = 'blur(0)'; });
      img.addEventListener('click', () => {
        imageGrid.querySelectorAll('img').forEach((el) => { el.style.borderColor = 'transparent'; });
        img.style.borderColor = '#2563eb';
        selectedImage.textContent = `選択中: ${image.image_url}（この画像をブログのアイキャッチ/挿絵として使います）`;
      });
      imageGrid.appendChild(img);
    }
    imageStatus.textContent = '使う画像をクリックして選択してください';
  } catch (error) {
    imageStatus.textContent = error instanceof Error ? error.message : 'Error';
  } finally {
    setButtonState(imageBtn, true);
  }
});

blogBtn.addEventListener('click', async () => {
  if (!draftId) {
    generateResult.textContent = '先に下書きを作成してください';
    return;
  }

  try {
    const data = await api('/generate/blog', {
      method: 'POST',
      body: JSON.stringify({ draft_id: draftId, output_type: 'blog', tenant_id: 'aiaruku' }),
    });
    generateResult.textContent = JSON.stringify(data, null, 2);
    generatedBody = data.body;
  } catch (error) {
    generateResult.textContent = error instanceof Error ? error.message : 'Error';
  }
});

crowdfundingBtn.addEventListener('click', async () => {
  if (!draftId) {
    generateResult.textContent = '先に下書きを作成してください';
    return;
  }

  try {
    const data = await api('/generate/crowdfunding', {
      method: 'POST',
      body: JSON.stringify({ draft_id: draftId, output_type: 'crowdfunding', tenant_id: 'aiaruku' }),
    });
    generateResult.textContent = JSON.stringify(data, null, 2);
    generatedBody = data.body;
  } catch (error) {
    generateResult.textContent = error instanceof Error ? error.message : 'Error';
  }
});
