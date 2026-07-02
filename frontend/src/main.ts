const app = document.getElementById('app');

if (!app) {
  throw new Error('App root not found');
}

app.innerHTML = `
  <main style="max-width: 900px; margin: 0 auto; padding: 24px; font-family: sans-serif;">
    <h1>Voice Draft Studio</h1>
    <p style="margin-top: 8px; color: #555;">口述メモから下書き・要点抽出・本文生成までをローカルで試せます。</p>

    <section style="margin-top: 24px; padding: 16px; border: 1px solid #ddd; border-radius: 12px; background: white;">
      <h2>1. 口述内容を入力</h2>
      <textarea id="rawText" rows="6" style="width: 100%; padding: 8px; margin-top: 8px;">今日は子どもたちが楽しく学べるプログラミング教室でした。</textarea>
      <div style="margin-top: 12px;">
        <button id="createDraftBtn">下書き作成</button>
      </div>
      <pre id="draftResult" style="margin-top: 12px; white-space: pre-wrap; background: #f8f8f8; padding: 12px; border-radius: 8px;"></pre>
    </section>

    <section style="margin-top: 24px; padding: 16px; border: 1px solid #ddd; border-radius: 12px; background: white;">
      <h2>2. 要点抽出</h2>
      <button id="extractBtn" disabled>要点抽出</button>
      <pre id="extractResult" style="margin-top: 12px; white-space: pre-wrap; background: #f8f8f8; padding: 12px; border-radius: 8px;"></pre>
    </section>

    <section style="margin-top: 24px; padding: 16px; border: 1px solid #ddd; border-radius: 12px; background: white;">
      <h2>3. 本文生成</h2>
      <button id="blogBtn" disabled>ブログ本文を生成</button>
      <button id="crowdfundingBtn" disabled style="margin-left: 8px;">クラファン本文を生成</button>
      <pre id="generateResult" style="margin-top: 12px; white-space: pre-wrap; background: #f8f8f8; padding: 12px; border-radius: 8px;"></pre>
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
    extractBtn.disabled = false;
    blogBtn.disabled = false;
    crowdfundingBtn.disabled = false;
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
