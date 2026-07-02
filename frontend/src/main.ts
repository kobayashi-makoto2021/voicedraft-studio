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
        <p style="margin: 0 0 12px; color: #6b7280; font-size: 14px;">話し言葉をそのまま書き込んで、下書きとして保存します。</p>
        <textarea id="rawText" rows="8" style="width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 10px; font-size: 14px; resize: vertical;">今日は子どもたちが楽しく学べるプログラミング教室でした。保護者の方に学びの楽しさを伝えることができました。</textarea>
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
  </main>
`;

let draftId: string | null = null;

const draftResult = document.getElementById('draftResult') as HTMLPreElement;
const extractResult = document.getElementById('extractResult') as HTMLPreElement;
const generateResult = document.getElementById('generateResult') as HTMLPreElement;
const extractBtn = document.getElementById('extractBtn') as HTMLButtonElement;
const blogBtn = document.getElementById('blogBtn') as HTMLButtonElement;
const crowdfundingBtn = document.getElementById('crowdfundingBtn') as HTMLButtonElement;

const setButtonState = (button: HTMLButtonElement, enabled: boolean) => {
  button.disabled = !enabled;
  button.style.background = enabled ? '#2563eb' : '#6b7280';
  button.style.cursor = enabled ? 'pointer' : 'not-allowed';
};

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
  } catch (error) {
    extractResult.textContent = error instanceof Error ? error.message : 'Error';
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
  } catch (error) {
    generateResult.textContent = error instanceof Error ? error.message : 'Error';
  }
});
